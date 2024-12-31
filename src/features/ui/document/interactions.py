"""Document interaction handlers for the library UI."""

import streamlit as st
from pathlib import Path
import subprocess
from typing import Dict, Any

from .document_service import Document

class DocumentInteractions:
    """Handles document-related user interactions."""
    
    @staticmethod
    def get_file_icon(doc: Document) -> str:
        """Get appropriate icon for file type."""
        ICONS = {
            '.pdf': '📕',
            '.txt': '📝',
            '.doc': '📘',
            '.docx': '📘',
            '.xls': '📊',
            '.xlsx': '📊',
            '.ppt': '📙',
            '.pptx': '📙',
            '.jpg': '🖼️',
            '.jpeg': '🖼️',
            '.png': '🖼️',
            '.gif': '🖼️',
            '.zip': '📦',
            '.rar': '📦'
        }
        return ICONS.get(doc.type.lower(), '📄')

    @staticmethod
    def format_size(size_bytes: int) -> str:
        """Format file size for display."""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024
        return f"{size_bytes:.1f} GB"

    @staticmethod
    def open_file_location(path: Path) -> None:
        """Open file location in explorer."""
        try:
            # Convert path to string and normalize for Windows
            file_path = str(path).replace('/', '\\')
            # Use /select to highlight the file in Explorer with shell=True for special characters
            subprocess.run(['explorer', '/select,', file_path], shell=True)
        except subprocess.CalledProcessError as e:
            st.error(f"Error opening file location: {e}")

    @staticmethod
    def create_document_row(doc: Document) -> Dict[str, Any]:
        """Create a row for the documents table."""
        modified_date = doc.last_modified_date
        return {
            "Type": DocumentInteractions.get_file_icon(doc),
            "Name": doc.name,
            "Size": "Unknown",  # We don't track file size in DB
            "Modified": modified_date.strftime("%Y-%m-%d %H:%M") if modified_date else "Unknown",
            "Path": str(Path(doc.file_path).parent),
            "Actions": "⚙️",
            "Folder": "📁"
        }

    @staticmethod
    def handle_row_click(row_data: Dict[str, Any], doc: Document) -> None:
        """Handle clicks on table rows."""
        # Handle folder icon click
        if row_data.get("_clicked_column") == "Folder":
            DocumentInteractions.open_file_location(Path(doc.file_path))
            
        # Handle settings icon click
        elif row_data.get("_clicked_column") == "Actions":
            with st.expander("Document Settings", expanded=True):
                st.write(f"Settings for: {doc.name}")
                st.write(f"Full path: {doc.file_path}")
                st.write(f"Status: {doc.status}")
                
                modified_date = doc.last_modified_date
                if modified_date:
                    st.write(f"Last modified: {modified_date.strftime('%Y-%m-%d %H:%M')}")
                
                processed_date = doc.last_processed_date
                if processed_date:
                    st.write(f"Last processed: {processed_date.strftime('%Y-%m-%d %H:%M')}")
                
                if doc.error_message:
                    st.error(f"Error: {doc.error_message}")
                
                # Add action buttons
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("Open File Location", key=f"open_{doc.workspace_id}_{doc.file_path}"):
                        DocumentInteractions.open_file_location(Path(doc.file_path))
                with col2:
                    if st.button("Copy Path", key=f"copy_{doc.workspace_id}_{doc.file_path}"):
                        st.write("Path copied to clipboard!")
                        st.session_state['clipboard'] = doc.file_path
