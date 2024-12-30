"""Handler for text-based document formats (JSON, Markdown, TXT)."""

import json
import markdown
from pathlib import Path
from typing import Dict, Any, Set

from .base_handler import BaseDocumentHandler

class TextHandler(BaseDocumentHandler):
    """Handler for text-based formats like JSON, Markdown, and plain text."""
    
    SUPPORTED_EXTENSIONS: Set[str] = {
        '.json', '.md', '.markdown', '.txt'
    }
    
    def __init__(self, max_file_size_mb: int = 10):
        """Initialize the handler."""
        super().__init__(max_file_size_mb)
    
    def can_handle(self, file_path: Path) -> bool:
        """Check if file can be handled by this handler."""
        if not super().can_handle(file_path):
            return False
        
        return file_path.suffix.lower() in self.SUPPORTED_EXTENSIONS
    
    def extract_text(self, file_path: Path) -> tuple[str, Dict[str, Any]]:
        """
        Extract text content from text-based files.
        
        Args:
            file_path: Path to the document
            
        Returns:
            Tuple of (text_content, metadata)
            
        Raises:
            ValueError: If file cannot be processed
        """
        try:
            content = file_path.read_text(encoding='utf-8')
            file_type = file_path.suffix.lower()
            
            if file_type == '.json':
                # Parse JSON to ensure it's valid
                data = json.loads(content)
                # Extract all string values recursively
                def extract_strings(obj) -> list[str]:
                    strings = []
                    if isinstance(obj, dict):
                        for value in obj.values():
                            strings.extend(extract_strings(value))
                    elif isinstance(obj, list):
                        for item in obj:
                            strings.extend(extract_strings(item))
                    elif isinstance(obj, (str, int, float, bool)):
                        strings.append(str(obj))
                    return strings
                
                text_content = '\n'.join(extract_strings(data))
            elif file_type in {'.md', '.markdown'}:
                # Convert markdown to plain text by first converting to HTML
                html = markdown.markdown(content)
                # Simple HTML tag removal (for basic plain text)
                text_content = content
            else:  # .txt and other text files
                text_content = content
            
            metadata = {
                'file_name': file_path.name,
                'file_size': file_path.stat().st_size,
                'file_type': file_type,
            }
            
            return text_content, metadata
            
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON file: {e}")
        except Exception as e:
            raise ValueError(f"Failed to process document: {e}")
