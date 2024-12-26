import streamlit as st
from utils.logging_config import setup_logging, get_logs
from ui.chat_ui import display_chat, init_chat_session
from ui.interactions import InteractionDisplayFactory
import os
import pyperclip
from features.agents.file_search_agent import launch_everything_gui

# Configurer le logging en premier
setup_logging()

# Configuration du style pour utiliser toute la largeur
st.set_page_config(layout="wide")

# CSS personnalisé pour maximiser la largeur des colonnes
st.markdown("""
<style>
    /* Configuration générale */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 0rem;
        padding-left: 2rem;
        padding-right: 2rem;
    }
    
    /* Style des colonnes */
    [data-testid="column"] {
        padding: 0 2rem;
        margin-top: 1rem;
    }
    [data-testid="column"]:first-child {
        padding-left: 0;
    }
    [data-testid="column"]:last-child {
        padding-right: 0;
    }
    
    /* Style des onglets */
    .stTabs {
        background-color: #f8f9fa;
        padding: 0.5rem;
        border-radius: 0.5rem;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: white;
        padding: 0.5rem;
        border-radius: 0.5rem;
    }
    .stTabs [data-baseweb="tab"] {
        height: 2.5rem;
        white-space: nowrap;
        font-size: 0.9rem;
        color: #0f1116;
        border-radius: 0.3rem;
        background-color: #f0f2f6;
        border: none;
        padding: 0 2rem;
        min-width: 120px;
        text-align: center;
    }
    .stTabs [aria-selected="true"] {
        background-color: #e0e2e6;
        font-weight: bold;
    }
    
    /* Style des logs */
    .log-entry {
        font-family: 'Consolas', monospace;
        font-size: 0.8rem;
        line-height: 1.2;
        padding: 0.2rem 0;
        border-bottom: 1px solid #f0f0f0;
    }
    
    /* Headers des sections */
    .section-header {
        font-size: 1.5rem;
        font-weight: 600;
        margin-bottom: 1rem;
        color: #0f1116;
    }

    /* Style du bouton de filtre */
    .filter-button {
        float: right;
        margin-top: -48px;
        margin-right: 10px;
    }
    
    /* Style de la barre de recherche */
    .search-container {
        margin-right: 140px;
    }
</style>
""", unsafe_allow_html=True)

# Initialiser la session si nécessaire
init_chat_session()

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
    
    # Style CSS pour les résultats
    st.markdown("""
        <style>
        .result-row {
            display: flex;
            align-items: center;
            padding: 4px 0;
            margin: 2px 0;
        }
        .result-number {
            min-width: 40px;
            font-weight: bold;
            color: #555;
        }
        .result-content {
            flex-grow: 1;
            margin-left: 10px;
        }
        .file-name {
            font-weight: bold;
            font-size: 0.9em;
            color: #1f1f1f;
        }
        .file-path {
            color: #666;
            font-size: 0.85em;
        }
        .remaining-count {
            color: #666;
            font-style: italic;
            text-align: center;
            padding: 10px;
            background: #f0f2f6;
            border-radius: 4px;
            margin: 10px 0;
        }
        .interaction-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 10px;
            background: #f8f9fa;
            border-radius: 4px;
            margin-bottom: 10px;
        }
        .interaction-time {
            color: #666;
            font-size: 0.9em;
        }
        .search-info {
            background-color: #f8f9fa;
            padding: 10px;
            border-radius: 4px;
            margin: 10px 0;
        }
        :target {
            scroll-margin-top: 60px;
            animation: highlight 2s ease-out;
        }
        @keyframes highlight {
            0% { background-color: #fff3cd; }
            100% { background-color: transparent; }
        }
        </style>
    """, unsafe_allow_html=True)
    
    # Afficher chaque interaction
    for i, interaction in enumerate(interactions):
        # Récupérer le handler approprié
        handler = InteractionDisplayFactory.get_display_handler(interaction['type'])
        
        # Créer un expander avec le titre généré par le handler
        with st.expander(handler.get_expander_title(interaction), expanded=(i == 0)):
            handler.display(interaction)

def display_reasoning():
    """Fonction obsolète maintenue pour compatibilité."""
    display_interactions()

if __name__ == "__main__":
    # Créer deux colonnes principales avec ratio 2:1
    col_main, col_side = st.columns([3, 2])
    
    # Colonne principale pour le chat (2/3)
    with col_main:
        chat_tab = st.tabs(["💬 Chat"])[0]
        with chat_tab:
            display_chat()
    
    # Colonne latérale pour les logs et les interactions (1/3)
    with col_side:
        tab_interactions, tab_logs = st.tabs(["⚡ Interactions", "📋 Logs"])
        
        with tab_interactions:
            display_interactions()
        
        with tab_logs:
            display_logs()
            
    # Compter les erreurs en arrière-plan
    logs = get_logs()
    error_count = sum(1 for log in logs if log['level'] in ['ERROR', 'CRITICAL'])
    if error_count > 0:
        st.sidebar.error(f"{error_count} erreur(s) détectée(s). Consultez les logs pour plus de détails.")