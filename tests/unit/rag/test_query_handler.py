"""Test RAG query handler."""

import pytest
from unittest.mock import Mock, patch
from rag.query_handler import RAGQueryHandler
from tests.helpers.rag_test_utils import RAGTestUtils

@pytest.fixture
def mock_vector_db():
    """Mock VectorDBManager."""
    with patch('rag.query_handler.VectorDBManager') as mock_class:
        instance = Mock()
        # Mock embeddings
        instance.embeddings = Mock()
        instance.embeddings.embed_query.return_value = RAGTestUtils.create_mock_embeddings()
        
        # Setup collection handling
        mock_collection = Mock()
        instance.get_collection.return_value = mock_collection
        
        # Setup instance return
        mock_class.get_instance.return_value = instance
        yield instance

@pytest.fixture
def query_handler(mock_vector_db):
    """Create RAGQueryHandler instance."""
    return RAGQueryHandler()

def test_initialization(query_handler, mock_vector_db):
    """Test query handler initialization."""
    assert query_handler.vector_db == mock_vector_db
    assert hasattr(query_handler, 'embeddings')

def test_query_success(query_handler, mock_vector_db):
    """Test successful query with semantic filtering."""
    # Mock results with varying similarities
    mock_results = RAGTestUtils.create_mock_documents(count=2, base_similarity=0.9)
    mock_vector_db.query.return_value = mock_results
    
    # Mock embeddings behavior for semantic verification
    mock_vector_db.embeddings.embed_query.side_effect = [
        RAGTestUtils.create_mock_embeddings(),  # Query embedding
        RAGTestUtils.create_mock_embeddings(),  # Doc 1 embedding
        RAGTestUtils.create_mock_embeddings()   # Doc 2 embedding
    ]
    
    # Test query with default threshold
    results = query_handler.query(
        query_text="test query",
        workspace_id="test_workspace",
        top_k=2
    )
    
    # Verify results format and content
    assert len(results) > 0
    for result in results:
        assert "content" in result
        assert "metadata" in result
        assert "distance" in result

def test_query_with_threshold_filtering(query_handler, mock_vector_db):
    """Test query with high similarity threshold."""
    # Create mock documents with different similarities
    mock_results = RAGTestUtils.create_mock_documents(count=2, base_similarity=0.9)
    mock_vector_db.query.return_value = mock_results
    
    # Mock embeddings to return high similarity for first doc, low for second
    mock_vector_db.embeddings.embed_query.side_effect = [
        RAGTestUtils.create_mock_embeddings(),  # Query embedding
        RAGTestUtils.create_mock_embeddings(),  # High similarity doc
        [0.2] + [0.0] * 2  # Low similarity doc
    ]
    
    # Test with high threshold
    results = query_handler.query(
        query_text="test query",
        workspace_id="test_workspace",
        similarity_threshold=0.8
    )
    
    # Should only return the highly relevant document
    assert len(results) == 1
    assert "distance" in results[0]
    assert 1 - results[0]["distance"] >= 0.8  # Check similarity threshold

def test_query_no_results(query_handler, mock_vector_db):
    """Test query with no results."""
    mock_vector_db.query.return_value = []
    
    results = query_handler.query(
        query_text="test query",
        workspace_id="test_workspace"
    )
    
    assert results == []

def test_query_error_handling(query_handler, mock_vector_db):
    """Test error handling in query process."""
    # Test vector DB query error
    mock_vector_db.query.side_effect = Exception("Vector DB error")
    results = query_handler.query(
        query_text="test query",
        workspace_id="test_workspace"
    )
    assert results == []
    
    # Test embedding error
    mock_vector_db.query.side_effect = None
    mock_vector_db.query.return_value = RAGTestUtils.create_mock_documents(1)
    mock_vector_db.embeddings.embed_query.side_effect = Exception("Embedding error")
    
    results = query_handler.query(
        query_text="test query",
        workspace_id="test_workspace"
    )
    assert results == []
