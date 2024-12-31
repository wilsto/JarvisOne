"""Test file system watching functionality."""

import pytest
from pathlib import Path
import tempfile
import time
from unittest.mock import Mock, patch, ANY
from datetime import datetime

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
    # Mock the handlers attribute directly
    mock_handler = Mock()
    mock_handler.SUPPORTED_EXTENSIONS = {".txt", ".md"}
    processor.handlers = [mock_handler]
    return processor

@pytest.fixture
def mock_doc_tracker():
    """Create a mock document tracker."""
    return Mock(spec=DocumentTracker)

class TestDocumentEventHandler:
    """Test document event handling."""
    
    def test_on_created(self, temp_dir, mock_doc_processor, mock_doc_tracker):
        """Test handling file creation event."""
        handler = DocumentEventHandler("COACHING", mock_doc_tracker, mock_doc_processor)
        
        # Create a test file
        test_file = temp_dir / "test.txt"
        test_file.write_text("test content")
        
        # Simulate file creation event
        event = Mock()
        event.is_directory = False
        event.src_path = str(test_file)
        
        handler.on_created(event)
        
        # Verify document was tracked
        mock_doc_tracker.update_document.assert_called_once_with(
            workspace_id="COACHING",
            file_path=str(test_file),
            status="pending",
            last_modified=ANY,  # On ne vérifie pas la valeur exacte
            hash_value=ANY      # On ne vérifie pas la valeur exacte
        )

    def test_on_modified(self, temp_dir, mock_doc_processor, mock_doc_tracker):
        """Test handling file modification event."""
        handler = DocumentEventHandler("COACHING", mock_doc_tracker, mock_doc_processor)
        
        # Create and modify a test file
        test_file = temp_dir / "test.txt"
        test_file.write_text("initial content")
        time.sleep(0.1)  # Ensure modification time changes
        test_file.write_text("modified content")
        
        # Simulate file modification event
        event = Mock()
        event.is_directory = False
        event.src_path = str(test_file)
        
        handler.on_modified(event)
        
        # Verify document was tracked
        mock_doc_tracker.update_document.assert_called_once_with(
            workspace_id="COACHING",
            file_path=str(test_file),
            status="pending",
            last_modified=ANY,  # On ne vérifie pas la valeur exacte
            hash_value=ANY      # On ne vérifie pas la valeur exacte
        )

    def test_ignores_unsupported_files(self, temp_dir, mock_doc_processor, mock_doc_tracker):
        """Test that unsupported file types are ignored."""
        handler = DocumentEventHandler("COACHING", mock_doc_tracker, mock_doc_processor)
        
        # Create an unsupported file
        test_file = temp_dir / "test.xyz"
        test_file.write_text("test content")
        
        # Simulate events
        event = Mock()
        event.is_directory = False
        event.src_path = str(test_file)
        
        handler.on_created(event)
        handler.on_modified(event)
        
        # Verify no tracking occurred
        mock_doc_tracker.update_document.assert_not_called()

class TestFileSystemWatcher:
    """Test file system watching functionality."""
    
    def test_setup_watchers(self, temp_dir, mock_doc_processor, mock_doc_tracker):
        """Test watcher setup with valid paths."""
        watcher = FileSystemWatcher(
            workspace_id="COACHING",
            paths=[temp_dir],
            doc_tracker=mock_doc_tracker,
            doc_processor=mock_doc_processor
        )
        
        try:
            # Start the watcher
            watcher.start()
            
            # Verify observer is set up and running
            assert watcher.observer is not None
            assert watcher.observer.is_alive()
            assert len(watcher.observer.emitters) > 0
            
            # Verify paths are being watched
            watched_paths = {
                str(Path(emitter.watch.path)) 
                for emitter in watcher.observer.emitters
            }
            assert str(temp_dir) in watched_paths
        finally:
            watcher.stop()

    def test_scan_existing_files(self, temp_dir, mock_doc_processor, mock_doc_tracker):
        """Test scanning existing files."""
        # Create some test files
        (temp_dir / "test1.txt").write_text("test1")
        (temp_dir / "test2.md").write_text("test2")
        (temp_dir / "test3.xyz").write_text("test3")  # Unsupported extension
        
        watcher = FileSystemWatcher(
            workspace_id="COACHING",
            paths=[temp_dir],
            doc_tracker=mock_doc_tracker,
            doc_processor=mock_doc_processor
        )
        
        try:
            # Start the watcher
            watcher.start()
            time.sleep(0.1)  # Attendre un peu que le scan soit terminé
            
            # Verify only supported files were processed
            assert mock_doc_tracker.update_document.call_count == 2  # Only .txt and .md files
            
            # Get all calls to update_document
            calls = mock_doc_tracker.update_document.call_args_list
            processed_files = {
                call.kwargs['file_path'] for call in calls
            }
            
            assert str(temp_dir / "test1.txt") in processed_files
            assert str(temp_dir / "test2.md") in processed_files
            assert str(temp_dir / "test3.xyz") not in processed_files
        finally:
            watcher.stop()
