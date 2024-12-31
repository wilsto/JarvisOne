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
    # Clean up
    try:
        Path(db_path).unlink(missing_ok=True)
    except PermissionError:
        # Ensure all connections are closed
        import gc
        gc.collect()  # Force garbage collection
        import time
        time.sleep(0.1)  # Wait a bit
        try:
            Path(db_path).unlink(missing_ok=True)
        except PermissionError:
            pass  # Let the OS clean it up later

@pytest.fixture
def tracker(temp_db_path):
    """Create a document tracker instance."""
    tracker = DocumentTracker(temp_db_path)
    yield tracker
    # Clean up
    tracker._close_connections()

class TestDocumentTracker:
    """Test document tracking functionality."""
    
    def test_init_creates_table(self, temp_db_path):
        """Test that initialization creates the tracking table."""
        tracker = DocumentTracker(temp_db_path)
        try:
            # Use tracker's connection to verify table
            conn = tracker._get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name='document_tracking'
            """)
            assert cursor.fetchone() is not None
        finally:
            tracker._close_connections()

    def test_update_document_new(self, tracker):
        """Test updating a new document."""
        test_path = "test/path/doc.txt"
        test_time = datetime.now()
        
        tracker.update_document(
            workspace_id="COACHING",
            file_path=test_path,
            status="pending",
            last_modified=test_time
        )
        
        try:
            # Verify document was added
            conn = tracker._get_connection()
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM document_tracking WHERE file_path = ? AND workspace_id = ?",
                (test_path, "COACHING")
            )
            row = cursor.fetchone()
            
            assert row is not None
            assert row['file_path'] == test_path
            assert row['last_modified'] == test_time.isoformat()
            assert row['status'] == 'pending'
        finally:
            tracker._close_connections()

    def test_update_document_deleted(self, tracker):
        """Test marking a document as deleted."""
        test_path = "test/path/doc.txt"
        test_time = datetime.now()
        
        try:
            # First add the document
            tracker.update_document(
                workspace_id="COACHING",
                file_path=test_path,
                status="pending",
                last_modified=test_time
            )
            
            # Then mark it as deleted
            tracker.update_document(
                workspace_id="COACHING",
                file_path=test_path,
                status="deleted",
                last_modified=None
            )
            
            # Verify document was marked as deleted
            conn = tracker._get_connection()
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM document_tracking WHERE file_path = ? AND workspace_id = ?",
                (test_path, "COACHING")
            )
            row = cursor.fetchone()
            
            assert row is not None
            assert row['status'] == 'deleted'
        finally:
            tracker._close_connections()

    def test_get_pending_documents(self, tracker):
        """Test retrieving pending documents."""
        try:
            # Add some test documents
            test_docs = [
                ("doc1.txt", datetime.now()),
                ("doc2.txt", datetime.now()),
                ("doc3.txt", datetime.now())
            ]
            
            for doc_path, mod_time in test_docs:
                tracker.update_document(
                    workspace_id="COACHING",
                    file_path=doc_path,
                    status="pending",
                    last_modified=mod_time
                )
            
            # Mark one as processed
            tracker.update_document(
                workspace_id="COACHING",
                file_path="doc2.txt",
                status="processed",
                last_modified=test_docs[1][1]
            )
            
            # Get pending documents
            pending = tracker.get_pending_documents("COACHING")
            
            # Should only see doc1 and doc3
            assert len(pending) == 2
            paths = [doc['file_path'] for doc in pending]
            assert "doc1.txt" in paths
            assert "doc3.txt" in paths
            assert "doc2.txt" not in paths
        finally:
            tracker._close_connections()
