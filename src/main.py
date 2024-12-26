import streamlit as st
from utils.logging_config import setup_logging, get_logs
from ui.chat_ui import display_chat, init_chat_session
from ui.interactions import InteractionDisplayFactory
from ui.styles import get_all_styles
import os
import pyperclip
from features.agents.file_search_agent import launch_everything_gui

# Configurer le logging en premier
setup_logging()

# Configuration du style pour utiliser toute la largeur
st.set_page_config(layout="wide")

# Charger et appliquer les styles CSS
st.markdown(f"<style>{get_all_styles()}</style>", unsafe_allow_html=True)

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
    
    # Afficher chaque interaction
    for i, interaction in enumerate(interactions):
        # Récupérer le handler approprié
        handler = InteractionDisplayFactory.get_display_handler(interaction['type'])
        
        # Créer un expander avec le titre généré par le handler
        with st.expander(handler.get_expander_title(interaction), expanded=(i == 0)):
            handler.display(interaction)

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