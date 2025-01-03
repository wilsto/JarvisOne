"""Tests for query analyzer display."""
import pytest
from unittest.mock import Mock, patch
import streamlit as st
from src.ui.interactions.agents.query_analyzer import QueryAnalyzerDisplay
from tests.mocks.session_state import SessionStateMock

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
        
        # Configure columns mock
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
        'id': 'test_id',
        'timestamp': '2024-01-01 12:00:00',
        'type': 'query_analysis',
        'data': {
            'query': 'test query',
            'analysis': {
                'intent': 'test intent',
                'entities': ['entity1', 'entity2'],
                'confidence': 0.95,
                'suggested_agent': 'test_agent'
            }
        }
    }

@pytest.fixture
def display_handler():
    """Fixture providing a QueryAnalyzerDisplay instance."""
    with SessionStateMock():
        return QueryAnalyzerDisplay()

def test_expander_title(display_handler, sample_interaction):
    """Test that expander title is correctly formatted."""
    title = display_handler.get_expander_title(sample_interaction)
    assert "🟢" in title  # High confidence badge
    assert "test_agent" in title  # Agent name
    assert "2024-01-01 12:00:00" in title  # Timestamp

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
    mock_streamlit['markdown'].assert_any_call("**Selected Agent:** test_agent")
    mock_streamlit['markdown'].assert_any_call("**Agent Confidence:** 95%")
    mock_streamlit['markdown'].assert_any_call("**Agent Reason:** None")
    
    # Verify verifier details displayed
    mock_streamlit['markdown'].assert_any_call("**Final Confidence:** 95%")
    mock_streamlit['markdown'].assert_any_call("**Confidence Check Level:** High")
    mock_streamlit['markdown'].assert_any_call("**Verifier Reason:** Verified successfully")

def test_display_without_analysis(mock_streamlit, display_handler):
    """Test display without analysis data."""
    # Create interaction without analysis
    interaction = {
        'id': 'test_id',
        'timestamp': '2024-01-01 12:00:00',
        'type': 'query_analysis',
        'data': {
            'query': 'test query'
        }
    }
    
    # Display should handle missing analysis gracefully
    with pytest.raises(KeyError):
        display_handler.display(interaction)

def test_display_with_empty_analysis(mock_streamlit, display_handler):
    """Test display with empty analysis."""
    # Create interaction with empty analysis
    interaction = {
        'id': 'test_id',
        'timestamp': '2024-01-01 12:00:00',
        'type': 'query_analysis',
        'data': {
            'query': 'test query',
            'analysis': {
                'intent': None,
                'entities': [],
                'confidence': 0,
                'suggested_agent': None
            }
        }
    }
    
    # Display the interaction
    display_handler.display(interaction)
    
    # Verify empty values are handled
    mock_streamlit['markdown'].assert_any_call("**Selected Agent:** None")
    mock_streamlit['markdown'].assert_any_call("**Agent Confidence:** 0%")
    mock_streamlit['markdown'].assert_any_call("**Agent Reason:** None")
