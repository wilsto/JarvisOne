"""Configuration manager for environment variables."""

import os
import json
from typing import Dict, Optional, Any
from dotenv import load_dotenv
import logging
from pathlib import Path
import yaml

logger = logging.getLogger(__name__)

def configure_logging(level_str: str = "INFO"):
    """Configure logging based on config file."""
    level = getattr(logging, level_str.upper(), logging.INFO)
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(levelname)s - %(name)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

# Charger les variables d'environnement depuis .env
load_dotenv()

# Get the config directory relative to this file
CONFIG_DIR = Path(__file__).parent.parent.parent / "config"
CONFIG_FILE = CONFIG_DIR / "config.yaml"

class ConfigManager:
    """Configuration manager for application settings."""
    
    CONFIG_FILE = str(CONFIG_FILE)
    _config_cache = None  # Add config cache
    
    @classmethod
    def _ensure_config_dir(cls):
        """Ensure the config directory exists."""
        config_dir = Path(cls.CONFIG_FILE).parent
        config_dir.mkdir(parents=True, exist_ok=True)
    
    @classmethod
    def _load_config(cls) -> Dict:
        """Load the unified configuration file."""
        # Return cached config if available
        if cls._config_cache is not None:
            return cls._config_cache
            
        try:
            if os.path.exists(cls.CONFIG_FILE):
                with open(cls.CONFIG_FILE, "r", encoding="utf-8") as f:
                    config = yaml.safe_load(f)
                    # Don't cache sensitive data
                    if isinstance(config, dict):
                        # Remove API keys if they were accidentally saved
                        for provider in ['Anthropic', 'OpenAI', 'Google']:
                            if provider in config:
                                del config[provider]
                    cls._config_cache = config
                    return config
        except Exception as e:
            logger.error(f"Error loading configuration: {e}")
        return {}
        
    @classmethod
    def save_config(cls, config: Dict) -> None:
        """Save the unified configuration."""
        cls._ensure_config_dir()
        try:
            # Remove any sensitive data before saving
            clean_config = config.copy()
            for provider in ['Anthropic', 'OpenAI', 'Google']:
                if provider in clean_config:
                    del clean_config[provider]
            
            # Preserve existing structure if possible
            existing_config = {}
            if os.path.exists(cls.CONFIG_FILE):
                with open(cls.CONFIG_FILE, "r", encoding="utf-8") as f:
                    existing_config = yaml.safe_load(f) or {}
            
            # Update only changed sections
            def deep_update(d, u):
                for k, v in u.items():
                    if isinstance(v, dict) and k in d and isinstance(d[k], dict):
                        deep_update(d[k], v)
                    else:
                        d[k] = v
            
            deep_update(existing_config, clean_config)
            
            # Save with structure preservation
            with open(cls.CONFIG_FILE, "w", encoding="utf-8") as f:
                yaml.dump(existing_config, f, indent=2, sort_keys=False, default_flow_style=False)
            
            logger.info("Configuration saved successfully")
            cls._config_cache = clean_config  # Update cache with clean config
        except Exception as e:
            logger.error(f"Error saving configuration: {e}")
    
    @classmethod
    def initialize_logging(cls):
        """Initialize logging configuration."""
        config = cls._load_config()
        if "logging" in config and "level" in config["logging"]:
            configure_logging(config["logging"]["level"])
    
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
        """Save LLM preferences to unified config while preserving other LLM settings.
        
        Args:
            provider: The LLM provider name
            model: The model name for the provider
        """
        config = cls._load_config()
        # Preserve existing LLM config
        llm_config = config.get("llm", {})
        # Only update provider and model
        llm_config.update({
            "provider": provider,
            "model": model
        })
        config["llm"] = llm_config
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
    def get_all_configs(cls) -> Dict[str, Any]:
        """Get all configurations including app settings and API keys."""
        # Load the full YAML config
        config = cls._load_config()
        
        # Add API configurations
        config.update({
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
        })
        
        return config

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

    @classmethod
    def load_workspace_preferences(cls) -> Dict:
        """Load workspace preferences from unified config."""
        config = cls._load_config()
        # Try to get from app_state first
        if 'app_state' in config and 'workspace' in config['app_state']:
            return {
                'workspace': config['app_state']['workspace'],
                'role': config['app_state'].get('role')
            }
        # Fallback to legacy workspace section for backward compatibility
        elif 'workspace' in config:
            workspace_config = config['workspace']
            # Migrate old config to new format
            cls.save_workspace_preferences(
                workspace_config.get('current', 'AGNOSTIC'),
                workspace_config.get('role')
            )
            return {
                'workspace': workspace_config.get('current'),
                'role': workspace_config.get('role')
            }
        return {
            'workspace': 'AGNOSTIC',
            'role': None
        }

    @classmethod
    def save_workspace_preferences(cls, workspace: str, role: str = None) -> None:
        """Save workspace preferences to unified config."""
        config = cls._load_config()
        if 'app_state' not in config:
            config['app_state'] = {}
        
        # Update app_state
        config['app_state']['workspace'] = workspace
        if role is not None:
            config['app_state']['role'] = role
        elif 'role' in config['app_state']:
            # Remove role if None and exists
            del config['app_state']['role']
        
        # Remove legacy workspace section if it exists
        if 'workspace' in config:
            del config['workspace']
        
        cls.save_config(config)
