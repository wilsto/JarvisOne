"""Document handlers package."""

from .base_handler import BaseDocumentHandler
from .markitdown_handler import MarkItDownHandler
from .text_handler import TextHandler
from .epub_handler import EpubHandler

__all__ = ['BaseDocumentHandler', 'MarkItDownHandler', 'TextHandler', 'EpubHandler']
