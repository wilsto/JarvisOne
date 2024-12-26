"""Display handler for configuration changes."""
import streamlit as st
from ..base import BaseInteractionDisplay
from typing import Dict, Any

class ConfigChangeDisplay(BaseInteractionDisplay):
    """Display handler for configuration changes."""

    def get_expander_title(self, interaction: Dict[str, Any]) -> str:
        """Get the title for the interaction expander."""
        config_type = interaction.get("config_type", "Configuration")
        return f"🔧 Modification de {config_type}"

    def display(self, interaction: Dict[str, Any]) -> None:
        """Display the configuration change."""
        config_type = interaction.get("config_type", "")
        old_value = interaction.get("old_value")
        new_value = interaction.get("new_value")
        
        # Display the change
        st.markdown(f"**Type de configuration:** {config_type}")
        
        if old_value is not None:
            st.markdown(f"**Ancienne valeur:** {old_value}")
        st.markdown(f"**Nouvelle valeur:** {new_value}")
        
        # Add timestamp if available
        if "timestamp" in interaction:
            st.text(f"Modifié le: {interaction['timestamp']}")
