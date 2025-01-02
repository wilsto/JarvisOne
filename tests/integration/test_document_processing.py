"""Integration tests for document processing chain."""

import pytest
from pathlib import Path
import tempfile
from datetime import datetime
import time
from unittest.mock import patch

from src.rag.document_watcher.document_tracker import DocumentTracker
from src.rag.document_watcher.watcher import DocumentEventHandler
from src.rag.document_watcher.processor import DocumentChangeProcessor
from src.rag.document_processor import DocumentProcessor

@pytest.fixture
def temp_test_file():
    """Create a temporary test file."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write("Test content for document processing")
        file_path = f.name
    yield Path(file_path)
    Path(file_path).unlink(missing_ok=True)

@pytest.fixture
def document_processor():
    """Create a document processor instance."""
    return DocumentProcessor()

@pytest.fixture
def document_tracker(temp_db_path):
    """Create a document tracker instance."""
    tracker = DocumentTracker(temp_db_path)
    yield tracker
    tracker._close_connections()

class TestDocumentProcessingChain:
    """Test the complete document processing chain."""
    
    def test_hash_propagation(self, temp_test_file, document_tracker, document_processor):
        """Test hash propagation through the processing chain."""
        workspace_id = "TEST_WORKSPACE"
        
        # Create processor and handler
        processor = DocumentChangeProcessor(workspace_id, document_processor, document_tracker)
        handler = DocumentEventHandler(
            workspace_id=workspace_id,
            doc_tracker=document_tracker,
            doc_processor=document_processor
        )
        
        # Calculate initial hash
        mtime, initial_hash = handler._get_file_info(temp_test_file)
        
        # Simulate file creation
        handler.doc_tracker.update_document(
            workspace_id=workspace_id,
            file_path=str(temp_test_file),
            hash_value=initial_hash
        )
        
        # Verify initial state
        doc_status = handler.doc_tracker.get_document_status(
            workspace_id=workspace_id,
            file_path=str(temp_test_file)
        )
        assert doc_status is not None
        assert doc_status['hash'] == initial_hash
        assert doc_status['status'] == 'pending'
        
        # Start processor and wait for processing
        processor.start()
        time.sleep(6)  # Wait for processing interval
        processor.stop()
        
        # Verify final state
        doc_status = handler.doc_tracker.get_document_status(
            workspace_id=workspace_id,
            file_path=str(temp_test_file)
        )
        assert doc_status['status'] == 'processed'
        assert doc_status['hash'] == initial_hash
        
    def test_hash_update_on_content_change(self, temp_test_file, document_tracker, document_processor):
        """Test hash updates when file content changes."""
        workspace_id = "TEST_WORKSPACE"
        
        # Create processor and handler
        processor = DocumentChangeProcessor(workspace_id, document_processor, document_tracker)
        handler = DocumentEventHandler(
            workspace_id=workspace_id,
            doc_tracker=document_tracker,
            doc_processor=document_processor
        )
        
        # Get initial hash
        mtime, initial_hash = handler._get_file_info(temp_test_file)
        
        # Add initial document
        handler.doc_tracker.update_document(
            workspace_id=workspace_id,
            file_path=str(temp_test_file),
            hash_value=initial_hash
        )
        
        # Start processor and wait for initial processing
        processor.start()
        time.sleep(6)  # Wait for processing interval
        
        # Modify file content
        with open(temp_test_file, 'a') as f:
            f.write("\nAdditional content")
        
        # Get new hash
        mtime, new_hash = handler._get_file_info(temp_test_file)
        
        # Update document with new hash
        handler.doc_tracker.update_document(
            workspace_id=workspace_id,
            file_path=str(temp_test_file),
            hash_value=new_hash
        )
        
        # Wait for processing
        time.sleep(6)  # Wait for processing interval
        processor.stop()
        
        # Verify hash was updated and file was processed
        doc_status = handler.doc_tracker.get_document_status(
            workspace_id=workspace_id,
            file_path=str(temp_test_file)
        )
        assert doc_status['hash'] == new_hash
        assert doc_status['hash'] != initial_hash
        assert doc_status['status'] == 'processed'
        
    def test_error_handling_with_hash(self, temp_test_file, document_tracker, document_processor):
        """Test error handling while preserving hash information."""
        workspace_id = "TEST_WORKSPACE"
        
        # Create processor and handler
        processor = DocumentChangeProcessor(workspace_id, document_processor, document_tracker)
        handler = DocumentEventHandler(
            workspace_id=workspace_id,
            doc_tracker=document_tracker,
            doc_processor=document_processor
        )
        
        # Get initial hash
        mtime, initial_hash = handler._get_file_info(temp_test_file)
        
        # Add initial document
        handler.doc_tracker.update_document(
            workspace_id=workspace_id,
            file_path=str(temp_test_file),
            hash_value=initial_hash
        )
        
        # Mock the document processor to simulate an error
        def mock_process_file(*args, **kwargs):
            error_msg = "Simulated processing error"
            document_processor._error_queue.put(error_msg)
            return False
            
        with patch.object(document_processor, '_process_file_internal', side_effect=mock_process_file):
            # Start processor
            processor.start()
            time.sleep(6)  # Wait for processing interval
            processor.stop()
        
        # Verify error state preserves hash
        doc_status = handler.doc_tracker.get_document_status(
            workspace_id=workspace_id,
            file_path=str(temp_test_file)
        )
        assert doc_status['status'] == 'error'
        assert doc_status['hash'] == initial_hash
        assert doc_status['error_message'] is not None
