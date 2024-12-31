"""Document service for managing document operations."""

from typing import List, Dict, Optional
from pathlib import Path

from .models import Document
from .repository import DocumentRepository
from src.core.workspace_manager import WorkspaceManager

class DocumentService:
    """Business logic layer for document operations."""
    
    def __init__(self, repository: DocumentRepository, workspace_manager: WorkspaceManager):
        """Initialize service with dependencies."""
        self._repository = repository
        self._workspace_manager = workspace_manager
        
    def get_documents_for_workspace(self, workspace_id: str) -> List[Document]:
        """Get all documents for workspace."""
        workspace_config = self._workspace_manager.get_current_space_config()
        if not workspace_config:
            return []
            
        documents = []
        workspace_paths = workspace_config.paths
        
        for path in workspace_paths:
            rows = self._repository.get_documents_by_path(f"{path}%")
            documents.extend(
                Document.from_db_row(row, workspace_id)
                for row in rows
            )
            
        return documents
        
    def search_documents(self, query: str, workspace_id: str) -> List[Document]:
        """Search documents in workspace."""
        if not query:
            return self.get_documents_for_workspace(workspace_id)
            
        documents = []
        workspace_config = self._workspace_manager.get_current_space_config()
        if not workspace_config:
            return []
            
        workspace_paths = workspace_config.paths
        
        for path in workspace_paths:
            rows = self._repository.search_documents(query, f"{path}%")
            documents.extend(
                Document.from_db_row(row, workspace_id)
                for row in rows
            )
            
        return documents
        
    def get_document_count(self, workspace_id: str) -> int:
        """Get total documents in workspace."""
        total_count = 0
        workspace_config = self._workspace_manager.get_current_space_config()
        if not workspace_config:
            return 0
            
        workspace_paths = workspace_config.paths
        
        for path in workspace_paths:
            total_count += self._repository.get_document_count(f"{path}%")
            
        return total_count
        
    def get_document_metadata(self, doc_id: str) -> Optional[Dict]:
        """Get document metadata."""
        return self._repository.get_document_by_id(doc_id)
