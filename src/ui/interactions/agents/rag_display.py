"""Display handler for RAG search interactions."""
import streamlit as st
import os
import pyperclip
import logging
from typing import Dict, Any
from ..base import BaseInteractionDisplay

logger = logging.getLogger(__name__)

class RAGSearchDisplay(BaseInteractionDisplay):
    """Display handler for RAG search interactions."""
    
    def get_expander_title(self, interaction: Dict[str, Any]) -> str:
        return f"📚 RAG Results • {interaction['timestamp']}"
    
    def _copy_path(self, path: str):
        """Copy a path to clipboard."""
        try:
            pyperclip.copy(path)
            st.toast(f"Copied to clipboard: {path}")
        except Exception as e:
            logger.error(f"Error copying to clipboard: {e}")
            st.error("Failed to copy to clipboard")
    
    def _open_file(self, path: str):
        """Open a file using the default application."""
        try:
            os.startfile(path)
            st.toast(f"Opened: {path}")
        except Exception as e:
            logger.error(f"Error opening file: {e}")
            st.error(f"Failed to open file: {path}")
            
    def _display_result_item(self, interaction_id: str, index: int, result: Dict[str, Any]) -> None:
        """Display a single RAG result item."""
        metadata = result.get('metadata', {})
        source = metadata.get('source', 'Unknown source')
        created_at = metadata.get('created_at', 'Unknown date')
        file_name = os.path.basename(source)
        dir_path = os.path.dirname(source)
        
        # Main container for the result
        st.markdown(
            f"<div class='rag-result' style='margin-bottom: 1rem;'>",
            unsafe_allow_html=True
        )
        
        # File info and action buttons
        cols = st.columns([0.4, 5, 0.6, 0.6])
        
        with cols[0]:
            st.markdown(f"<div style='margin: 0; color: #555;'>#{index}</div>", unsafe_allow_html=True)
        
        with cols[1]:
            st.markdown(
                f"<div style='line-height: 1.2;'>"
                f"<span class='file-name'>{file_name}</span><br/>"
                f"<span class='file-path'>{dir_path}</span><br/>"
                f"<span class='metadata' style='color: #666; font-size: 0.9em;'>"
                f"Created: {created_at} | Score: {result['similarity_score']:.2f}"
                f"</span>"
                f"</div>",
                unsafe_allow_html=True
            )
        
        with cols[2]:
            if st.button("📋", key=f"copy_{interaction_id}_{index}", help="Copy path"):
                self._copy_path(source)
        
        with cols[3]:
            if st.button("📂", key=f"open_{interaction_id}_{index}", help="Open file"):
                self._open_file(source)
        
        # Content section with citation
        content_with_citation = (
            f"<div class='content' style='margin-top: 0.5rem; padding: 0.5rem; "
            f"background: #f5f5f5; border-radius: 4px;'>"
            f"{result['content'].strip()}<br/><br/>"
            f"<span style='color: #666; font-size: 0.9em;'>"
            f"Source: {file_name} (Score: {result['similarity_score']:.2f})"
            f"</span>"
            f"</div>"
        )
        st.markdown(content_with_citation, unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    def display(self, interaction: Dict[str, Any]) -> None:
        """Display RAG search results."""
        # Header with query info
        col1, col2 = st.columns([3, 1])
        with col1:
            st.markdown(
                f"<div class='search-info'>"
                f"<b>Query:</b> <code>{interaction['query']}</code>"
                f"</div>",
                unsafe_allow_html=True
            )
        with col2:
            st.metric("Matches", len(interaction['results']), label_visibility="visible")
        
        # Display results
        for i, result in enumerate(interaction['results'], 1):
            self._display_result_item(interaction['id'], i, result)
