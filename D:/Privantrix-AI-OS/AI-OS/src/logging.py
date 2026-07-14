"""
Privantrix AI OS - Logging System
Production-grade logging with rotation, formatting, and multiple handlers
"""

import os
import sys
import logging
from pathlib import Path
from typing import Optional, Dict, Any
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler
from datetime import datetime


class LogFormatter(logging.Formatter):
    """Custom formatter with color support for console output"""
    
    COLORS = {
        'DEBUG': '\033[36m',     # Cyan
        'INFO': '\033[32m',      # Green
        'WARNING': '\033[33m',   # Yellow
        'ERROR': '\033[31m',     # Red
        'CRITICAL': '\033[35m',  # Magenta
        'RESET': '\033[0m'       # Reset
    }
    
    def __init__(self, fmt: str, use_color: bool = True):
        super().__init__(fmt)
        self.use_color = use_color
    
    def format(self, record: logging.LogRecord) -> str:
        if self.use_color and hasattr(sys.stdout, 'isatty') and sys.stdout.isatty():
            color = self.COLORS.get(record.levelname, self.COLORS['RESET'])
            record.levelname = f"{color}{record.levelname}{self.COLORS['RESET']}"
        return super().format(record)


class PrivantrixLogger:
    """Main logging class for Privantrix AI OS"""
    
    _instance: Optional['PrivantrixLogger'] = None
    _loggers: Dict[str, logging.Logger] = {}
    
    def __new__(cls, *args, **kwargs) -> 'PrivantrixLogger':
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(
        self,
        log_dir: str = "logs",
        log_level: str = "INFO",
        log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        max_file_size_mb: int = 100,
        backup_count: int = 5,
        console_output: bool = True,
        file_output: bool = True
    ):
        if hasattr(self, '_initialized') and self._initialized:
            return
        
        self._initialized = True
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        self.log_level = getattr(logging, log_level.upper(), logging.INFO)
        self.log_format = log_format
        self.max_file_size_bytes = max_file_size_mb * 1024 * 1024
        self.backup_count = backup_count
        self.console_output = console_output
        self.file_output = file_output
        
        self._setup_root_logger()
    
    def _setup_root_logger(self) -> None:
        """Setup the root logger with all handlers"""
        self.root_logger = logging.getLogger("privantrix")
        self.root_logger.setLevel(self.log_level)
        
        # Clear existing handlers
        self.root_logger.handlers.clear()
        
        # Console handler
        if self.console_output:
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setLevel(self.log_level)
            console_formatter = LogFormatter(self.log_format, use_color=True)
            console_handler.setFormatter(console_formatter)
            self.root_logger.addHandler(console_handler)
        
        # File handler with rotation
        if self.file_output:
            log_file = self.log_dir / "privantrix.log"
            file_handler = RotatingFileHandler(
                log_file,
                maxBytes=self.max_file_size_bytes,
                backupCount=self.backup_count
            )
            file_handler.setLevel(self.log_level)
            file_formatter = LogFormatter(self.log_format, use_color=False)
            file_handler.setFormatter(file_formatter)
            self.root_logger.addHandler(file_handler)
            
            # Also create a timestamped log file for each session
            session_log = self.log_dir / f"privantrix_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
            session_handler = logging.FileHandler(session_log)
            session_handler.setLevel(self.log_level)
            session_handler.setFormatter(file_formatter)
            self.root_logger.addHandler(session_handler)
    
    def get_logger(self, name: str) -> logging.Logger:
        """Get a named logger instance"""
        if name not in self._loggers:
            logger = logging.getLogger(f"privantrix.{name}")
            logger.setLevel(self.log_level)
            self._loggers[name] = logger
        return self._loggers[name]
    
    def debug(self, message: str, *args, **kwargs) -> None:
        self.root_logger.debug(message, *args, **kwargs)
    
    def info(self, message: str, *args, **kwargs) -> None:
        self.root_logger.info(message, *args, **kwargs)
    
    def warning(self, message: str, *args, **kwargs) -> None:
        self.root_logger.warning(message, *args, **kwargs)
    
    def error(self, message: str, *args, **kwargs) -> None:
        self.root_logger.error(message, *args, **kwargs)
    
    def critical(self, message: str, *args, **kwargs) -> None:
        self.root_logger.critical(message, *args, **kwargs)
    
    def exception(self, message: str, *args, **kwargs) -> None:
        self.root_logger.exception(message, *args, **kwargs)
    
    def set_level(self, level: str) -> None:
        """Change log level dynamically"""
        self.log_level = getattr(logging, level.upper(), logging.INFO)
        self.root_logger.setLevel(self.log_level)
        for handler in self.root_logger.handlers:
            handler.setLevel(self.log_level)
    
    def add_file_handler(
        self,
        filename: str,
        level: str = "INFO",
        use_rotation: bool = True
    ) -> None:
        """Add an additional file handler"""
        filepath = self.log_dir / filename
        logger = logging.getLogger("privantrix")
        
        if use_rotation:
            handler = RotatingFileHandler(
                filepath,
                maxBytes=self.max_file_size_bytes,
                backupCount=self.backup_count
            )
        else:
            handler = logging.FileHandler(filepath)
        
        handler.setLevel(getattr(logging, level.upper(), logging.INFO))
        handler.setFormatter(LogFormatter(self.log_format, use_color=False))
        logger.addHandler(handler)
    
    def close(self) -> None:
        """Close all handlers properly"""
        for handler in self.root_logger.handlers:
            handler.close()
        self.root_logger.handlers.clear()


# Global logger instance
_logger_instance: Optional[PrivantrixLogger] = None


def init_logging(
    log_dir: str = "logs",
    log_level: str = "INFO",
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    max_file_size_mb: int = 100,
    backup_count: int = 5,
    console_output: bool = True,
    file_output: bool = True
) -> PrivantrixLogger:
    """Initialize the logging system"""
    global _logger_instance
    _logger_instance = PrivantrixLogger(
        log_dir=log_dir,
        log_level=log_level,
        log_format=log_format,
        max_file_size_mb=max_file_size_mb,
        backup_count=backup_count,
        console_output=console_output,
        file_output=file_output
    )
    return _logger_instance


def get_logger(name: str = "") -> logging.Logger:
    """Get a logger instance"""
    global _logger_instance
    if _logger_instance is None:
        _logger_instance = PrivantrixLogger()
    
    if name:
        return _logger_instance.get_logger(name)
    return _logger_instance.root_logger


def log_debug(message: str, *args, **kwargs) -> None:
    get_logger().debug(message, *args, **kwargs)


def log_info(message: str, *args, **kwargs) -> None:
    get_logger().info(message, *args, **kwargs)


def log_warning(message: str, *args, **kwargs) -> None:
    get_logger().warning(message, *args, **kwargs)


def log_error(message: str, *args, **kwargs) -> None:
    get_logger().error(message, *args, **kwargs)


def log_critical(message: str, *args, **kwargs) -> None:
    get_logger().critical(message, *args, **kwargs)


def log_exception(message: str, *args, **kwargs) -> None:
    get_logger().exception(message, *args, **kwargs)
