import streamlit as st
from utils.logging_config import setup_logging, get_logs
from ui.chat_ui import display_chat, init_chat_session
from ui.interactions import InteractionDisplayFactory
from ui.styles import get_all_styles
from core.workspace_manager import WorkspaceManager, SpaceType
from pathlib import Path
from core.core_agent import CoreAgent
from core.database.db_cleaner import clean_database
from core.database.models import init_database
from sqlalchemy.orm import sessionmaker
from ui.apps import display_apps
import yaml
from datetime import datetime

# Configurer le logging en premier
setup_logging()

def load_app_state() -> dict:
    """Charge l'état de l'application depuis le fichier de configuration."""
    config_file = Path(__file__).parent.parent / "config" / "app_state.yaml"
    default_state = {
        "workspace": "AGNOSTIC",
        "cache_enabled": True
    }
    if config_file.exists():
        with open(config_file, 'r', encoding='utf-8') as f:
            loaded_state = yaml.safe_load(f)
            return {**default_state, **loaded_state}  # Merge with defaults
    return default_state

def initialize_session_state():
    if 'workspace' not in st.session_state:
        # Charger le dernier espace utilisé
        app_state = load_app_state()
        st.session_state.workspace = SpaceType[app_state["workspace"]]
        st.session_state.cache_enabled = app_state["cache_enabled"]
        print(f"Initialized workspace to: {st.session_state.workspace}")  # Debug
    
    if 'workspace_manager' not in st.session_state:
        config_dir = Path(__file__).parent.parent / "config"
        st.session_state.workspace_manager = WorkspaceManager(config_dir)
        st.session_state.workspace_manager.set_current_space(st.session_state.workspace)
        print("Created new workspace manager")  # Debug
        print(f"Set current space to: {st.session_state.workspace}")  # Debug
    else:
        # Synchroniser l'espace actuel avec le workspace manager
        st.session_state.workspace_manager.set_current_space(st.session_state.workspace)
        print(f"Synchronized workspace manager to: {st.session_state.workspace}")  # Debug

def get_search_title(query: str) -> str:
    """Génère un titre court et explicite pour la recherche."""
    # Extraire les mots clés de la requête
    words = query.lower().split()
    if "ext:" in query:
        # Si la recherche contient une extension
        for word in words:
            if word.startswith("ext:"):
                return f"Fichiers {word[4:].upper()}"
    elif any(word.startswith("dm:") for word in words):
        # Si la recherche contient une date
        return "Fichiers récents"
    else:
        # Sinon, prendre les 3 premiers mots significatifs
        significant_words = [w for w in words if len(w) > 2 and not w.startswith(("le", "la", "les", "un", "une", "des"))]
        return " ".join(significant_words[:3]).title()

def display_logs():
    """Affiche les logs dans un onglet dédié."""
    # Barre de recherche et bouton de filtres sur la même ligne
    search_col, button_col = st.columns([5,1])
    
    with search_col:
        search_term = st.text_input("🔍 Rechercher dans les logs", "")
    
    with button_col:
        show_filters = st.button("⚙️", key="show_filters", use_container_width=True)
    
    # Options de filtrage dans un expander
    if show_filters:
        with st.expander("Filtres", expanded=True):
            level_filter = st.multiselect(
                "Niveau de log",
                ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
                default=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
            )
    else:
        level_filter = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
    
    # Récupérer et filtrer les logs
    logs = get_logs()
    if level_filter:
        logs = [log for log in logs if log['level'] in level_filter]
    if search_term:
        logs = [log for log in logs if search_term.lower() in log['message'].lower()]
    
    # Afficher les logs
    for log in reversed(logs):  # Du plus récent au plus ancien
        color = {
            'DEBUG': '#6c757d',
            'INFO': '#0d6efd',
            'WARNING': '#ffc107',
            'ERROR': '#dc3545',
            'CRITICAL': '#dc3545'
        }.get(log['level'], 'black')
        
        st.markdown(
            f'<div class="log-entry">'
            f'<span style="color:{color}">[{log["timestamp"]}] [{log["level"]}]</span> '
            f'{log["message"]}'
            f'</div>',
            unsafe_allow_html=True
        )

def display_interactions():
    """Affiche les interactions et résultats de recherche."""
    if "interactions" not in st.session_state:
        st.session_state.interactions = []
        
    if not st.session_state.interactions:
        st.info("Aucune interaction pour le moment. Les résultats de vos recherches apparaîtront ici.")
        return
    
    # Inverser l'ordre des interactions pour avoir les plus récentes en haut
    interactions = list(reversed(st.session_state.interactions))
    
    # Afficher chaque interaction
    for i, interaction in enumerate(interactions):
        # Récupérer le handler approprié
        handler = InteractionDisplayFactory.get_display_handler(interaction['type'])
        
        # Créer un expander avec le titre généré par le handler
        with st.expander(handler.get_expander_title(interaction), expanded=(i == 0)):
            handler.display(interaction)

def create_agent(agent_type: str) -> CoreAgent:
    """Create and initialize an agent with the current knowledge space."""
    agent = CoreAgent(
        agent_name=agent_type,
        system_instructions=f"You are a {agent_type} agent.",  # Instructions simples pour le moment
        workspace_manager=st.session_state.workspace_manager
    )
    return agent

def save_app_state(space_type: SpaceType):
    """Sauvegarde l'état de l'application."""
    config_file = Path(__file__).parent.parent / "config" / "app_state.yaml"
    current_state = load_app_state()  # Load existing state
    current_state["workspace"] = space_type.name
    with open(config_file, 'w', encoding='utf-8') as f:
        yaml.dump(current_state, f)

def sidebar():
    """Render the sidebar."""
    with st.sidebar:
        st.title("JarvisOne")
        
        # Knowledge Space Selection
        space_options = [
            ("Agnostic", SpaceType.AGNOSTIC),
            ("Servier", SpaceType.SERVIER),
            ("Personnel", SpaceType.PERSONAL),
            ("Coaching", SpaceType.COACHING),
            ("Développement", SpaceType.DEV)
        ]
        
        current_index = next(
            (i for i, (_, space_type) in enumerate(space_options) 
             if space_type == st.session_state.workspace), 
            0
        )
        
        selected_space = st.selectbox(
            "Espace de connaissances",
            options=[name for name, _ in space_options],
            index=current_index,
            key="workspace_select"
        )
        
        # Cache Control
        cache_enabled = st.toggle(
            "Activer le cache",
            value=st.session_state.cache_enabled,
            help="Active ou désactive le cache des requêtes",
            key="cache_toggle"
        )
        
        # Update cache state if changed
        if cache_enabled != st.session_state.cache_enabled:
            old_value = st.session_state.cache_enabled
            st.session_state.cache_enabled = cache_enabled
            current_state = load_app_state()
            current_state["cache_enabled"] = cache_enabled
            config_file = Path(__file__).parent.parent / "config" / "app_state.yaml"
            with open(config_file, 'w', encoding='utf-8') as f:
                yaml.dump(current_state, f)
            
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
        
        # Update knowledge space if changed
        selected_space_type = next(space_type for name, space_type in space_options if name == selected_space)
        if selected_space_type != st.session_state.workspace:
            old_space = st.session_state.workspace
            st.session_state.workspace = selected_space_type
            save_app_state(selected_space_type)
            
            # Log the configuration change
            if 'interactions' not in st.session_state:
                st.session_state.interactions = []
            st.session_state.interactions.append({
                'type': 'config_change',
                'config_type': 'Espace de connaissances',
                'old_value': old_space.name,
                'new_value': selected_space_type.name,
                'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })
            st.rerun()

# Configuration du style pour utiliser toute la largeur
st.set_page_config( 
    page_title="JarvisOne",
    page_icon="💬",
    layout="wide"
)

# Charger et appliquer les styles CSS
st.markdown(f"<style>{get_all_styles()}</style>", unsafe_allow_html=True)

# Initialiser la session state d'abord
initialize_session_state()

# Initialiser la session chat après l'initialisation du workspace
init_chat_session()

if __name__ == "__main__":
    # Créer deux colonnes principales avec ratio 2:1
    col_main, col_side = st.columns([3, 2])
    
    # Colonne principale pour le chat (2/3)
    with col_main:
        chat_tab, library_tab, apps_tab = st.tabs(["💬 Chat", "📚 Library", "🔧 Apps"])
        with chat_tab:
            st.markdown('<div id="chat-tab-content">', unsafe_allow_html=True)
            display_chat()  # Votre fonction qui génère le contenu du chat
            st.markdown('</div>', unsafe_allow_html=True)
        with library_tab:
            st.markdown("### Library")
            st.info("Library features coming soon!")
        with apps_tab:
            display_apps()

    # Colonne latérale pour les logs et les interactions (1/3)
    with col_side:
        tab_interactions, tab_logs, tab_params = st.tabs([
            "⚡ Interactions", 
            "📋 Logs",
            "⚙️ Parameters"
        ])
        
        with tab_interactions:
            display_interactions()
        
        with tab_logs:
            display_logs()
            
        with tab_params:
            from ui.parameters import display_parameters
            display_parameters()
            
    # Compter les erreurs en arrière-plan
    logs = get_logs()
    error_count = sum(1 for log in logs if log['level'] in ['ERROR', 'CRITICAL'])
    if error_count > 0:
        st.sidebar.error(f"{error_count} erreur(s) détectée(s). Consultez les logs pour plus de détails.")