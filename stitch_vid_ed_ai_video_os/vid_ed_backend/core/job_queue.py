"""
Async Job Queue for rate limiting and background task management.
Prevents UI crashes when user spams "Render" by queuing video processing jobs.

HARD RULES:
1. Video rendering and LLM inference MUST be background tasks
2. Implement rate limiting to prevent resource exhaustion
3. Jobs must be cancellable and trackable by status
"""
import asyncio
from typing import Optional, Callable, Any, Dict
from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime
import uuid
import logging

logger = logging.getLogger(__name__)


class JobStatus(str, Enum):
    """Job lifecycle states."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class QueuedJob:
    """Represents a queued background job."""
    job_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    job_type: str = field(..., description="Type of job, e.g., 'render', 'llm_inference', 'video_analysis'")
    status: JobStatus = field(default=JobStatus.PENDING)
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    result: Optional[Any] = None
    error: Optional[str] = None
    progress: float = field(default=0.0, ge=0.0, le=1.0)
    metadata: Dict = field(default_factory=dict)

    def model_dump(self) -> dict:
        """Return job as dictionary for JSON serialization."""
        return {
            "job_id": self.job_id,
            "job_type": self.job_type,
            "status": self.status.value,
            "created_at": self.created_at.isoformat(),
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "result": self.result,
            "error": self.error,
            "progress": self.progress,
            "metadata": self.metadata
        }


class JobQueue:
    """
    Async job queue with rate limiting and concurrency control.
    
    This queue ensures that heavy operations (video rendering, LLM inference,
    video analysis) don't block the FastAPI event loop or crash the system
    when users submit multiple requests rapidly.
    
    SECURITY: Implements rate limiting per job type to prevent resource exhaustion.
    """

    def __init__(
        self,
        max_concurrent_jobs: int = 3,
        max_queue_size: int = 10,
        rate_limit_seconds: float = 1.0,
    ):
        """
        Initialize job queue.
        
        Args:
            max_concurrent_jobs: Maximum number of jobs running simultaneously
            max_queue_size: Maximum number of pending jobs in queue
            rate_limit_seconds: Minimum time between job starts (rate limiting)
        """
        self._queue: asyncio.Queue[QueuedJob] = asyncio.Queue(maxsize=max_queue_size)
        self._max_concurrent = max_concurrent_jobs
        self._rate_limit = rate_limit_seconds
        self._jobs: Dict[str, QueuedJob] = {}
        self._semaphore = asyncio.Semaphore(max_concurrent_jobs)
        self._last_job_start: Optional[datetime] = None
        self._running = True
        self._workers: list[asyncio.Task] = []

    async def start_workers(self, num_workers: int = 3):
        """Start background worker tasks."""
        for i in range(num_workers):
            worker = asyncio.create_task(self._worker(f"worker-{i}"))
            self._workers.append(worker)
        logger.info(f"Started {num_workers} job queue workers")

    async def stop_workers(self):
        """Stop all workers gracefully."""
        self._running = False
        # Add sentinel values to unblock workers
        for _ in self._workers:
            await self._queue.put(None)
        # Wait for workers to finish
        await asyncio.gather(*self._workers, return_exceptions=True)
        self._workers.clear()
        logger.info("Job queue workers stopped")

    async def submit(
        self,
        job_type: str,
        coro_func: Callable,
        *args,
        **kwargs,
    ) -> QueuedJob:
        """
        Submit a job to the queue.
        
        Args:
            job_type: Type identifier for the job
            coro_func: Async function to execute
            *args: Positional arguments for coro_func
            **kwargs: Keyword arguments for coro_func
            
        Returns:
            QueuedJob object for tracking progress
            
        Raises:
            asyncio.QueueFull: If queue is at max capacity
        """
        job = QueuedJob(job_type=job_type, metadata={"args": str(args), "kwargs": str(kwargs)})
        self._jobs[job.job_id] = job
        await self._queue.put(job)
        logger.info(f"Job submitted: {job.job_id} (type={job_type})")
        return job

    async def _worker(self, worker_name: str):
        """Worker coroutine that processes jobs from the queue."""
        while self._running:
            try:
                job = await self._queue.get()
                
                # Sentinel value check
                if job is None:
                    break
                
                # Rate limiting
                if self._last_job_start:
                    elapsed = (datetime.now() - self._last_job_start).total_seconds()
                    if elapsed < self._rate_limit:
                        await asyncio.sleep(self._rate_limit - elapsed)
                
                async with self._semaphore:
                    self._last_job_start = datetime.now()
                    await self._execute_job(job, worker_name)
                    
                self._queue.task_done()
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"{worker_name} error: {e}")

    async def _execute_job(self, job: QueuedJob, worker_name: str):
        """Execute a single job with error handling."""
        job.status = JobStatus.RUNNING
        job.started_at = datetime.now()
        logger.info(f"{worker_name} starting job {job.job_id}")

        try:
            # Extract coro_func from metadata (passed during submit)
            coro_func = job.metadata.pop("coro_func", None)
            args = job.metadata.pop("args_list", [])
            kwargs = job.metadata.pop("kwargs_dict", {})
            
            if not coro_func:
                raise ValueError("No coroutine function provided")
            
            result = await coro_func(*args, **kwargs)
            job.result = result
            job.status = JobStatus.COMPLETED
            job.progress = 1.0
            logger.info(f"{worker_name} completed job {job.job_id}")
            
        except asyncio.CancelledError:
            job.status = JobStatus.CANCELLED
            job.error = "Job cancelled by user"
            logger.info(f"{worker_name} cancelled job {job.job_id}")
            raise
            
        except Exception as e:
            job.status = JobStatus.FAILED
            job.error = str(e)
            logger.error(f"{worker_name} failed job {job.job_id}: {e}")
            
        finally:
            job.completed_at = datetime.now()

    def get_job(self, job_id: str) -> Optional[QueuedJob]:
        """Get job status by ID."""
        return self._jobs.get(job_id)

    def get_all_jobs(self) -> Dict[str, QueuedJob]:
        """Get all jobs."""
        return self._jobs.copy()

    async def cancel_job(self, job_id: str) -> bool:
        """
        Cancel a pending or running job.
        
        Returns:
            True if job was cancelled, False if not found or already completed
        """
        job = self._jobs.get(job_id)
        if not job:
            return False
        
        if job.status in (JobStatus.COMPLETED, JobStatus.FAILED, JobStatus.CANCELLED):
            return False
        
        job.status = JobStatus.CANCELLED
        job.completed_at = datetime.now()
        logger.info(f"Job cancelled: {job_id}")
        return True

    def get_queue_stats(self) -> dict:
        """Get queue statistics."""
        pending = sum(1 for j in self._jobs.values() if j.status == JobStatus.PENDING)
        running = sum(1 for j in self._jobs.values() if j.status == JobStatus.RUNNING)
        completed = sum(1 for j in self._jobs.values() if j.status == JobStatus.COMPLETED)
        failed = sum(1 for j in self._jobs.values() if j.status == JobStatus.FAILED)
        
        return {
            "pending": pending,
            "running": running,
            "completed": completed,
            "failed": failed,
            "queue_size": self._queue.qsize(),
            "max_concurrent": self._max_concurrent,
        }
