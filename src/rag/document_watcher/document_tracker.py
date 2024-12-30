"""Document tracking database for managing file changes."""

import sqlite3
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict
import threading

logger = logging.getLogger(__name__)

def adapt_datetime(dt):
    """Convert datetime to string for SQLite."""
    return dt.isoformat()

def convert_datetime(s):
    """Convert string to datetime from SQLite."""
    return datetime.fromisoformat(s)

sqlite3.register_adapter(datetime, adapt_datetime)
sqlite3.register_converter("datetime", convert_datetime)

class DocumentTracker:
    """Tracks document changes and processing status."""
    
    def __init__(self, db_path: str = "data/documents.db"):
        """Initialize document tracker with database path."""
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._local = threading.local()
        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        """Get a thread-local database connection."""
        if not hasattr(self._local, 'connection'):
            self._local.connection = sqlite3.connect(str(self.db_path), detect_types=sqlite3.PARSE_DECLTYPES)
            self._local.connection.row_factory = sqlite3.Row
        return self._local.connection

    def _close_connections(self):
        """Close any open database connections."""
        if hasattr(self._local, 'connection'):
            try:
                self._local.connection.close()
            except Exception as e:
                logger.error(f"Error closing connection: {e}")
            finally:
                del self._local.connection

    def _init_db(self):
        """Initialize the SQLite database schema."""
        with sqlite3.connect(str(self.db_path), detect_types=sqlite3.PARSE_DECLTYPES) as conn:
            cursor = conn.cursor()
            
            # Create table if not exists with current schema
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS document_tracking (
                    workspace_id TEXT NOT NULL,
                    file_path TEXT NOT NULL,
                    status TEXT CHECK(status IN ('pending', 'processed', 'error', 'deleted')) NOT NULL,
                    error_message TEXT,
                    last_modified datetime NOT NULL,
                    last_processed datetime,
                    hash TEXT,
                    PRIMARY KEY (workspace_id, file_path)
                )
            ''')
            conn.commit()
            logger.info("Document tracking database initialized")
            
    def update_document(
        self,
        workspace_id: str,
        file_path: str,
        status: str = 'pending',
        error_message: Optional[str] = None,
        last_modified: Optional[datetime] = None,
        hash_value: Optional[str] = None
    ):
        """Update or insert a document record.
        
        Args:
            workspace_id: ID of the workspace
            file_path: Path to the document
            status: Document status (pending, processed, error, deleted)
            error_message: Error message if status is error
            last_modified: Last modification time of the document
            hash_value: Hash of the document content
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            now = datetime.now()
            last_modified = last_modified or now
            
            cursor.execute('''
                INSERT INTO document_tracking (
                    workspace_id,
                    file_path,
                    status,
                    error_message,
                    last_modified,
                    last_processed,
                    hash
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(workspace_id, file_path) DO UPDATE SET
                    status = ?,
                    error_message = ?,
                    last_modified = ?,
                    last_processed = CASE 
                        WHEN ? = 'processed' THEN ?
                        ELSE last_processed
                    END,
                    hash = ?
            ''', (
                workspace_id, str(file_path), status, error_message,
                last_modified, now if status == 'processed' else None,
                hash_value,
                status, error_message, last_modified,
                status, now,
                hash_value
            ))
            
            conn.commit()
            logger.debug(f"Updated document tracking for {file_path}: {status}")
            
        except Exception as e:
            logger.error(f"Error updating document tracking: {e}")
            raise

    def get_pending_documents(self, workspace_id: str) -> List[Dict]:
        """Get list of documents that need processing."""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM document_tracking 
                WHERE workspace_id = ? AND status = 'pending'
                ORDER BY last_modified ASC
            ''', (workspace_id,))
            
            results = []
            for row in cursor.fetchall():
                doc = dict(row)
                # Convert any datetime objects to isoformat strings
                for key, value in doc.items():
                    if isinstance(value, datetime):
                        doc[key] = value.isoformat()
                results.append(doc)
            return results
            
        except Exception as e:
            logger.error(f"Error getting pending documents: {e}")
            raise

    def get_document_status(self, workspace_id: str, file_path: str) -> Optional[Dict]:
        """Get the current status of a document."""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM document_tracking 
                WHERE workspace_id = ? AND file_path = ?
            ''', (workspace_id, str(file_path)))
            row = cursor.fetchone()
            if row:
                doc = dict(row)
                # Convert any datetime objects to isoformat strings
                for key, value in doc.items():
                    if isinstance(value, datetime):
                        doc[key] = value.isoformat()
                return doc
            return None
            
        except Exception as e:
            logger.error(f"Error getting document status: {e}")
            raise

    def __del__(self):
        """Ensure connections are closed on deletion."""
        self._close_connections()
