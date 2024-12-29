"""Tests for the RAG enhancer."""

import pytest
from unittest.mock import Mock, AsyncMock

from src.rag.enhancer import RAGEnhancer
from src.rag.middleware import RAGConfig
from src.rag.document_processor import DocumentProcessor
from src.rag.processor import MessageProcessor

class MockMessageProcessor(MessageProcessor):
    """Mock implementation of MessageProcessor for testing."""
    async def process_message(self, message: str, workspace_id: str, **kwargs):
        return "Processed: " + message

@pytest.fixture
def mock_processor():
    """Fixture providing a mock message processor."""
    processor = Mock(spec=MessageProcessor)
    processor.process_message = AsyncMock(return_value="Processed response")
    return processor

@pytest.fixture
def mock_doc_processor():
    """Fixture providing a mock document processor."""
    processor = Mock(spec=DocumentProcessor)
    return processor

@pytest.fixture
def rag_config():
    """Fixture providing RAG configuration."""
    return RAGConfig(
        max_results=2,
        min_similarity=0.5,  # Lower threshold to include all test documents
        importance_filter="High"
    )

@pytest.fixture
def enhancer(mock_processor, mock_doc_processor, rag_config):
    """Fixture providing a configured RAG enhancer."""
    return RAGEnhancer(mock_processor, mock_doc_processor, rag_config)

@pytest.mark.asyncio
async def test_process_message_with_context(enhancer, mock_processor, mock_doc_processor):
    """Test message processing with document context."""
    # Setup document processor mock
    mock_doc_processor.search_documents.return_value = [
        {
            'content': 'Relevant context',
            'similarity_score': 0.8,
            'metadata': {'importance_level': 'High'}
        }
    ]
    
    # Process message
    message = "What is the meaning of life?"
    response = await enhancer.process_message(message, "test_workspace")
    
    # Verify processor was called with enhanced prompt
    mock_processor.process_message.assert_called_once()
    enhanced_prompt = mock_processor.process_message.call_args[0][0]
    assert "Relevant context" in enhanced_prompt
    assert message in enhanced_prompt
    
    # Verify response
    assert response == "Processed response"

@pytest.mark.asyncio
async def test_process_message_error_fallback(enhancer, mock_processor, mock_doc_processor):
    """Test fallback to processor on error."""
    # Setup document processor to raise error
    mock_doc_processor.search_documents.side_effect = Exception("Search failed")
    
    # Process message
    message = "What is the meaning of life?"
    response = await enhancer.process_message(message, "test_workspace")
    
    # Verify processor was called with original message
    mock_processor.process_message.assert_called_once_with(
        message,
        "test_workspace"
    )
    
    # Verify response
    assert response == "Processed response"

@pytest.mark.asyncio
async def test_process_message_with_kwargs(enhancer, mock_processor, mock_doc_processor):
    """Test passing additional kwargs to processor."""
    # Setup document processor mock
    mock_doc_processor.search_documents.return_value = []
    
    # Process message with additional kwargs
    message = "What is the meaning of life?"
    kwargs = {"temperature": 0.7, "max_tokens": 100}
    response = await enhancer.process_message(message, "test_workspace", **kwargs)
    
    # Verify processor was called with kwargs
    mock_processor.process_message.assert_called_once()
    call_kwargs = mock_processor.process_message.call_args[1]
    assert call_kwargs["temperature"] == 0.7
    assert call_kwargs["max_tokens"] == 100

@pytest.mark.asyncio
async def test_concrete_message_processor():
    """Test with concrete MessageProcessor implementation."""
    processor = MockMessageProcessor()
    doc_processor = Mock(spec=DocumentProcessor)
    enhancer = RAGEnhancer(processor, doc_processor)
    
    # Test basic processing
    message = "Test message"
    response = await enhancer.process_message(message, "test_workspace")
    assert "Processed: " in response
