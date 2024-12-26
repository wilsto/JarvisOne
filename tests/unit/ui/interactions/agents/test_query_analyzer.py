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
         patch('streamlit.json') as mock_json:
        yield {
            'markdown': mock_markdown,
            'json': mock_json,
        }

@pytest.fixture
def sample_interaction():
    """Fixture providing a sample interaction."""
    return {
        'id': 'test-id-123',
        'type': 'query_analyzer',
        'query': 'test query',
        'timestamp': '15:30:00',
        'analysis': {
            'agent_selected': 'Test Agent',
            'intent': 'test',
            'confidence': 0.95
        }
    }

@pytest.fixture
def display_handler():
    """Fixture providing a QueryAnalyzerDisplay instance."""
    return QueryAnalyzerDisplay()

def test_expander_title(display_handler, sample_interaction):
    """Test that expander title is correctly formatted."""
    title = display_handler.get_expander_title(sample_interaction)
    # Test without emoji to avoid encoding issues
    assert f"Analyse : {sample_interaction['analysis']['agent_selected']}" in title
    assert sample_interaction['timestamp'] in title

def test_display_with_analysis(mock_streamlit, display_handler, sample_interaction):
    """Test display with analysis data."""
    # Display interaction
    display_handler.display(sample_interaction)
    
    # Verify query display
    mock_streamlit['markdown'].assert_any_call(
        f"**Requête analysée :** {sample_interaction['query']}"
    )
    
    # Verify analysis header
    mock_streamlit['markdown'].assert_any_call("**Résultat de l'analyse :**")
    
    # Verify analysis content
    mock_streamlit['json'].assert_called_once_with(sample_interaction['analysis'])

def test_display_without_analysis(mock_streamlit, display_handler):
    """Test display without analysis data."""
    # Create interaction without analysis
    interaction = {
        'id': 'test-id-123',
        'type': 'query_analyzer',
        'query': 'test query',
        'timestamp': '15:30:00'
    }
    
    # Display interaction
    display_handler.display(interaction)
    
    # Verify only query is displayed
    mock_streamlit['markdown'].assert_called_once_with(
        f"**Requête analysée :** {interaction['query']}"
    )
    
    # Verify analysis is not displayed
    mock_streamlit['json'].assert_not_called()

def test_display_with_empty_analysis(mock_streamlit, display_handler):
    """Test display with empty analysis."""
    # Create interaction with empty analysis
    interaction = {
        'id': 'test-id-123',
        'type': 'query_analyzer',
        'query': 'test query',
        'timestamp': '15:30:00',
        'analysis': {}
    }
    
    # Display interaction
    display_handler.display(interaction)
    
    # Verify only query is displayed (empty analysis should not trigger analysis display)
    mock_streamlit['markdown'].assert_called_once_with(
        f"**Requête analysée :** {interaction['query']}"
    )
    
    # Verify analysis is not displayed for empty dict
    mock_streamlit['json'].assert_not_called()
