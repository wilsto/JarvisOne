"""Handler for EPUB documents."""

from pathlib import Path
from typing import Dict, Any, Set
import ebooklib
from ebooklib import epub
from bs4 import BeautifulSoup

from .base_handler import BaseDocumentHandler

class EpubHandler(BaseDocumentHandler):
    """Handler for EPUB format."""
    
    SUPPORTED_EXTENSIONS: Set[str] = {'.epub'}
    
    def __init__(self, max_file_size_mb: int = 10):
        """Initialize the handler."""
        super().__init__(max_file_size_mb)
    
    def can_handle(self, file_path: Path) -> bool:
        """Check if file can be handled by this handler."""
        if not super().can_handle(file_path):
            return False
        
        return file_path.suffix.lower() in self.SUPPORTED_EXTENSIONS
    
    def _extract_text_from_html(self, html_content: str) -> str:
        """Extract text from HTML content."""
        soup = BeautifulSoup(html_content, 'html.parser')
        return soup.get_text(separator='\n', strip=True)
    
    def _get_metadata_value(self, book: epub.EpubBook, name: str) -> str:
        """Safely extract metadata value."""
        values = book.get_metadata('DC', name)
        if values:
            # Get first value and ensure it's a string
            value = values[0][0] if isinstance(values[0], tuple) else values[0]
            return str(value)
        return ""
    
    def extract_text(self, file_path: Path) -> tuple[str, Dict[str, Any]]:
        """
        Extract text content from EPUB file.
        
        Args:
            file_path: Path to the document
            
        Returns:
            Tuple of (text_content, metadata)
            
        Raises:
            ValueError: If file cannot be processed
        """
        try:
            book = epub.read_epub(str(file_path))
            
            # Extract metadata safely
            metadata = {
                'file_name': file_path.name,
                'file_size': file_path.stat().st_size,
                'file_type': '.epub',
                'title': self._get_metadata_value(book, 'title'),
                'author': self._get_metadata_value(book, 'creator'),
                'language': self._get_metadata_value(book, 'language'),
            }
            
            # Extract text from all documents
            text_content = []
            for item in book.get_items_of_type(ebooklib.ITEM_DOCUMENT):
                text_content.append(self._extract_text_from_html(item.get_content().decode('utf-8')))
            
            return '\n\n'.join(text_content), metadata
            
        except Exception as e:
            raise ValueError(f"Failed to process EPUB document: {e}")
