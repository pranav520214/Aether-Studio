"""
Privantrix AI OS - Hardware Detector
Production-grade hardware detection and benchmarking system
"""

import os
import sys
import platform
import subprocess
import shutil
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass, field, asdict
import json


@dataclass
class CPUInfo:
    """CPU information"""
    architecture: str = ""
    processor: str = ""
    cores_physical: int = 0
    cores_logical: int = 0
    frequency_mhz: float = 0.0
    cache_l2_kb: int = 0
    cache_l3_kb: int = 0


@dataclass
class RAMInfo:
    """RAM information"""
    total_gb: float = 0.0
    available_gb: float = 0.0
    used_gb: float = 0.0
    percent_used: float = 0.0


@dataclass
class GPUInfo:
    """GPU information"""
    name: str = ""
    vendor: str = ""
    vram_total_gb: float = 0.0
    vram_available_gb: float = 0.0
    cuda_version: Optional[str] = None
    cuda_cores: int = 0
    driver_version: str = ""
    is_integrated: bool = False


@dataclass
class DiskInfo:
    """Disk information"""
    mount_point: str = ""
    total_gb: float = 0.0
    free_gb: float = 0.0
    used_gb: float = 0.0
    percent_used: float = 0.0
    filesystem: str = ""


@dataclass
class SystemInfo:
    """Complete system information"""
    os_name: str = ""
    os_version: str = ""
    python_version: str = ""
    python_implementation: str = ""
    hostname: str = ""
    cpu: CPUInfo = field(default_factory=CPUInfo)
    ram: RAMInfo = field(default_factory=RAMInfo)
    gpus: List[GPUInfo] = field(default_factory=list)
    disks: List[DiskInfo] = field(default_factory=list)
    cuda_available: bool = False
    torch_available: bool = False


class HardwareDetector:
    """Detects and benchmarks hardware capabilities"""
    
    def __init__(self):
        self.system_info = SystemInfo()
    
    def detect_all(self) -> SystemInfo:
        """Detect all hardware components"""
        self._detect_system()
        self._detect_cpu()
        self._detect_ram()
        self._detect_gpus()
        self._detect_disks()
        self._check_cuda()
        return self.system_info
    
    def _detect_system(self) -> None:
        """Detect system information"""
        self.system_info.os_name = platform.system()
        self.system_info.os_version = platform.version()
        self.system_info.python_version = platform.python_version()
        self.system_info.python_implementation = platform.python_implementation()
        self.system_info.hostname = platform.node()
        
        # Check for PyTorch availability
        try:
            import torch
            self.system_info.torch_available = True
        except ImportError:
            self.system_info.torch_available = False
    
    def _detect_cpu(self) -> None:
        """Detect CPU information"""
        cpu = CPUInfo()
        
        cpu.architecture = platform.machine()
        cpu.processor = platform.processor()
        cpu.cores_physical = os.cpu_count() or 1
        
        # Try to get logical cores (may differ from physical on hyperthreading)
        try:
            if platform.system() == "Windows":
                result = subprocess.run(
                    ["wmic", "cpu", "get", "NumberOfCores,NumberOfLogicalProcessors"],
                    capture_output=True,
                    text=True
                )
                lines = result.stdout.strip().split('\n')[1:]
                if lines:
                    parts = lines[0].split()
                    if len(parts) >= 2:
                        cpu.cores_physical = int(parts[0])
                        cpu.cores_logical = int(parts[1])
            else:
                cpu.cores_logical = os.cpu_count() or cpu.cores_physical
        except Exception:
            cpu.cores_logical = cpu.cores_physical
        
        # Try to get CPU frequency
        try:
            import psutil
            freq = psutil.cpu_freq()
            if freq:
                cpu.frequency_mhz = freq.current
        except ImportError:
            pass
        
        self.system_info.cpu = cpu
    
    def _detect_ram(self) -> None:
        """Detect RAM information"""
        ram = RAMInfo()
        
        try:
            import psutil
            mem = psutil.virtual_memory()
            ram.total_gb = mem.total / (1024 ** 3)
            ram.available_gb = mem.available / (1024 ** 3)
            ram.used_gb = mem.used / (1024 ** 3)
            ram.percent_used = mem.percent
        except ImportError:
            # Fallback for systems without psutil
            if platform.system() == "Windows":
                try:
                    result = subprocess.run(
                        ["wmic", "OS", "get", "FreePhysicalMemory,TotalVisibleMemorySize"],
                        capture_output=True,
                        text=True
                    )
                    lines = result.stdout.strip().split('\n')[1:]
                    if lines:
                        parts = lines[0].split()
                        ram.total_gb = int(parts[1]) / (1024 * 1024)
                        ram.available_gb = int(parts[0]) / (1024 * 1024)
                        ram.used_gb = ram.total_gb - ram.available_gb
                        ram.percent_used = (ram.used_gb / ram.total_gb) * 100 if ram.total_gb > 0 else 0
                except Exception:
                    pass
        
        self.system_info.ram = ram
    
    def _detect_gpus(self) -> None:
        """Detect GPU information"""
        gpus = []
        
        # Try NVIDIA detection via nvidia-smi
        try:
            result = subprocess.run(
                ["nvidia-smi", "--query-gpu=name,memory.total,memory.free,driver_version,cuda_version", "--format=csv,noheader,nounits"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0 and result.stdout.strip():
                for line in result.stdout.strip().split('\n'):
                    parts = [p.strip() for p in line.split(',')]
                    if len(parts) >= 5:
                        gpu = GPUInfo()
                        gpu.name = parts[0]
                        gpu.vendor = "NVIDIA"
                        gpu.vram_total_gb = float(parts[1]) / 1024
                        gpu.vram_available_gb = float(parts[2]) / 1024
                        gpu.driver_version = parts[3]
                        gpu.cuda_version = parts[4]
                        gpu.is_integrated = "integrated" in gpu.name.lower()
                        gpus.append(gpu)
        except (subprocess.TimeoutExpired, FileNotFoundError, Exception):
            pass
        
        # Try Windows WMI for additional GPU info
        if not gpus and platform.system() == "Windows":
            try:
                result = subprocess.run(
                    ["wmic", "path", "win32_VideoController", "get", "Name,AdapterRAM,DriverVersion"],
                    capture_output=True,
                    text=True
                )
                
                if result.returncode == 0:
                    lines = result.stdout.strip().split('\n')[1:]
                    for line in lines:
                        if line.strip():
                            parts = line.split()
                            if len(parts) >= 3:
                                gpu = GPUInfo()
                                gpu.name = ' '.join(parts[:-2])
                                gpu.vendor = self._detect_gpu_vendor(gpu.name)
                                try:
                                    gpu.vram_total_gb = int(parts[-2]) / (1024 ** 3)
                                except ValueError:
                                    pass
                                gpu.driver_version = parts[-1]
                                gpus.append(gpu)
            except Exception:
                pass
        
        self.system_info.gpus = gpus
    
    def _detect_gpu_vendor(self, name: str) -> str:
        """Detect GPU vendor from name"""
        name_lower = name.lower()
        if "nvidia" in name_lower or "geforce" in name_lower or "quadro" in name_lower:
            return "NVIDIA"
        elif "amd" in name_lower or "radeon" in name_lower:
            return "AMD"
        elif "intel" in name_lower or "hd graphics" in name_lower or "iris" in name_lower:
            return "Intel"
        return "Unknown"
    
    def _detect_disks(self) -> None:
        """Detect disk information"""
        disks = []
        
        # Check D: drive first (preferred for Privantrix)
        if platform.system() == "Windows":
            for drive in ['D:', 'C:', 'E:']:
                if Path(f"{drive}/").exists():
                    try:
                        usage = shutil.disk_usage(drive)
                        disk = DiskInfo()
                        disk.mount_point = drive
                        disk.total_gb = usage.total / (1024 ** 3)
                        disk.free_gb = usage.free / (1024 ** 3)
                        disk.used_gb = usage.used / (1024 ** 3)
                        disk.percent_used = (usage.used / usage.total) * 100 if usage.total > 0 else 0
                        
                        # Get filesystem type
                        try:
                            result = subprocess.run(
                                ["wmic", "logicaldisk", "where", f"DeviceID='{drive}'", "get", "FileSystem"],
                                capture_output=True,
                                text=True
                            )
                            lines = result.stdout.strip().split('\n')[1:]
                            if lines and lines[0].strip():
                                disk.filesystem = lines[0].strip()
                        except Exception:
                            disk.filesystem = "NTFS"
                        
                        disks.append(disk)
                    except Exception:
                        pass
        else:
            # Unix-like systems
            try:
                usage = shutil.disk_usage("/")
                disk = DiskInfo()
                disk.mount_point = "/"
                disk.total_gb = usage.total / (1024 ** 3)
                disk.free_gb = usage.free / (1024 ** 3)
                disk.used_gb = usage.used / (1024 ** 3)
                disk.percent_used = (usage.used / usage.total) * 100 if usage.total > 0 else 0
                disk.filesystem = "ext4"
                disks.append(disk)
            except Exception:
                pass
        
        self.system_info.disks = disks
    
    def _check_cuda(self) -> None:
        """Check CUDA availability"""
        try:
            import torch
            self.system_info.cuda_available = torch.cuda.is_available()
        except ImportError:
            self.system_info.cuda_available = len([g for g in self.system_info.gpus if g.vendor == "NVIDIA"]) > 0
    
    def benchmark(self) -> Dict[str, Any]:
        """Run hardware benchmarks"""
        results = {
            "cpu_score": 0,
            "memory_bandwidth_gb_s": 0.0,
            "gpu_compute_score": 0,
            "disk_read_mb_s": 0.0,
            "disk_write_mb_s": 0.0,
            "overall_score": 0
        }
        
        # CPU benchmark (simple calculation test)
        try:
            import time
            start = time.time()
            total = 0
            for i in range(1000000):
                total += i * i
            elapsed = time.time() - start
            results["cpu_score"] = int(1000 / elapsed) if elapsed > 0 else 0
        except Exception:
            results["cpu_score"] = 100
        
        # Memory bandwidth test
        try:
            import time
            import numpy as np
            size = 100 * 1024 * 1024  # 100 MB
            arr = np.random.rand(size // 8)
            
            start = time.time()
            _ = arr * 2
            elapsed = time.time() - start
            
            if elapsed > 0:
                results["memory_bandwidth_gb_s"] = round((size / (1024 ** 3)) / elapsed, 2)
        except ImportError:
            results["memory_bandwidth_gb_s"] = 10.0
        
        # GPU benchmark (if available)
        if self.system_info.cuda_available and self.system_info.torch_available:
            try:
                import torch
                import time
                
                # Simple matrix multiplication benchmark
                matrix_size = 4096
                a = torch.randn(matrix_size, matrix_size).cuda()
                b = torch.randn(matrix_size, matrix_size).cuda()
                
                # Warmup
                _ = torch.matmul(a, b)
                torch.cuda.synchronize()
                
                start = time.time()
                for _ in range(10):
                    _ = torch.matmul(a, b)
                torch.cuda.synchronize()
                elapsed = time.time() - start
                
                results["gpu_compute_score"] = int(10000 / elapsed) if elapsed > 0 else 0
            except Exception:
                results["gpu_compute_score"] = 0
        
        # Disk benchmark
        try:
            import tempfile
            import time
            
            test_file = Path("temp/disk_benchmark.tmp")
            test_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Write test
            data = b'x' * (10 * 1024 * 1024)  # 10 MB
            start = time.time()
            with open(test_file, 'wb') as f:
                for _ in range(5):
                    f.write(data)
                f.flush()
                os.fsync(f.fileno())
            elapsed_write = time.time() - start
            
            if elapsed_write > 0:
                results["disk_write_mb_s"] = round((50 * 1024 * 1024) / (elapsed_write * 1024 * 1024), 2)
            
            # Read test
            start = time.time()
            with open(test_file, 'rb') as f:
                _ = f.read()
            elapsed_read = time.time() - start
            
            if elapsed_read > 0:
                results["disk_read_mb_s"] = round((50 * 1024 * 1024) / (elapsed_read * 1024 * 1024), 2)
            
            test_file.unlink(missing_ok=True)
        except Exception:
            results["disk_read_mb_s"] = 100.0
            results["disk_write_mb_s"] = 100.0
        
        # Calculate overall score
        results["overall_score"] = (
            results["cpu_score"] +
            results["memory_bandwidth_gb_s"] * 10 +
            results["gpu_compute_score"] +
            int(results["disk_read_mb_s"]) +
            int(results["disk_write_mb_s"])
        )
        
        return results
    
    def get_recommendations(self) -> List[str]:
        """Get optimization recommendations based on hardware"""
        recommendations = []
        
        # RAM recommendations
        if self.system_info.ram.total_gb < 8:
            recommendations.append("Upgrade RAM to at least 8GB for optimal performance")
        elif self.system_info.ram.total_gb < 16:
            recommendations.append("Consider upgrading to 16GB RAM for better multitasking")
        
        # GPU recommendations
        if not self.system_info.gpus:
            recommendations.append("No dedicated GPU detected. Consider adding one for AI workloads")
        elif all(g.is_integrated for g in self.system_info.gpus):
            recommendations.append("Only integrated graphics detected. A dedicated GPU is recommended for AI tasks")
        elif any(g.vendor == "NVIDIA" and g.vram_total_gb < 6 for g in self.system_info.gpus):
            recommendations.append("GPU VRAM is limited (<6GB). Consider a GPU with more VRAM for larger models")
        
        # Disk recommendations
        d_drive = next((d for d in self.system_info.disks if d.mount_point == "D:"), None)
        if d_drive and d_drive.free_gb < 50:
            recommendations.append("D: drive has less than 50GB free. Consider freeing up space")
        
        # CUDA recommendations
        if self.system_info.cuda_available and not self.system_info.torch_available:
            recommendations.append("CUDA available but PyTorch not installed. Install PyTorch for GPU acceleration")
        
        return recommendations
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert system info to dictionary"""
        return asdict(self.system_info)
    
    def save_report(self, filepath: str = "benchmarks/hardware_report.json") -> None:
        """Save hardware report to file"""
        path = Path(filepath)
        path.parent.mkdir(parents=True, exist_ok=True)
        
        report = {
            "system_info": self.to_dict(),
            "benchmark_results": self.benchmark(),
            "recommendations": self.get_recommendations(),
            "timestamp": __import__('datetime').datetime.now().isoformat()
        }
        
        with open(path, 'w') as f:
            json.dump(report, f, indent=2)


def detect_hardware() -> SystemInfo:
    """Convenience function to detect hardware"""
    detector = HardwareDetector()
    return detector.detect_all()


def get_hardware_report(save_path: Optional[str] = None) -> Dict[str, Any]:
    """Get complete hardware report"""
    detector = HardwareDetector()
    detector.detect_all()
    
    if save_path:
        detector.save_report(save_path)
    
    return {
        "system_info": detector.to_dict(),
        "benchmark": detector.benchmark(),
        "recommendations": detector.get_recommendations()
    }
