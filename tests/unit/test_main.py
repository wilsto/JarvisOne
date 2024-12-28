"""Tests for main application."""

import pytest
from unittest.mock import Mock, patch, MagicMock
import streamlit as st
from src.main import (
    get_search_title,
    display_logs,
    display_interactions,
)
from tests.utils import mock_session_state

@pytest.fixture
def mock_streamlit():
    """Mock Streamlit components."""
    # Create context manager mocks
    expander_mock = MagicMock()
    expander_mock.__enter__ = Mock(return_value=expander_mock)
    expander_mock.__exit__ = Mock(return_value=None)
    
    tab_mock = MagicMock()
    tab_mock.__enter__ = Mock(return_value=tab_mock)
    tab_mock.__exit__ = Mock(return_value=None)
    
    col_mock = MagicMock()
    col_mock.__enter__ = Mock(return_value=col_mock)
    col_mock.__exit__ = Mock(return_value=None)
    
    with patch('streamlit.expander', return_value=expander_mock) as mock_expander, \
         patch('streamlit.columns', return_value=[col_mock, col_mock]) as mock_columns, \
         patch('streamlit.tabs', return_value=[tab_mock]) as mock_tabs, \
         patch('streamlit.markdown') as mock_markdown, \
         patch('streamlit.text_input', return_value="") as mock_text_input, \
         patch('streamlit.button', return_value=False) as mock_button, \
         patch('streamlit.multiselect') as mock_multiselect, \
         patch('streamlit.info') as mock_info:
        yield {
            'expander': mock_expander,
            'columns': mock_columns,
            'tabs': mock_tabs,
            'markdown': mock_markdown,
            'text_input': mock_text_input,
            'button': mock_button,
            'multiselect': mock_multiselect,
            'info': mock_info,
            'col_mock': col_mock,
            'tab_mock': tab_mock,
            'expander_mock': expander_mock
        }

@pytest.fixture
def mock_get_logs():
    """Mock get_logs function."""
    with patch('src.main.get_logs') as mock:
        mock.return_value = [
            {
                'timestamp': '2024-12-26 15:30:00',
                'level': 'INFO',
                'message': 'Test log message'
            },
            {
                'timestamp': '2024-12-26 15:31:00',
                'level': 'ERROR',
                'message': 'Test error message'
            }
        ]
        yield mock

def test_get_search_title():
    """Test search title generation."""
    # Test extension search
    assert get_search_title("find files ext:py") == "Files PY"
    assert get_search_title("ext:pdf in documents") == "Files PDF"
    
    # Test date search
    assert get_search_title("dm:today modified files") == "Recent files"
    assert get_search_title("find dm:yesterday") == "Recent files"
    
    # Test regular search
    assert get_search_title("important project file") == "Important Project File"

def test_display_logs_without_filters(mock_streamlit, mock_get_logs):
    """Test logs display without filters."""
    display_logs()
    
    # Verify search input was created
    mock_streamlit['text_input'].assert_called_once()
    
    # Verify logs were displayed
    assert mock_streamlit['markdown'].call_count >= 2  # Au moins un appel par log
    
    # Verify filter button was created
    mock_streamlit['button'].assert_called_once()

def test_display_logs_with_filters(mock_streamlit, mock_get_logs):
    """Test logs display with filters."""
    # Simuler le clic sur le bouton des filtres
    mock_streamlit['button'].return_value = True
    
    display_logs()
    
    # Verify filter options were displayed
    mock_streamlit['multiselect'].assert_called_once()

def test_display_logs_with_search(mock_streamlit, mock_get_logs):
    """Test logs display with search term."""
    # Simuler une recherche
    mock_streamlit['text_input'].return_value = "error"
    
    display_logs()
    
    # Verify only matching logs were displayed
    calls = mock_streamlit['markdown'].call_args_list
    matching_calls = [call for call in calls if "error" in str(call).lower()]
    assert len(matching_calls) > 0

def test_display_interactions_empty(mock_streamlit, mock_session_state):
    """Test displaying interactions when there are none."""
    with patch("streamlit.info") as mock_info:
        display_interactions()
        mock_info.assert_called_once_with(
            "No interactions yet. Search results will appear here."
        )

def test_display_interactions_with_data(mock_streamlit, mock_session_state):
    """Test interactions display with data."""
    # Add test interaction
    st.session_state.interactions = [{
        'id': 'test-id',
        'type': 'file_search',
        'query': 'test query',
        'results': ['file1.txt', 'file2.txt'],
        'timestamp': '15:30:00'
    }]
    
    with patch('src.main.InteractionDisplayFactory') as mock_factory:
        # Configure mock handler
        mock_handler = Mock()
        mock_handler.get_expander_title.return_value = "Test Title"
        mock_factory.get_display_handler.return_value = mock_handler
        
        display_interactions()
        
        # Verify handler was used
        mock_factory.get_display_handler.assert_called_once_with('file_search')
        mock_handler.get_expander_title.assert_called_once()
        mock_handler.display.assert_called_once()
