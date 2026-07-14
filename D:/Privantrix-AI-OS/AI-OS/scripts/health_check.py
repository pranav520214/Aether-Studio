#!/usr/bin/env python3
"""
Privantrix AI OS - Health Check Script
Monitors system health and reports issues
"""

import os
import sys
from pathlib import Path
from datetime import datetime


def check_disk_space(path: str, min_gb: float = 10.0) -> bool:
    """Check available disk space"""
    import shutil
    try:
        usage = shutil.disk_usage(path)
        free_gb = usage.free / (1024 ** 3)
        return free_gb >= min_gb
    except Exception:
        return False


def check_memory(min_gb: float = 4.0) -> bool:
    """Check available RAM"""
    try:
        import psutil
        mem = psutil.virtual_memory()
        available_gb = mem.available / (1024 ** 3)
        return available_gb >= min_gb
    except ImportError:
        return True  # Can't check without psutil


def check_database(db_path: str) -> bool:
    """Check database accessibility"""
    db_file = Path(db_path)
    return db_file.exists() and db_file.stat().st_size >= 0


def check_lmstudio(host: str = "localhost", port: int = 1234) -> bool:
    """Check LM Studio availability"""
    try:
        import requests
        response = requests.get(f"http://{host}:{port}/v1/models", timeout=5)
        return response.status_code == 200
    except Exception:
        return False


def run_health_checks(base_dir: str = "D:/Privantrix-AI-OS/AI-OS") -> dict:
    """Run all health checks and return results"""
    results = {
        "timestamp": datetime.now().isoformat(),
        "checks": {},
        "overall_healthy": True
    }
    
    # Disk space check
    results["checks"]["disk_space"] = check_disk_space(base_dir)
    if not results["checks"]["disk_space"]:
        results["overall_healthy"] = False
    
    # Memory check
    results["checks"]["memory"] = check_memory()
    if not results["checks"]["memory"]:
        results["overall_healthy"] = False
    
    # Database check
    db_path = Path(base_dir) / "database" / "privantrix.db"
    results["checks"]["database"] = check_database(str(db_path))
    
    # LM Studio check
    results["checks"]["lmstudio"] = check_lmstudio()
    
    # Directory structure check
    required_dirs = ["src", "configs", "database", "logs", "memory"]
    dirs_exist = all((Path(base_dir) / d).exists() for d in required_dirs)
    results["checks"]["directories"] = dirs_exist
    if not dirs_exist:
        results["overall_healthy"] = False
    
    return results


def main():
    """Main entry point"""
    base_dir = os.environ.get("PRIVANTRIX_BASE_DIR", "D:/Privantrix-AI-OS/AI-OS")
    
    print("=" * 50)
    print("PRIVANTRIX AI OS - Health Check")
    print("=" * 50)
    
    results = run_health_checks(base_dir)
    
    for check_name, passed in results["checks"].items():
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"  {status}: {check_name}")
    
    print("-" * 50)
    if results["overall_healthy"]:
        print("Overall Status: HEALTHY")
    else:
        print("Overall Status: UNHEALTHY - Some checks failed")
        sys.exit(1)


if __name__ == "__main__":
    main()
