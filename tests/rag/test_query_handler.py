"""Test RAG query handler."""

import pytest
from unittest.mock import Mock, patch
from rag.query_handler import RAGQueryHandler

@pytest.fixture
def mock_vector_db():
    """Mock VectorDBManager."""
    with patch('vector_db.manager.VectorDBManager') as mock:
        instance = Mock()
        mock.get_instance.return_value = instance
        yield instance

@pytest.fixture
def query_handler(mock_vector_db):
    """Create RAGQueryHandler instance."""
    return RAGQueryHandler()

def test_initialization(query_handler, mock_vector_db):
    """Test query handler initialization."""
    assert query_handler.vector_db == mock_vector_db

def test_query_success(query_handler, mock_vector_db):
    """Test successful query."""
    # Mock results
    mock_results = [
        {
            "content": "test document",
            "metadata": {"source": "test"},
            "distance": 0.5
        }
    ]
    mock_vector_db.query.return_value = mock_results
    
    # Test query
    results = query_handler.query(
        query_text="test query",
        workspace_id="test_workspace",
        top_k=3
    )
    
    # Verify results
    assert results == mock_results
    mock_vector_db.query.assert_called_once_with(
        workspace_id="test_workspace",
        query_text="test query",
        n_results=3
    )

def test_query_no_results(query_handler, mock_vector_db):
    """Test query with no results."""
    mock_vector_db.query.return_value = []
    
    results = query_handler.query(
        query_text="test query",
        workspace_id="test_workspace"
    )
    
    assert results == []

def test_query_error(query_handler, mock_vector_db):
    """Test query with error."""
    mock_vector_db.query.side_effect = Exception("Test error")
    
    results = query_handler.query(
        query_text="test query",
        workspace_id="test_workspace"
    )
    
    assert results == []
