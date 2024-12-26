"""Unit tests for ollama_manager.py."""

import subprocess
import pytest
from unittest.mock import patch, MagicMock
from src.core.providers.ollama_manager import get_installed_models, update_ollama_config

# Sample test data
MOCK_OLLAMA_OUTPUT = """
NAME            SIZE   
mistral:latest  4.1GB  
llama2:latest   3.8GB  
"""

EXPECTED_MODELS = [
    {
        "name": "mistral:latest",
        "size": "4.1GB",
        "description": "Modèle local Ollama",
        "context_length": 8192,
        "local": True
    },
    {
        "name": "llama2:latest",
        "size": "3.8GB",
        "description": "Modèle local Ollama",
        "context_length": 8192,
        "local": True
    }
]

@pytest.fixture
def mock_subprocess_success():
    """Fixture for successful subprocess execution."""
    with patch('subprocess.run') as mock_run:
        mock_process = MagicMock()
        mock_process.stdout = MOCK_OLLAMA_OUTPUT
        mock_process.returncode = 0
        mock_run.return_value = mock_process
        yield mock_run

@pytest.fixture
def mock_subprocess_failure():
    """Fixture for failed subprocess execution."""
    with patch('subprocess.run') as mock_run:
        mock_run.side_effect = subprocess.CalledProcessError(1, 'ollama list', stderr="Command failed")
        yield mock_run

class TestGetInstalledModels:
    """Tests for get_installed_models function."""
    
    def test_successful_model_list(self, mock_subprocess_success):
        """Test successful retrieval of installed models."""
        models = get_installed_models()
        assert models == EXPECTED_MODELS
        mock_subprocess_success.assert_called_once_with(
            ["ollama", "list"],
            capture_output=True,
            text=True,
            check=True
        )

    def test_command_failure(self, mock_subprocess_failure):
        """Test handling of command failure."""
        models = get_installed_models()
        assert models == []
        mock_subprocess_failure.assert_called_once()

    def test_empty_output(self):
        """Test handling of empty command output."""
        with patch('subprocess.run') as mock_run:
            mock_process = MagicMock()
            mock_process.stdout = "\nNAME            SIZE   \n"
            mock_run.return_value = mock_process
            models = get_installed_models()
            assert models == []

    def test_malformed_output(self):
        """Test handling of malformed command output."""
        with patch('subprocess.run') as mock_run:
            mock_process = MagicMock()
            mock_process.stdout = "Invalid output format"
            mock_run.return_value = mock_process
            models = get_installed_models()
            assert models == []

class TestUpdateOllamaConfig:
    """Tests for update_ollama_config function."""
    
    def test_successful_config_update(self, mock_subprocess_success):
        """Test successful configuration update with installed models."""
        initial_config = {
            "Ollama (Local)": {
                "models": {},
                "default_model": None
            }
        }
        
        expected_config = {
            "Ollama (Local)": {
                "models": {
                    "mistral:latest": {
                        "name": "mistral:latest",
                        "description": "Modèle local Ollama",
                        "context_length": 8192,
                        "local": True,
                        "size": "4.1GB"
                    },
                    "llama2:latest": {
                        "name": "llama2:latest",
                        "description": "Modèle local Ollama",
                        "context_length": 8192,
                        "local": True,
                        "size": "3.8GB"
                    }
                },
                "default_model": "mistral:latest"
            }
        }
        
        updated_config = update_ollama_config(initial_config)
        assert updated_config == expected_config

    def test_no_models_found(self, mock_subprocess_failure):
        """Test configuration update when no models are found."""
        initial_config = {
            "Ollama (Local)": {
                "models": {},
                "default_model": None
            }
        }
        
        updated_config = update_ollama_config(initial_config)
        assert updated_config == initial_config

    def test_missing_ollama_key(self, mock_subprocess_success):
        """Test handling of missing Ollama key in config."""
        initial_config = {}
        updated_config = update_ollama_config(initial_config)
        assert updated_config == initial_config

    def test_preserve_other_config(self, mock_subprocess_success):
        """Test preservation of other configuration settings."""
        initial_config = {
            "Ollama (Local)": {
                "models": {},
                "default_model": None,
                "custom_setting": "value"
            },
            "Other Provider": {
                "setting": "value"
            }
        }
        
        updated_config = update_ollama_config(initial_config)
        assert "custom_setting" in updated_config["Ollama (Local)"]
        assert updated_config["Other Provider"] == {"setting": "value"}
