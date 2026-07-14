"""
Privantrix AI OS - Planner
Creates execution graphs, milestones, and assigns agents (NO CODE WRITING)
"""

import os
import json
from pathlib import Path
from typing import Optional, List, Dict, Any
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class TaskStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    BLOCKED = "blocked"
    FAILED = "failed"


class MilestoneStatus(Enum):
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"


@dataclass
class Task:
    id: str
    title: str
    description: str
    status: TaskStatus = TaskStatus.PENDING
    assigned_agent: Optional[str] = None
    dependencies: List[str] = field(default_factory=list)
    estimated_duration_minutes: int = 30
    actual_duration_minutes: int = 0
    created_at: str = ""
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    
    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now().isoformat()
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id, "title": self.title, "description": self.description,
            "status": self.status.value, "assigned_agent": self.assigned_agent,
            "dependencies": self.dependencies, "estimated_duration_minutes": self.estimated_duration_minutes,
            "actual_duration_minutes": self.actual_duration_minutes,
            "created_at": self.created_at, "started_at": self.started_at, "completed_at": self.completed_at
        }


@dataclass
class Milestone:
    id: str
    name: str
    description: str
    status: MilestoneStatus = MilestoneStatus.NOT_STARTED
    tasks: List[str] = field(default_factory=list)
    target_date: Optional[str] = None
    completed_at: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id, "name": self.name, "description": self.description,
            "status": self.status.value, "tasks": self.tasks,
            "target_date": self.target_date, "completed_at": self.completed_at
        }


class Planner:
    """Plans execution without writing code"""
    
    def __init__(self, memory_dir: str = "memory", checkpoints_dir: str = "checkpoints"):
        self.memory_dir = Path(memory_dir)
        self.checkpoints_dir = Path(checkpoints_dir)
        self.memory_dir.mkdir(parents=True, exist_ok=True)
        self.checkpoints_dir.mkdir(parents=True, exist_ok=True)
        
        self._tasks: Dict[str, Task] = {}
        self._milestones: Dict[str, Milestone] = {}
        self._execution_graph: Dict[str, List[str]] = {}
        self._load_state()
    
    def _load_state(self) -> None:
        state_file = self.memory_dir / "planner_state.json"
        if state_file.exists():
            with open(state_file, 'r') as f:
                data = json.load(f)
                for task_data in data.get("tasks", []):
                    task = Task(**task_data)
                    task.status = TaskStatus(task_data["status"])
                    self._tasks[task.id] = task
                for ms_data in data.get("milestones", []):
                    ms = Milestone(**ms_data)
                    ms.status = MilestoneStatus(ms_data["status"])
                    self._milestones[ms.id] = ms
                self._execution_graph = data.get("execution_graph", {})
    
    def _save_state(self) -> None:
        state_file = self.memory_dir / "planner_state.json"
        data = {
            "tasks": [t.to_dict() for t in self._tasks.values()],
            "milestones": [m.to_dict() for m in self._milestones.values()],
            "execution_graph": self._execution_graph
        }
        with open(state_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def create_execution_graph(self, project_memory: Dict[str, Any], roadmap: List[Dict]) -> Dict[str, List[str]]:
        """Create execution graph from project memory and roadmap"""
        self._execution_graph = {}
        
        for i, phase in enumerate(roadmap):
            phase_id = f"phase_{i}"
            self._execution_graph[phase_id] = []
            
            for task_info in phase.get("tasks", []):
                task_id = f"{phase_id}_{len(self._execution_graph[phase_id])}"
                self.create_task(
                    title=task_info.get("title", "Untitled Task"),
                    description=task_info.get("description", ""),
                    dependencies=[f"phase_{i-1}"] if i > 0 else []
                )
                self._execution_graph[phase_id].append(task_id)
        
        self._save_state()
        return self._execution_graph
    
    def create_milestone(self, name: str, description: str, target_date: Optional[str] = None) -> str:
        """Create a new milestone"""
        import hashlib
        ms_id = hashlib.md5(f"{name}{datetime.now()}".encode()).hexdigest()[:12]
        milestone = Milestone(id=ms_id, name=name, description=description, target_date=target_date)
        self._milestones[ms_id] = milestone
        self._save_state()
        return ms_id
    
    def create_task(
        self, title: str, description: str, 
        dependencies: Optional[List[str]] = None,
        estimated_duration: int = 30
    ) -> str:
        """Create a new task"""
        import hashlib
        task_id = hashlib.md5(f"{title}{datetime.now()}".encode()).hexdigest()[:12]
        task = Task(
            id=task_id, title=title, description=description,
            dependencies=dependencies or [],
            estimated_duration_minutes=estimated_duration
        )
        self._tasks[task_id] = task
        self._save_state()
        return task_id
    
    def assign_agent(self, task_id: str, agent_name: str) -> bool:
        """Assign an agent to a task"""
        if task_id in self._tasks:
            self._tasks[task_id].assigned_agent = agent_name
            self._save_state()
            return True
        return False
    
    def update_task_status(self, task_id: str, status: TaskStatus) -> bool:
        """Update task status"""
        if task_id not in self._tasks:
            return False
        
        task = self._tasks[task_id]
        old_status = task.status
        task.status = status
        
        if status == TaskStatus.IN_PROGRESS and old_status != TaskStatus.IN_PROGRESS:
            task.started_at = datetime.now().isoformat()
        elif status == TaskStatus.COMPLETED:
            task.completed_at = datetime.now().isoformat()
            self._update_milestone_progress(task_id)
        
        self._save_state()
        return True
    
    def _update_milestone_progress(self, task_id: str) -> None:
        """Update milestone when task completes"""
        for milestone in self._milestones.values():
            if task_id in milestone.tasks:
                if all(self._tasks.get(tid, Task(id="", title="", description="")).status == TaskStatus.COMPLETED 
                       for tid in milestone.tasks):
                    milestone.status = MilestoneStatus.COMPLETED
                    milestone.completed_at = datetime.now().isoformat()
                elif any(self._tasks.get(tid, Task(id="", title="", description="")).status == TaskStatus.IN_PROGRESS 
                         for tid in milestone.tasks):
                    milestone.status = MilestoneStatus.IN_PROGRESS
    
    def add_task_to_milestone(self, milestone_id: str, task_id: str) -> bool:
        """Add task to milestone"""
        if milestone_id in self._milestones and task_id in self._tasks:
            if task_id not in self._milestones[milestone_id].tasks:
                self._milestones[milestone_id].tasks.append(task_id)
            self._save_state()
            return True
        return False
    
    def get_ready_tasks(self) -> List[Task]:
        """Get tasks ready to execute (dependencies met)"""
        ready = []
        for task in self._tasks.values():
            if task.status != TaskStatus.PENDING:
                continue
            
            deps_met = all(
                self._tasks.get(dep_id, Task(id="", title="", description="")).status == TaskStatus.COMPLETED
                for dep_id in task.dependencies
            )
            
            if deps_met:
                ready.append(task)
        
        return ready
    
    def get_pending_tasks(self) -> List[Task]:
        """Get all pending tasks"""
        return [t for t in self._tasks.values() if t.status == TaskStatus.PENDING]
    
    def get_in_progress_tasks(self) -> List[Task]:
        """Get all in-progress tasks"""
        return [t for t in self._tasks.values() if t.status == TaskStatus.IN_PROGRESS]
    
    def get_milestones(self) -> List[Milestone]:
        """Get all milestones"""
        return list(self._milestones.values())
    
    def get_progress(self) -> Dict[str, Any]:
        """Get overall progress"""
        total_tasks = len(self._tasks)
        completed_tasks = sum(1 for t in self._tasks.values() if t.status == TaskStatus.COMPLETED)
        
        total_milestones = len(self._milestones)
        completed_milestones = sum(1 for m in self._milestones.values() if m.status == MilestoneStatus.COMPLETED)
        
        return {
            "task_progress": completed_tasks / total_tasks if total_tasks > 0 else 0,
            "milestone_progress": completed_milestones / total_milestones if total_milestones > 0 else 0,
            "total_tasks": total_tasks,
            "completed_tasks": completed_tasks,
            "pending_tasks": sum(1 for t in self._tasks.values() if t.status == TaskStatus.PENDING),
            "total_milestones": total_milestones,
            "completed_milestones": completed_milestones
        }
    
    def save_checkpoint(self, name: str) -> str:
        """Save planner checkpoint"""
        checkpoint_file = self.checkpoints_dir / f"planner_{name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        data = self.get_progress()
        data["tasks"] = [t.to_dict() for t in self._tasks.values()]
        data["milestones"] = [m.to_dict() for m in self._milestones.values()]
        data["execution_graph"] = self._execution_graph
        
        with open(checkpoint_file, 'w') as f:
            json.dump(data, f, indent=2)
        
        return str(checkpoint_file)


def init_planner(base_dir: str = "D:/Privantrix-AI-OS/AI-OS") -> Planner:
    os.chdir(base_dir)
    return Planner()
