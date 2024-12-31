import pytest
import streamlit as st
from src.core.llm_manager import (
    init_session_state, update_llm_preferences, get_llm_model,
    OpenAILLM, AnthropicLLM, GeminiLLM, OllamaLLM,
    DEFAULT_PARAMS
)
from src.core.llm_base import LLM
from unittest.mock import patch, MagicMock
from tests.utils import mock_session_state, MockSessionState

@pytest.fixture
def mock_workspace_manager():
    """Mock workspace manager."""
    mock = MagicMock()
    mock.get_current_context_prompt.return_value = "Test system prompt"
    return mock

@pytest.fixture
def mock_config_manager():
    with patch('src.core.llm_manager.ConfigManager') as mock:
        mock.load_llm_preferences.return_value = {
            "provider": "Ollama (Local)",
            "model": "mistral:latest"
        }
        yield mock

@pytest.fixture
def mock_cache():
    """Mock LLM cache."""
    with patch('src.core.llm_manager.llm_cache') as mock:
        mock.get.return_value = None
        yield mock

@pytest.fixture
def mock_requests():
    """Mock requests for Ollama."""
    with patch('src.core.llm_manager.requests') as mock:
        mock.post.return_value.json.return_value = {"response": "Test response"}
        mock.post.return_value.status_code = 200
        yield mock

@pytest.fixture
def mock_anthropic():
    """Mock Anthropic client."""
    with patch('src.core.llm_manager.anthropic') as mock:
        mock_client = MagicMock()
        mock_client.messages.create.return_value.content[0].text = "Test response"
        mock.Client.return_value = mock_client
        yield mock

@pytest.fixture
def mock_openai():
    """Mock OpenAI client."""
    with patch('src.core.llm_manager.OpenAI') as mock:
        mock_client = MagicMock()
        mock_stream = [
            MagicMock(choices=[MagicMock(delta=MagicMock(content="Test "))]),
            MagicMock(choices=[MagicMock(delta=MagicMock(content="response"))])
        ]
        mock_client.chat.completions.create.return_value = mock_stream
        mock.return_value = mock_client
        yield mock

def test_init_session_state_with_preferences(mock_config_manager, mock_session_state, mock_workspace_manager):
    """Test initialization of session state with saved preferences"""
    st.session_state.workspace_manager = mock_workspace_manager
    init_session_state()
    
    assert st.session_state.llm_provider == "Ollama (Local)"
    assert st.session_state.llm_model == "mistral:latest"
    mock_config_manager.load_llm_preferences.assert_called_once()

def test_init_session_state_without_preferences(mock_config_manager, mock_session_state, mock_workspace_manager):
    """Test initialization of session state without saved preferences"""
    st.session_state.workspace_manager = mock_workspace_manager
    
    # Configure mock to return None for preferences and default values from config
    mock_config_manager.load_llm_preferences.return_value = None
    config_mock = MagicMock()
    config_mock.get.return_value = {'default_provider': 'Ollama (Local)', 'default_model': 'mistral:latest'}
    mock_config_manager._load_config.return_value = config_mock
    
    init_session_state()
    
    assert st.session_state.llm_provider == 'Ollama (Local)'
    assert st.session_state.llm_model == 'mistral:latest'

def test_update_llm_preferences(mock_config_manager, mock_session_state, mock_workspace_manager):
    """Test updating LLM preferences"""
    st.session_state.workspace_manager = mock_workspace_manager
    st.session_state.llm_provider = "OpenAI"
    st.session_state.llm_model = "gpt-4"
    
    update_llm_preferences()
    
    mock_config_manager.save_llm_preferences.assert_called_once_with("OpenAI", "gpt-4")

def test_ollama_llm(mock_cache, mock_requests, mock_session_state, mock_workspace_manager):
    """Test OllamaLLM functionality."""
    st.session_state.workspace_manager = mock_workspace_manager
    
    # Initialize LLM
    llm = OllamaLLM("mistral:latest")
    
    # Test generate_response
    response = llm.generate_response("Test prompt")
    
    # Verify cache check
    mock_cache.get.assert_called_once_with("Test prompt", "mistral:latest")
    
    # Verify API call
    mock_requests.post.assert_called_once()
    assert mock_requests.post.call_args[0][0] == "http://localhost:11434/api/generate"
    assert mock_requests.post.call_args[1]["json"]["model"] == "mistral:latest"
    assert mock_requests.post.call_args[1]["json"]["prompt"] == "Test prompt"
    
    # Verify response
    assert response == "Test response"
    
    # Verify cache set
    mock_cache.set.assert_called_once_with("Test prompt", "mistral:latest", "Test response")

def test_openai_llm(mock_cache, mock_openai, mock_session_state, mock_workspace_manager):
    """Test OpenAILLM functionality"""
    st.session_state.workspace_manager = mock_workspace_manager
    
    # Configure cache to miss
    mock_cache.get.return_value = None
    
    # Set API key in environment
    with patch.dict('src.core.llm_manager.API_KEYS', {'openai': 'test-key'}):
        # Initialize LLM
        llm = OpenAILLM("gpt-4")
        
        # Test generate_response
        response = llm.generate_response("Test prompt")
        
        # Verify cache check
        mock_cache.get.assert_called_once_with("Test prompt", "gpt-4")
        
        # Verify API call
        mock_openai.assert_called_once_with(api_key='test-key', timeout=300)
        mock_openai.return_value.chat.completions.create.assert_called_once()
        
        # Verify response
        assert response == "Test response"
        
        # Verify cache set
        mock_cache.set.assert_called_once_with("Test prompt", "gpt-4", "Test response")

def test_anthropic_llm(mock_cache, mock_anthropic, mock_session_state, mock_workspace_manager):
    """Test AnthropicLLM functionality."""
    st.session_state.workspace_manager = mock_workspace_manager
    
    # Set API key in environment
    with patch.dict('src.core.llm_manager.API_KEYS', {'anthropic': 'test_key'}):
        # Initialize LLM
        llm = AnthropicLLM("claude-3")
        
        # Test generate_response
        response = llm.generate_response("Test prompt")
        
        # Verify cache check
        mock_cache.get.assert_called_once_with("Test prompt", "claude-3")
        
        # Verify API call
        mock_anthropic.Client.assert_called_once_with(api_key='test_key', timeout=300)
        mock_anthropic.Client.return_value.messages.create.assert_called_once()
        
        # Verify response
        assert response == "Test response"
        
        # Verify cache set
        mock_cache.set.assert_called_once_with("Test prompt", "claude-3", "Test response")

@patch('src.core.llm_manager.genai')
@patch('src.core.llm_manager.GenerativeModel')
@patch('src.core.llm_manager.llm_cache')
def test_gemini_llm(mock_cache, mock_generative_model, mock_genai, mock_session_state, mock_workspace_manager):
    """Test GeminiLLM functionality"""
    st.session_state.workspace_manager = mock_workspace_manager
    # Configure cache to miss
    mock_cache.get.return_value = None
    
    # Configure Gemini mock
    mock_model = MagicMock()
    mock_model.generate_content.return_value = MagicMock(text="Test response")
    mock_generative_model.return_value = mock_model
    
    # Patch configure to avoid authentication
    mock_genai.configure = MagicMock()
    
    with patch('src.core.llm_manager.API_KEYS', {'google': 'test-key'}):
        llm = GeminiLLM("gemini-pro")
        response = llm.generate_response("Test prompt")
    
    # Verify response
    assert response == "Test response"
    
    # Verify cache was checked
    mock_cache.get.assert_called_once_with("Test prompt", "gemini-pro")
    
    # Verify API call
    mock_model.generate_content.assert_called_once_with(
        "Test prompt",
        generation_config={
            "temperature": DEFAULT_PARAMS['temperature'],
            "max_output_tokens": DEFAULT_PARAMS['max_tokens']
        }
    )
    
    # Verify cache was updated
    mock_cache.set.assert_called_once_with("Test prompt", "gemini-pro", "Test response")

@patch('src.core.llm_manager.OpenAI')
def test_openai_llm_no_api_key(mock_openai, mock_session_state, mock_workspace_manager):
    """Test OpenAILLM raises error without API key"""
    st.session_state.workspace_manager = mock_workspace_manager
    with patch('src.core.llm_manager.API_KEYS', {'openai': None}):
        with pytest.raises(ValueError, match="OpenAI API key not found"):
            OpenAILLM("gpt-4")

@patch('src.core.llm_manager.anthropic')
def test_anthropic_llm_no_api_key(mock_anthropic, mock_session_state, mock_workspace_manager):
    """Test AnthropicLLM raises error without API key"""
    st.session_state.workspace_manager = mock_workspace_manager
    with patch('src.core.llm_manager.API_KEYS', {'anthropic': None}):
        with pytest.raises(ValueError, match="Anthropic API key not found"):
            AnthropicLLM("claude-2")

@patch('src.core.llm_manager.genai')
def test_gemini_llm_no_api_key(mock_genai, mock_session_state, mock_workspace_manager):
    """Test GeminiLLM raises error without API key"""
    st.session_state.workspace_manager = mock_workspace_manager
    with patch('src.core.llm_manager.API_KEYS', {'google': None}):
        with pytest.raises(ValueError, match="Google API key not found"):
            GeminiLLM("gemini-pro")

def test_get_llm_model_ollama(mock_session_state, mock_workspace_manager):
    """Test get_llm_model returns OllamaLLM"""
    st.session_state.workspace_manager = mock_workspace_manager
    st.session_state.llm_provider = "Ollama (Local)"
    st.session_state.llm_model = "mistral:latest"
    
    model = get_llm_model()
    assert isinstance(model, OllamaLLM)
    assert model.model == "mistral:latest"

@patch('src.core.llm_manager.OpenAI')
def test_get_llm_model_openai(mock_openai, mock_session_state, mock_workspace_manager):
    """Test get_llm_model returns OpenAILLM"""
    st.session_state.workspace_manager = mock_workspace_manager
    st.session_state.llm_provider = "OpenAI"
    st.session_state.llm_model = "gpt-4"
    
    with patch('src.core.llm_manager.API_KEYS', {'openai': 'test-key'}):
        model = get_llm_model()
        assert isinstance(model, OpenAILLM)
        assert model.model == "gpt-4"

@patch('src.core.llm_manager.anthropic')
def test_get_llm_model_anthropic(mock_anthropic, mock_session_state, mock_workspace_manager):
    """Test get_llm_model returns AnthropicLLM"""
    st.session_state.workspace_manager = mock_workspace_manager
    st.session_state.llm_provider = "Anthropic"
    st.session_state.llm_model = "claude-2"
    
    with patch('src.core.llm_manager.API_KEYS', {'anthropic': 'test-key'}):
        model = get_llm_model()
        assert isinstance(model, AnthropicLLM)
        assert model.model == "claude-2"

@patch('src.core.llm_manager.genai')
def test_get_llm_model_gemini(mock_genai, mock_session_state, mock_workspace_manager):
    """Test get_llm_model returns GeminiLLM"""
    st.session_state.workspace_manager = mock_workspace_manager
    st.session_state.llm_provider = "Google"
    st.session_state.llm_model = "gemini-pro"
    
    with patch('src.core.llm_manager.API_KEYS', {'google': 'test-key'}):
        model = get_llm_model()
        assert isinstance(model, GeminiLLM)
        assert model.model == "gemini-pro"

def test_get_llm_model_invalid_provider(mock_session_state, mock_workspace_manager):
    """Test get_llm_model raises error for invalid provider."""
    st.session_state.workspace_manager = mock_workspace_manager
    st.session_state.llm_provider = "Invalid Provider"
    st.session_state.llm_model = "invalid-model"
    
    with pytest.raises(ValueError, match=f"Unknown provider: {st.session_state.llm_provider}"):
        get_llm_model()

def test_get_llm_model_error_fallback(mock_config_manager, mock_session_state, mock_workspace_manager):
    """Test get_llm_model fallback on error."""
    st.session_state.workspace_manager = mock_workspace_manager
    
    # Configure initial provider to fail
    st.session_state.llm_provider = "OpenAI"
    st.session_state.llm_model = "gpt-4"
    
    # Mock OpenAI to raise error
    with patch('src.core.llm_manager.OpenAI') as mock_openai:
        mock_openai.side_effect = ValueError("API key not found")
        
        # Should fall back to Ollama
        llm = get_llm_model()
        
        assert isinstance(llm, OllamaLLM)
        assert llm.model == "mistral:latest"
        # Session state should be updated to reflect fallback
        assert st.session_state.llm_provider == "Ollama (Local)"
        assert st.session_state.llm_model == "mistral:latest"

@patch('src.core.llm_manager.OpenAI')
@patch('src.core.llm_manager.llm_cache')
def test_openai_llm_error(mock_cache, mock_openai, mock_session_state, mock_workspace_manager):
    """Test OpenAILLM error handling"""
    st.session_state.workspace_manager = mock_workspace_manager
    mock_cache.get.return_value = None
    mock_client = MagicMock()
    mock_client.chat.completions.create.side_effect = Exception("API Error")
    mock_openai.return_value = mock_client
    
    with patch('src.core.llm_manager.API_KEYS', {'openai': 'test-key'}):
        llm = OpenAILLM("gpt-4")
        with pytest.raises(Exception):
            llm.generate_response("Test prompt")
            
    mock_cache.set.assert_not_called()

@patch('src.core.llm_manager.anthropic')
@patch('src.core.llm_manager.llm_cache')
def test_anthropic_llm_error(mock_cache, mock_anthropic, mock_session_state, mock_workspace_manager):
    """Test AnthropicLLM error handling"""
    st.session_state.workspace_manager = mock_workspace_manager
    mock_cache.get.return_value = None
    mock_client = MagicMock()
    mock_client.messages.create.side_effect = Exception("API Error")
    mock_anthropic.Client.return_value = mock_client
    
    with patch('src.core.llm_manager.API_KEYS', {'anthropic': 'test-key'}):
        llm = AnthropicLLM("claude-2")
        with pytest.raises(Exception):
            llm.generate_response("Test prompt")
            
    mock_cache.set.assert_not_called()

@patch('src.core.llm_manager.genai')
@patch('src.core.llm_manager.GenerativeModel')
@patch('src.core.llm_manager.llm_cache')
def test_gemini_llm_error(mock_cache, mock_generative_model, mock_genai, mock_session_state, mock_workspace_manager):
    """Test GeminiLLM error handling"""
    st.session_state.workspace_manager = mock_workspace_manager
    mock_cache.get.return_value = None
    mock_model = MagicMock()
    mock_model.generate_content.side_effect = Exception("API Error")
    mock_generative_model.return_value = mock_model
    mock_genai.configure = MagicMock()
    
    with patch('src.core.llm_manager.API_KEYS', {'google': 'test-key'}):
        llm = GeminiLLM("gemini-pro")
        with pytest.raises(Exception):
            llm.generate_response("Test prompt")
            
    mock_cache.set.assert_not_called()

@patch('src.core.llm_manager.requests')
@patch('src.core.llm_manager.llm_cache')
def test_ollama_llm_error(mock_cache, mock_requests, mock_session_state, mock_workspace_manager):
    """Test OllamaLLM error handling"""
    st.session_state.workspace_manager = mock_workspace_manager
    mock_cache.get.return_value = None
    mock_requests.post.side_effect = Exception("API Error")
    
    llm = OllamaLLM("mistral:latest")
    with pytest.raises(Exception):
        llm.generate_response("Test prompt")
        
    mock_cache.set.assert_not_called()
