"""Tests for chat processor."""

import pytest
import logging
from unittest.mock import Mock, patch
from src.features.chat_processor import ChatProcessor
from tests.utils import mock_session_state  # Import the fixture

@pytest.fixture
def mock_orchestrator():
    """Mock agent orchestrator."""
    with patch('src.features.chat_processor.AgentOrchestrator') as mock:
        instance = Mock()
        mock.return_value = instance
        yield instance

def test_chat_processor_initialization(mock_orchestrator, mock_session_state):
    """Test chat processor initialization."""
    processor = ChatProcessor()
    
    # Verify orchestrator initialization
    assert processor.orchestrator == mock_orchestrator
    
    # Verify session state initialization
    assert mock_session_state.messages is not None
    assert isinstance(mock_session_state.messages, list)
    assert len(mock_session_state.messages) == 0

def test_chat_processor_initialization_error():
    """Test chat processor initialization with error."""
    with patch('src.features.chat_processor.AgentOrchestrator') as mock:
        # Configure mock to raise exception
        mock.side_effect = Exception("Test error")
        
        with pytest.raises(Exception) as exc_info:
            ChatProcessor()
        assert "Test error" in str(exc_info.value)

def test_format_response_none(mock_session_state):
    """Test response formatting with None input."""
    processor = ChatProcessor()
    response = processor._format_response(None)
    assert "❌" in response
    assert "Pas de réponse" in response

def test_format_response_dict(mock_session_state):
    """Test response formatting with dict input."""
    processor = ChatProcessor()
    
    # Test error case
    error_response = {"error": "Test error"}
    response = processor._format_response(error_response)
    assert "❌" in response
    assert "Test error" in response
    
    # Test content case
    content_response = {"content": ["file1.py", "file2.py"]}
    response = processor._format_response(content_response)
    assert "file1.py" in response
    assert "file2.py" in response

def test_format_response_string(mock_session_state):
    """Test response formatting with string input."""
    processor = ChatProcessor()
    test_str = "Test response"
    response = processor._format_response(test_str)
    assert response == test_str

def test_process_user_input_success(mock_orchestrator, mock_session_state):
    """Test successful user input processing."""
    processor = ChatProcessor()
    
    # Configure mock
    mock_orchestrator.process_query.return_value = {"content": "Test response"}
    
    # Test processing
    response = processor.process_user_input("test query")
    assert "Test response" in response
    
    # Verify orchestrator call
    mock_orchestrator.process_query.assert_called_once_with("test query")

def test_process_user_input_error(mock_orchestrator, mock_session_state):
    """Test user input processing with error."""
    processor = ChatProcessor()
    
    # Configure mock to raise exception
    mock_orchestrator.process_query.side_effect = Exception("Test error")
    
    # Test processing
    response = processor.process_user_input("test query")
    assert "désolé" in response.lower()
    assert "erreur" in response.lower()

def test_logging(caplog, mock_orchestrator, mock_session_state):
    """Test logging in chat processor."""
    processor = ChatProcessor()
    
    # Test successful case
    with caplog.at_level(logging.INFO):
        mock_orchestrator.process_query.return_value = "Test response"
        processor.process_user_input("test query")
    
    # Verify logs
    assert "Processing user input: test query" in caplog.text
    assert "Successfully processed" in caplog.text
    
    # Test error case
    caplog.clear()
    with caplog.at_level(logging.ERROR):
        mock_orchestrator.process_query.side_effect = Exception("Test error")
        processor.process_user_input("test query")
    
    # Verify error logs
    assert "Error in chat processor" in caplog.text
