"""Gestionnaire centralisé des modèles LLM."""

import logging
import streamlit as st
from phi.model.openai import OpenAIChat
from phi.model.anthropic import Claude
from phi.model.ollama import Ollama
from phi.model.google import Gemini
from .config_manager import ConfigManager

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

def get_llm_model():
    """Get the appropriate LLM model based on configuration."""
    # Initialize session state if needed
    init_session_state()
    
    # Log current state
    logger.info("Current session state:")
    for key, value in st.session_state.items():
        logger.info(f"  {key}: {value}")
    
    provider = st.session_state.llm_provider
    model = st.session_state.llm_model
    
    try:
        # Tenter d'initialiser le modèle configuré
        llm = _initialize_model(provider, model)
        update_llm_preferences()  # Sauvegarder uniquement si succès
        return llm
    except Exception as e:
        logger.error(f"Error initializing {provider} model {model}: {str(e)}")
        # Tenter le fallback vers Ollama
        try:
            logger.info("Attempting fallback to Ollama (Local)/mistral:latest")
            st.session_state.llm_provider = "Ollama (Local)"
            st.session_state.llm_model = "mistral:latest"
            return _initialize_model("Ollama (Local)", "mistral:latest")
        except Exception as fallback_error:
            logger.error(f"Fallback also failed: {str(fallback_error)}")
            raise RuntimeError("Could not initialize any LLM model")

def _initialize_model(provider: str, model: str):
    """Initialize a specific LLM model."""
    if provider == "OpenAI":
        return OpenAIChat(
            model=model or "gpt-4o-mini",
            temperature=0.7,
            max_tokens=2000,
            streaming=True
        )
    elif provider == "Anthropic":
        return Claude(
            model=model or "claude-2",
            temperature=0.7,
            max_tokens=2000
        )
    elif provider == "Google":
        return Gemini(
            model=model or "gemini-pro",
            temperature=0.7,
            max_tokens=2000
        )
    elif provider == "Ollama (Local)":
        return Ollama(
            model=model or "mistral:latest",
            temperature=0.7,
            max_tokens=2000
        )
    else:
        raise ValueError(f"Unknown provider: {provider}")
