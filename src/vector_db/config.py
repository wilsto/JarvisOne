"""Vector database configuration."""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

@dataclass
class CollectionConfig:
    """Configuration for a vector database collection."""
    
    distance_metric: str = "cosine"
    embedding_function: str = "sentence-transformers/all-MiniLM-L6-v2"
    chunk_size: int = 1000
    chunk_overlap: int = 200

@dataclass
class VectorDBConfig:
    """Configuration for the vector database."""
    
    persist_directory: str
    collection_prefix: str = "workspace_"
    default_collection: CollectionConfig = field(default_factory=CollectionConfig)
    monitoring_enabled: bool = True
    
    def __post_init__(self):
        """Ensure persist_directory is a Path object."""
        if isinstance(self.persist_directory, str):
            self.persist_directory = Path(self.persist_directory)
            
    @property
    def is_valid(self) -> bool:
        """Check if configuration is valid."""
        return bool(self.persist_directory)
