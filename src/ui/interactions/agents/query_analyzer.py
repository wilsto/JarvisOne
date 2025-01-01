"""Display handler for query analyzer interactions."""
import streamlit as st
from typing import Dict, Any
from ..base import BaseInteractionDisplay

class QueryAnalyzerDisplay(BaseInteractionDisplay):
    """Display handler for query analyzer interactions."""
    
    def get_confidence_badge(self, confidence: float) -> str:
        """Get confidence badge emoji and color based on score."""
        if confidence >= 80:
            return "🟢"  # High confidence
        elif confidence >= 50:
            return "🟡"  # Medium confidence
        else:
            return "🔴"  # Low confidence

    def get_expander_title(self, interaction: Dict[str, Any]) -> str:
        """Get the title for the expander."""
        analysis = interaction['analysis']
        confidence = analysis.get('confidence', 0)
        badge = self.get_confidence_badge(confidence)
        return f"{badge} Analysis: {analysis['agent_selected']} • {analysis['verifier']['confidence']:.0f}%"

    def display(self, interaction: Dict[str, Any]) -> None:
        """Display the interaction in the UI."""
        analysis = interaction['analysis']
                
        # Display agent selection details
        st.markdown("***Agent Selection***")
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown(f"**Selected Agent:** {analysis['agent']['name']}")
            st.markdown(f"**Agent Confidence:** {analysis['agent']['confidence']:.0f}%")
            st.markdown(f"**Agent Reason:** {analysis['agent']['reason']}")
        
        with col2:
            st.markdown(f"**Final Confidence:** {analysis['verifier']['confidence']:.0f}%")
            st.markdown(f"**Confidence Check Level:** {analysis['verifier']['level'].title()}")
            st.markdown(f"**Verifier Reason:** {analysis['verifier']['reason']}")
