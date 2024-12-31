"""Document repository for data access."""

from typing import List, Dict, Optional, Tuple
from src.rag.document_watcher.document_tracker import DocumentTracker
from pathlib import Path

import logging

logger = logging.getLogger(__name__)

class DocumentRepository:
    """Data access layer for documents."""
    
    # Column definitions for consistent mapping
    DB_COLUMNS = ['workspace_id', 'file_path', 'status', 'error_message', 'last_modified', 'last_processed', 'hash']
    
    def __init__(self, document_tracker: DocumentTracker):
        """Initialize repository."""
        self._tracker = document_tracker
    
    def _row_to_dict(self, row: Tuple) -> Dict:
        """Convert a database row to a dictionary."""
        if not row:
            return None
            
        # Convert row to dict with DB column names
        if hasattr(row, 'keys'):
            return dict(row)
        
        # Handle tuple case - use exact DB column names
        return dict(zip(self.DB_COLUMNS, row))
        
    def get_documents_by_path(self, path_pattern: str) -> List[Dict]:
        """Get documents matching path pattern."""
        conn = self._tracker._get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT workspace_id, file_path, status, error_message, last_modified, last_processed, hash
            FROM document_tracking
            WHERE file_path LIKE ?
            AND status != 'deleted'
        """, (path_pattern,))
        rows = cursor.fetchall()
        return [self._row_to_dict(row) for row in rows] if rows else []
        
    def search_documents(self, query: str, path_pattern: str) -> List[Dict]:
        """Search documents by content and path."""
        conn = self._tracker._get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT workspace_id, file_path, status, error_message, last_modified, last_processed, hash
            FROM document_tracking
            WHERE file_path LIKE ?
            AND status != 'deleted'
            AND (file_path LIKE ? OR hash LIKE ?)
        """, (path_pattern, f"%{query}%", f"%{query}%"))
        rows = cursor.fetchall()
        return [self._row_to_dict(row) for row in rows] if rows else []
        
    def get_document_count(self, path_pattern: str) -> int:
        """Get document count for path pattern."""
        conn = self._tracker._get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT COUNT(*)
            FROM document_tracking
            WHERE file_path LIKE ?
            AND status != 'deleted'
        """, (path_pattern,))
        return cursor.fetchone()[0]
        
    def get_document_by_id(self, workspace_file_path: str) -> Optional[Dict]:
        """Get single document by workspace_id and file_path combined."""
        if '|' not in workspace_file_path:
            return None
            
        workspace_id, file_path = workspace_file_path.split('|', 1)
        conn = self._tracker._get_connection()
        cursor = conn.cursor()
        cursor.execute(f"""
            SELECT {', '.join(self.DB_COLUMNS)}
            FROM document_tracking 
            WHERE workspace_id = ? AND file_path = ?
        """, (workspace_id, file_path))
        result = self._row_to_dict(cursor.fetchone())
        logger.info(f"Retrieved document: {result}")
        return result
