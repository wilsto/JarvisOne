"""Tests for the RAG middleware."""

import pytest
from unittest.mock import Mock, patch
from src.rag.middleware import RAGMiddleware, RAGConfig
from src.rag.document_processor import DocumentProcessor

@pytest.fixture
def mock_processor():
    """Fixture providing a mock document processor."""
    processor = Mock(spec=DocumentProcessor)
    return processor

@pytest.fixture
def config():
    """Fixture providing a RAG configuration."""
    return RAGConfig(
        max_results=2,
        min_similarity=0.5,  # Lower threshold to include all test documents
        importance_filter="High",
        context_template="Context:\n{context}\nQuery: {query}"
    )

@pytest.fixture
def middleware(mock_processor, config):
    """Fixture providing a configured RAG middleware."""
    return RAGMiddleware(mock_processor, config)

@pytest.mark.asyncio
async def test_enhance_prompt_with_context(middleware, mock_processor):
    """Test prompt enhancement with relevant context."""
    # Setup mock response
    mock_processor.search_documents.return_value = [
        {
            'content': 'Relevant document content',
            'similarity_score': 0.8,
            'metadata': {'importance_level': 'High'}
        },
        {
            'content': 'Another relevant document',
            'similarity_score': 0.75,
            'metadata': {'importance_level': 'High'}
        }
    ]
    
    # Test prompt enhancement
    query = "What is the meaning of life?"
    enhanced = await middleware.enhance_prompt(query, "test_workspace")
    
    # Verify the search was called correctly
    mock_processor.search_documents.assert_called_once_with(
        query=query,
        workspace_id="test_workspace",
        n_results=2,
        importance_filter="High"
    )
    
    # Verify the enhanced prompt contains both context and query
    assert "Relevant document content" in enhanced
    assert "Another relevant document" in enhanced
    assert query in enhanced
    assert "[Score: 0.80]" in enhanced
    assert "[Score: 0.75]" in enhanced

@pytest.mark.asyncio
async def test_enhance_prompt_no_results(middleware, mock_processor):
    """Test prompt enhancement when no relevant documents are found."""
    # Setup mock to return no results
    mock_processor.search_documents.return_value = []
    
    # Test prompt enhancement
    query = "What is the meaning of life?"
    enhanced = await middleware.enhance_prompt(query, "test_workspace")
    
    # Verify original query is returned unchanged
    assert enhanced == query

@pytest.mark.asyncio
async def test_enhance_prompt_below_similarity(middleware, mock_processor):
    """Test prompt enhancement with documents below similarity threshold."""
    # Create a middleware with higher similarity threshold
    config = RAGConfig(
        max_results=2,
        min_similarity=0.7,  # Set higher threshold
        importance_filter="High"
    )
    middleware_strict = RAGMiddleware(mock_processor, config)
    
    # Setup mock with low similarity scores
    mock_processor.search_documents.return_value = [
        {
            'content': 'Less relevant content',
            'similarity_score': 0.5,  # Below threshold
            'metadata': {'importance_level': 'High'}
        }
    ]
    
    # Test prompt enhancement
    query = "What is the meaning of life?"
    enhanced = await middleware_strict.enhance_prompt(query, "test_workspace")
    
    # Verify original query is returned (no context added)
    assert enhanced == query

@pytest.mark.asyncio
async def test_enhance_prompt_error_handling(middleware, mock_processor):
    """Test error handling during prompt enhancement."""
    # Setup mock to raise an exception
    mock_processor.search_documents.side_effect = Exception("Search failed")
    
    # Test prompt enhancement
    query = "What is the meaning of life?"
    enhanced = await middleware.enhance_prompt(query, "test_workspace")
    
    # Verify original query is returned on error
    assert enhanced == query

def test_format_context_sorting():
    """Test context formatting with proper sorting by similarity."""
    # Create middleware with low similarity threshold
    config = RAGConfig(min_similarity=0.5)  # Allow all test documents
    middleware = RAGMiddleware(Mock(spec=DocumentProcessor), config)
    
    documents = [
        {'content': 'Less relevant', 'similarity_score': 0.75},
        {'content': 'Most relevant', 'similarity_score': 0.95},
        {'content': 'Somewhat relevant', 'similarity_score': 0.85}
    ]
    
    context = middleware._format_context(documents)
    
    # Verify order of documents in context
    assert "[Score: 0.95] Most relevant" in context
    assert "[Score: 0.85] Somewhat relevant" in context
    assert "[Score: 0.75] Less relevant" in context
    
    # Verify ordering by checking positions in formatted string
    assert context.index("[Score: 0.95]") < context.index("[Score: 0.85]")
    assert context.index("[Score: 0.85]") < context.index("[Score: 0.75]")
