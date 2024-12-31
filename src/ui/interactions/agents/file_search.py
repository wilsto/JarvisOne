"""Display handler for file search interactions."""
import streamlit as st
import os
import pyperclip
import logging
import shlex
import subprocess
from typing import Dict, Any
from ..base import BaseInteractionDisplay
from core.config_manager import ConfigManager

# Configure logger
logger = logging.getLogger(__name__)

class FileSearchDisplay(BaseInteractionDisplay):
    """Display handler for file search interactions."""
    
    def get_expander_title(self, interaction: Dict[str, Any]) -> str:
        return f"🔍 {interaction['query']} • {interaction['timestamp']}"
    
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
    
    def _launch_everything_gui(self, search_term: str = ""):
        """Launch Everything GUI with optional search term."""
        try:
            # Get Everything GUI path from config
            gui_path = ConfigManager.get_tool_config("everything", "gui_path")
            if not gui_path or not os.path.exists(gui_path):
                logger.error(f"Everything GUI not found at {gui_path}")
                st.error("Everything GUI not found")
                return
                
            cmd = [gui_path]
            if search_term:
                cmd.extend(["-search", search_term])
                
            subprocess.Popen(cmd)
            st.toast(f"Opened Everything with search: {search_term}")
        except Exception as e:
            logger.error(f"Error launching Everything GUI: {e}")
            st.error("Failed to launch Everything")
    
    def display(self, interaction: Dict[str, Any]) -> None:
        # Header with total results count and query
        col1, col2 = st.columns([3, 1])
        with col1:
            st.markdown(
                f"<div class='search-info'>"
                f"<b>Query:</b> <code>{interaction['query']}</code>"
                f"</div>",
                unsafe_allow_html=True
            )
        with col2:
            st.metric("Total found", len(interaction['results']), label_visibility="visible")
        
        # Limit display to first 10 results
        display_results = interaction['results'][:10]
        remaining_count = len(interaction['results']) - 10 if len(interaction['results']) > 10 else 0
        
        # Display results
        for i, result in enumerate(display_results, 1):
            self._display_result_item(interaction['id'], i, result)
        
        # Show remaining results count
        if remaining_count > 0:
            st.markdown(
                f"<div class='remaining-count'>+ {remaining_count} more files found</div>",
                unsafe_allow_html=True
            )
        
        # Everything button at the bottom
        st.button("🔍 Open in Everything", 
                 key=f"open_everything_{interaction['id']}", 
                 use_container_width=True,
                 on_click=self._launch_everything_gui,
                 args=(interaction['query'],))

    def _display_result_item(self, interaction_id: str, index: int, file_path: str) -> None:
        """Display a single result item."""
        file_name = os.path.basename(file_path)
        dir_path = os.path.dirname(file_path)
        
        cols = st.columns([0.4, 5, 0.6, 0.6])
        
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
            if st.button("📋", key=f"copy_{interaction_id}_{index}", help="Copy path"):
                self._copy_path(file_path)
                st.toast("Path copied!", icon="✅")
        with cols[3]:                
            if st.button("📂", key=f"open_{interaction_id}_{index}", help="Open file"):
                self._open_file(file_path)
