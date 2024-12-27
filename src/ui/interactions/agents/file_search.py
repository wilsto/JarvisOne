"""Display handler for file search interactions."""
import streamlit as st
import os
import pyperclip
import logging
import shlex
from typing import Dict, Any
from ..base import BaseInteractionDisplay

# Configuration du logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

class FileSearchDisplay(BaseInteractionDisplay):
    """Display handler for file search interactions."""
    
    def get_expander_title(self, interaction: Dict[str, Any]) -> str:
        return f"🔍 {interaction['query']} • {interaction['timestamp']}"
    
    def display(self, interaction: Dict[str, Any]) -> None:
        # En-tête avec le nombre total de résultats et la requête
        col1, col2 = st.columns([3, 1])
        with col1:
            st.markdown(
                f"<div class='search-info'>"
                f"<b>Requête :</b> <code>{interaction['query']}</code>"
                f"</div>",
                unsafe_allow_html=True
            )
        with col2:
            st.metric("Total trouvé", len(interaction['results']), label_visibility="visible")
        
        # Limiter l'affichage aux 10 premiers résultats
        display_results = interaction['results'][:10]
        remaining_count = len(interaction['results']) - 10 if len(interaction['results']) > 10 else 0
        
        # Affichage des résultats
        for i, result in enumerate(display_results, 1):
            self._display_result_item(interaction['id'], i, result)
        
        # Afficher le nombre de résultats restants
        if remaining_count > 0:
            st.markdown(
                f"<div class='remaining-count'>+ {remaining_count} autres fichiers trouvés</div>",
                unsafe_allow_html=True
            )
        
        # Bouton Everything en bas
        st.button("🔍 Ouvrir dans Everything", 
                 key=f"open_everything_{interaction['id']}", 
                 use_container_width=True,
                 on_click=self._launch_everything_gui,
                 args=(interaction['query'],))

    def _display_result_item(self, interaction_id: str, index: int, file_path: str) -> None:
        """Display a single result item."""
        file_name = os.path.basename(file_path)
        dir_path = os.path.dirname(file_path)
        
        cols = st.columns([0.4, 5, 0.6])
        
        with cols[0]:
            st.markdown(f"<div style='margin: 0; color: #555;'>#{index}</div>", unsafe_allow_html=True)
        
        with cols[1]:
            st.markdown(
                f"<div style='line-height: 1.2;'>"
                f"<span class='file-name'>{file_name}</span><br/>"
                f"<span class='file-path'>{dir_path}</span>"
                f"</div>",
                unsafe_allow_html=True
            )
        
        with cols[2]:
            if st.button("📋", key=f"copy_{interaction_id}_{index}", help="Copier le chemin"):
                pyperclip.copy(file_path)
                st.toast("Chemin copié !", icon="✅")

    #TODO: améliorer la gestion des path avec everything.exe
    def _launch_everything_gui(self, query: str) -> None:
        """Launch Everything GUI with the given query."""
        if not isinstance(query, str):
            logger.warning("Invalid query type provided")
            return
            
        logger.info("Launching Everything GUI with query: %s", query)
        
        # Split query and path components safely
        query_parts = query.split('path:', 1)
        search_query = query_parts[0].strip()
        query_path = query_parts[1].strip() if len(query_parts) > 1 else ''
        
        # Combine query components safely
        query4everything = f'{search_query} {query_path}'.strip()
        logger.info("Query for Everything: %s", query4everything)
        
        try:
            everything_path = r"C:\Program Files\Everything\Everything.exe"
            cmd = [everything_path, "-search"]
            cmd.extend(shlex.split(query4everything))
            
            subprocess.Popen(cmd)
        except Exception as e:
            logger.error("Failed to launch Everything GUI: %s", str(e))
            st.error("Failed to launch Everything GUI. Please try again.")
