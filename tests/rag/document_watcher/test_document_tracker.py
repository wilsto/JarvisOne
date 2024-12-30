"""Test document tracking functionality."""

import pytest
from pathlib import Path
import tempfile
import sqlite3
from datetime import datetime

from src.rag.document_watcher.document_tracker import DocumentTracker

@pytest.fixture
def temp_db_path():
    """Create a temporary database path for testing."""
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
        db_path = f.name
    yield db_path
    # Ensure we wait for any connections to be closed
    import time
    time.sleep(0.1)  # Small delay to ensure connections are closed
    Path(db_path).unlink(missing_ok=True)

@pytest.fixture
def tracker(temp_db_path):
    """Create a document tracker instance."""
    tracker = DocumentTracker(temp_db_path)
    yield tracker
    # Ensure connections are closed
    tracker._close_connections()

class TestDocumentTracker:
    """Test document tracking functionality."""
    
    def test_init_creates_table(self, temp_db_path):
        """Test that initialization creates the tracking table."""
        # Create a new connection for this test
        tracker = None
        conn = None
        try:
            tracker = DocumentTracker(temp_db_path)
            conn = sqlite3.connect(temp_db_path)
            cursor = conn.cursor()
            cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name='document_tracking'
            """)
            assert cursor.fetchone() is not None
        finally:
            if conn:
                conn.close()
            if tracker:
                tracker._close_connections()
            
    def test_update_document_new(self, tracker, tmp_path):
        """Test adding a new document."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("test content")
        
        tracker.update_document("COACHING", str(test_file))
        
        status = tracker.get_document_status("COACHING", str(test_file))
        assert status is not None
        assert status["status"] == "pending"
        assert status["workspace_id"] == "COACHING"
        
    def test_update_document_deleted(self, tracker, tmp_path):
        """Test marking a document as deleted."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("test content")
        
        # First add the document
        tracker.update_document("COACHING", str(test_file))
        
        # Then mark it as deleted
        import time
        time.sleep(0.1)  # Small delay before file deletion
        test_file.unlink()
        tracker.update_document("COACHING", str(test_file), status="deleted")
        
        status = tracker.get_document_status("COACHING", str(test_file))
        assert status["status"] == "deleted"
        
    def test_get_pending_documents(self, tracker, tmp_path):
        """Test retrieving pending documents."""
        # Create test files
        files = []
        for i in range(3):
            f = tmp_path / f"test{i}.txt"
            f.write_text(f"content {i}")
            files.append(f)
            tracker.update_document("COACHING", str(f))
            
        # Mark one as processed
        tracker.update_document("COACHING", str(files[0]), status="processed")
        
        pending = tracker.get_pending_documents("COACHING")
        assert len(pending) == 2
        assert all(doc["status"] == "pending" for doc in pending)
