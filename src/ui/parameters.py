"""Parameters UI components."""
import streamlit as st
import logging
from datetime import datetime
from pathlib import Path
import yaml
from core.llm_config import (
    LLM_PROVIDERS,
    get_provider_models,
    get_model_info,
    needs_api_key,
    get_default_model,
    refresh_ollama_models
)
from core.config_manager import ConfigManager

logger = logging.getLogger(__name__)

def on_provider_change():
    """Handle provider change."""
    provider = st.session_state.provider_select
    model = get_default_model(provider)
    logger.info(f"Provider changed to: {provider}, setting default model: {model}")
    
    # Save preferences
    ConfigManager.save_llm_preferences(provider, model)
    logger.info("Preferences saved after provider change")

def on_model_change():
    """Handle model change."""
    provider = st.session_state.provider_select
    model = st.session_state.model_select
    logger.info(f"Model changed to: {model} for provider: {provider}")
    
    # Save preferences
    ConfigManager.save_llm_preferences(provider, model)
    logger.info("Preferences saved after model change")

def display_parameters():
    """Display the parameters tab content."""
    
    # Cache Control
    st.subheader("Cache")
    cache_enabled = st.toggle(
        "Enable cache",
        value=st.session_state.cache_enabled,
        help="Enable or disable request caching",
        key="cache_toggle"
    )
    
    # Update cache state if changed
    if cache_enabled != st.session_state.cache_enabled:
        old_value = st.session_state.cache_enabled
        st.session_state.cache_enabled = cache_enabled
        
        # Update app state
        config = ConfigManager._load_config()
        config["app_state"]["cache_enabled"] = cache_enabled
        ConfigManager.save_config(config)
        
        logger.info(f"Cache {'enabled' if cache_enabled else 'disabled'}")
        
        # Log the configuration change
        if 'interactions' not in st.session_state:
            st.session_state.interactions = []
        st.session_state.interactions.append({
            'type': 'config_change',
            'config_type': 'Cache',
            'old_value': str(old_value),
            'new_value': str(cache_enabled),
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
        st.rerun()

    # Load initial preferences
    preferences = ConfigManager.load_llm_preferences()
    logger.debug(f"Loading preferences: {preferences}")
    
    # Initialize provider selection
    provider_options = list(LLM_PROVIDERS.keys())
    current_provider = preferences["provider"]
    current_index = provider_options.index(current_provider)
        
    logger.debug(f"Rendering provider select with current={current_provider}, index={current_index}")
    
    st.subheader("LLM Provider")
    
    st.markdown("Provider:", help="Select the LLM provider")
    selected_provider = st.selectbox(
        label="Provider Selection",
        options=provider_options,
        index=current_index,
        on_change=on_provider_change,
        key="provider_select",
        label_visibility="collapsed"
    )
    
    # Model selection based on provider
    models = get_provider_models(selected_provider)
    
    if not models and selected_provider == "Ollama (Local)":
        st.warning("No Ollama models found. Install models using 'ollama pull'")
        return
    
    # Initialize model selection
    current_model = preferences["model"]
    if current_model not in models:
        current_model = get_default_model(selected_provider)
        
    model_index = models.index(current_model) if current_model in models else 0
    
    logger.debug(f"Rendering model select with current={current_model}, index={model_index}")
    
    st.markdown("Model:", help="Select the model to use")
    selected_model = st.selectbox(
        label="Model Selection",
        options=models,
        index=model_index,
        on_change=on_model_change,
        key="model_select",
        label_visibility="collapsed"
    )
    
    # Show model information
    model_info = get_model_info(selected_provider, selected_model)
    st.subheader("Model information")
    st.markdown(f"**Name:** {model_info['name']}")
    st.markdown(f"**Description:** {model_info['description']}")
    st.markdown(f"**Context length:** {model_info['context_length']} tokens")

    #TODO: ajout les informations d'usage du model
    if "size" in model_info:
        st.markdown(f"**Size:** {model_info['size']}")
    
    # API Configuration
    if needs_api_key(selected_provider):
        
        # Get current API key from env
        current_key = ConfigManager.get_api_key(selected_provider)
        if current_key:
            st.success("✅ API key configured in .env")
        else:
            # Allow temporary key input
            st.warning("⚠️ API key not found in .env")
            api_key = st.text_input(
                f"{selected_provider} API key:",
                type="password",
                help=f"Enter your API key for {selected_provider} (temporary for this session)"
            )
            if api_key:
                st.session_state[f"{selected_provider.lower()}_api_key"] = api_key
                
        # Show organization ID if available
        org_id = ConfigManager.get_org_id(selected_provider)
        if org_id:
            st.info(f"🏢 Organization ID configured: {org_id}")
            

            
    # Log configuration changes
    if selected_provider != st.session_state.get("last_provider") or selected_model != st.session_state.get("last_model"):
        if 'interactions' not in st.session_state:
            st.session_state.interactions = []
            
        st.session_state.interactions.append({
            'type': 'config_change',
            'config_type': 'LLM Configuration',
            'old_value': f"{st.session_state.get('last_provider', 'Not set')} - {st.session_state.get('last_model', 'Not set')}",
            'new_value': f"{selected_provider} - {selected_model}",
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
        
        st.session_state.last_provider = selected_provider
        st.session_state.last_model = selected_model
