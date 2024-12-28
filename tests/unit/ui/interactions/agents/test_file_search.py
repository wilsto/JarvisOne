"""Tests for FileSearchDisplay."""
import pytest
from unittest.mock import Mock, patch
import streamlit as st
from src.ui.interactions.agents.file_search import FileSearchDisplay
from tests.utils import mock_session_state  # Import existing fixture

@pytest.fixture
def mock_streamlit():
    """Mock Streamlit components."""
    with patch('streamlit.columns') as mock_cols, \
         patch('streamlit.markdown') as mock_markdown, \
         patch('streamlit.metric') as mock_metric, \
         patch('streamlit.button') as mock_button, \
         patch('streamlit.toast') as mock_toast:
        
        # Configure column mock
        mock_col = Mock()
        mock_col.__enter__ = Mock(return_value=mock_col)
        mock_col.__exit__ = Mock(return_value=None)
        mock_col.markdown = Mock()
        mock_col.metric = Mock()
        mock_col.button = Mock()
        
        # Return 2 columns for header, 3 for file display
        def mock_cols_factory(ratios):
            return [mock_col for _ in range(len(ratios))]
        
        mock_cols.side_effect = mock_cols_factory
        
        yield {
            'columns': mock_cols,
            'markdown': mock_markdown,
            'metric': mock_metric,
            'button': mock_button,
            'toast': mock_toast,
            'col': mock_col
        }

@pytest.fixture
def sample_interaction():
    """Fixture providing a sample interaction."""
    return {
        'id': 'test-id-123',
        'type': 'file_search',
        'query': 'test query',
        'results': [
            r'C:\test\file1.txt',
            r'C:\test\subdir\file2.py',
            r'C:\test\file3.md'
        ],
        'timestamp': '15:30:00'
    }

@pytest.fixture
def large_interaction():
    """Fixture providing an interaction with more than 10 results."""
    return {
        'id': 'test-id-456',
        'type': 'file_search',
        'query': 'large query',
        'results': [f'C:\\test\\file{i}.txt' for i in range(15)],
        'timestamp': '15:30:00'
    }

def test_expander_title(sample_interaction):
    """Test that expander title is correctly formatted."""
    display = FileSearchDisplay()
    title = display.get_expander_title(sample_interaction)
    # Test without emoji to avoid encoding issues
    assert f"{sample_interaction['query']} • {sample_interaction['timestamp']}" in title

def test_display_result_item(mock_streamlit, sample_interaction):
    """Test display of a single result item."""
    display = FileSearchDisplay()
    
    # Test display without errors
    display._display_result_item(
        sample_interaction['id'], 
        1, 
        sample_interaction['results'][0]
    )
    
    # Verify calls
    assert mock_streamlit['columns'].called
    
    # Vérifie que st.markdown est appelé avec le nom du fichier
    mock_markdown_calls = [str(call) for call in mock_streamlit['markdown'].mock_calls]
    assert any('file1.txt' in call for call in mock_markdown_calls)

def test_display_results_limit(mock_streamlit, large_interaction):
    """Test that results are limited to 10 items."""
    display = FileSearchDisplay()
    
    with patch.object(display, '_display_result_item') as mock_display_item:
        # Display results
        display.display(large_interaction)
        
        # Verify only 10 items were displayed
        assert mock_display_item.call_count == 10
        
        # Verify metric shows total count
        mock_streamlit['metric'].assert_called_once_with(
            "Total found", 15, label_visibility="visible"
        )
        
        # Verify remaining count message for items > 10
        remaining_msg = "+ 5 more files found"
        mock_streamlit['markdown'].assert_any_call(
            f"<div class='remaining-count'>{remaining_msg}</div>",
            unsafe_allow_html=True
        )

def test_launch_everything_gui():
    """Test launching Everything GUI."""
    display = FileSearchDisplay()
    
    with patch('subprocess.Popen') as mock_popen:
        display._launch_everything_gui("test query")
        
        # Verify correct command
        mock_popen.assert_called_once()
        args = mock_popen.call_args[0][0]
        assert args[1:] == ["-search", "test query"]
        assert "Everything.exe" in args[0]
