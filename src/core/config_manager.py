"""Configuration manager for environment variables."""

import os
import json
from typing import Dict, Optional
from dotenv import load_dotenv
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

# Charger les variables d'environnement depuis .env
load_dotenv()

class ConfigManager:
    """Configuration manager for API keys."""
    
    CONFIG_FILE = "config/llm_preferences.json"
    
    @classmethod
    def _ensure_config_dir(cls):
        """Ensure the config directory exists."""
        config_dir = Path(cls.CONFIG_FILE).parent
        config_dir.mkdir(parents=True, exist_ok=True)
        
    @classmethod
    def save_llm_preferences(cls, provider: str, model: str) -> None:
        """Save LLM preferences."""
        cls._ensure_config_dir()
        
        try:
            preferences = {
                "provider": provider,
                "model": model
            }
            
            with open(cls.CONFIG_FILE, "w", encoding="utf-8") as f:
                json.dump(preferences, f, indent=2)
                
            logger.info(f"LLM preferences saved: {preferences}")
        except Exception as e:
            logger.error(f"Error saving LLM preferences: {e}")
            
    @classmethod
    def load_llm_preferences(cls) -> Dict[str, str]:
        """Load LLM preferences."""
        try:
            if os.path.exists(cls.CONFIG_FILE):
                with open(cls.CONFIG_FILE, "r", encoding="utf-8") as f:
                    preferences = json.load(f)
                logger.info(f"LLM preferences loaded: {preferences}")
                return preferences
        except Exception as e:
            logger.error(f"Error loading LLM preferences: {e}")
            
        # Default preferences
        return {
            "provider": "Ollama (Local)",
            "model": "mistral:latest"
        }
        
    @staticmethod
    def get_api_key(provider: str) -> Optional[str]:
        """Get API key for a given provider."""
        key_mapping = {
            "OpenAI": "OPENAI_API_KEY",
            "Anthropic": "ANTHROPIC_API_KEY",
            "Google": "GOOGLE_API_KEY"
        }
        
        if provider not in key_mapping:
            logger.warning(f"Provider {provider} not recognized")
            return None
            
        key = os.getenv(key_mapping[provider])
        if not key:
            logger.warning(f"No API key found for {provider}")
        return key
        
    @staticmethod
    def get_org_id(provider: str) -> Optional[str]:
        """Get organization ID for a given provider."""
        org_mapping = {
            "OpenAI": "OPENAI_ORG_ID",
            "Anthropic": "ANTHROPIC_ORG_ID"
        }
        
        if provider not in org_mapping:
            return None
            
        org_id = os.getenv(org_mapping[provider])
        if not org_id:
            logger.debug(f"No organization ID found for {provider}")
        return org_id
        
    @classmethod
    def get_all_configs(cls) -> Dict[str, Dict[str, Optional[str]]]:
        """Get all configurations."""
        return {
            "OpenAI": {
                "api_key": cls.get_api_key("OpenAI"),
                "org_id": cls.get_org_id("OpenAI")
            },
            "Anthropic": {
                "api_key": cls.get_api_key("Anthropic"),
                "org_id": cls.get_org_id("Anthropic")
            },
            "Google": {
                "api_key": cls.get_api_key("Google")
            }
        }
