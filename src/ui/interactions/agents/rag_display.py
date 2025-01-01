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
        """Get the title for the RAG results expander."""
        logger.debug(f"Getting expander title for interaction {interaction.get('id', 'unknown')}")
        return f"📚 Found in Documents • {interaction['timestamp']}"
    
    def _copy_path(self, path: str):
        """Copy a path to clipboard."""
        try:
            logger.debug(f"Copying path to clipboard: {path}")
            pyperclip.copy(path)
            st.toast(f"Copied to clipboard: {path}")
        except Exception as e:
            logger.error(f"Error copying to clipboard: {e}")
            st.error("Failed to copy to clipboard")
    
    def _open_file(self, path: str):
        """Open a file using the default application."""
        try:
            logger.debug(f"Opening file: {path}")
            os.startfile(path)
            st.toast(f"Opened: {path}")
        except Exception as e:
            logger.error(f"Error opening file: {e}")
            st.error(f"Failed to open file: {path}")
            
    def _display_result_item(self, interaction_id: str, index: int, result: Dict[str, Any]) -> None:
        """Display a single RAG result item."""
        logger.debug(f"Displaying result {index} for interaction {interaction_id}")
        
        metadata = result.get('metadata', {})
        source = metadata.get('source', 'Unknown source')
        file_name = os.path.basename(source)
        dir_path = os.path.dirname(source)
        
        logger.debug(f"Result details - File: {file_name}, Path: {dir_path}")
        
        cols = st.columns([0.7, 5, 0.6, 0.6])
        
        with cols[0]:
            st.markdown(f"<div style='margin: 0; color: #555;font-size: 0.9em;'>Score: {result.get('similarity_score', 0):.2f}</div>", unsafe_allow_html=True)
        
        with cols[1]:
            st.markdown(
                f"<div style='line-height: 1.2;'>"
                f"<span class='file-name'>{file_name}</span><br/>"
                f"<span class='file-path'>{dir_path}</span><br/>"
                f"<span class='metadata' style='color: #666; font-size: 0.9em;'>"
                f"</span>"
                f"</div>",
                unsafe_allow_html=True
            )
        
        with cols[2]:
            if st.button("📋", key=f"copy_{interaction_id}_{index}", help="Copy path"):
                self._copy_path(source)
                st.toast("Path copied!", icon="✅")
        
        with cols[3]:
            if st.button("📂", key=f"open_{interaction_id}_{index}", help="Open file"):
                self._open_file(source)

    def display(self, interaction: Dict[str, Any]) -> None:
        """Display RAG search results."""
        logger.info(f"Displaying RAG interaction {interaction.get('id', 'unknown')}")
        
        results = interaction.get('results', [])
        if not results:
            logger.warning("No results to display")
            st.info("No relevant documents found")
            return
            
        # Display each result
        for i, result in enumerate(results, 1):
            logger.debug(f"Displaying result {i}/{len(results)}")
            self._display_result_item(interaction['id'], i, result)
        
        logger.info("Finished displaying RAG results")
