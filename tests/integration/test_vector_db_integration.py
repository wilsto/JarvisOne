"""Integration tests for Vector DB functionality."""

import pytest
from pathlib import Path
import tempfile
import shutil
from datetime import datetime

from vector_db.manager import VectorDBManager
from vector_db.config import VectorDBConfig, CollectionConfig
from rag.document_processor import DocumentProcessor
from rag.query_handler import RAGQueryHandler

@pytest.fixture(scope="module")
def test_dir():
    """Create a temporary directory for test data."""
    tmp_dir = tempfile.mkdtemp()
    yield Path(tmp_dir)
    try:
        shutil.rmtree(tmp_dir, ignore_errors=True)
    except Exception as e:
        print(f"Error during cleanup: {e}")

@pytest.fixture(scope="module")
def vector_db_config(test_dir):
    """Create test vector DB config."""
    return VectorDBConfig(
        persist_directory=str(test_dir / "vector_db"),
        collection_prefix="workspace_",  # Use standard prefix
        default_collection=CollectionConfig(
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
        manager.close()
    except Exception as e:
        print(f"Error during cleanup: {e}")

@pytest.fixture(scope="module")
def processor(vector_db):
    """Create document processor."""
    return DocumentProcessor()

@pytest.fixture(scope="module")
def query_handler(vector_db):
    """Create query handler."""
    return RAGQueryHandler()

def create_test_file(directory: Path, filename: str, content: str) -> Path:
    """Create a test file with content."""
    file_path = directory / filename
    file_path.write_text(content)
    return file_path

class TestVectorDBIntegration:
    """Integration tests for Vector DB functionality."""
    
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
        file2 = create_test_file(docs_dir, "data_science.txt",
            "Data science combines statistics and programming. Python is widely used in data science "
            "with libraries like pandas and numpy."
        )
        
        # Process documents
        assert processor.process_file(str(file1), workspace_id)
        assert processor.process_file(str(file2), workspace_id)
        
        # Test queries
        results = query_handler.query(
            query_text="What programming language is mentioned?",  # Fixed parameter name
            workspace_id=workspace_id,
            top_k=2  # Use correct parameter name
        )
        assert results is not None
        assert len(results) > 0
        assert any("Python" in result["content"] for result in results), "Python should be mentioned in results"
        
        # Test semantic search
        results = query_handler.query(
            query_text="Tell me about data analysis tools",  # Fixed parameter name
            workspace_id=workspace_id,
            top_k=2  # Use correct parameter name
        )
        assert results is not None
        assert len(results) > 0
        assert any("pandas" in result["content"] for result in results)
    
    def test_performance_metrics(self, vector_db, processor, test_dir):
        """Test performance metrics and monitoring."""
        workspace_id = "test_workspace_3"
        
        # Create test document
        docs_dir = test_dir / "docs"
        docs_dir.mkdir(exist_ok=True)
        
        # Create a larger file for performance testing
        content = " ".join(["Performance test content"] * 100)  # Create larger content
        test_file = create_test_file(docs_dir, "performance.txt", content)
        
        # Measure processing time
        start_time = datetime.now()
        success = processor.process_file(str(test_file), workspace_id)
        processing_time = (datetime.now() - start_time).total_seconds()
        
        assert success
        assert processing_time < 5.0  # Should process within 5 seconds
        
        # Check collection metrics
        collection_name = f"{vector_db.config.collection_prefix}{workspace_id}"
        stats = vector_db.monitor.get_collection_stats(collection_name)
        assert stats is not None
        assert stats.document_count > 0
        
        # Verify monitoring data
        monitoring_data = vector_db.monitor.get_monitoring_data()
        assert collection_name in monitoring_data["collections"], "Collection should be in monitoring data"
        assert monitoring_data["collections"][collection_name]["document_count"] > 0, "Collection should have documents"
        assert monitoring_data["metrics"]["total_documents"] > 0, "Total documents should be greater than 0"
        assert monitoring_data["metrics"]["total_collections"] > 0, "Should have at least one collection"
