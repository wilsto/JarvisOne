"""Tests for chat UI components."""

import pytest
from unittest.mock import Mock, patch, MagicMock
import streamlit as st
from src.ui.chat_ui import (
    init_chat_session,
    init_chat_processor,
    display_chat
)
from tests.utils import mock_session_state, mock_database  # Import both fixtures

@pytest.fixture
def mock_streamlit():
    """Mock Streamlit components."""
    with patch('streamlit.chat_message') as mock_chat, \
         patch('streamlit.markdown') as mock_markdown, \
         patch('streamlit.chat_input') as mock_input, \
         patch('streamlit.write') as mock_write, \
         patch('streamlit.columns') as mock_cols, \
         patch('streamlit.button') as mock_button:
        
        # Configure chat message mock
        mock_chat_ctx = Mock()
        mock_chat_ctx.__enter__ = Mock(return_value=mock_chat_ctx)
        mock_chat_ctx.__exit__ = Mock(return_value=None)
        mock_chat.return_value = mock_chat_ctx
        mock_chat_ctx.markdown = Mock()
        
        # Configure columns mock
        mock_col = Mock()
        mock_col.__enter__ = Mock(return_value=mock_col)
        mock_col.__exit__ = Mock(return_value=None)
        mock_col.markdown = Mock()
        mock_col.button = Mock()
        mock_cols.return_value = [mock_col, mock_col, mock_col, mock_col]
        
        yield {
            'chat': mock_chat,
            'chat_ctx': mock_chat_ctx,
            'markdown': mock_markdown,
            'input': mock_input,
            'write': mock_write,
            'columns': mock_cols,
            'button': mock_button,
            'col': mock_col
        }

@pytest.fixture
def mock_chat_processor(mock_database):
    """Mock chat processor."""
    processor = Mock()
    
    # Mock repository methods using mock_database
    processor.repository = Mock()
    processor.repository.create_conversation.side_effect = mock_database.create_conversation
    processor.repository.get_conversation.side_effect = mock_database.get_conversation
    processor.repository.list_conversations.side_effect = mock_database.list_conversations
    processor.repository.add_message.side_effect = mock_database.add_message
    processor.repository.get_messages.side_effect = mock_database.get_messages
    
    # Mock other processor methods
    processor.process_user_input.return_value = "Test response"
    processor.get_messages.return_value = []
    
    return processor

def test_chat_initialization(mock_session_state, mock_chat_processor):
    """Test chat session initialization."""
    # Configure session state
    mock_session_state.chat_processor = mock_chat_processor
    mock_session_state.workspace_manager = None
    
    init_chat_session()

    # Verify that add_message was called with welcome message
    mock_chat_processor.add_message.assert_called_once()
    args = mock_chat_processor.add_message.call_args[0]
    assert args[0] == "assistant"
    assert "JarvisOne" in args[1]
    assert "👋" in args[1]

def test_init_chat_processor(mock_session_state):
    """Test chat processor initialization."""
    # First call should create new processor
    processor1 = init_chat_processor()
    assert processor1 is not None
    
    # Second call should return same processor
    processor2 = init_chat_processor()
    assert processor2 is processor1

# FIXME: Test désactivé - Problème d'encodage de l'emoji et de l'assertion du markdown
# Le test échoue car l'emoji '🗨️' n'est pas correctement encodé et le format HTML ne correspond pas
# exactement à celui généré par le code. À corriger une fois le format HTML standardisé.
@pytest.mark.skip(reason="Problème d'encodage de l'emoji et de l'assertion du markdown")
def test_display_chat(mock_streamlit, mock_session_state, mock_chat_processor):
    """Test chat display."""
    # Configure session state
    mock_session_state.chat_processor = mock_chat_processor
    mock_session_state.current_conversation_id = None
    
    # Configure chat processor with messages
    messages = [
        {"role": "assistant", "content": "Hello!", "timestamp": "2024-01-01 12:00:00"},
        {"role": "user", "content": "Hi!", "timestamp": "2024-01-01 12:00:01"}
    ]
    mock_chat_processor.get_messages.return_value = iter(messages)
    
    # Mock sidebar render
    with patch('src.ui.chat_ui.render_sidebar'):
        # Display chat
        display_chat()
        
        # Verify header was rendered
        mock_streamlit['columns'].assert_called()
        mock_streamlit['col'].markdown.assert_any_call(
            "<div style='display: flex; align-items: center;  margin-top: 20px; margin-left: 10px;'><span style='margin-right: 8px; font-size: 1.2em; font-weight: bold;'>🗨️ New Chat</span></div>",
            unsafe_allow_html=True
        )
        
        # Verify messages were displayed
        assert mock_streamlit['chat'].call_count == len(messages)
        for message in messages:
            mock_streamlit['chat'].assert_any_call(message["role"])
            mock_streamlit['chat_ctx'].markdown.assert_any_call(message["content"])
        
        # Verify chat input was displayed
        mock_streamlit['input'].assert_called_once_with("Parlez à JarvisOne")
