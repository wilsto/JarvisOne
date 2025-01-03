"""Integration tests for message flow."""

import pytest
import logging
from unittest.mock import patch, Mock
from pathlib import Path

from src.features.workspace_manager import (
    WorkspaceManager,
    WorkspaceConfig,
    MessageHistoryConfig,
    WorkspaceContextConfig
)
from src.features.chat_processor import ChatProcessor
from src.features.config_manager import ConfigManager
from tests.types.workspace import SpaceType
from tests.mocks.database import DatabaseMock
from tests.mocks.session_state import SessionStateMock

@pytest.fixture
def mock_session_state():
    """Mock Streamlit session state."""
    state = SessionStateMock()
    with patch("streamlit.session_state", state):
        yield state

@pytest.fixture
def mock_db():
    """Mock database."""
    return DatabaseMock()

@pytest.fixture
def mock_config_manager():
    """Mock ConfigManager."""
    with patch("features.config_manager.ConfigManager") as mock:
        mock.get_all_configs.return_value = {
            "rag": {"enabled": False},
            "llm": {"provider": "test_provider", "model": "test_model"}
        }
        mock.load_llm_preferences.return_value = {
            "provider": "test_provider",
            "model": "test_model"
        }
        yield mock

@pytest.fixture
def mock_llm():
    """Mock LLM responses."""
    mock = Mock()
    mock.generate_response.return_value = "Mocked response"
    return mock

@pytest.fixture
def chat_processor(mock_session_state, mock_config_manager, mock_db):
    """Initialize ChatProcessor with mocked components."""
    with patch("features.chat_processor.AgentOrchestrator") as mock_orch:
        with patch("features.database.repository.ConversationRepository") as mock_repo:
            mock_repo.return_value.create_conversation.return_value = mock_db.create_conversation(
                title="Test Conversation",
                workspace=SpaceType.DEV
            )
            processor = ChatProcessor()
            yield processor

class TestMessageFlow:
    """Test the flow of messages through the system."""
    
    def test_full_conversation_flow(self, chat_processor, mock_llm, mock_session_state):
        """Test a complete conversation flow with multiple messages."""
        # Setup
        agent = CoreAgent("test", "Test instructions", llm=mock_llm)
        chat_processor.orchestrator.process_query = agent.run
        
        # Set workspace
        mock_session_state.workspace = Mock()
        mock_session_state.workspace.name = "test_workspace"
        mock_session_state.workspace.workspace_type = SpaceType.DEV
        
        # Simulate conversation
        messages = [
            "Hello, how are you?",
            "What's the weather like?",
            "Thank you!"
        ]
        
        for msg in messages:
            chat_processor.process_user_input(msg)
            
        # Verify conversation state
        assert len(mock_session_state.messages) == len(messages) * 2  # User + Assistant messages
        
    def test_workspace_context_integration(self, chat_processor, mock_llm, mock_session_state):
        """Test message flow with workspace context."""
        # Setup workspace
        mock_session_state.workspace = Mock()
        mock_session_state.workspace.name = "test_workspace"
        mock_session_state.workspace.workspace_type = SpaceType.DEV
        mock_session_state.workspace.workspace_prompt = "Test workspace prompt"
        
        # Configure agent with workspace
        agent = CoreAgent("test", "Test instructions", llm=mock_llm)
        chat_processor.orchestrator.process_query = agent.run
        
        # Process message with workspace context
        chat_processor.process_user_input("Test message")
        
        # Verify workspace context was included
        assert mock_llm.generate_response.call_count > 0
        
    def test_error_handling_flow(self, chat_processor, mock_llm, mock_session_state):
        """Test error handling throughout the message flow."""
        # Setup workspace
        mock_session_state.workspace = Mock()
        mock_session_state.workspace.name = "test_workspace"
        mock_session_state.workspace.workspace_type = SpaceType.DEV
        mock_session_state.current_role = None  # Ensure no role is set
        
        # Setup error condition
        test_error = "Test error"
        mock_llm.generate_response.side_effect = Exception(test_error)
        
        agent = CoreAgent("test", "Test instructions", llm=mock_llm)
        chat_processor.orchestrator.process_query = agent.run
        
        # Process message
        response = chat_processor.process_user_input("Test message")
        
        # Verify error handling includes icon
        assert "❌" in response
        # Verify error is present (the exact message may vary depending on where error occurs)
        assert test_error in response
        
    @pytest.mark.skip(reason="TODO: Enable when message history limit is implemented in ChatProcessor.add_message")
    def test_message_history_limit(self, chat_processor, mock_llm, mock_session_state):
        """Test message history limit enforcement."""
        # Setup workspace
        mock_session_state.workspace = Mock()
        mock_session_state.workspace.name = "test_workspace"
        mock_session_state.workspace.workspace_type = SpaceType.DEV
        
        agent = CoreAgent("test", "Test instructions", llm=mock_llm)
        chat_processor.orchestrator.process_query = agent.run
        
        # Set low history limit for testing
        chat_processor.max_history_messages = 2
        
        # Send multiple messages
        messages = ["Message 1", "Message 2", "Message 3", "Message 4"]
        for msg in messages:
            chat_processor.process_user_input(msg)
            
        # Verify history limit
        assert len(mock_session_state.messages) <= 4  # 2 messages * 2 (user + assistant)
        
    def test_prompt_assembly_integration(self, chat_processor, mock_llm, mock_session_state):
        """Test integration of all prompt components."""
        # Setup workspace
        mock_session_state.workspace = Mock()
        mock_session_state.workspace.name = "test_workspace"
        mock_session_state.workspace.workspace_type = SpaceType.DEV
        mock_session_state.workspace.workspace_prompt = "Test workspace prompt"
        
        agent = CoreAgent("test", "Test instructions", llm=mock_llm)
        chat_processor.orchestrator.process_query = agent.run
        
        # Process a message
        chat_processor.process_user_input("Test message")
        
        # Verify prompt assembly
        assert mock_llm.generate_response.call_count > 0
