"""Tests for sidebar component."""

import pytest
from unittest.mock import Mock, patch
import streamlit as st
from src.ui.components.sidebar import (
    render_sidebar,
    on_provider_change,
    on_model_change
)
from tests.utils import mock_session_state

# Mock des providers LLM
MOCK_LLM_PROVIDERS = {
    "ChatGPT": {
        "models": ["gpt-4", "gpt-3.5-turbo"],
        "needs_key": True
    },
    "Ollama (Local)": {
        "models": [],
        "needs_key": False
    }
}

@pytest.fixture
def mock_streamlit_sidebar():
    """Mock Streamlit sidebar components."""
    with patch('streamlit.sidebar') as mock_sidebar, \
         patch('streamlit.title') as mock_title, \
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
        mock_sidebar.return_value.__enter__ = Mock()
        mock_sidebar.return_value.__exit__ = Mock(return_value=None)
        
        col_mock = Mock()
        col_mock.__enter__ = Mock(return_value=col_mock)
        col_mock.__exit__ = Mock(return_value=None)
        mock_columns.return_value = [col_mock, col_mock]
        
        yield {
            'sidebar': mock_sidebar,
            'title': mock_title,
            'markdown': mock_markdown,
            'selectbox': mock_selectbox,
            'columns': mock_columns,
            'button': mock_button,
            'text_input': mock_text_input,
            'success': mock_success,
            'warning': mock_warning,
            'info': mock_info,
            'rerun': mock_rerun,
            'col_mock': col_mock
        }

@pytest.fixture
def mock_config():
    """Mock configuration related functions."""
    with patch('src.ui.components.sidebar.ConfigManager') as mock_config, \
         patch('src.ui.components.sidebar.get_provider_models') as mock_get_models, \
         patch('src.ui.components.sidebar.get_model_info') as mock_get_info, \
         patch('src.ui.components.sidebar.get_default_model') as mock_get_default, \
         patch('src.ui.components.sidebar.needs_api_key') as mock_needs_key, \
         patch('src.ui.components.sidebar.refresh_ollama_models') as mock_refresh, \
         patch('src.ui.components.sidebar.LLM_PROVIDERS', MOCK_LLM_PROVIDERS):
        
        # Configure mocks
        mock_config.load_llm_preferences.return_value = {
            "provider": "ChatGPT",
            "model": "gpt-4"
        }
        mock_get_models.return_value = ["gpt-4", "gpt-3.5-turbo"]
        mock_get_info.return_value = {
            "name": "GPT-4",
            "description": "Latest model",
            "context_length": "8k",
            "size": "175B"
        }
        mock_get_default.return_value = "gpt-4"
        mock_needs_key.return_value = True
        mock_config.get_api_key.return_value = None
        mock_config.get_org_id.return_value = "org-123"
        
        yield {
            'config': mock_config,
            'get_models': mock_get_models,
            'get_info': mock_get_info,
            'get_default': mock_get_default,
            'needs_key': mock_needs_key,
            'refresh': mock_refresh
        }

def test_render_sidebar_basic(mock_streamlit_sidebar, mock_config, mock_session_state):
    """Test basic sidebar rendering."""
    # Initialize session state
    mock_session_state.provider_select = "ChatGPT"
    mock_session_state.model_select = "gpt-4"
    
    render_sidebar()
    
    # Verify basic UI elements
    mock_streamlit_sidebar['title'].assert_called_once_with("JarvisOne")
    assert mock_streamlit_sidebar['markdown'].call_count >= 3  # Title + Model Info
    mock_streamlit_sidebar['selectbox'].assert_called()  # Provider selection
    
    # Verify config loading
    mock_config['config'].load_llm_preferences.assert_called_once()
    mock_config['get_models'].assert_called_once()
    mock_config['get_info'].assert_called_once()

def test_render_sidebar_api_key(mock_streamlit_sidebar, mock_config, mock_session_state):
    """Test API key section rendering."""
    # Initialize session state
    mock_session_state.provider_select = "ChatGPT"
    mock_session_state.model_select = "gpt-4"
    
    # Configure mock to require API key
    mock_config['needs_key'].return_value = True
    mock_config['config'].get_api_key.return_value = None
    
    render_sidebar()
    
    # Verify API key section
    mock_streamlit_sidebar['warning'].assert_called_once()  # Warning about missing key
    mock_streamlit_sidebar['text_input'].assert_called_once()  # API key input

def test_render_sidebar_ollama(mock_streamlit_sidebar, mock_config, mock_session_state):
    """Test Ollama-specific features."""
    # Initialize session state
    mock_session_state.provider_select = "Ollama (Local)"
    mock_session_state.model_select = None
    
    # Configure mock for Ollama
    mock_config['config'].load_llm_preferences.return_value = {
        "provider": "Ollama (Local)",
        "model": "llama2"
    }
    mock_config['get_models'].return_value = []  # No models found
    mock_config['needs_key'].return_value = False  # Ollama n'a pas besoin de clé API
    
    # Configure selectbox to return Ollama
    mock_streamlit_sidebar['selectbox'].return_value = "Ollama (Local)"
    
    render_sidebar()
    
    # Verify Ollama warning
    mock_streamlit_sidebar['warning'].assert_called_once_with(
        "Aucun modèle Ollama trouvé. Installez des modèles avec 'ollama pull'"
    )

def test_on_provider_change(mock_config, mock_session_state):
    """Test provider change handler."""
    # Initialize session state
    mock_session_state.provider_select = "ChatGPT"
    
    # Test
    on_provider_change()
    
    # Verify
    mock_config['get_default'].assert_called_once_with("ChatGPT")
    mock_config['config'].save_llm_preferences.assert_called_once()

def test_on_model_change(mock_config, mock_session_state):
    """Test model change handler."""
    # Initialize session state
    mock_session_state.provider_select = "ChatGPT"
    mock_session_state.model_select = "gpt-4"
    
    # Test
    on_model_change()
    
    # Verify
    mock_config['config'].save_llm_preferences.assert_called_once_with("ChatGPT", "gpt-4")

def test_render_sidebar_reset(mock_streamlit_sidebar, mock_config, mock_session_state):
    """Test conversation reset."""
    # Initialize session state
    mock_session_state.provider_select = "ChatGPT"
    mock_session_state.model_select = "gpt-4"
    mock_session_state.messages = ["message1", "message2"]
    
    # Setup button behavior
    def button_side_effect(label, **kwargs):
        return {
            "🔄": False,  # Refresh Ollama button
            "🔄 Réinitialiser la conversation": True  # Reset button
        }.get(label, False)
    mock_streamlit_sidebar['button'].side_effect = button_side_effect
    mock_streamlit_sidebar['selectbox'].return_value = "ChatGPT"  # Nécessaire pour éviter le warning Ollama
    
    # Test
    render_sidebar()
    
    # Verify
    assert mock_session_state.messages is None  # Vérifie que messages a été supprimé
    mock_streamlit_sidebar['rerun'].assert_called_once()
