"""Tests for MarkItDown document handler."""

import pytest
from pathlib import Path
import tempfile
import shutil

from src.rag.document_handlers import MarkItDownHandler

@pytest.fixture
def temp_dir():
    """Create a temporary directory for test files."""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    try:
        shutil.rmtree(temp_dir)
    except PermissionError:
        pass

@pytest.fixture
def handler():
    """Create a MarkItDownHandler instance."""
    return MarkItDownHandler(max_file_size_mb=1)  # Small size for testing

def create_test_file(temp_dir: str, filename: str, content: str) -> Path:
    """Create a test file with given content."""
    file_path = Path(temp_dir) / filename
    file_path.write_text(content)
    return file_path

def test_supported_extensions(handler):
    """Test that handler recognizes supported file extensions."""
    assert '.pdf' in handler.SUPPORTED_EXTENSIONS
    assert '.docx' in handler.SUPPORTED_EXTENSIONS
    assert '.xlsx' in handler.SUPPORTED_EXTENSIONS
    assert '.unsupported' not in handler.SUPPORTED_EXTENSIONS

def test_file_size_limit(handler, temp_dir):
    """Test that handler enforces file size limit."""
    # Create a file larger than 1MB
    large_file = create_test_file(temp_dir, "large.pdf", "x" * (2 * 1024 * 1024))
    assert not handler.can_handle(large_file)

def test_unsupported_extension(handler, temp_dir):
    """Test that handler rejects unsupported file types."""
    unsupported_file = create_test_file(temp_dir, "test.unsupported", "content")
    assert not handler.can_handle(unsupported_file)

def test_nonexistent_file(handler):
    """Test that handler rejects nonexistent files."""
    assert not handler.can_handle(Path("nonexistent.pdf"))

def test_extract_text_basic(handler, temp_dir):
    """Test basic text extraction from a markdown file."""
    content = "# Test\nThis is a test document."
    test_file = create_test_file(temp_dir, "test.md", content)
    
    text, metadata = handler.extract_text(test_file)
    
    assert "Test" in text
    assert "test document" in text
    assert metadata['file_name'] == "test.md"
    assert metadata['file_type'] == ".md"
    assert metadata['file_size'] > 0
