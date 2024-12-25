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
    """Gestionnaire de configuration pour les clés API."""
    
    CONFIG_FILE = "config/llm_preferences.json"
    
    @classmethod
    def _ensure_config_dir(cls):
        """Ensure the config directory exists."""
        config_dir = Path(cls.CONFIG_FILE).parent
        config_dir.mkdir(parents=True, exist_ok=True)
        
    @classmethod
    def save_llm_preferences(cls, provider: str, model: str) -> None:
        """Sauvegarde les préférences LLM."""
        cls._ensure_config_dir()
        
        try:
            preferences = {
                "provider": provider,
                "model": model
            }
            
            with open(cls.CONFIG_FILE, "w", encoding="utf-8") as f:
                json.dump(preferences, f, indent=2)
                
            logger.info(f"Préférences LLM sauvegardées: {preferences}")
        except Exception as e:
            logger.error(f"Erreur lors de la sauvegarde des préférences LLM: {e}")
            
    @classmethod
    def load_llm_preferences(cls) -> Dict[str, str]:
        """Charge les préférences LLM."""
        try:
            if os.path.exists(cls.CONFIG_FILE):
                with open(cls.CONFIG_FILE, "r", encoding="utf-8") as f:
                    preferences = json.load(f)
                logger.info(f"Préférences LLM chargées: {preferences}")
                return preferences
        except Exception as e:
            logger.error(f"Erreur lors du chargement des préférences LLM: {e}")
            
        # Default preferences
        return {
            "provider": "Ollama (Local)",
            "model": "mistral:latest"
        }
        
    @staticmethod
    def get_api_key(provider: str) -> Optional[str]:
        """Récupère la clé API pour un provider donné."""
        key_mapping = {
            "OpenAI": "OPENAI_API_KEY",
            "Anthropic": "ANTHROPIC_API_KEY",
            "Google": "GOOGLE_API_KEY"
        }
        
        if provider not in key_mapping:
            logger.warning(f"Provider {provider} non reconnu")
            return None
            
        key = os.getenv(key_mapping[provider])
        if not key:
            logger.warning(f"Clé API non trouvée pour {provider}")
        return key
        
    @staticmethod
    def get_org_id(provider: str) -> Optional[str]:
        """Récupère l'ID d'organisation pour un provider donné."""
        org_mapping = {
            "OpenAI": "OPENAI_ORG_ID",
            "Anthropic": "ANTHROPIC_ORG_ID"
        }
        
        if provider not in org_mapping:
            return None
            
        return os.getenv(org_mapping[provider])
        
    @staticmethod
    def get_all_configs() -> Dict[str, Dict[str, Optional[str]]]:
        """Récupère toutes les configurations."""
        return {
            "OpenAI": {
                "api_key": ConfigManager.get_api_key("OpenAI"),
                "org_id": ConfigManager.get_org_id("OpenAI")
            },
            "Anthropic": {
                "api_key": ConfigManager.get_api_key("Anthropic"),
                "org_id": ConfigManager.get_org_id("Anthropic")
            },
            "Google": {
                "api_key": ConfigManager.get_api_key("Google")
            }
        }
