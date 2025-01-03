"""Test vector database configuration."""

import pytest
from pathlib import Path
from vector_db.config import VectorDBConfig, CollectionConfig

def test_collection_config_defaults():
    """Test CollectionConfig default values."""
    config = CollectionConfig()
    assert config.distance_metric == "cosine"
    assert config.chunk_size == 1000
    assert config.chunk_overlap == 200
    
def test_vector_db_config():
    """Test VectorDBConfig initialization."""
    # Test with Path
    path = Path("data/vector_db")
    config = VectorDBConfig(base_path=path)
    assert config.base_path == path
    assert config.collection_prefix == "workspace_"
    assert isinstance(config.default_collection, CollectionConfig)
    
    # Test with string
    config = VectorDBConfig(base_path="data/vector_db")
    assert isinstance(config.base_path, Path)
    assert config.base_path == Path("data/vector_db")
    
def test_vector_db_config_validation():
    """Test VectorDBConfig validation."""
    config = VectorDBConfig(base_path="data/vector_db")
    assert config.is_valid
    
    # Empty path should be invalid
    config = VectorDBConfig(base_path="")
    assert not config.is_valid
