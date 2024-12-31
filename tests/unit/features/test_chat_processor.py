"""Tests for chat processor."""

import pytest
import logging
from unittest.mock import Mock, patch
from src.features.chat_processor import ChatProcessor
from tests.utils import mock_session_state, mock_database  # Import both fixtures

@pytest.fixture
def mock_orchestrator():
    """Mock agent orchestrator."""
    with patch('src.features.chat_processor.AgentOrchestrator') as mock:
        instance = Mock()
        mock.return_value = instance
        yield instance

@pytest.fixture
def mock_repository(mock_database):
    """Mock conversation repository."""
    repository = Mock()
    
    # Mock repository methods using mock_database
    repository.create_conversation.side_effect = mock_database.create_conversation
    repository.get_conversation.side_effect = mock_database.get_conversation
    repository.list_conversations.side_effect = mock_database.list_conversations
    repository.add_message.side_effect = mock_database.add_message
    repository.get_messages.side_effect = mock_database.get_messages
    
    return repository

@pytest.fixture
def mock_analyzer():
    """Mock conversation analyzer."""
    analyzer = Mock()
    analyzer.extract_title.return_value = "Test Conversation"
    return analyzer

@pytest.fixture
def chat_processor(mock_orchestrator, mock_session_state, mock_repository, mock_analyzer):
    """Create a chat processor with mocked dependencies."""
    with patch('src.features.chat_processor.ConversationRepository', return_value=mock_repository), \
         patch('src.features.chat_processor.ConversationAnalyzer', return_value=mock_analyzer):
        processor = ChatProcessor()
        return processor

def test_chat_processor_initialization(chat_processor, mock_orchestrator, mock_session_state):
    """Test chat processor initialization."""
    # Verify orchestrator initialization
    assert chat_processor.orchestrator == mock_orchestrator
    
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

def test_format_response_none(chat_processor):
    """Test response formatting with None input."""
    response = chat_processor._format_response(None)
    assert "❌" in response
    assert "No response from agent" in response

def test_format_response_dict(chat_processor):
    """Test response formatting with dict input."""
    # Test error case
    error_response = {"error": "Test error"}
    response = chat_processor._format_response(error_response)
    assert "❌" in response
    assert "Test error" in response
    
    # Test success case
    success_response = {"content": "Test message"}
    response = chat_processor._format_response(success_response)
    assert "Test message" in response

def test_format_response_string(chat_processor):
    """Test response formatting with string input."""
    response = chat_processor._format_response("Test message")
    assert "Test message" in response

def test_process_user_input_success(chat_processor, mock_orchestrator, mock_session_state, mock_repository):
    """Test successful user input processing."""
    # Configure mock orchestrator response
    mock_orchestrator.process_query.return_value = {"content": "Test response"}
    
    # Add user message
    user_input = "Test input"
    chat_processor.add_message("user", user_input)
    
    # Process user input
    response = chat_processor.process_user_input(user_input)
    
    # Verify orchestrator called
    mock_orchestrator.process_query.assert_called_once()
    assert "Test input" in mock_orchestrator.process_query.call_args[0][0]
    
    # Verify response
    assert "Test response" in response
    
    # Add assistant response
    chat_processor.add_message("assistant", response)
    
    # Verify messages in session state
    assert len(mock_session_state.messages) == 2
    assert mock_session_state.messages[0]["role"] == "user"
    assert mock_session_state.messages[0]["content"] == "Test input"
    assert mock_session_state.messages[1]["role"] == "assistant"
    assert "Test response" in mock_session_state.messages[1]["content"]

def test_process_user_input_error(chat_processor, mock_orchestrator, mock_session_state, mock_repository):
    """Test user input processing with error."""
    # Configure mock orchestrator to raise exception
    error_msg = "Test error"
    mock_orchestrator.process_query.side_effect = Exception(error_msg)
    
    # Add user message
    user_input = "Test input"
    chat_processor.add_message("user", user_input)
    
    # Process user input
    response = chat_processor.process_user_input(user_input)
    
    # Verify error response
    assert "❌" in response
    assert error_msg in response
    
    # Add error response
    chat_processor.add_message("assistant", response)
    
    # Verify messages in session state
    assert len(mock_session_state.messages) == 2
    assert mock_session_state.messages[0]["role"] == "user"
    assert mock_session_state.messages[0]["content"] == "Test input"
    assert mock_session_state.messages[1]["role"] == "assistant"
    assert "❌" in mock_session_state.messages[1]["content"]
    assert error_msg in mock_session_state.messages[1]["content"]

def test_logging(caplog, mock_orchestrator, mock_session_state, mock_repository, mock_analyzer):
    """Test logging in chat processor."""
    with caplog.at_level(logging.INFO):
        # Create chat processor to capture initialization logs
        with patch('src.features.chat_processor.ConversationRepository', return_value=mock_repository), \
             patch('src.features.chat_processor.ConversationAnalyzer', return_value=mock_analyzer):
            chat_processor = ChatProcessor()
        
        # Add and process user input
        user_input = "Test input"
        chat_processor.add_message("user", user_input)
        chat_processor.process_user_input(user_input)
        
        # Verify logging
        log_messages = [record.message for record in caplog.records]
        assert "ChatProcessor initialized successfully" in log_messages
        assert "Session initialized" in log_messages
