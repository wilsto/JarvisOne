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
from .llm_utils import (
    llm_cache, retry_on_error, API_KEYS,
    DEFAULT_PARAMS, OLLAMA_DEFAULT_MODELS
)

# Configuration du logger
logger = logging.getLogger(__name__)

def init_session_state():
    """Initialize session state with saved preferences."""
    if "llm_provider" not in st.session_state or "llm_model" not in st.session_state:
        preferences = ConfigManager.load_llm_preferences()
        # Si pas de préférences ou préférences invalides, utiliser les valeurs par défaut
        if not preferences or "provider" not in preferences:
            preferences = {
                "provider": "Ollama (Local)",
                "model": "mistral:latest"
            }
            logger.info("Using default LLM configuration: Ollama (Local)/mistral:latest")
        
        st.session_state.llm_provider = preferences["provider"]
        st.session_state.llm_model = preferences["model"]
        logger.info(f"Session state initialized with preferences: {preferences}")

def update_llm_preferences():
    """Save current LLM preferences."""
    provider = st.session_state.llm_provider
    model = st.session_state.llm_model
    ConfigManager.save_llm_preferences(provider, model)
    logger.info(f"LLM preferences updated: provider={provider}, model={model}")

class OpenAILLM(LLM):
    def __init__(self, model: str):
        self.model = model
        if not API_KEYS['openai']:
            raise ValueError("OpenAI API key not found in environment")
        self.client = OpenAI(api_key=API_KEYS['openai'])
        
    @retry_on_error()
    def generate_response(self, prompt: str) -> str:
        # Check cache first
        cached = llm_cache.get(prompt, self.model)
        if cached:
            return cached
            
        try:
            # Create a streaming completion
            stream = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=DEFAULT_PARAMS['temperature'],
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
            
        except Exception as e:
            logger.error(f"OpenAI API error: {str(e)}")
            raise

class AnthropicLLM(LLM):
    def __init__(self, model: str):
        self.model = model
        if not API_KEYS['anthropic']:
            raise ValueError("Anthropic API key not found in environment")
        self.client = anthropic.Client(api_key=API_KEYS['anthropic'])
        
    @retry_on_error()
    def generate_response(self, prompt: str) -> str:
        # Check cache first
        cached = llm_cache.get(prompt, self.model)
        if cached:
            return cached
            
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=DEFAULT_PARAMS['max_tokens'],
                temperature=DEFAULT_PARAMS['temperature'],
                messages=[{"role": "user", "content": prompt}]
            )
            
            result = response.content[0].text
            
            # Cache the response
            llm_cache.set(prompt, self.model, result)
            return result
            
        except Exception as e:
            logger.error(f"Anthropic API error: {str(e)}")
            raise

class GeminiLLM(LLM):
    def __init__(self, model: str):
        self.model = model
        if not API_KEYS['google']:
            raise ValueError("Google API key not found in environment")
        genai.configure(api_key=API_KEYS['google'])
        self.client = GenerativeModel(model)
        
    @retry_on_error()
    def generate_response(self, prompt: str) -> str:
        # Check cache first
        cached = llm_cache.get(prompt, self.model)
        if cached:
            return cached
            
        try:
            response = self.client.generate_content(
                prompt,
                generation_config={
                    "temperature": DEFAULT_PARAMS['temperature'],
                    "max_output_tokens": DEFAULT_PARAMS['max_tokens'],
                }
            )
            
            result = response.text
            
            # Cache the response
            llm_cache.set(prompt, self.model, result)
            return result
            
        except Exception as e:
            logger.error(f"Google API error: {str(e)}")
            raise

class OllamaLLM(LLM):
    def __init__(self, model: str):
        self.model = model
        self.base_url = "http://localhost:11434/api"
        
    @retry_on_error()
    def generate_response(self, prompt: str) -> str:
        # Check cache first
        cached = llm_cache.get(prompt, self.model)
        if cached:
            return cached
            
        try:
            response = requests.post(
                f"{self.base_url}/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": DEFAULT_PARAMS['temperature'],
                        "num_predict": DEFAULT_PARAMS['max_tokens'],
                    }
                }
            )
            response.raise_for_status()
            
            result = response.json()["response"]
            
            # Cache the response
            llm_cache.set(prompt, self.model, result)
            return result
            
        except Exception as e:
            logger.error(f"Ollama API error: {str(e)}")
            raise

def get_llm_model() -> LLM:
    """Get the appropriate LLM model based on configuration."""
    try:
        # Utiliser les préférences du session state
        if "llm_provider" in st.session_state and "llm_model" in st.session_state:
            provider = st.session_state.llm_provider
            model = st.session_state.llm_model
            logger.info(f"Using LLM from session state: {provider}/{model}")
        else:
            # Charger depuis le fichier si pas dans le session state
            preferences = ConfigManager.load_llm_preferences()
            if preferences and "provider" in preferences:
                provider = preferences["provider"]
                model = preferences["model"]
                logger.info(f"Using LLM from preferences file: {provider}/{model}")
            else:
                # Utiliser les valeurs par défaut
                provider = "Ollama (Local)"
                model = "mistral:latest"
                logger.info(f"Using default LLM: {provider}/{model}")
        
        return _initialize_model(provider, model)
        
    except Exception as e:
        logger.error(f"Error getting LLM model: {str(e)}")
        # Fallback to Ollama
        logger.info("Falling back to Ollama/mistral")
        return _initialize_model("Ollama (Local)", "mistral:latest")

def _initialize_model(provider: str, model: str) -> LLM:
    """Initialize a specific LLM model."""
    if provider == "OpenAI":
        return OpenAILLM(model or "gpt-4o-mini")
    elif provider == "Anthropic":
        return AnthropicLLM(model or "claude-2")
    elif provider == "Google":
        return GeminiLLM(model or "gemini-pro")
    elif provider == "Ollama (Local)":
        return OllamaLLM(model or "mistral:latest")
    else:
        raise ValueError(f"Unknown provider: {provider}")
