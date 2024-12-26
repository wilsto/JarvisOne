import pytest
import streamlit as st
from src.core.llm_manager import (
    init_session_state, update_llm_preferences, get_llm_model,
    OpenAILLM, AnthropicLLM, GeminiLLM, OllamaLLM,
    DEFAULT_PARAMS, _initialize_model
)
from src.core.llm_base import LLM
from unittest.mock import patch, MagicMock
from tests.utils import mock_session_state, MockSessionState

@pytest.fixture
def mock_config_manager():
    with patch('src.core.llm_manager.ConfigManager') as mock:
        mock.load_llm_preferences.return_value = {
            "provider": "Ollama (Local)",
            "model": "mistral:latest"
        }
        yield mock

def test_init_session_state_with_preferences(mock_config_manager, mock_session_state):
    """Test initialization of session state with saved preferences"""
    init_session_state()
    
    assert st.session_state.llm_provider == "Ollama (Local)"
    assert st.session_state.llm_model == "mistral:latest"
    mock_config_manager.load_llm_preferences.assert_called_once()

def test_init_session_state_without_preferences(mock_config_manager, mock_session_state):
    """Test initialization of session state without saved preferences"""
    mock_config_manager.load_llm_preferences.return_value = None
    
    init_session_state()
    
    assert st.session_state.llm_provider == "Ollama (Local)"
    assert st.session_state.llm_model == "mistral:latest"

def test_update_llm_preferences(mock_config_manager, mock_session_state):
    """Test updating LLM preferences"""
    st.session_state.llm_provider = "OpenAI"
    st.session_state.llm_model = "gpt-4"
    
    update_llm_preferences()
    
    mock_config_manager.save_llm_preferences.assert_called_once_with("OpenAI", "gpt-4")

@patch('src.core.llm_manager.requests')
@patch('src.core.llm_manager.llm_cache')
def test_ollama_llm(mock_cache, mock_requests):
    """Test OllamaLLM functionality"""
    # Configure cache to miss
    mock_cache.get.return_value = None
    
    # Configure requests mock
    mock_response = MagicMock()
    mock_response.json.return_value = {"response": "Test response"}
    mock_requests.post.return_value = mock_response
    
    llm = OllamaLLM("mistral:latest")
    response = llm.generate_response("Test prompt")
    
    # Verify response
    assert response == "Test response"
    
    # Verify cache was checked
    mock_cache.get.assert_called_once_with("Test prompt", "mistral:latest")
    
    # Verify API call
    mock_requests.post.assert_called_once_with(
        "http://localhost:11434/api/generate",
        json={
            "model": "mistral:latest",
            "prompt": "Test prompt",
            "stream": False,
            "options": {
                "temperature": DEFAULT_PARAMS['temperature'],
                "num_predict": DEFAULT_PARAMS['max_tokens'],
            }
        }
    )
    
    # Verify cache was updated
    mock_cache.set.assert_called_once_with("Test prompt", "mistral:latest", "Test response")

@patch('src.core.llm_manager.OpenAI')
@patch('src.core.llm_manager.llm_cache')
def test_openai_llm(mock_cache, mock_openai):
    """Test OpenAILLM functionality"""
    # Configure cache to miss
    mock_cache.get.return_value = None
    
    # Configure OpenAI mock
    mock_client = MagicMock()
    mock_stream = [
        MagicMock(choices=[MagicMock(delta=MagicMock(content="Test "))]),
        MagicMock(choices=[MagicMock(delta=MagicMock(content="response"))]),
    ]
    mock_client.chat.completions.create.return_value = mock_stream
    mock_openai.return_value = mock_client
    
    with patch('src.core.llm_manager.API_KEYS', {'openai': 'test-key'}):
        llm = OpenAILLM("gpt-4")
        response = llm.generate_response("Test prompt")
    
    # Verify response
    assert response == "Test response"
    
    # Verify cache was checked
    mock_cache.get.assert_called_once_with("Test prompt", "gpt-4")
    
    # Verify API call
    mock_client.chat.completions.create.assert_called_once_with(
        model="gpt-4",
        messages=[{"role": "user", "content": "Test prompt"}],
        temperature=DEFAULT_PARAMS['temperature'],
        max_tokens=DEFAULT_PARAMS['max_tokens'],
        presence_penalty=DEFAULT_PARAMS['presence_penalty'],
        frequency_penalty=DEFAULT_PARAMS['frequency_penalty'],
        stream=True
    )
    
    # Verify cache was updated
    mock_cache.set.assert_called_once_with("Test prompt", "gpt-4", "Test response")

@patch('src.core.llm_manager.anthropic')
@patch('src.core.llm_manager.llm_cache')
def test_anthropic_llm(mock_cache, mock_anthropic):
    """Test AnthropicLLM functionality"""
    # Configure cache to miss
    mock_cache.get.return_value = None
    
    # Configure Anthropic mock
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.content = [MagicMock(text="Test response")]
    mock_client.messages.create.return_value = mock_response
    mock_anthropic.Client.return_value = mock_client
    
    with patch('src.core.llm_manager.API_KEYS', {'anthropic': 'test-key'}):
        llm = AnthropicLLM("claude-2")
        response = llm.generate_response("Test prompt")
    
    # Verify response
    assert response == "Test response"
    
    # Verify cache was checked
    mock_cache.get.assert_called_once_with("Test prompt", "claude-2")
    
    # Verify API call
    mock_client.messages.create.assert_called_once_with(
        model="claude-2",
        max_tokens=DEFAULT_PARAMS['max_tokens'],
        temperature=DEFAULT_PARAMS['temperature'],
        messages=[{"role": "user", "content": "Test prompt"}]
    )
    
    # Verify cache was updated
    mock_cache.set.assert_called_once_with("Test prompt", "claude-2", "Test response")

@patch('src.core.llm_manager.genai')
@patch('src.core.llm_manager.GenerativeModel')
@patch('src.core.llm_manager.llm_cache')
def test_gemini_llm(mock_cache, mock_generative_model, mock_genai):
    """Test GeminiLLM functionality"""
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
def test_openai_llm_no_api_key(mock_openai):
    """Test OpenAILLM raises error without API key"""
    with patch('src.core.llm_manager.API_KEYS', {'openai': None}):
        with pytest.raises(ValueError, match="OpenAI API key not found"):
            OpenAILLM("gpt-4")

@patch('src.core.llm_manager.anthropic')
def test_anthropic_llm_no_api_key(mock_anthropic):
    """Test AnthropicLLM raises error without API key"""
    with patch('src.core.llm_manager.API_KEYS', {'anthropic': None}):
        with pytest.raises(ValueError, match="Anthropic API key not found"):
            AnthropicLLM("claude-2")

@patch('src.core.llm_manager.genai')
def test_gemini_llm_no_api_key(mock_genai):
    """Test GeminiLLM raises error without API key"""
    with patch('src.core.llm_manager.API_KEYS', {'google': None}):
        with pytest.raises(ValueError, match="Google API key not found"):
            GeminiLLM("gemini-pro")

def test_get_llm_model_ollama(mock_session_state):
    """Test get_llm_model returns OllamaLLM"""
    st.session_state.llm_provider = "Ollama (Local)"
    st.session_state.llm_model = "mistral:latest"
    
    model = get_llm_model()
    assert isinstance(model, OllamaLLM)
    assert model.model == "mistral:latest"

@patch('src.core.llm_manager.OpenAI')
def test_get_llm_model_openai(mock_openai, mock_session_state):
    """Test get_llm_model returns OpenAILLM"""
    st.session_state.llm_provider = "OpenAI"
    st.session_state.llm_model = "gpt-4"
    
    with patch('src.core.llm_manager.API_KEYS', {'openai': 'test-key'}):
        model = get_llm_model()
        assert isinstance(model, OpenAILLM)
        assert model.model == "gpt-4"

@patch('src.core.llm_manager.anthropic')
def test_get_llm_model_anthropic(mock_anthropic, mock_session_state):
    """Test get_llm_model returns AnthropicLLM"""
    st.session_state.llm_provider = "Anthropic"
    st.session_state.llm_model = "claude-2"
    
    with patch('src.core.llm_manager.API_KEYS', {'anthropic': 'test-key'}):
        model = get_llm_model()
        assert isinstance(model, AnthropicLLM)
        assert model.model == "claude-2"

@patch('src.core.llm_manager.genai')
def test_get_llm_model_gemini(mock_genai, mock_session_state):
    """Test get_llm_model returns GeminiLLM"""
    st.session_state.llm_provider = "Google"
    st.session_state.llm_model = "gemini-pro"
    
    with patch('src.core.llm_manager.API_KEYS', {'google': 'test-key'}):
        model = get_llm_model()
        assert isinstance(model, GeminiLLM)
        assert model.model == "gemini-pro"

def test_get_llm_model_invalid_provider(mock_session_state):
    """Test get_llm_model falls back to Ollama for invalid provider"""
    st.session_state.llm_provider = "Invalid"
    st.session_state.llm_model = "model"
    
    model = get_llm_model()
    assert isinstance(model, OllamaLLM)
    assert model.model == "mistral:latest"

def test_initialize_model_invalid_provider():
    """Test _initialize_model raises error for invalid provider"""
    with pytest.raises(ValueError, match="Unknown provider"):
        _initialize_model("Invalid", "model")

@patch('src.core.llm_manager.OpenAI')
@patch('src.core.llm_manager.llm_cache')
def test_openai_llm_error(mock_cache, mock_openai):
    """Test OpenAILLM error handling"""
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
def test_anthropic_llm_error(mock_cache, mock_anthropic):
    """Test AnthropicLLM error handling"""
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
def test_gemini_llm_error(mock_cache, mock_generative_model, mock_genai):
    """Test GeminiLLM error handling"""
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
def test_ollama_llm_error(mock_cache, mock_requests):
    """Test OllamaLLM error handling"""
    mock_cache.get.return_value = None
    mock_requests.post.side_effect = Exception("API Error")
    
    llm = OllamaLLM("mistral:latest")
    with pytest.raises(Exception):
        llm.generate_response("Test prompt")
        
    mock_cache.set.assert_not_called()

@patch('src.core.llm_manager.ConfigManager')
def test_get_llm_model_error_fallback(mock_config_manager, mock_session_state):
    """Test get_llm_model fallback on error"""
    # Test error when loading from session state
    st.session_state.llm_provider = "OpenAI"
    st.session_state.llm_model = "gpt-4"
    
    with patch('src.core.llm_manager.API_KEYS', {'openai': None}):
        model = get_llm_model()
        
    assert isinstance(model, OllamaLLM)
    assert model.model == "mistral:latest"
    
    # Test error when loading from preferences file
    st.session_state = MockSessionState()  # Reset session state
    
    mock_config_manager.load_llm_preferences.return_value = {
        "provider": "OpenAI",
        "model": "gpt-4"
    }
    
    with patch('src.core.llm_manager.API_KEYS', {'openai': None}):
        model = get_llm_model()
        
    assert isinstance(model, OllamaLLM)
    assert model.model == "mistral:latest"
