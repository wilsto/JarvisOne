import streamlit as st
import logging
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

def render_sidebar():
    """Render the sidebar with LLM configuration options."""
    with st.sidebar:
        st.title("JarvisOne")
        
        st.markdown("## Configuration LLM")
        
        # Load initial preferences
        preferences = ConfigManager.load_llm_preferences()
        logger.info(f"Loading preferences: {preferences}")
        
        # Initialize provider selection
        provider_options = list(LLM_PROVIDERS.keys())
        current_provider = preferences["provider"]
        current_index = provider_options.index(current_provider)
            
        logger.info(f"Rendering provider select with current={current_provider}, index={current_index}")
        
        # LLM Provider selection and refresh button on same line
        col1, col2 = st.columns([0.8, 0.2])
        with col1:
            selected_provider = st.selectbox(
                "Provider LLM:",
                options=provider_options,
                index=current_index,
                label_visibility="collapsed",
                on_change=on_provider_change,
                key="provider_select"
            )
        
        # Refresh button for Ollama models
        with col2:
            if selected_provider == "Ollama (Local)":
                if st.button("🔄", help="Rafraîchir les modèles"):
                    refresh_ollama_models()
                    st.rerun()
        
        # Model selection based on provider
        models = get_provider_models(selected_provider)
        
        if not models and selected_provider == "Ollama (Local)":
            st.warning("Aucun modèle Ollama trouvé. Installez des modèles avec 'ollama pull'")
            return
        
        # Initialize model selection
        current_model = preferences["model"]
        if current_model not in models:
            current_model = get_default_model(selected_provider)
            
        model_index = models.index(current_model) if current_model in models else 0
        
        logger.info(f"Rendering model select with current={current_model}, index={model_index}")
        selected_model = st.selectbox(
            "Modèle:",
            options=models,
            index=model_index,
            on_change=on_model_change,
            key="model_select"
        )
        
        # Show model information
        model_info = get_model_info(selected_provider, selected_model)
        st.markdown("### Information Modèle")
        st.markdown(f"**Nom:** {model_info['name']}")
        st.markdown(f"**Description:** {model_info['description']}")
        st.markdown(f"**Contexte:** {model_info['context_length']} tokens")
        if "size" in model_info:
            st.markdown(f"**Taille:** {model_info['size']}")
        
        # API Key management
        if needs_api_key(selected_provider):
            st.markdown("### Configuration API")
            
            # Get current API key from env
            current_key = ConfigManager.get_api_key(selected_provider)
            if current_key:
                st.success("✅ Clé API configurée dans .env")
                if st.button("❌ Supprimer la clé de la session"):
                    st.session_state.pop(f"{selected_provider.lower()}_api_key", None)
            else:
                # Allow temporary key input
                st.warning("⚠️ Clé API non trouvée dans .env")
                api_key = st.text_input(
                    f"Clé API {selected_provider}:",
                    type="password",
                    help=f"Entrez votre clé API pour {selected_provider} (temporaire pour cette session)"
                )
                if api_key:
                    st.session_state[f"{selected_provider.lower()}_api_key"] = api_key
                    
            # Show organization ID if available
            org_id = ConfigManager.get_org_id(selected_provider)
            if org_id:
                st.info(f"🏢 ID Organisation configuré: {org_id}")
        
        # Bouton de réinitialisation
        st.markdown("---")
        if st.button("🔄 Réinitialiser la conversation"):
            # Réinitialiser l'historique des messages
            if "messages" in st.session_state:
                del st.session_state.messages
            st.rerun()
