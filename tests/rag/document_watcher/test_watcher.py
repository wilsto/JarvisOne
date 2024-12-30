"""Test file system watching functionality."""

import pytest
from pathlib import Path
import tempfile
import time
from unittest.mock import Mock, patch

from src.rag.document_watcher.watcher import FileSystemWatcher, DocumentEventHandler
from src.rag.document_processor import DocumentProcessor
from src.rag.document_watcher.document_tracker import DocumentTracker

@pytest.fixture
def temp_dir():
    """Create a temporary directory for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)

@pytest.fixture
def mock_doc_processor():
    """Create a mock document processor."""
    processor = Mock(spec=DocumentProcessor)
    processor.handlers = [Mock(SUPPORTED_EXTENSIONS={".txt", ".md"})]
    return processor

@pytest.fixture
def mock_doc_tracker():
    """Create a mock document tracker."""
    return Mock(spec=DocumentTracker)

class TestDocumentEventHandler:
    """Test document event handling."""
    
    def test_on_created(self, temp_dir, mock_doc_processor, mock_doc_tracker):
        """Test handling file creation event."""
        handler = DocumentEventHandler("COACHING", mock_doc_processor, mock_doc_tracker)
        
        # Create a test file
        test_file = temp_dir / "test.txt"
        test_file.write_text("test content")
        
        # Simulate file creation event
        event = Mock()
        event.is_directory = False
        event.src_path = str(test_file)
        
        handler.on_created(event)
        
        mock_doc_tracker.update_document.assert_called_once_with(
            "COACHING", 
            str(test_file), 
            status="pending"
        )
        
    def test_on_modified(self, temp_dir, mock_doc_processor, mock_doc_tracker):
        """Test handling file modification event."""
        handler = DocumentEventHandler("COACHING", mock_doc_processor, mock_doc_tracker)
        
        # Create and modify a test file
        test_file = temp_dir / "test.txt"
        test_file.write_text("initial content")
        
        event = Mock()
        event.is_directory = False
        event.src_path = str(test_file)
        
        handler.on_modified(event)
        
        mock_doc_tracker.update_document.assert_called_once_with(
            "COACHING", 
            str(test_file), 
            status="pending"
        )
        
    def test_ignores_unsupported_files(self, temp_dir, mock_doc_processor, mock_doc_tracker):
        """Test that unsupported file types are ignored."""
        handler = DocumentEventHandler("COACHING", mock_doc_processor, mock_doc_tracker)
        
        # Create an unsupported file
        test_file = temp_dir / "test.xyz"
        test_file.write_text("test content")
        
        event = Mock()
        event.is_directory = False
        event.src_path = str(test_file)
        
        handler.on_created(event)
        
        mock_doc_tracker.update_document.assert_not_called()

class TestFileSystemWatcher:
    """Test file system watching functionality."""
    
    def test_setup_watchers(self, temp_dir, mock_doc_processor):
        """Test watcher setup with valid paths."""
        watcher = FileSystemWatcher(
            "COACHING",
            [temp_dir],
            mock_doc_processor
        )
        
        assert len(watcher.observer.emitters) == 1
        
    def test_scan_existing_files(self, temp_dir, mock_doc_processor):
        """Test scanning existing files."""
        # Create test files
        test_file = temp_dir / "test.txt"
        test_file.write_text("test content")
        
        unsupported_file = temp_dir / "test.xyz"
        unsupported_file.write_text("test content")
        
        watcher = FileSystemWatcher(
            "COACHING",
            [temp_dir],
            mock_doc_processor
        )
        
        with patch.object(watcher.doc_tracker, 'update_document') as mock_update:
            watcher.scan_existing_files()
            mock_update.assert_called_once_with(
                "COACHING",
                str(test_file),
                status="pending"
            )
