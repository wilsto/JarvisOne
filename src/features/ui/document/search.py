"""Search functionality for document library."""

from dataclasses import dataclass
from typing import List, Optional, Callable
import streamlit as st

from .document_service import DocumentService, Document

@dataclass
class SearchState:
    """Search state management."""
    query: str = ""
    file_type_filter: Optional[str] = None

class DocumentSearch:
    """Handles document search and filtering."""
    
    def __init__(self, document_service: DocumentService):
        """Initialize search component."""
        self._service = document_service
        self._init_state()
        
    def _init_state(self):
        """Initialize search state in session."""
        if 'doc_search_state' not in st.session_state:
            st.session_state.doc_search_state = SearchState()
            
    def render_search_bar(self) -> None:
        """Render search input and filters."""
        col1, col2 = st.columns([4, 1])
        
        with col1:
            # Search input
            query = st.text_input(
                "Search documents",
                value=st.session_state.doc_search_state.query,
                placeholder="Search by filename or content...",
                key="doc_search_input"
            )
            if query != st.session_state.doc_search_state.query:
                st.session_state.doc_search_state.query = query
                
        with col2:
            # File type filter
            file_types = [".txt", ".pdf", ".doc", ".docx"]  # Common types
            selected_type = st.selectbox(
                "Filter by type",
                options=["All"] + file_types,
                key="doc_type_filter"
            )
            st.session_state.doc_search_state.file_type_filter = (
                None if selected_type == "All" else selected_type
            )
            
    def get_filtered_documents(self, workspace_id: str) -> List[Document]:
        """Get filtered documents based on current search state."""
        state = st.session_state.doc_search_state
        
        # Get base document list
        documents = (
            self._service.search_documents(state.query, workspace_id)
            if state.query
            else self._service.get_documents_for_workspace(workspace_id)
        )
        
        # Apply type filter if set
        if state.file_type_filter:
            documents = [
                doc for doc in documents
                if doc.type.lower() == state.file_type_filter.lower()
            ]
            
        return documents
