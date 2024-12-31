"""Test vector database manager."""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch
from vector_db.manager import VectorDBManager

@pytest.fixture
def mock_config():
    """Mock configuration."""
    return {
        "vector_db": {
            "path": "data/test_vector_db",
            "collection_prefix": "test_",
            "collection_settings": {
                "distance_metric": "cosine",
                "chunk_size": 1000
            }
        }
    }

@pytest.fixture
def manager(mock_config):
    """Create VectorDBManager instance."""
    with patch('chromadb.PersistentClient'):
        manager = VectorDBManager(mock_config)
        return manager

def test_singleton(mock_config):
    """Test singleton pattern."""
    with patch('chromadb.PersistentClient'):
        manager1 = VectorDBManager.get_instance(mock_config)
        manager2 = VectorDBManager.get_instance()
        assert manager1 is manager2

def test_initialization(manager):
    """Test manager initialization."""
    assert manager.config.base_path == Path("data/test_vector_db")
    assert manager.config.collection_prefix == "test_"
    assert manager.monitor is not None

def test_get_collection(manager):
    """Test getting a collection."""
    mock_collection = Mock()
    mock_collection.get.return_value = {"ids": ["1", "2"]}
    manager.client.get_or_create_collection.return_value = mock_collection
    
    collection = manager.get_collection("workspace1")
    assert collection is mock_collection
    assert "test_workspace1" in manager._collections

def test_add_documents(manager):
    """Test adding documents."""
    mock_collection = Mock()
    mock_collection.get.return_value = {"ids": ["1", "2", "3"]}
    manager.client.get_or_create_collection.return_value = mock_collection
    
    texts = ["doc1", "doc2"]
    metadatas = [{"source": "test1"}, {"source": "test2"}]
    
    success = manager.add_documents("workspace1", texts, metadatas)
    assert success
    mock_collection.add.assert_called_once()

def test_query(manager):
    """Test querying documents."""
    mock_collection = Mock()
    mock_collection.get.return_value = {"ids": ["1"]}
    mock_collection.query.return_value = {
        "documents": [["doc1"]],
        "metadatas": [[{"source": "test"}]],
        "distances": [[0.5]]
    }
    manager.client.get_or_create_collection.return_value = mock_collection
    
    results = manager.query("workspace1", "test query")
    assert len(results) == 1
    assert results[0]["content"] == "doc1"
    assert results[0]["distance"] == 0.5

def test_get_stats(manager):
    """Test getting statistics."""
    mock_collection = Mock()
    mock_collection.get.return_value = {"ids": ["1", "2"]}
    manager.client.get_or_create_collection.return_value = mock_collection
    
    # Add a collection
    manager.get_collection("workspace1")
    
    stats = manager.get_stats()
    assert stats["collections"] == 1
    assert stats["base_path"] == str(Path("data/test_vector_db"))
