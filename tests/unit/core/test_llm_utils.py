"""Tests for LLM utilities."""

import os
import json
import time
import pytest
from pathlib import Path
from unittest.mock import patch, mock_open, MagicMock
from src.core.llm_utils import LLMCache, retry_on_error

@pytest.fixture
def cache_dir(tmp_path):
    """Create a temporary cache directory."""
    cache_dir = tmp_path / "llm_cache"
    cache_dir.mkdir()
    return str(cache_dir)

@pytest.fixture
def llm_cache(cache_dir):
    """Create an LLMCache instance with temporary directory."""
    return LLMCache(cache_dir)

def test_cache_initialization(cache_dir):
    """Test cache initialization."""
    cache = LLMCache(cache_dir)
    assert Path(cache.cache_dir).exists()
    assert Path(cache.cache_dir).is_dir()

def test_cache_key_generation(llm_cache):
    """Test cache key generation."""
    key1 = llm_cache._get_cache_key("prompt1", "model1")
    key2 = llm_cache._get_cache_key("prompt1", "model1")
    key3 = llm_cache._get_cache_key("prompt2", "model1")
    
    assert key1 == key2  # Same prompt and model should give same key
    assert key1 != key3  # Different prompt should give different key

def test_cache_miss(llm_cache):
    """Test cache miss."""
    result = llm_cache.get("test prompt", "test model")
    assert result is None

def test_cache_set_and_get(llm_cache):
    """Test setting and getting cache."""
    prompt = "test prompt"
    model = "test model"
    response = "test response"
    
    llm_cache.set(prompt, model, response)
    result = llm_cache.get(prompt, model)
    
    assert result == response

def test_cache_expiration(llm_cache):
    """Test cache expiration."""
    prompt = "test prompt"
    model = "test model"
    response = "test response"
    
    # Set cache
    llm_cache.set(prompt, model, response)
    
    # Mock time to be 25 hours later
    future_time = time.time() + 25 * 3600
    with patch('time.time', return_value=future_time):
        result = llm_cache.get(prompt, model)
        assert result is None

def test_cache_read_error(llm_cache):
    """Test error handling when reading cache."""
    prompt = "test prompt"
    model = "test model"
    
    # Create an invalid cache file
    cache_key = llm_cache._get_cache_key(prompt, model)
    cache_file = Path(llm_cache.cache_dir) / f"{cache_key}.json"
    cache_file.write_text("invalid json")
    
    result = llm_cache.get(prompt, model)
    assert result is None

def test_retry_on_error_success():
    """Test retry_on_error with successful function."""
    mock_func = MagicMock(return_value="success")
    decorated = retry_on_error()(mock_func)
    
    result = decorated()
    assert result == "success"
    assert mock_func.call_count == 1

def test_retry_on_error_retry_and_succeed():
    """Test retry_on_error with function that fails then succeeds."""
    mock_func = MagicMock(side_effect=[Exception("error"), "success"])
    decorated = retry_on_error(max_retries=2, delay=0)(mock_func)
    
    result = decorated()
    assert result == "success"
    assert mock_func.call_count == 2

def test_retry_on_error_max_retries():
    """Test retry_on_error with function that always fails."""
    mock_func = MagicMock(side_effect=Exception("error"))
    decorated = retry_on_error(max_retries=2, delay=0)(mock_func)
    
    with pytest.raises(Exception):
        decorated()
    assert mock_func.call_count == 2  # max_retries=2 means 2 attempts total

def test_retry_on_error_custom_params():
    """Test retry_on_error with custom parameters."""
    mock_func = MagicMock(side_effect=[Exception("error"), Exception("error"), "success"])
    decorated = retry_on_error(max_retries=3, delay=0)(mock_func)
    
    result = decorated()
    assert result == "success"
    assert mock_func.call_count == 3
