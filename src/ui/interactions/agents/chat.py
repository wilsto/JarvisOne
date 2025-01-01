"""Display handler for chat interactions."""
import streamlit as st
import logging
from typing import Dict, Any
from ..base import BaseInteractionDisplay

logger = logging.getLogger(__name__)

class ChatDisplay(BaseInteractionDisplay):
    """Display handler for chat interactions."""
    
    def get_expander_title(self, interaction: Dict[str, Any]) -> str:
        """Get the title for the interaction expander."""
        if interaction['type'] == 'chat_response':
            return f"💬 Chat Response • {interaction['timestamp']}"
        elif interaction['type'] == 'rag_search':
            return f"📚 Context Search • {interaction['timestamp']}"
        return f"❓ Unknown • {interaction['timestamp']}"
    
    def display_content(self, interaction: Dict[str, Any]):
        """Display the interaction content."""
        try:
            if interaction['type'] == 'chat_response':
                self._display_chat_response(interaction['data'])
            elif interaction['type'] == 'rag_search':
                self._display_rag_results(interaction['data'])
        except Exception as e:
            logger.error(f"Error displaying chat interaction: {e}")
            st.error("Failed to display interaction content")
    
    def _display_chat_response(self, data: Dict[str, Any]):
        """Display a chat response interaction."""
        # Display the query
        st.markdown("**Query:**")
        st.markdown(f"_{data['query']}_")
        
        # Display the response
        st.markdown("**Response:**")
        st.markdown(data['response'])
        
        # If there's a linked RAG interaction, add a reference
        if 'rag_interaction_id' in data:
            st.markdown("---")
            st.markdown("*This response uses context from the search results above.*")
    
    def _display_rag_results(self, data: Dict[str, Any]):
        """Display RAG search results."""
        # Display search summary
        st.markdown(f"**Found {len(data['results'])} relevant documents**")
        
        # Display each result
        for idx, result in enumerate(data['results'], 1):
            with st.expander(f"Result {idx}: {result['title'][:50]}..."):
                st.markdown(f"**Relevance Score:** {result['score']:.2f}")
                st.markdown(f"**Source:** {result['source']}")
                st.markdown("**Content:**")
                st.markdown(result['content'])
