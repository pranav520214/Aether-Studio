#!/usr/bin/env python3
"""
Privantrix AI OS - Bootstrap Installer
Production-quality automatic installation and initialization
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path
from typing import Optional, List, Dict, Any


class BootstrapInstaller:
    """Main bootstrap installer class"""
    
    def __init__(self, base_dir: str = "D:/Privantrix-AI-OS/AI-OS"):
        self.base_dir = Path(base_dir)
        self.venv_dir = self.base_dir / "venv"
        self.python_exec: Optional[Path] = None
        
    def run(self) -> bool:
        """Run complete bootstrap installation"""
        print("=" * 60)
        print("PRIVANTRIX AI OS - Bootstrap Installer")
        print("=" * 60)
        
        steps = [
            ("Creating directory structure", self._create_directories),
            ("Setting up Python virtual environment", self._setup_venv),
            ("Installing dependencies", self._install_dependencies),
            ("Initializing databases", self._init_databases),
            ("Generating configuration files", self._generate_configs),
            ("Creating launch scripts", self._create_scripts),
            ("Initializing Git repository", self._init_git),
            ("Creating Cursor configuration", self._create_cursor_config),
            ("Running verification", self._verify_installation),
        ]
        
        for step_name, step_func in steps:
            print(f"\n[*] {step_name}...")
            try:
                step_func()
                print(f"[+] {step_name} - COMPLETE")
            except Exception as e:
                print(f"[-] {step_name} - FAILED: {e}")
                return False
        
        print("\n" + "=" * 60)
        print("BOOTSTRAP INSTALLATION COMPLETE")
        print("=" * 60)
        return True
    
    def _create_directories(self) -> None:
        """Create all required directories"""
        dirs = [
            "src", "configs", "database", "embeddings", "memory",
            "projects", "logs", "checkpoints", "benchmarks",
            "backups", "temp", "cache", "repositories",
            "scripts", "docker", "plugins", "dashboard",
            "templates", "tests", "docs", "workflows", "output",
            "agents", "prompts", "architecture", "roadmap", "summaries"
        ]
        
        for dir_name in dirs:
            dir_path = self.base_dir / dir_name
            dir_path.mkdir(parents=True, exist_ok=True)
            print(f"  Created: {dir_path}")
    
    def _setup_venv(self) -> None:
        """Set up Python virtual environment"""
        if not self.venv_dir.exists():
            subprocess.run([sys.executable, "-m", "venv", str(self.venv_dir)], check=True)
        
        # Determine correct pip path based on OS
        if sys.platform == "win32":
            self.python_exec = self.venv_dir / "Scripts" / "python.exe"
            pip_path = self.venv_dir / "Scripts" / "pip.exe"
        else:
            self.python_exec = self.venv_dir / "bin" / "python"
            pip_path = self.venv_dir / "bin" / "pip"
        
        # Upgrade pip
        subprocess.run([str(pip_path), "install", "--upgrade", "pip"], check=True)
    
    def _install_dependencies(self) -> None:
        """Install all dependencies"""
        requirements_file = self.base_dir / "requirements.txt"
        if requirements_file.exists() and self.python_exec:
            pip_path = self.python_exec.parent / "pip" if sys.platform != "win32" else self.python_exec.parent / "pip.exe"
            subprocess.run([str(pip_path), "install", "-r", str(requirements_file)], check=True)
    
    def _init_databases(self) -> None:
        """Initialize SQLite and ChromaDB"""
        os.chdir(self.base_dir)
        sys.path.insert(0, str(self.base_dir))
        
        try:
            from src.database import init_all_databases
            db, chroma = init_all_databases(str(self.base_dir))
            print("  SQLite database initialized")
            print("  ChromaDB initialized")
        except ImportError as e:
            print(f"  Database initialization deferred (dependencies not yet installed): {e}")
    
    def _generate_configs(self) -> None:
        """Generate configuration files"""
        configs_dir = self.base_dir / "configs"
        configs_dir.mkdir(parents=True, exist_ok=True)
        
        # Default config.yaml
        config_yaml = """# Privantrix AI OS Configuration
base_dir: "D:/Privantrix-AI-OS/AI-OS"
environment: development
debug: false

hardware:
  cpu_cores: 4
  ram_gb: 8
  gpu_enabled: false

model:
  default_model: local-model
  max_context_length: 8192
  temperature: 0.7

database:
  sqlite_path: database/privantrix.db
  chroma_path: embeddings/chroma_db

logging:
  level: INFO
  file_path: logs/privantrix.log
"""
        with open(configs_dir / "config.yaml", 'w') as f:
            f.write(config_yaml)
        
        # Copy .env.example to .env
        env_example = self.base_dir / ".env.example"
        env_file = self.base_dir / ".env"
        if env_example.exists() and not env_file.exists():
            shutil.copy2(env_example, env_file)
    
    def _create_scripts(self) -> None:
        """Create launch and utility scripts"""
        scripts_dir = self.base_dir / "scripts"
        scripts_dir.mkdir(parents=True, exist_ok=True)
        
        # Windows batch script
        start_bat = scripts_dir / "start.bat"
        start_bat.write_text("""@echo off
cd /d "%~dp0.."
call venv\\Scripts\\activate
python main.py %*
""")
        
        # Linux/Mac shell script
        start_sh = scripts_dir / "start.sh"
        start_sh.write_text("""#!/bin/bash
cd "$(dirname "$0")/.."
source venv/bin/activate
python main.py "$@"
""")
        start_sh.chmod(0o755)
        
        # Update script
        update_py = scripts_dir / "update.py"
        update_py.write_text("""#!/usr/bin/env python3
import subprocess
import sys
subprocess.run([sys.executable, "-m", "pip", "install", "-U", "-r", "requirements.txt"])
""")
        
        # Backup script
        backup_py = scripts_dir / "backup.py"
        backup_py.write_text("""#!/usr/bin/env python3
import shutil
from pathlib import Path
from datetime import datetime

base = Path("D:/Privantrix-AI-OS/AI-OS")
backup_dir = base / "backups"
backup_dir.mkdir(exist_ok=True)

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
db_backup = backup_dir / f"database_backup_{timestamp}.db"

if (base / "database" / "privantrix.db").exists():
    shutil.copy2(base / "database" / "privantrix.db", db_backup)
    print(f"Backup created: {db_backup}")
""")
    
    def _init_git(self) -> None:
        """Initialize Git repository"""
        os.chdir(self.base_dir)
        
        if not (self.base_dir / ".git").exists():
            subprocess.run(["git", "init"], check=True, capture_output=True)
            
            # Create .gitignore
            gitignore = self.base_dir / ".gitignore"
            gitignore.write_text("""# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
venv/
ENV/
env/
*.egg-info/
dist/
build/

# IDE
.idea/
.vscode/
*.swp
*.swo

# Project specific
logs/*.log
database/*.db
embeddings/chroma_db/*
!embeddings/chroma_db/.gitkeep
memory/*.json
checkpoints/*.json
.env
.backups/
temp/
cache/
""")
            
            # Create initial commit
            subprocess.run(["git", "add", "."], check=True, capture_output=True)
            subprocess.run(["git", "commit", "-m", "Initial commit: Privantrix AI OS bootstrap"], 
                          check=True, capture_output=True)
    
    def _create_cursor_config(self) -> None:
        """Create Cursor IDE configuration"""
        cursor_dir = self.base_dir / ".cursor"
        cursor_dir.mkdir(parents=True, exist_ok=True)
        
        rules_json = cursor_dir / "rules.json"
        rules_json.write_text("""{
  "rules": [
    {
      "name": "Python Best Practices",
      "pattern": "**/*.py",
      "rules": [
        "Use type hints for all function signatures",
        "Follow PEP 8 style guidelines",
        "Use docstrings for all public functions and classes",
        "Handle errors with appropriate exceptions",
        "Log errors using the logging module"
      ]
    },
    {
      "name": "Project Structure",
      "pattern": "**/*",
      "rules": [
        "Keep business logic in src/ directory",
        "Store configurations in configs/ directory",
        "Place tests in tests/ directory",
        "Documentation goes in docs/ directory"
      ]
    }
  ]
}
""")
        
        settings_json = cursor_dir / "settings.json"
        settings_json.write_text("""{
  "editor.formatOnSave": true,
  "editor.defaultFormatter": "ms-python.black-formatter",
  "python.linting.enabled": true,
  "python.linting.ruffEnabled": true,
  "python.testing.pytestEnabled": true
}
""")
    
    def _verify_installation(self) -> None:
        """Verify installation is complete"""
        checks = [
            ("Virtual environment", self.venv_dir.exists()),
            ("Source directory", (self.base_dir / "src").exists()),
            ("Config directory", (self.base_dir / "configs").exists()),
            ("Database directory", (self.base_dir / "database").exists()),
            ("Requirements file", (self.base_dir / "requirements.txt").exists()),
            ("README file", (self.base_dir / "README.md").exists()),
        ]
        
        print("\nVerification Results:")
        all_passed = True
        for check_name, passed in checks:
            status = "✓" if passed else "✗"
            print(f"  {status} {check_name}")
            if not passed:
                all_passed = False
        
        if all_passed:
            print("\nAll verification checks passed!")
        else:
            print("\nSome verification checks failed. Please review.")


def main():
    """Main entry point"""
    installer = BootstrapInstaller()
    success = installer.run()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
