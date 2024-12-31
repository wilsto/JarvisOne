"""Test vector database monitoring."""

import pytest
from datetime import datetime
from vector_db.monitoring import VectorDBMonitor, CollectionStats

def test_collection_stats():
    """Test CollectionStats functionality."""
    stats = CollectionStats()
    assert stats.document_count == 0
    assert stats.last_updated is None
    assert stats.last_queried is None
    
    # Test update
    stats.update_stats(10)
    assert stats.document_count == 10
    assert isinstance(stats.last_updated, datetime)
    
    # Test query recording
    stats.record_query()
    assert isinstance(stats.last_queried, datetime)
    
def test_vector_db_monitor():
    """Test VectorDBMonitor functionality."""
    monitor = VectorDBMonitor()
    
    # Test new collection
    stats = monitor.get_collection_stats("test_collection")
    assert isinstance(stats, CollectionStats)
    assert stats.document_count == 0
    
    # Test update
    monitor.update_collection("test_collection", 5)
    stats = monitor.get_collection_stats("test_collection")
    assert stats.document_count == 5
    
    # Test query recording
    monitor.record_query("test_collection")
    stats = monitor.get_collection_stats("test_collection")
    assert stats.last_queried is not None
    
def test_monitor_all_stats():
    """Test getting all statistics."""
    monitor = VectorDBMonitor()
    
    # Add some data
    monitor.update_collection("col1", 5)
    monitor.update_collection("col2", 10)
    monitor.record_query("col1")
    
    # Get all stats
    all_stats = monitor.get_all_stats()
    assert len(all_stats) == 2
    assert all_stats["col1"]["document_count"] == 5
    assert all_stats["col2"]["document_count"] == 10
    assert all_stats["col1"]["last_queried"] is not None
    assert all_stats["col2"]["last_queried"] is None
