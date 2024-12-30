"""Base document handler interface."""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional, Dict, Any, Set

class BaseDocumentHandler(ABC):
    """Base class for document handlers."""
    
    def __init__(self, max_file_size_mb: int = 10):
        """Initialize the handler with size limits."""
        self.max_file_size_bytes = max_file_size_mb * 1024 * 1024
    
    @property
    @abstractmethod
    def SUPPORTED_EXTENSIONS(self) -> Set[str]:
        """Set of file extensions this handler supports."""
        pass

    def can_handle(self, file_path: Path) -> bool:
        """Check if file can be handled (size, existence and extension)."""
        if not file_path.exists():
            return False
            
        file_size = file_path.stat().st_size
        if file_size > self.max_file_size_bytes:
            return False
            
        return file_path.suffix.lower() in self.SUPPORTED_EXTENSIONS
    
    @abstractmethod
    def extract_text(self, file_path: Path) -> tuple[str, Dict[str, Any]]:
        """
        Extract text content and metadata from document.
        
        Args:
            file_path: Path to the document
            
        Returns:
            Tuple of (text_content, metadata)
        
        Raises:
            ValueError: If file is password protected or cannot be processed
        """
        pass
