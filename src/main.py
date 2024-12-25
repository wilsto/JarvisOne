import streamlit as st
from utils.logging_config import setup_logging, get_logs
from ui.chat_ui import display_chat, init_chat_session

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

def display_logs():
    """Affiche les logs dans un onglet dédié."""
    # Barre de recherche et bouton de filtres sur la même ligne
    search_col, button_col = st.columns([5, 1])
    
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

def display_reasoning():
    """Affiche le raisonnement de l'agent (à implémenter)."""
    st.info("Le raisonnement de l'agent sera affiché ici prochainement.")

if __name__ == "__main__":
    # Créer deux colonnes principales avec ratio 2:1
    col_main, col_side = st.columns([2, 1])
    
    # Colonne principale pour le chat (2/3)
    with col_main:
        chat_tab = st.tabs(["💬 Chat"])[0]
        with chat_tab:
            display_chat()
    
    # Colonne latérale pour les logs et le raisonnement (1/3)
    with col_side:
        tab_logs, tab_reasoning = st.tabs(["📋 Logs", "🤔 Raisonnement"])
        
        with tab_logs:
            display_logs()
        
        with tab_reasoning:
            display_reasoning()
            
    # Compter les erreurs en arrière-plan
    logs = get_logs()
    error_count = sum(1 for log in logs if log['level'] in ['ERROR', 'CRITICAL'])
    if error_count > 0:
        st.sidebar.error(f"{error_count} erreur(s) détectée(s). Consultez les logs pour plus de détails.")