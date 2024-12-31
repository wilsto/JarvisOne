"""Tests for sidebar component."""

import pytest
from unittest.mock import Mock, patch, ANY
import streamlit as st
from src.ui.components.sidebar import render_sidebar
from core.workspace_manager import SpaceType
from tests.utils import mock_session_state

# Define space options for testing
SPACE_OPTIONS = [
    ("General", SpaceType.AGNOSTIC),
    ("Work", SpaceType.WORK),
    ("Personal", SpaceType.PERSONAL),
    ("Dev", SpaceType.DEV),
    ("Coaching", SpaceType.COACHING),
]

@pytest.fixture
def mock_streamlit_sidebar():
    """Mock Streamlit sidebar components."""
    with patch('streamlit.sidebar') as mock_sidebar, \
         patch('streamlit.header') as mock_header, \
         patch('streamlit.markdown') as mock_markdown, \
         patch('streamlit.selectbox') as mock_selectbox, \
         patch('streamlit.columns') as mock_columns, \
         patch('streamlit.button') as mock_button, \
         patch('streamlit.text_input') as mock_text_input, \
         patch('streamlit.success') as mock_success, \
         patch('streamlit.warning') as mock_warning, \
         patch('streamlit.info') as mock_info, \
         patch('streamlit.rerun') as mock_rerun:
        
        # Configure mocks
        mock_sidebar.return_value.__enter__ = Mock(return_value=mock_sidebar)
        mock_sidebar.return_value.__exit__ = Mock(return_value=None)
        
        col_mock = Mock()
        col_mock.__enter__ = Mock(return_value=col_mock)
        col_mock.__exit__ = Mock(return_value=None)
        mock_columns.return_value = [col_mock, col_mock]
        
        # Configure selectbox to return index 0 by default
        mock_selectbox.return_value = 0
        
        yield {
            'sidebar': mock_sidebar,
            'header': mock_header,
            'markdown': mock_markdown,
            'selectbox': mock_selectbox,
            'columns': mock_columns,
            'button': mock_button,
            'text_input': mock_text_input,
            'success': mock_success,
            'warning': mock_warning,
            'info': mock_info,
            'rerun': mock_rerun,
            'col': col_mock
        }

@pytest.fixture
def mock_workspace_manager():
    """Mock workspace manager."""
    manager = Mock()
    manager.get_current_space_config.return_value = Mock(
        metadata={
            'scope': """
            - File Search: Search through your files and documents
            - Chat: Natural language conversation
            - Document Analysis: Process and analyze documents
            """
        }
    )
    manager.get_current_space_roles.return_value = []  # No roles by default
    manager.set_current_space = Mock()
    return manager

@pytest.fixture
def mock_chat_processor():
    """Mock chat processor."""
    processor = Mock()
    processor.get_conversations.return_value = []  # Return empty list by default
    processor.get_conversation_history = Mock(return_value=[])  # Return empty list for history
    return processor

def test_render_sidebar_basic(mock_streamlit_sidebar, mock_workspace_manager, mock_session_state):
    """Test basic sidebar rendering."""
    # Configure session state
    mock_session_state.workspace = SpaceType.AGNOSTIC
    mock_session_state.workspace_manager = mock_workspace_manager
    mock_session_state.current_role = None
    
    # Render sidebar
    render_sidebar()
    
    # Verify header
    mock_streamlit_sidebar['header'].assert_called_with(
        "🤖 JarvisOne",
        anchor="cool-header",
        help="This is a custom header",
        divider="rainbow"
    )
    
    # Verify workspace selector
    mock_streamlit_sidebar['selectbox'].assert_called_with(
        "Workspace",
        options=ANY,  # Use ANY for the range object
        format_func=ANY,  # Use ANY for the lambda function
        index=0,
        key="workspace_selector"
    )

def test_render_sidebar_workspace_change(mock_streamlit_sidebar, mock_workspace_manager, mock_session_state):
    """Test workspace change handling."""
    # Configure session state
    mock_session_state.workspace = SpaceType.AGNOSTIC
    mock_session_state.workspace_manager = mock_workspace_manager
    mock_session_state.current_role = None
    
    # Simulate workspace change by returning index 1 (Work workspace)
    mock_streamlit_sidebar['selectbox'].return_value = 1
    
    # Render sidebar
    render_sidebar()
    
    # Verify workspace manager was updated
    mock_workspace_manager.set_current_space.assert_called_once_with(SpaceType.WORK)
    mock_streamlit_sidebar['rerun'].assert_called_once()

@pytest.mark.skip(reason="FIXME: Need to properly mock conversation history and handle iterable requirements")
def test_render_sidebar_conversation_history(mock_streamlit_sidebar, mock_workspace_manager, mock_chat_processor, mock_session_state):
    """Test conversation history rendering."""
    # Configure session state
    mock_session_state.workspace = SpaceType.AGNOSTIC
    mock_session_state.workspace_manager = mock_workspace_manager
    mock_session_state.current_role = None
    mock_session_state.chat_processor = mock_chat_processor
    
    # Mock conversation history
    with patch('src.ui.components.conversation_history.render_conversation_history') as mock_history:
        # Render sidebar
        render_sidebar()
        
        # Verify conversation history was rendered with empty list
        mock_history.assert_called_once_with([], ANY, None)
