"""Configuration manager for environment variables."""

import os
import json
from typing import Dict, Optional, Any
from dotenv import load_dotenv
import logging
from pathlib import Path
import yaml

logger = logging.getLogger(__name__)

# Charger les variables d'environnement depuis .env
load_dotenv()

class ConfigManager:
    """Configuration manager for application settings."""
    
    CONFIG_FILE = "config/config.yaml"
    
    @classmethod
    def _ensure_config_dir(cls):
        """Ensure the config directory exists."""
        config_dir = Path(cls.CONFIG_FILE).parent
        config_dir.mkdir(parents=True, exist_ok=True)
    
    @classmethod
    def _load_config(cls) -> Dict:
        """Load the unified configuration file."""
        try:
            if os.path.exists(cls.CONFIG_FILE):
                with open(cls.CONFIG_FILE, "r", encoding="utf-8") as f:
                    config = yaml.safe_load(f)
                logger.info(f"Configuration loaded: {config}")
                return config
        except Exception as e:
            logger.error(f"Error loading configuration: {e}")
        
        # Default configuration
        return {
            "llm": {
                "provider": "Ollama (Local)",
                "model": "mistral:latest"
            },
            "app_state": {
                "workspace": "AGNOSTIC",
                "cache_enabled": True
            }
        }
    
    @classmethod
    def save_config(cls, config: Dict) -> None:
        """Save the unified configuration."""
        cls._ensure_config_dir()
        try:
            with open(cls.CONFIG_FILE, "w", encoding="utf-8") as f:
                yaml.dump(config, f, indent=2)
            logger.info(f"Configuration saved: {config}")
        except Exception as e:
            logger.error(f"Error saving configuration: {e}")
    
    @classmethod
    def load_llm_preferences(cls) -> Dict[str, str]:
        """Load LLM preferences from unified config."""
        config = cls._load_config()
        return config.get("llm", {
            "provider": "Ollama (Local)",
            "model": "mistral:latest"
        })
    
    @classmethod
    def save_llm_preferences(cls, provider: str, model: str) -> None:
        """Save LLM preferences to unified config."""
        config = cls._load_config()
        config["llm"] = {
            "provider": provider,
            "model": model
        }
        cls.save_config(config)

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

    @classmethod
    def get_tool_config(cls, tool_name: str, config_key: Optional[str] = None) -> Any:
        """Get configuration for a specific tool.
        
        Args:
            tool_name: Name of the tool (e.g., 'everything')
            config_key: Specific configuration key (e.g., 'cli_path')
        
        Returns:
            Tool configuration value or entire tool config if config_key is None
        """
        config = cls._load_config()
        tool_config = config.get("tools", {}).get(tool_name, {})
        
        if config_key is None:
            return tool_config
        return tool_config.get(config_key)

    @classmethod
    def get_ui_config(cls) -> Dict:
        """Get UI configuration."""
        config = cls._load_config()
        return config.get("ui", {
            "theme": "default"
        })
    
    @classmethod
    def get_logging_config(cls) -> Dict:
        """Get logging configuration."""
        config = cls._load_config()
        return config.get("logging", {
            "level": "INFO"
        })
