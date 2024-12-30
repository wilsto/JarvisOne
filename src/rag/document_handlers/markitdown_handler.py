"""MarkItDown document handler for converting various file types to text."""

from pathlib import Path
from typing import Dict, Any, Set
from markitdown import MarkItDown

from .base_handler import BaseDocumentHandler

class MarkItDownHandler(BaseDocumentHandler):
    """Handler for converting documents using MarkItDown."""
    
    @property
    def SUPPORTED_EXTENSIONS(self) -> Set[str]:
        """Supported Microsoft Office and PDF formats."""
        return {'.pdf', '.docx', '.xlsx', '.pptx'}
    
    def __init__(self, max_file_size_mb: int = 10):
        """Initialize the handler."""
        super().__init__(max_file_size_mb)
        self.converter = MarkItDown()
        
    def extract_text(self, file_path: Path) -> tuple[str, Dict[str, Any]]:
        """
        Extract text content using MarkItDown.
        
        Args:
            file_path: Path to the document
            
        Returns:
            Tuple of (text_content, metadata)
            
        Raises:
            ValueError: If file is password protected or cannot be processed
        """
        try:
            result = self.converter.convert(str(file_path))
            
            # Extract basic metadata
            metadata = {
                'file_name': file_path.name,
                'file_size': file_path.stat().st_size,
                'file_type': file_path.suffix.lower(),
            }
            
            return result.text_content, metadata
            
        except Exception as e:
            if "password" in str(e).lower():
                raise ValueError(f"Document is password protected: {file_path}")
            raise ValueError(f"Failed to process document: {e}")
