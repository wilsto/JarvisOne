"""Library tab component for document management."""

import streamlit as st
from typing import Optional
from pathlib import Path

from .document.document_service import DocumentService
from .document.repository import DocumentRepository
from .document.search import DocumentSearch
from .document.interactions import DocumentInteractions
from src.core.workspace_manager import WorkspaceManager
from src.rag.document_watcher.document_tracker import DocumentTracker

class LibraryTab:
    """Main library tab component."""
    
    def __init__(self, workspace_manager: WorkspaceManager):
        """Initialize library tab component."""
        self._workspace_manager = workspace_manager
        # Create dependencies
        repository = DocumentRepository(DocumentTracker())
        self._document_service = DocumentService(repository, workspace_manager)
        self._search = DocumentSearch(self._document_service)
        
    def render(self):
        """Render the library tab content."""
        current_workspace = self._workspace_manager.current_space
        
        with st.container():
            # Render search bar and filters
            self._search.render_search_bar()
            
            # Show document count
            doc_count = self._document_service.get_document_count(current_workspace)
            st.markdown(f"**{doc_count}** documents in workspace")
            
            # Get and display filtered documents
            documents = self._search.get_filtered_documents(current_workspace)
            
            st.markdown("---")  # Add a separator

            # Display documents table
            if documents:
                self._render_documents_table(documents)
            else:
                st.info("No documents found in this workspace")
                
    def _render_documents_table(self, documents):
        """Render the documents table with interactions."""

        # Header row
        cols = st.columns([0.5, 6, 1, 1.5,  0.5, 0.5])
        cols[0].markdown(" ")
        cols[1].markdown("**Document Name**")
        cols[2].markdown("**Size**")
        cols[3].markdown("**Modified**")
        cols[4].write(" ")
        cols[5].write(" ")

        # Document rows
        for doc in documents:
            row = DocumentInteractions.create_document_row(doc)
            cols = st.columns([0.5, 6, 1, 1.5,  0.5, 0.5])
            
            # Display document info
            cols[0].write(row["Type"])
            cols[1].markdown(f"<span style='font-size: 0.8em;'>***{row['Name']}***</span><br><span style='color: gray; font-style: italic; font-size: 0.8em;'>{row['Path']}</span>", unsafe_allow_html=True)
            cols[2].markdown(f"<span style='font-size: 0.8em;'>{row['Size']}</span>", unsafe_allow_html=True)
            cols[3].markdown(f"<span style='font-size: 0.8em;'>{row['Modified']}</span>", unsafe_allow_html=True)
            
            # Settings button
            if cols[4].button("⚙️", key=f"settings_{doc.workspace_id}_{doc.file_path}"):
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
            
            # Open folder button
            if cols[5].button("📁", key=f"folder_{doc.workspace_id}_{doc.file_path}"):
                DocumentInteractions.open_file_location(Path(doc.file_path))

    def _handle_table_click(self, row_idx: Optional[int], col_idx: Optional[int], documents: list):
        """Handle table click events."""
        if row_idx is not None and col_idx is not None:
            # Create a mock clicked data structure for backwards compatibility
            clicked = {
                "_clicked_row": row_idx,
                "_clicked_column": list(DocumentInteractions.create_document_row(documents[0]).keys())[col_idx]
            }
            DocumentInteractions.handle_row_click(clicked, documents[row_idx])
