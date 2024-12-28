"""Display handler for configuration changes."""
import streamlit as st
from ..base import BaseInteractionDisplay
from typing import Dict, Any

class ConfigChangeDisplay(BaseInteractionDisplay):
    """Display handler for configuration changes."""

    def get_expander_title(self, interaction: Dict[str, Any]) -> str:
        """Get the title for the interaction expander."""
        config_type = interaction.get("config_type", "Configuration")
        return f"🔧 Modification of {config_type}"

    def display(self, interaction: Dict[str, Any]) -> None:
        """Display the configuration change."""
        config_type = interaction.get("config_type", "")
        old_value = interaction.get("old_value")
        new_value = interaction.get("new_value")
        
        # Display the change
        st.markdown(f"**Configuration Type:** {config_type}")
        
        if old_value is not None:
            st.markdown(f"**Previous value:** {old_value}")
        st.markdown(f"**New value:** {new_value}")
        
        # Add timestamp if available
        if "timestamp" in interaction:
            st.text(f"Modified on: {interaction['timestamp']}")
