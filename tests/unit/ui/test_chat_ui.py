"""Tests for chat UI components."""

import pytest
from unittest.mock import Mock, patch
import streamlit as st
from src.ui.chat_ui import (
    init_chat_session,
    init_chat_processor,
    display_chat
)
from tests.utils import mock_session_state  # Import existing fixture

@pytest.fixture
def mock_streamlit():
    """Mock Streamlit components."""
    with patch('streamlit.chat_message') as mock_chat, \
         patch('streamlit.markdown') as mock_markdown, \
         patch('streamlit.chat_input') as mock_input, \
         patch('streamlit.write') as mock_write:
        
        # Configure mocks
        mock_chat.return_value.__enter__ = Mock()
        mock_chat.return_value.__exit__ = Mock(return_value=None)
        
        yield {
            'chat': mock_chat,
            'markdown': mock_markdown,
            'input': mock_input,
            'write': mock_write,
        }

def test_chat_initialization(mock_session_state):
    """Test chat session initialization."""
    init_chat_session()

    # Check that messages list exists and contains welcome message
    assert mock_session_state.messages is not None
    assert len(mock_session_state.messages) == 1
    assert mock_session_state.messages[0]["role"] == "assistant"

    # Check welcome message content
    welcome_content = mock_session_state.messages[0]["content"]
    assert "JarvisOne" in welcome_content
    assert "file search" in welcome_content.lower()
    assert "👋" in welcome_content

def test_init_chat_processor(mock_session_state):
    """Test chat processor initialization."""
    # First call should create new processor
    processor1 = init_chat_processor()
    assert processor1 is not None
    assert mock_session_state.chat_processor == processor1
    
    # Second call should return same processor
    processor2 = init_chat_processor()
    assert processor2 == processor1

def test_display_chat(mock_streamlit, mock_session_state):
    """Test chat display."""
    # Setup
    mock_session_state.messages = [
        {"role": "assistant", "content": "Hello"},
        {"role": "user", "content": "Hi"}
    ]
    mock_session_state.chat_processor = Mock()
    mock_streamlit['input'].return_value = "Test input"
    mock_session_state.chat_processor.process_user_input.return_value = "Test response"
    
    # Mock render_sidebar
    with patch('src.ui.chat_ui.render_sidebar'):
        # Test display
        display_chat()
    
    # Verify
    # 4 appels à chat_message :
    # 2 pour les messages initiaux
    # 1 pour le nouveau message utilisateur
    # 1 pour la réponse assistant
    assert mock_streamlit['chat'].call_count == 4
    assert mock_streamlit['markdown'].call_count >= 3  # Messages + CSS
    assert len(mock_session_state.messages) == 4  # Initial 2 + user input + response
