"""Document domain models."""

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional

@dataclass
class Document:
    """Document data model."""
    workspace_id: str
    file_path: str
    status: str
    error_message: str
    last_modified: str  # ISO-8601 format
    last_processed: Optional[str]  # ISO-8601 format
    hash: str

    @property
    def name(self) -> str:
        """Get document name from file path."""
        return Path(self.file_path).name

    @property
    def type(self) -> str:
        """Get document type from file path."""
        return Path(self.file_path).suffix.lower()

    @property
    def last_modified_date(self) -> datetime:
        """Convert last_modified string to datetime."""
        return datetime.fromisoformat(self.last_modified) if self.last_modified else None

    @property
    def last_processed_date(self) -> Optional[datetime]:
        """Convert last_processed string to datetime."""
        return datetime.fromisoformat(self.last_processed) if self.last_processed else None

    @classmethod
    def from_db_row(cls, row: Dict, workspace_id: str) -> 'Document':
        """Create document from database row."""
        return cls(
            workspace_id=workspace_id,
            file_path=row['file_path'],
            status=row['status'],
            error_message=row.get('error_message'),
            last_modified=row['last_modified'],
            last_processed=row.get('last_processed'),
            hash=row.get('hash', '')
        )
