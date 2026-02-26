import os
from pathlib import Path
from typing import Union

# Base exception for IO Jail violations
class SecurityViolationError(Exception):
    """Raised when an operation attempts to bypass the IO Jail."""
    pass

class IOJail:
    def __init__(self, allowed_directory: str):
        self.allowed_directory = Path(allowed_directory).resolve()
        
        if not self.allowed_directory.exists():
            # In a real scenario, this might be created. Erroring for strict zero-trust initialization
            raise ValueError(f"CRITICAL: Allowed directory {self.allowed_directory} does not exist.")

    def _verify_path(self, target_path: Union[str, Path]) -> Path:
        """
        Resolves the target path and verifies it is a strict subdirectory of the allowed directory.
        Returns the resolved Path object if safe. Raises SecurityViolationError otherwise.
        """
        # Resolve resolves symlinks and standardizes path to absolute
        resolved_path = Path(target_path).resolve()
        
        # Check if the resolved path starts with the allowed directory path
        try:
            resolved_path.relative_to(self.allowed_directory)
        except ValueError:
            raise SecurityViolationError(
                f"SECURITY VIOLATION: Attempted access to '{resolved_path}' outside of jail '{self.allowed_directory}'"
            )
        
        return resolved_path

    def read_file(self, filepath: str) -> str:
        """Reads a file securely within the jail."""
        safe_path = self._verify_path(filepath)
        if not safe_path.is_file():
            raise FileNotFoundError(f"File not found or is a directory: {safe_path}")
        
        with open(safe_path, 'r', encoding='utf-8') as f:
            return f.read()

    def write_file(self, filepath: str, content: str) -> None:
        """Writes to a file securely within the jail."""
        safe_path = self._verify_path(filepath)
        
        # Ensure parent directories exist
        safe_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(safe_path, 'w', encoding='utf-8') as f:
            f.write(content)
            
    def list_files(self, dir_path: str = ".") -> list[str]:
        """Lists files securely within a directory in the jail."""
        # Handle relative pathing from the jail root
        if dir_path == ".":
            target = self.allowed_directory
        else:
            target = self.allowed_directory / dir_path
            
        safe_path = self._verify_path(target)
        if not safe_path.is_dir():
            raise NotADirectoryError(f"Not a directory: {safe_path}")
            
        return [str(p.relative_to(self.allowed_directory)) for p in safe_path.iterdir()]

# Singleton instance initialized from environment variables
# In practice this is imported and used, so initialization happens at module load
import os
from dotenv import load_dotenv

load_dotenv()
ALLOWED_MISSIONS_DIR = os.getenv("ALLOWED_MISSIONS_DIR")

# Fallback for dev/railway if not set. Use current working directory.
if not ALLOWED_MISSIONS_DIR:
    import logging
    logging.warning("ALLOWED_MISSIONS_DIR not set in environment. Defaulting to current working directory ('.').")
    ALLOWED_MISSIONS_DIR = "."

jail = IOJail(ALLOWED_MISSIONS_DIR)

# Expose standard functions to be used by other modules, locking them to the singleton
read_file = jail.read_file
write_file = jail.write_file
list_files = jail.list_files
verify_path = jail._verify_path
