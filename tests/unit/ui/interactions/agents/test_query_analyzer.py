"""Tests for query analyzer display."""
import pytest
from unittest.mock import Mock, patch
import streamlit as st
from src.ui.interactions.agents.query_analyzer import QueryAnalyzerDisplay
from tests.utils import mock_session_state

@pytest.fixture
def mock_streamlit():
    """Mock Streamlit components."""
    with patch('streamlit.markdown') as mock_markdown, \
         patch('streamlit.json') as mock_json, \
         patch('streamlit.columns') as mock_cols:
        
        # Configure column mock
        mock_col = Mock()
        mock_col.__enter__ = Mock(return_value=mock_col)
        mock_col.__exit__ = Mock(return_value=None)
        mock_col.markdown = Mock()
        
        # Return 2 columns for analysis display
        mock_cols.return_value = [mock_col, mock_col]
        
        yield {
            'markdown': mock_markdown,
            'json': mock_json,
            'columns': mock_cols,
            'col': mock_col
        }

@pytest.fixture
def sample_interaction():
    """Fixture providing a sample interaction."""
    return {
        'id': 'test-id',
        'type': 'query_analyzer',
        'query': 'test query',
        'timestamp': '15:30:00',
        'analysis': {
            'agent_selected': 'Test Agent',
            'confidence': 95,
            'agent': {
                'name': 'Test Agent',
                'confidence': 95,
                'reason': 'Test reason'
            },
            'verifier': {
                'confidence': 90,
                'level': 'high',
                'reason': 'Verified successfully'
            }
        }
    }

@pytest.fixture
def display_handler():
    """Fixture providing a QueryAnalyzerDisplay instance."""
    return QueryAnalyzerDisplay()

def test_expander_title(display_handler, sample_interaction):
    """Test that expander title is correctly formatted."""
    title = display_handler.get_expander_title(sample_interaction)
    assert "🟢" in title  # High confidence badge
    assert "Test Agent" in title  # Agent name
    assert "15:30:00" in title  # Timestamp

def test_display_with_analysis(mock_streamlit, display_handler, sample_interaction):
    """Test display with analysis data."""
    # Display the interaction
    display_handler.display(sample_interaction)
    
    # Verify query displayed
    mock_streamlit['markdown'].assert_any_call(
        "**Analyzed Query:** test query"
    )
    
    # Verify agent selection displayed
    mock_streamlit['markdown'].assert_any_call("### Agent Selection")
    mock_streamlit['markdown'].assert_any_call("**Selected Agent:** Test Agent")
    mock_streamlit['markdown'].assert_any_call("**Agent Confidence:** 95%")
    mock_streamlit['markdown'].assert_any_call("**Agent Reason:** Test reason")
    
    # Verify verifier details displayed
    mock_streamlit['markdown'].assert_any_call("**Final Confidence:** 90%")
    mock_streamlit['markdown'].assert_any_call("**Confidence Check Level:** High")
    mock_streamlit['markdown'].assert_any_call("**Verifier Reason:** Verified successfully")

def test_display_without_analysis(mock_streamlit, display_handler):
    """Test display without analysis data."""
    # Create interaction without analysis
    interaction = {
        'id': 'test-id',
        'type': 'query_analyzer',
        'query': 'test query',
        'timestamp': '15:30:00'
    }
    
    # Display should handle missing analysis gracefully
    with pytest.raises(KeyError):
        display_handler.display(interaction)

def test_display_with_empty_analysis(mock_streamlit, display_handler):
    """Test display with empty analysis."""
    # Create interaction with empty analysis
    interaction = {
        'id': 'test-id',
        'type': 'query_analyzer',
        'query': 'test query',
        'timestamp': '15:30:00',
        'analysis': {
            'agent_selected': None,
            'confidence': 0,
            'agent': {
                'name': None,
                'confidence': 0,
                'reason': None
            },
            'verifier': {
                'confidence': 0,
                'level': 'low',
                'reason': None
            }
        }
    }
    
    # Display the interaction
    display_handler.display(interaction)
    
    # Verify empty values are handled
    mock_streamlit['markdown'].assert_any_call("**Selected Agent:** None")
    mock_streamlit['markdown'].assert_any_call("**Agent Confidence:** 0%")
    mock_streamlit['markdown'].assert_any_call("**Agent Reason:** None")
