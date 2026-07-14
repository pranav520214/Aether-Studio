"""
Security Manager for VID-ED.
Handles path sanitization, sandbox enforcement, and safe subprocess execution.

HARD RULES:
1. FastAPI must bind strictly to 127.0.0.1 (never 0.0.0.0)
2. All file operations must be sandboxed within designated directories
3. Never use eval(), exec(), or pass unsanitized strings to subprocess shells
4. FFmpeg arguments must always be passed as lists, never shell strings
"""
import os
import re
from pathlib import Path
from typing import Optional, List, Union
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class SecurityManager:
    """
    Security utilities for local file system access and subprocess execution.
    
    This class enforces the security boundaries required for a local AI video
    production platform that processes user files on their machine.
    """

    def __init__(self, sandbox_root: str):
        """
        Initialize security manager with a sandbox root directory.
        
        Args:
            sandbox_root: Absolute path to the root directory for all file operations.
                         All file access will be restricted to this directory tree.
        """
        self.sandbox_root = Path(sandbox_root).resolve()
        
        # Ensure sandbox root exists
        if not self.sandbox_root.exists():
            self.sandbox_root.mkdir(parents=True, exist_ok=True)
            logger.info(f"Created sandbox root: {self.sandbox_root}")
        
        logger.info(f"SecurityManager initialized with sandbox: {self.sandbox_root}")

    def sanitize_path(self, user_path: str) -> Path:
        """
        Sanitize and resolve a user-provided path, ensuring it's within the sandbox.
        
        HARD RULE: This method MUST be called on ANY path received from user input
        before any file operation is performed.
        
        Args:
            user_path: Raw path string from user input
            
        Returns:
            Resolved Path object within sandbox
            
        Raises:
            ValueError: If path resolves outside sandbox (path traversal attempt)
        """
        if not user_path:
            raise ValueError("Empty path provided")
        
        # Remove any null bytes or dangerous characters
        sanitized = user_path.replace('\x00', '')
        
        # Convert to Path and resolve to absolute
        try:
            resolved = Path(sanitized).resolve()
        except Exception as e:
            raise ValueError(f"Invalid path format: {e}")
        
        # Check if resolved path is within sandbox
        try:
            resolved.relative_to(self.sandbox_root)
        except ValueError:
            # Path is outside sandbox - this is a path traversal attempt
            logger.warning(
                f"SECURITY: Path traversal attempt detected: {user_path} "
                f"resolved to {resolved}"
            )
            raise ValueError(
                f"Path '{user_path}' resolves outside allowed sandbox. "
                f"All files must be within {self.sandbox_root}"
            )
        
        return resolved

    def is_path_safe(self, user_path: str) -> bool:
        """
        Check if a path is safe to access without raising exceptions.
        
        Args:
            user_path: Raw path string from user input
            
        Returns:
            True if path is within sandbox, False otherwise
        """
        try:
            self.sanitize_path(user_path)
            return True
        except ValueError:
            return False

    def validate_file_extension(
        self, 
        filepath: Union[str, Path], 
        allowed_extensions: List[str]
    ) -> bool:
        """
        Validate that a file has an allowed extension.
        
        Args:
            filepath: Path to validate
            allowed_extensions: List of allowed extensions (e.g., ['.mp4', '.mov'])
            
        Returns:
            True if extension is allowed
        """
        path = Path(filepath)
        ext = path.suffix.lower()
        return ext in [e.lower() for e in allowed_extensions]

    def build_ffmpeg_args(
        self,
        command_parts: List[str],
        input_files: Optional[List[Union[str, Path]]] = None,
        output_file: Optional[Union[str, Path]] = None,
    ) -> List[str]:
        """
        Build a safe FFmpeg argument list.
        
        HARD RULE: FFmpeg must NEVER be called with shell=True or as a single string.
        All arguments must be passed as a list to prevent command injection.
        
        Args:
            command_parts: Base FFmpeg command parts (e.g., ['-i', 'input.mp4'])
            input_files: List of input file paths (will be sanitized)
            output_file: Output file path (will be sanitized)
            
        Returns:
            Complete argument list ready for subprocess.run()
        """
        args = ["ffmpeg"]
        
        # Add command parts (already assumed safe)
        args.extend(command_parts)
        
        # Sanitize and add input files
        if input_files:
            for infile in input_files:
                safe_path = str(self.sanitize_path(str(infile)))
                args.extend(["-i", safe_path])
        
        # Sanitize and add output file
        if output_file:
            safe_output = str(self.sanitize_path(str(output_file)))
            args.append(safe_output)
        
        return args

    def get_safe_temp_path(self, prefix: str = "temp_") -> Path:
        """
        Generate a safe temporary path within the sandbox.
        
        Args:
            prefix: Prefix for the temporary filename
            
        Returns:
            Path object for temporary file
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_prefix = re.sub(r'[^a-zA-Z0-9]', '', prefix)
        temp_name = f"{safe_prefix}{timestamp}"
        return self.sandbox_root / "cache" / temp_name

    def create_sandbox_subdirectory(self, subdir_name: str) -> Path:
        """
        Create a subdirectory within the sandbox.
        
        Args:
            subdir_name: Name for the subdirectory
            
        Returns:
            Path to created directory
        """
        # Sanitize directory name (no path separators allowed)
        safe_name = re.sub(r'[/\\]', '_', subdir_name)
        new_dir = self.sandbox_root / safe_name
        new_dir.mkdir(parents=True, exist_ok=True)
        return new_dir


# Module-level convenience functions
_default_security_manager: Optional[SecurityManager] = None


def init_security_manager(sandbox_root: str) -> SecurityManager:
    """Initialize the default security manager."""
    global _default_security_manager
    _default_security_manager = SecurityManager(sandbox_root)
    return _default_security_manager


def get_security_manager() -> SecurityManager:
    """Get the default security manager."""
    if _default_security_manager is None:
        raise RuntimeError("SecurityManager not initialized. Call init_security_manager() first.")
    return _default_security_manager


def sanitize_path(user_path: str) -> Path:
    """Convenience function to sanitize a path using default security manager."""
    return get_security_manager().sanitize_path(user_path)


def is_path_safe(user_path: str) -> bool:
    """Convenience function to check path safety using default security manager."""
    return get_security_manager().is_path_safe(user_path)
