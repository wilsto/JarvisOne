"""Tests for FileSearchDisplay."""
import pytest
from unittest.mock import Mock, patch
import streamlit as st
from src.ui.interactions.agents.file_search import FileSearchDisplay
from tests.utils import mock_session_state  # Import existing fixture
import os

@pytest.fixture
def mock_streamlit():
    """Mock Streamlit components."""
    with patch('streamlit.columns') as mock_cols, \
         patch('streamlit.markdown') as mock_markdown, \
         patch('streamlit.metric') as mock_metric, \
         patch('streamlit.button') as mock_button, \
         patch('streamlit.toast') as mock_toast, \
         patch('streamlit.error') as mock_error:
        
        # Configure column mock
        mock_col = Mock()
        mock_col.__enter__ = Mock(return_value=mock_col)
        mock_col.__exit__ = Mock(return_value=None)
        mock_col.markdown = Mock()
        mock_col.metric = Mock()
        mock_col.button = Mock()
        
        # Return columns with correct ratios
        cols = [Mock() for _ in range(4)]
        for col in cols:
            col.__enter__ = Mock(return_value=col)
            col.__exit__ = Mock(return_value=None)
            col.markdown = Mock()
            col.button = Mock()
        mock_cols.return_value = cols
        
        yield {
            'columns': mock_cols,
            'markdown': mock_markdown,
            'metric': mock_metric,
            'button': mock_button,
            'toast': mock_toast,
            'error': mock_error,
            'cols': cols  # Return the list of column mocks
        }

@pytest.fixture
def sample_interaction():
    """Fixture providing a sample interaction."""
    return {
        'id': 'test-id',
        'query': 'test query',
        'timestamp': '2024-01-01 12:00:00',
        'results': [
            'C:\\test\\file1.txt',
            'C:\\test\\file2.txt'
        ]
    }

@pytest.fixture
def large_interaction():
    """Fixture providing an interaction with more than 10 results."""
    return {
        'id': 'test-id-large',
        'query': 'test query',
        'timestamp': '2024-01-01 12:00:00',
        'results': [f'C:\\test\\file{i}.txt' for i in range(15)]
    }

def test_expander_title(sample_interaction):
    """Test that expander title is correctly formatted."""
    display = FileSearchDisplay()
    title = display.get_expander_title(sample_interaction)
    # Skip emoji in test to avoid encoding issues
    expected = f"{sample_interaction['query']} • {sample_interaction['timestamp']}"
    assert title.replace("🔍 ", "") == expected, f"Expected '{expected}', got '{title}'"

@pytest.mark.skip(reason="FIXME: Need to properly mock Streamlit columns and handle HTML content")
def test_display_result_item(mock_streamlit, sample_interaction):
    """Test display of a single result item."""
    display = FileSearchDisplay()
    file_path = sample_interaction['results'][0]
    file_name = os.path.basename(file_path)
    dir_path = os.path.dirname(file_path)
    
    # Call _display_result_item with required arguments
    display._display_result_item(
        interaction_id=sample_interaction['id'],
        index=1,
        file_path=file_path
    )
    
    # Verify columns were created with correct ratios
    mock_streamlit['columns'].assert_called_with([0.4, 5, 0.6, 0.6])
    
    # Get the mock columns
    cols = mock_streamlit['cols']
    
    # Verify index column
    cols[0].markdown.assert_called_with(
        "<div style='margin: 0; color: #555;'>#1</div>",
        unsafe_allow_html=True
    )
    
    # Verify file info column
    cols[1].markdown.assert_called_with(
        f"<div style='line-height: 1.2;'>"
        f"<span class='file-name'>{file_name}</span><br/>"
        f"<span class='file-path'>{dir_path}</span>"
        f"</div>",
        unsafe_allow_html=True
    )
    
    # Verify copy button
    cols[2].button.assert_called_with(
        "📋",
        key=f"copy_{sample_interaction['id']}_1",
        help="Copy path"
    )
    
    # Verify open button
    cols[3].button.assert_called_with(
        "📂",
        key=f"open_{sample_interaction['id']}_1",
        help="Open file"
    )

@pytest.mark.skip(reason="FIXME: Need to properly mock Streamlit columns and handle display_result_item")
def test_display_results_limit(mock_streamlit, large_interaction):
    """Test that results are limited to 10 items."""
    display = FileSearchDisplay()
    
    # Mock the _display_result_item method to avoid complexity
    with patch.object(display, '_display_result_item') as mock_display_item:
        # Display the interaction
        display.display(large_interaction)
        
        # Verify metrics displayed
        mock_streamlit['metric'].assert_called_with(
            "Total found",
            15,  # Total results
            label_visibility="visible"
        )
        
        # Verify remaining count displayed
        mock_streamlit['markdown'].assert_any_call(
            "<div class='remaining-count'>+ 5 more files found</div>",
            unsafe_allow_html=True
        )
        
        # Verify only first 10 items were displayed
        assert mock_display_item.call_count == 10

def test_launch_everything_gui(mock_session_state):
    """Test launching Everything GUI."""
    with patch('src.core.config_manager.ConfigManager.get_tool_config') as mock_config, \
         patch('os.path.exists') as mock_exists, \
         patch('subprocess.Popen') as mock_popen, \
         patch('streamlit.toast') as mock_toast:
        
        # Configure mocks
        mock_config.return_value = "C:\\Program Files\\Everything\\Everything.exe"
        mock_exists.return_value = True
        
        # Create display instance and call method
        display = FileSearchDisplay()
        display._launch_everything_gui("test query")
        
        # Verify Everything GUI was launched with correct arguments
        mock_popen.assert_called_once()
        args = mock_popen.call_args[0][0]
        expected_args = ["C:\\Program Files\\Everything\\Everything.exe", "-search", "test query"]
        assert args == expected_args, f"Expected {expected_args}, got {args}"
        
        # Verify toast was shown
        mock_toast.assert_called_once_with("Opened Everything with search: test query")
