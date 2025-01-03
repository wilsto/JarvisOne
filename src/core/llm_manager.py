"""Gestionnaire centralisé des modèles LLM."""

import logging
import streamlit as st
from typing import Optional
import requests
from openai import OpenAI
import anthropic
from google.generativeai import GenerativeModel
import google.generativeai as genai
from .llm_base import LLM
from .config_manager import ConfigManager
from .workspace_manager import WorkspaceManager
from pathlib import Path
from .llm_utils import (
    llm_cache, retry_on_error, API_KEYS,
    DEFAULT_PARAMS, OLLAMA_DEFAULT_MODELS
)
from . import llm_utils

# Configuration du logger
logger = logging.getLogger(__name__)

# Load timeout settings from config at module level
try:
    config = ConfigManager._load_config()
    DEFAULT_CONNECT_TIMEOUT = config.get('llm', {}).get('timeout', {}).get('connect', 10)
    DEFAULT_READ_TIMEOUT = config.get('llm', {}).get('timeout', {}).get('read', 300)
except Exception as e:
    logger.warning(f"Failed to load config, using default timeouts: {e}")
    DEFAULT_CONNECT_TIMEOUT = 10
    DEFAULT_READ_TIMEOUT = 300

def init_session_state():
    """Initialize session state with saved preferences."""
    if "llm_provider" not in st.session_state or "llm_model" not in st.session_state:
        preferences = ConfigManager.load_llm_preferences()
        config = ConfigManager._load_config()
        llm_config = config.get('llm', {})
        
        # Si pas de préférences ou préférences invalides, utiliser les valeurs de config
        if not preferences or "provider" not in preferences:
            preferences = {
                "provider": llm_config.get('default_provider', DEFAULT_PARAMS['provider']),
                "model": llm_config.get('default_model', DEFAULT_PARAMS['model'])
            }
            
        st.session_state.llm_provider = preferences["provider"]
        st.session_state.llm_model = preferences["model"]
        logger.info(f"Session state initialized with LLM: {preferences['provider']}/{preferences['model']}")

def update_llm_preferences():
    """Save current LLM preferences."""
    provider = st.session_state.llm_provider
    model = st.session_state.llm_model
    ConfigManager.save_llm_preferences(provider, model)
    logger.info(f"LLM preferences updated: provider={provider}, model={model}")

class OpenAILLM(LLM):
    def __init__(self, model: str):
        super().__init__()
        self.model = model
        if not API_KEYS['openai']:
            raise ValueError("OpenAI API key not found in environment")
        self.client = OpenAI(
            api_key=API_KEYS['openai'],
            timeout=DEFAULT_READ_TIMEOUT
        )
        
    @retry_on_error()
    def generate_response(self, prompt: str) -> str:
        # Check cache first
        cached = llm_cache.get(prompt, self.model)
        if cached:
            return cached
            
        try:
            messages = []
            if self.system_prompt:
                messages.append({"role": "system", "content": self.system_prompt})
            messages.append({"role": "user", "content": prompt})
            
            # Create a streaming completion
            stream = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=llm_utils.get_temperature(),
                max_tokens=DEFAULT_PARAMS['max_tokens'],
                presence_penalty=DEFAULT_PARAMS['presence_penalty'],
                frequency_penalty=DEFAULT_PARAMS['frequency_penalty'],
                stream=True
            )
            
            # Collect streamed response
            collected_messages = []
            for chunk in stream:
                if chunk.choices[0].delta.content is not None:
                    collected_messages.append(chunk.choices[0].delta.content)
                    
            full_response = "".join(collected_messages)
            
            # Cache the response
            llm_cache.set(prompt, self.model, full_response)
            return full_response
            
        except TimeoutError:
            logger.error(f"Timeout error while calling OpenAI API: Timeout={self.client.timeout}s")
            raise TimeoutError("Request to OpenAI API timed out. Please try again.")
        except Exception as e:
            logger.error(f"OpenAI API error: {str(e)}")
            raise

class AnthropicLLM(LLM):
    def __init__(self, model: str):
        super().__init__()
        self.model = model
        if not API_KEYS['anthropic']:
            raise ValueError("Anthropic API key not found in environment")
        self.client = anthropic.Client(
            api_key=API_KEYS['anthropic'],
            timeout=DEFAULT_READ_TIMEOUT
        )
        
    @retry_on_error()
    def generate_response(self, prompt: str) -> str:
        # Check cache first
        cached = llm_cache.get(prompt, self.model)
        if cached:
            return cached
            
        try:
            if self.system_prompt:
                full_prompt = f"\n\nSystem: {self.system_prompt}\n\nHuman: {prompt}\n\nAssistant:"
            else:
                full_prompt = f"\n\nHuman: {prompt}\n\nAssistant:"

            response = self.client.messages.create(
                model=self.model,
                max_tokens=DEFAULT_PARAMS['max_tokens'],
                temperature=llm_utils.get_temperature(),
                messages=[{"role": "user", "content": full_prompt}]
            )
            
            result = response.content[0].text
            
            # Cache the response
            llm_cache.set(prompt, self.model, result)
            return result
            
        except TimeoutError:
            logger.error(f"Timeout error while calling Anthropic API: Timeout={self.client.timeout}s")
            raise TimeoutError("Request to Anthropic API timed out. Please try again.")
        except Exception as e:
            logger.error(f"Anthropic API error: {str(e)}")
            raise

class GeminiLLM(LLM):
    def __init__(self, model: str):
        super().__init__()
        self.model = model
        if not API_KEYS['google']:
            raise ValueError("Google API key not found in environment")
        self.timeout = DEFAULT_READ_TIMEOUT
        genai.configure(
            api_key=API_KEYS['google']
        )
        self.client = GenerativeModel(model)
        
    @retry_on_error()
    def generate_response(self, prompt: str) -> str:
        # Check cache first
        cached = llm_cache.get(prompt, self.model)
        if cached:
            return cached
            
        try:
            if self.system_prompt:
                full_prompt = f"System: {self.system_prompt}\n\nUser: {prompt}"
            else:
                full_prompt = prompt

            response = self.client.generate_content(
                full_prompt,
                generation_config={
                    "temperature": llm_utils.get_temperature(),
                    "max_output_tokens": DEFAULT_PARAMS['max_tokens'],
                }
            )
            
            result = response.text
            
            # Cache the response
            llm_cache.set(prompt, self.model, result)
            return result
            
        except TimeoutError:
            logger.error(f"Timeout error while calling Google API: Timeout={self.timeout}s")
            raise TimeoutError("Request to Google API timed out. Please try again.")
        except Exception as e:
            logger.error(f"Google API error: {str(e)}")
            raise

class OllamaLLM(LLM):
    def __init__(self, model: str):
        super().__init__()
        self.model = model
        self.base_url = "http://localhost:11434/api"
        self.timeout = (DEFAULT_CONNECT_TIMEOUT, DEFAULT_READ_TIMEOUT)
        
    @retry_on_error()
    def generate_response(self, prompt: str) -> str:
        # Check cache first
        cached = llm_cache.get(prompt, self.model)
        if cached:
            return cached
            
        try:
            template = {
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": llm_utils.get_temperature(),
                    "num_predict": DEFAULT_PARAMS['max_tokens'],
                }
            }
            
            if self.system_prompt:
                template["system"] = self.system_prompt

            response = requests.post(
                f"{self.base_url}/generate", 
                json=template,
                timeout=self.timeout
            )
            response.raise_for_status()
            
            result = response.json()["response"]
            
            # Cache the response
            llm_cache.set(prompt, self.model, result)
            return result
            
        except requests.Timeout:
            logger.error(f"Timeout error while calling Ollama API: Connection timeout={self.timeout[0]}s, Read timeout={self.timeout[1]}s")
            raise TimeoutError("Request to Ollama API timed out. Please try again or check if the server is responsive.")
        except requests.RequestException as e:
            logger.error(f"Ollama API request error: {str(e)}")
            raise

def _fallback_to_ollama(system_prompt: Optional[str] = None) -> LLM:
    """Fallback vers Ollama en cas d'erreur."""
    st.session_state.llm_provider = "Ollama (Local)"
    st.session_state.llm_model = "mistral:latest"
    llm = OllamaLLM("mistral:latest")
    if system_prompt:
        llm.system_prompt = system_prompt
    return llm

def get_llm_model() -> LLM:
    """
    Récupère une instance du modèle LLM configuré.
    """
    # Get provider and model from session state
    if not hasattr(st.session_state, 'llm_provider') or not st.session_state.llm_provider:
        # Load preferences
        preferences = ConfigManager.load_llm_preferences()
        if preferences:
            logger.info(f"Loaded LLM preferences: {preferences}")
            # Update session state with loaded preferences
            st.session_state.llm_provider = preferences["provider"]
            st.session_state.llm_model = preferences["model"]
        else:
            # Use default provider and model
            provider = DEFAULT_PARAMS['provider']
            model = DEFAULT_PARAMS['model']
            st.session_state.llm_provider = provider
            st.session_state.llm_model = model
            logger.info(f"Using default LLM: {provider}/{model}")
    
    # Get workspace system prompt if available
    if hasattr(st.session_state, 'workspace_manager'):
        workspace_manager = st.session_state.workspace_manager
        system_prompt = workspace_manager.get_current_context_prompt()
    else:
        workspace_manager = WorkspaceManager(Path("config"))
        system_prompt = workspace_manager.get_current_context_prompt() 
    
    # Initialize the model
    provider = st.session_state.llm_provider
    model = st.session_state.llm_model
    
    try:
        if provider == "OpenAI":
            llm = OpenAILLM(model or DEFAULT_PARAMS['default_models']['OpenAI'])
        elif provider == "Anthropic":
            llm = AnthropicLLM(model or DEFAULT_PARAMS['default_models']['Anthropic'])
        elif provider == "Google":
            llm = GeminiLLM(model or DEFAULT_PARAMS['default_models']['Google'])
        elif provider == "Ollama (Local)":
            llm = OllamaLLM(model or DEFAULT_PARAMS['default_models']['Ollama (Local)'])
        else:
            logger.error(f"Unknown provider: {provider}")
            raise ValueError(f"Unknown provider: {provider}")
        
        # Set the system prompt if available
        if system_prompt:
            llm.system_prompt = system_prompt
        
        return llm
        
    except ValueError as e:
        if "Unknown provider" in str(e):
            # Propager l'erreur de provider invalide
            raise
        else:
            # Pour les autres ValueError (comme API key invalide), faire un fallback
            logger.error(f"Error initializing {provider} LLM: {e}")
            return _fallback_to_ollama(system_prompt)
    except Exception as e:
        logger.error(f"Error initializing {provider} LLM: {e}")
        return _fallback_to_ollama(system_prompt)
