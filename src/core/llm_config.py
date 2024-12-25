"""Configuration for LLM providers and models."""

from typing import Dict, List
from .providers.ollama_manager import update_ollama_config

# Configuration de base des providers LLM
BASE_CONFIG = {
    "Ollama (Local)": {
        "models": {},  # Will be populated by Ollama manager
        "requires_api_key": False,
        "default_model": None  # Will be set by Ollama manager
    },
    "OpenAI": {
        "models": {
            "gpt-4o-mini": {
                "name": "GPT-4 Optimized Mini",
                "description": "Version optimisée et rapide de GPT-4",
                "context_length": 128000,
                "local": False,
                "id": "gpt-4o-mini"  # Add explicit ID to prevent truncation
            }
        },
        "requires_api_key": True,
        "default_model": "gpt-4o-mini"
    },
    "Anthropic": {
        "models": {
            "claude-3-haiku": {
                "name": "Claude 3 Haiku",
                "description": "Version rapide et efficace de Claude",
                "context_length": 200000,
                "local": False
            }
        },
        "requires_api_key": True,
        "default_model": "claude-3-haiku"
    },
    "Google": {
        "models": {
            "gemini-2.0-flash-experimental": {
                "name": "Gemini 2.0 Flash",
                "description": "Version expérimentale ultra-rapide de Gemini",
                "context_length": 32768,
                "local": False
            }
        },
        "requires_api_key": True,
        "default_model": "gemini-2.0-flash-experimental"
    }
}

# Update configuration with installed Ollama models
LLM_PROVIDERS = update_ollama_config(BASE_CONFIG)

def get_provider_models(provider: str) -> List[str]:
    """Get list of models for a provider."""
    return list(LLM_PROVIDERS[provider]["models"].keys())

def get_model_info(provider: str, model: str) -> Dict:
    """Get information about a specific model."""
    return LLM_PROVIDERS[provider]["models"][model]

def needs_api_key(provider: str) -> bool:
    """Check if provider requires an API key."""
    return LLM_PROVIDERS[provider]["requires_api_key"]

def get_default_model(provider: str) -> str:
    """Get default model for a provider."""
    return LLM_PROVIDERS[provider]["default_model"]

def refresh_ollama_models() -> None:
    """Refresh the list of Ollama models."""
    global LLM_PROVIDERS
    LLM_PROVIDERS = update_ollama_config(BASE_CONFIG.copy())
