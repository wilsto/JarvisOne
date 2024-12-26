"""Display handler for query analyzer interactions."""
import streamlit as st
from typing import Dict, Any
from ..base import BaseInteractionDisplay

class QueryAnalyzerDisplay(BaseInteractionDisplay):
    """Display handler for query analyzer interactions."""
    
    def get_expander_title(self, interaction: Dict[str, Any]) -> str:
        return f"🤔 Analyse : {interaction['analysis']['agent_selected']} • {interaction['timestamp']}"
    
    def display(self, interaction: Dict[str, Any]) -> None:
        st.markdown(f"**Requête analysée :** {interaction['query']}")
        
        if 'analysis' in interaction and interaction['analysis']:
            st.markdown("**Résultat de l'analyse :**")
            st.json(interaction['analysis'])
