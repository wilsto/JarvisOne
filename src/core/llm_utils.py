"""Utilities for LLM providers."""

import os
import json
import time
import logging
from functools import wraps
from typing import Any, Dict, Optional
from pathlib import Path
import hashlib
from dotenv import load_dotenv
import yaml
from core.config_manager import ConfigManager

# Load environment variables
load_dotenv()

# Load configuration
config = ConfigManager._load_config()
app_state = config.get("app_state", {})

# Configuration du logger
logger = logging.getLogger(__name__)

class LLMCache:
    """Simple cache for LLM responses."""
    
    def __init__(self, cache_dir: str = ".cache/llm"):
        self.cache_dir = Path(cache_dir)
        self.cache_enabled = app_state.get('cache_enabled', True)
        if self.cache_enabled:
            self.cache_dir.mkdir(parents=True, exist_ok=True)
        
    def _get_cache_key(self, prompt: str, model: str) -> str:
        """Generate a cache key from prompt and model."""
        content = f"{prompt}:{model}"
        return hashlib.sha256(content.encode()).hexdigest()
        
    def get(self, prompt: str, model: str) -> Optional[str]:
        """Get cached response if exists."""
        if not self.cache_enabled:
            return None
            
        cache_key = self._get_cache_key(prompt, model)
        cache_file = self.cache_dir / f"{cache_key}.json"
        
        if cache_file.exists():
            try:
                with open(cache_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # Check if cache is still valid (24h)
                    if time.time() - data['timestamp'] < 86400:
                        logger.debug(f"Cache hit for prompt: {prompt[:50]}...")
                        return data['response']
            except Exception as e:
                logger.warning(f"Error reading cache: {str(e)}")
        return None
        
    def set(self, prompt: str, model: str, response: str):
        """Cache a response."""
        if not self.cache_enabled:
            return
            
        cache_key = self._get_cache_key(prompt, model)
        cache_file = self.cache_dir / f"{cache_key}.json"
        
        try:
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump({
                    'prompt': prompt,
                    'model': model,
                    'response': response,
                    'timestamp': time.time()
                }, f, ensure_ascii=False, indent=2)
            logger.debug(f"Cached response for prompt: {prompt[:50]}...")
        except Exception as e:
            logger.warning(f"Error writing cache: {str(e)}")

def retry_on_error(max_retries: int = 3, delay: float = 1.0):
    """Decorator for retrying failed API calls."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_error = None
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_error = e
                    if attempt < max_retries - 1:
                        sleep_time = delay * (2 ** attempt)  # Exponential backoff
                        logger.warning(f"Attempt {attempt + 1} failed: {str(e)}. Retrying in {sleep_time}s...")
                        time.sleep(sleep_time)
            logger.error(f"All {max_retries} attempts failed. Last error: {str(last_error)}")
            raise last_error
        return wrapper
    return decorator

# Default parameters
DEFAULT_PARAMS = {
    'provider': config.get('llm', {}).get('default_provider', 'Ollama (Local)'),
    'model': config.get('llm', {}).get('default_model', 'mistral:latest'),
    'max_tokens': 2000,
    'top_p': 0.95,
    'frequency_penalty': 0.0,
    'presence_penalty': 0.0,
}

# Get dynamic temperature based on creativity level
def get_temperature() -> float:
    """Get the current temperature setting based on creativity level."""
    from core.prompts.generic_prompts import get_llm_temperature
    return get_llm_temperature()

# API Keys from environment
API_KEYS = {
    'openai': os.getenv('OPENAI_API_KEY'),
    'anthropic': os.getenv('ANTHROPIC_API_KEY'),
    'google': os.getenv('GOOGLE_API_KEY')
}

# Ollama default models
OLLAMA_DEFAULT_MODELS = [
    "mistral:latest"
]

# Initialize global cache
llm_cache = LLMCache()
