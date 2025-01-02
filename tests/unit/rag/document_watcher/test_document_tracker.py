"""Test document tracking functionality."""

import pytest
from datetime import datetime

from src.rag.document_watcher.document_tracker import DocumentTracker

@pytest.fixture
def tracker(temp_db_path):
    """Create a document tracker instance."""
    tracker = DocumentTracker(temp_db_path)
    yield tracker
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
        test_hash = "test_hash_123"
        
        tracker.update_document(
            workspace_id="COACHING",
            file_path=test_path,
            hash_value=test_hash,
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
            assert row['status'] == 'pending'  # Default status
            assert row['hash'] == test_hash
        finally:
            tracker._close_connections()

    def test_hash_value_required(self, tracker):
        """Test that hash_value is required."""
        with pytest.raises(TypeError, match="missing 1 required positional argument: 'hash_value'"):
            tracker.update_document(
                workspace_id="COACHING",
                file_path="test.txt",
                status="pending"
            )

    def test_hash_value_validation(self, tracker):
        """Test that empty hash_value is rejected."""
        with pytest.raises(ValueError, match="Hash value is required"):
            tracker.update_document(
                workspace_id="COACHING",
                file_path="test.txt",
                hash_value="",  # Empty hash
                status="pending"
            )

    def test_update_document_deleted(self, tracker):
        """Test marking a document as deleted."""
        test_path = "test/path/doc.txt"
        test_time = datetime.now()
        test_hash = "test_hash_123"
        deleted_hash = "deleted_hash_456"
        
        try:
            # First add the document
            tracker.update_document(
                workspace_id="COACHING",
                file_path=test_path,
                hash_value=test_hash,
                last_modified=test_time
            )
            
            # Then mark it as deleted
            tracker.update_document(
                workspace_id="COACHING",
                file_path=test_path,
                status="deleted",
                hash_value=deleted_hash
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
            assert row['hash'] == deleted_hash  # Verify hash was updated
        finally:
            tracker._close_connections()

    def test_get_pending_documents(self, tracker):
        """Test retrieving pending documents."""
        try:
            # Add some test documents
            test_docs = [
                ("doc1.txt", datetime.now(), "hash1"),
                ("doc2.txt", datetime.now(), "hash2"),
                ("doc3.txt", datetime.now(), "hash3")
            ]
            
            for doc_path, mod_time, doc_hash in test_docs:
                tracker.update_document(
                    workspace_id="COACHING",
                    file_path=doc_path,
                    hash_value=doc_hash,
                    last_modified=mod_time
                )
            
            # Mark one as processed
            tracker.update_document(
                workspace_id="COACHING",
                file_path="doc2.txt",
                status="processed",
                hash_value="hash2_processed"
            )
            
            # Get pending documents
            pending = tracker.get_pending_documents("COACHING")
            
            # Should only see doc1 and doc3
            assert len(pending) == 2
            paths = [doc['file_path'] for doc in pending]
            hashes = [doc['hash'] for doc in pending]
            assert "doc1.txt" in paths
            assert "doc3.txt" in paths
            assert "doc2.txt" not in paths
            assert "hash1" in hashes
            assert "hash3" in hashes
        finally:
            tracker._close_connections()

    def test_hash_preservation(self, tracker):
        """Test that hash is preserved when updating other fields."""
        test_path = "test/path/doc.txt"
        original_hash = "original_hash_123"
        
        # Create document with initial hash
        tracker.update_document(
            workspace_id="COACHING",
            file_path=test_path,
            hash_value=original_hash
        )
        
        # Update status without changing hash
        tracker.update_document(
            workspace_id="COACHING",
            file_path=test_path,
            status="processed",
            hash_value=original_hash
        )
        
        # Verify hash remains unchanged
        doc = tracker.get_document_status("COACHING", test_path)
        assert doc['hash'] == original_hash
        assert doc['status'] == "processed"
