"""Tests for the ConfigManager class."""

import os
import yaml
import pytest
from pathlib import Path
from unittest.mock import patch, mock_open
from src.core.config_manager import ConfigManager

@pytest.fixture
def mock_config_file(tmp_path):
    """Create a temporary config file."""
    original_config = ConfigManager.CONFIG_FILE
    ConfigManager.CONFIG_FILE = str(tmp_path / "config.yaml")
    yield ConfigManager.CONFIG_FILE
    ConfigManager.CONFIG_FILE = original_config

def test_save_llm_preferences(mock_config_file):
    """Test saving LLM preferences."""
    ConfigManager.save_llm_preferences("Ollama (Local)", "mistral:latest")
    
    with open(mock_config_file, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)
        preferences = config.get("llm", {})
        
    assert preferences == {
        "provider": "Ollama (Local)",
        "model": "mistral:latest"
    }

def test_save_llm_preferences_error():
    """Test error handling when saving LLM preferences."""
    with patch("builtins.open", mock_open()) as mock_file:
        mock_file.side_effect = Exception("Write error")
        ConfigManager.save_llm_preferences("Ollama (Local)", "mistral:latest")
        # Should log error but not raise exception

def test_load_llm_preferences_existing(mock_config_file):
    """Test loading existing LLM preferences."""
    # Create test preferences
    test_config = {
        "llm": {
            "provider": "Ollama (Local)",
            "model": "mistral:latest"
        }
    }
    with open(mock_config_file, "w", encoding="utf-8") as f:
        yaml.safe_dump(test_config, f)
    
    preferences = ConfigManager.load_llm_preferences()
    assert preferences == test_config["llm"]

def test_load_llm_preferences_missing_file():
    """Test loading preferences with missing file."""
    # Use a non-existent path
    ConfigManager.CONFIG_FILE = "non_existent.yaml"
    preferences = ConfigManager.load_llm_preferences()
    
    # Should return default values
    assert preferences == {
        "provider": "Ollama (Local)",
        "model": "mistral:latest"
    }

def test_load_llm_preferences_error():
    """Test error handling when loading preferences."""
    with patch("os.path.exists") as mock_exists, \
         patch("builtins.open", mock_open()) as mock_file:
        mock_exists.return_value = True
        mock_file.side_effect = Exception("Read error")
        preferences = ConfigManager.load_llm_preferences()
        
    assert preferences == {
        "provider": "Ollama (Local)",
        "model": "mistral:latest"
    }

@pytest.mark.parametrize("provider,env_var", [
    ("OpenAI", "OPENAI_API_KEY"),
    ("Anthropic", "ANTHROPIC_API_KEY"),
    ("Google", "GOOGLE_API_KEY")
])
def test_get_api_key(provider, env_var):
    """Test getting API key for different providers."""
    with patch.dict(os.environ, {env_var: "test-key"}):
        assert ConfigManager.get_api_key(provider) == "test-key"

def test_get_api_key_invalid_provider():
    """Test getting API key for invalid provider."""
    assert ConfigManager.get_api_key("InvalidProvider") is None

def test_get_api_key_missing():
    """Test getting missing API key."""
    with patch.dict(os.environ, clear=True):
        assert ConfigManager.get_api_key("OpenAI") is None

@pytest.mark.parametrize("provider,env_var", [
    ("OpenAI", "OPENAI_ORG_ID"),
    ("Anthropic", "ANTHROPIC_ORG_ID")
])
def test_get_org_id(provider, env_var):
    """Test getting org ID for different providers."""
    with patch.dict(os.environ, {env_var: "test-org"}):
        assert ConfigManager.get_org_id(provider) == "test-org"

def test_get_org_id_invalid_provider():
    """Test getting org ID for invalid provider."""
    assert ConfigManager.get_org_id("InvalidProvider") is None

def test_get_org_id_missing():
    """Test getting missing org ID."""
    with patch.dict(os.environ, clear=True):
        assert ConfigManager.get_org_id("OpenAI") is None

def test_get_all_configs():
    """Test getting all configurations."""
    env_vars = {
        "OPENAI_API_KEY": "openai-key",
        "OPENAI_ORG_ID": "openai-org",
        "ANTHROPIC_API_KEY": "anthropic-key",
        "ANTHROPIC_ORG_ID": "anthropic-org",
        "GOOGLE_API_KEY": "google-key"
    }
    
    with patch.dict(os.environ, env_vars):
        configs = ConfigManager.get_all_configs()
        
    assert configs == {
        "OpenAI": {
            "api_key": "openai-key",
            "org_id": "openai-org"
        },
        "Anthropic": {
            "api_key": "anthropic-key",
            "org_id": "anthropic-org"
        },
        "Google": {
            "api_key": "google-key"
        }
    }
