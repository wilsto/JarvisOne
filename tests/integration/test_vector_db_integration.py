"""Integration tests for vector database."""

import pytest
import logging
import tempfile
import shutil
from pathlib import Path
from unittest.mock import patch, Mock
from datetime import datetime
import time

from src.vector_db import VectorDBManager
from src.vector_db.config import VectorDBConfig, CollectionConfig
from src.rag.document_processor import DocumentProcessor
from src.rag.query_handler import RAGQueryHandler

@pytest.fixture(scope="module")
def test_dir():
    """Create a temporary directory for test data."""
    tmp_dir = tempfile.mkdtemp()
    yield Path(tmp_dir)
    try:
        shutil.rmtree(tmp_dir)
    except Exception as e:
        logging.warning(f"Failed to cleanup test directory: {e}")

@pytest.fixture(scope="module")
def vector_db_config(test_dir):
    """Create test vector DB config."""
    return VectorDBConfig(
        persist_directory=str(test_dir / "vector_db"),
        collection_prefix="test_",
        default_collection=CollectionConfig(
            distance_metric="cosine",
            embedding_function="sentence-transformers/all-MiniLM-L6-v2",
            chunk_size=1000,
            chunk_overlap=200
        )
    )

@pytest.fixture(scope="module")
def vector_db(vector_db_config):
    """Initialize vector DB manager."""
    manager = VectorDBManager.get_instance()
    manager.initialize(config=vector_db_config)
    yield manager
    # Cleanup
    try:
        manager.client.reset()
    except Exception as e:
        logging.warning(f"Failed to cleanup vector DB: {e}")

@pytest.fixture
def processor():
    """Create document processor."""
    return DocumentProcessor()

@pytest.fixture
def query_handler():
    """Create query handler."""
    return RAGQueryHandler()

def create_test_file(directory: Path, filename: str, content: str):
    """Create a test file with content."""
    file_path = directory / filename
    file_path.write_text(content)
    return file_path

class TestVectorDBIntegration:
    """Integration tests for vector database functionality."""
    
    def test_collection_lifecycle(self, vector_db):
        """Test collection creation and management."""
        workspace_id = "test_workspace_1"
        
        # Create collection
        collection = vector_db.get_collection(workspace_id, create=True)
        assert collection is not None
        
        # Get collection name
        collection_name = f"{vector_db.config.collection_prefix}{workspace_id}"
        
        # Verify collection exists via direct client check
        collections = vector_db.client.list_collections()
        assert any(c.name == collection_name for c in collections)
        
        # Get collection stats
        stats = vector_db.monitor.get_collection_stats(collection_name)
        assert stats is not None
        assert stats.document_count == 0
    
    def test_document_processing_and_query(self, processor, query_handler, test_dir):
        """Test document processing and querying."""
        workspace_id = "test_workspace_2"
        
        # Create test documents
        docs_dir = test_dir / "docs"
        docs_dir.mkdir(exist_ok=True)
        
        # Create files with different content
        file1 = create_test_file(docs_dir, "python_tips.txt", 
            "Python is a versatile programming language. It supports multiple paradigms including "
            "object-oriented, imperative and functional programming."
        )
        
        file2 = create_test_file(docs_dir, "java_tips.txt",
            "Java is a class-based, object-oriented programming language. It follows the principle "
            "of 'Write Once, Run Anywhere'."
        )
        
        # Process documents
        processor.process_file(file1, workspace_id)
        processor.process_file(file2, workspace_id)
        
        # Wait for processing to complete and stats to update
        time.sleep(1)
        
        # Query for Python-related content
        results = query_handler.query(
            query_text="Tell me about Python programming",
            workspace_id=workspace_id,
            top_k=1
        )
        
        # Verify results
        assert results is not None
        assert len(results) > 0
        assert any("Python" in doc["content"] for doc in results)
        
        # Query for Java-related content
        results = query_handler.query(
            query_text="What is Java's main principle?",
            workspace_id=workspace_id,
            top_k=1
        )
        
        # Verify results
        assert results is not None
        assert len(results) > 0
        assert any("Write Once, Run Anywhere" in doc["content"] for doc in results)
    
    def test_performance_metrics(self, vector_db, processor, test_dir):
        """Test performance metrics and monitoring."""
        workspace_id = "test_workspace_3"
        
        # Create and process a test document
        docs_dir = test_dir / "docs"
        docs_dir.mkdir(exist_ok=True)
        
        test_file = create_test_file(docs_dir, "test.txt", "Test content for monitoring.")
        processor.process_file(test_file, workspace_id)
        
        # Wait for processing to complete and stats to update
        time.sleep(1)
        
        # Get collection name
        collection_name = f"{vector_db.config.collection_prefix}{workspace_id}"
        
        # Get metrics
        stats = vector_db.monitor.get_collection_stats(collection_name)
        
        # Verify metrics
        assert stats is not None
        assert stats.document_count > 0
        assert stats.last_updated is not None
