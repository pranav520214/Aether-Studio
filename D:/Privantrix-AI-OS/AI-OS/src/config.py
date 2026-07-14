"""
Privantrix AI OS - Configuration Manager
Production-grade configuration management system
"""

import os
import json
import yaml
from pathlib import Path
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, validator
from dotenv import load_dotenv


class HardwareConfig(BaseModel):
    """Hardware configuration settings"""
    cpu_cores: int = Field(default=4, ge=1)
    ram_gb: int = Field(default=8, ge=2)
    gpu_enabled: bool = Field(default=False)
    gpu_vram_gb: int = Field(default=0, ge=0)
    cuda_version: Optional[str] = None
    disk_space_gb: int = Field(default=100, ge=10)


class ModelConfig(BaseModel):
    """Model configuration settings"""
    default_model: str = Field(default="local-model")
    fallback_model: str = Field(default="backup-model")
    max_context_length: int = Field(default=8192, ge=512)
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    max_tokens: int = Field(default=4096, ge=100)
    timeout_seconds: int = Field(default=120, ge=10)
    retry_attempts: int = Field(default=3, ge=1)


class DatabaseConfig(BaseModel):
    """Database configuration settings"""
    sqlite_path: str = Field(default="database/privantrix.db")
    chroma_path: str = Field(default="embeddings/chroma_db")
    embedding_model: str = Field(default="all-MiniLM-L6-v2")
    collection_name: str = Field(default="privantrix_memory")


class MemoryConfig(BaseModel):
    """Memory system configuration"""
    working_memory_limit: int = Field(default=100, ge=10)
    session_ttl_hours: int = Field(default=24, ge=1)
    long_term_compression: bool = Field(default=True)
    knowledge_graph_enabled: bool = Field(default=True)
    vector_store_enabled: bool = Field(default=True)


class LMStudioConfig(BaseModel):
    """LM Studio client configuration"""
    host: str = Field(default="localhost")
    port: int = Field(default=1234, ge=1, le=65535)
    api_base: str = Field(default="/v1")
    enabled: bool = Field(default=True)
    auto_detect: bool = Field(default=True)


class AgentConfig(BaseModel):
    """Agent framework configuration"""
    max_concurrent_agents: int = Field(default=5, ge=1)
    agent_timeout_seconds: int = Field(default=300, ge=60)
    enable_logging: bool = Field(default=True)
    checkpoint_interval: int = Field(default=5, ge=1)


class WorkflowConfig(BaseModel):
    """Workflow engine configuration"""
    max_workflows: int = Field(default=50, ge=1)
    max_steps_per_workflow: int = Field(default=100, ge=10)
    enable_parallel: bool = Field(default=True)
    retry_on_failure: bool = Field(default=True)


class DashboardConfig(BaseModel):
    """Dashboard configuration"""
    host: str = Field(default="0.0.0.0")
    port: int = Field(default=8000, ge=1, le=65535)
    refresh_interval_seconds: int = Field(default=5, ge=1)
    enable_realtime: bool = Field(default=True)


class LoggingConfig(BaseModel):
    """Logging configuration"""
    level: str = Field(default="INFO")
    format: str = Field(default="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    file_path: str = Field(default="logs/privantrix.log")
    max_file_size_mb: int = Field(default=100, ge=10)
    backup_count: int = Field(default=5, ge=1)
    console_output: bool = Field(default=True)


class PrivantrixConfig(BaseModel):
    """Main configuration class for Privantrix AI OS"""
    base_dir: str = Field(default="D:/Privantrix-AI-OS/AI-OS")
    environment: str = Field(default="development", pattern="^(development|staging|production)$")
    debug: bool = Field(default=False)
    
    hardware: HardwareConfig = Field(default_factory=HardwareConfig)
    model: ModelConfig = Field(default_factory=ModelConfig)
    database: DatabaseConfig = Field(default_factory=DatabaseConfig)
    memory: MemoryConfig = Field(default_factory=MemoryConfig)
    lmstudio: LMStudioConfig = Field(default_factory=LMStudioConfig)
    agent: AgentConfig = Field(default_factory=AgentConfig)
    workflow: WorkflowConfig = Field(default_factory=WorkflowConfig)
    dashboard: DashboardConfig = Field(default_factory=DashboardConfig)
    logging: LoggingConfig = Field(default_factory=LoggingConfig)
    
    @validator('base_dir')
    def validate_base_dir(cls, v):
        path = Path(v)
        if not path.exists():
            path.mkdir(parents=True, exist_ok=True)
        return str(path.resolve())
    
    class Config:
        arbitrary_types_allowed = True
        json_encoders = {
            Path: lambda v: str(v)
        }


class ConfigurationManager:
    """Manages configuration loading, saving, and validation"""
    
    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path or "configs/config.yaml"
        self.env_path = ".env"
        self._config: Optional[PrivantrixConfig] = None
    
    def load(self) -> PrivantrixConfig:
        """Load configuration from file and environment"""
        load_dotenv(self.env_path)
        
        config_data = {}
        
        if Path(self.config_path).exists():
            with open(self.config_path, 'r') as f:
                config_data = yaml.safe_load(f) or {}
        
        self._config = PrivantrixConfig(**config_data)
        return self._config
    
    def save(self, config: PrivantrixConfig) -> None:
        """Save configuration to file"""
        config_dict = config.dict(exclude_none=True)
        
        config_dir = Path(self.config_path).parent
        config_dir.mkdir(parents=True, exist_ok=True)
        
        with open(self.config_path, 'w') as f:
            yaml.dump(config_dict, f, default_flow_style=False, sort_keys=False)
    
    def get(self) -> PrivantrixConfig:
        """Get current configuration, loading if necessary"""
        if self._config is None:
            self.load()
        return self._config
    
    def update(self, **kwargs) -> PrivantrixConfig:
        """Update configuration values"""
        config = self.get()
        
        for key, value in kwargs.items():
            if hasattr(config, key):
                setattr(config, key, value)
        
        self.save(config)
        return config
    
    def validate(self) -> bool:
        """Validate current configuration"""
        try:
            config = self.get()
            return True
        except Exception as e:
            print(f"Configuration validation failed: {e}")
            return False
    
    def create_default(self) -> PrivantrixConfig:
        """Create default configuration"""
        config = PrivantrixConfig()
        self.save(config)
        return config


def get_config() -> PrivantrixConfig:
    """Convenience function to get configuration"""
    manager = ConfigurationManager()
    return manager.get()


def init_config(base_dir: str = "D:/Privantrix-AI-OS/AI-OS") -> ConfigurationManager:
    """Initialize configuration manager with base directory"""
    manager = ConfigurationManager()
    config = manager.load()
    return manager
