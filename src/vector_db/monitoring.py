"""Vector database monitoring utilities."""

import logging
from dataclasses import dataclass
from typing import Dict, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

@dataclass
class CollectionStats:
    """Statistics for a collection."""
    
    document_count: int = 0
    last_updated: Optional[datetime] = None
    last_queried: Optional[datetime] = None
    
    def update_stats(self, doc_count: int):
        """Update collection statistics."""
        self.document_count = doc_count
        self.last_updated = datetime.now()
        
    def record_query(self):
        """Record a query to this collection."""
        self.last_queried = datetime.now()

class VectorDBMonitor:
    """Monitor vector database operations."""
    
    def __init__(self):
        """Initialize monitor."""
        self.collection_stats: Dict[str, CollectionStats] = {}
        
    def get_collection_stats(self, collection_name: str) -> CollectionStats:
        """Get statistics for a collection."""
        if collection_name not in self.collection_stats:
            self.collection_stats[collection_name] = CollectionStats()
        return self.collection_stats[collection_name]
        
    def update_collection(self, collection_name: str, doc_count: int):
        """Update collection statistics."""
        stats = self.get_collection_stats(collection_name)
        stats.update_stats(doc_count)
        logger.info(f"Updated stats for {collection_name}: {doc_count} documents")
        
    def record_query(self, collection_name: str):
        """Record a query to a collection."""
        stats = self.get_collection_stats(collection_name)
        stats.record_query()
        
    def get_all_stats(self) -> Dict[str, Dict]:
        """Get statistics for all collections."""
        return {
            name: {
                "document_count": stats.document_count,
                "last_updated": stats.last_updated.isoformat() if stats.last_updated else None,
                "last_queried": stats.last_queried.isoformat() if stats.last_queried else None
            }
            for name, stats in self.collection_stats.items()
        }
        
    def get_monitoring_data(self) -> Dict[str, Dict]:
        """Get monitoring data for all collections.
        
        Returns:
            Dict containing collection statistics and performance metrics
        """
        return {
            "collections": self.get_all_stats(),
            "metrics": {
                "total_collections": len(self.collection_stats),
                "total_documents": sum(stats.document_count for stats in self.collection_stats.values())
            }
        }
