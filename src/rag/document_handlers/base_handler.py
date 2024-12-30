"""Base document handler interface."""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional, Dict, Any

class BaseDocumentHandler(ABC):
    """Base class for document handlers."""
    
    def __init__(self, max_file_size_mb: int = 10):
        """Initialize the handler with size limits."""
        self.max_file_size_bytes = max_file_size_mb * 1024 * 1024
    
    def can_handle(self, file_path: Path) -> bool:
        """Check if file can be handled (size and extension)."""
        if not file_path.exists():
            return False
            
        file_size = file_path.stat().st_size
        if file_size > self.max_file_size_bytes:
            return False
            
        return True
    
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
