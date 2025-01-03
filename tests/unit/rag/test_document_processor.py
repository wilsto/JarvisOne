"""Test document processor."""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch, ANY
from datetime import datetime
import hashlib
from rag.document_processor import DocumentProcessor, ImportanceLevelType

@pytest.fixture
def mock_vector_db():
    """Mock VectorDBManager."""
    with patch('vector_db.manager.VectorDBManager') as mock:
        instance = Mock()
        instance.config.default_collection.chunk_size = 1000
        instance.config.default_collection.chunk_overlap = 200
        mock.get_instance.return_value = instance
        yield instance

@pytest.fixture
def processor(mock_vector_db):
    """Create DocumentProcessor instance."""
    return DocumentProcessor()

@pytest.fixture
def mock_handler():
    """Mock document handler."""
    handler = Mock()
    handler.can_handle.return_value = True
    return handler

def test_initialization(processor, mock_vector_db):
    """Test processor initialization."""
    assert processor.vector_db == mock_vector_db
    assert processor.text_splitter.chunk_size == 1000
    assert processor.text_splitter.chunk_overlap == 200

def test_process_file_with_handler_metadata(processor, mock_vector_db, mock_handler, tmp_path):
    """Test processing with handler metadata."""
    # Setup
    test_file = tmp_path / "test.txt"
    test_file.write_text("Test content")
    handler_metadata = {"format_version": "1.0", "encoding": "utf-8"}
    mock_handler.extract_text.return_value = ("Test content", handler_metadata)
    processor.handlers = [mock_handler]
    
    # Configure mock
    mock_vector_db.add_documents.return_value = True
    
    # Process file
    success = processor.process_file(
        file_path=str(test_file),
        workspace_id="test_workspace"
    )
    
    assert success
    # Verify metadata was passed
    call_args = mock_vector_db.add_documents.call_args
    assert call_args is not None
    _, kwargs = call_args
    metadata = kwargs["metadatas"][0]
    assert metadata["format_version"] == "1.0"
    assert metadata["encoding"] == "utf-8"

def test_process_file_with_stats(processor, mock_vector_db, mock_handler, tmp_path):
    """Test processing with file statistics."""
    # Setup
    test_file = tmp_path / "test.txt"
    test_file.write_text("Test content")
    mock_handler.extract_text.return_value = "Test content"
    processor.handlers = [mock_handler]
    
    # Process file
    success = processor.process_file(
        file_path=str(test_file),
        workspace_id="test_workspace"
    )
    
    assert success
    # Verify file stats
    call_args = mock_vector_db.add_documents.call_args
    assert call_args is not None
    _, kwargs = call_args
    metadata = kwargs["metadatas"][0]
    assert "created_at" in metadata
    assert "modified_at" in metadata
    assert "size_bytes" in metadata
    assert isinstance(metadata["size_bytes"], int)

def test_process_file_with_unique_ids(processor, mock_vector_db, mock_handler, tmp_path):
    """Test processing with unique document IDs."""
    # Setup
    test_file = tmp_path / "test.txt"
    test_file.write_text("Test content\nSecond line")
    mock_handler.extract_text.return_value = "Test content\nSecond line"
    processor.handlers = [mock_handler]
    
    # Calculate expected IDs
    file_path_hash = hashlib.sha256(str(test_file).encode()).hexdigest()[:8]
    expected_ids = [f"test_workspace_{file_path_hash}_0", f"test_workspace_{file_path_hash}_1"]
    
    # Process file
    success = processor.process_file(
        file_path=str(test_file),
        workspace_id="test_workspace"
    )
    
    assert success
    # Verify document IDs
    call_args = mock_vector_db.add_documents.call_args
    assert call_args is not None
    _, kwargs = call_args
    assert kwargs["doc_ids"] == expected_ids

def test_process_file_with_chunk_metadata(processor, mock_vector_db, mock_handler, tmp_path):
    """Test processing with chunk-specific metadata."""
    # Setup
    test_file = tmp_path / "test.txt"
    test_file.write_text("Test content\nSecond line")
    mock_handler.extract_text.return_value = "Test content\nSecond line"
    processor.handlers = [mock_handler]
    
    # Process file
    success = processor.process_file(
        file_path=str(test_file),
        workspace_id="test_workspace",
        importance_level="High"
    )
    
    assert success
    # Verify chunk metadata
    call_args = mock_vector_db.add_documents.call_args
    assert call_args is not None
    _, kwargs = call_args
    metadatas = kwargs["metadatas"]
    assert len(metadatas) == 2
    assert metadatas[0]["chunk_index"] == 0
    assert metadatas[1]["chunk_index"] == 1
    assert metadatas[0]["importance_level"] == "High"
    assert metadatas[1]["importance_level"] == "High"

def test_process_file_not_found(processor):
    """Test processing non-existent file."""
    success = processor.process_file(
        file_path="nonexistent.txt",
        workspace_id="test_workspace"
    )
    
    assert not success
    errors = processor.get_errors()
    assert len(errors) == 1
    assert "File not found" in errors[0]

def test_process_file_no_handler(processor, tmp_path):
    """Test processing with no suitable handler."""
    test_file = tmp_path / "test.unknown"
    test_file.write_text("Test content")
    processor.handlers = []  # Clear handlers
    
    success = processor.process_file(
        file_path=str(test_file),
        workspace_id="test_workspace"
    )
    
    assert not success
    errors = processor.get_errors()
    assert len(errors) == 1
    assert "No handler found" in errors[0]

def test_process_file_empty_content(processor, mock_handler, tmp_path):
    """Test processing with empty content."""
    test_file = tmp_path / "test.txt"
    test_file.write_text("")
    mock_handler.extract_text.return_value = ""
    processor.handlers = [mock_handler]
    
    success = processor.process_file(
        file_path=str(test_file),
        workspace_id="test_workspace"
    )
    
    assert not success
    errors = processor.get_errors()
    assert len(errors) == 1
    assert "No content extracted" in errors[0]

def test_search_pdf_with_accents(processor, mock_vector_db, mock_handler):
    """Test searching in PDF documents with accented characters."""
    # Mock the test PDF file
    test_file = Path("tests/unit/rag/test_files/Présentation-thérapie-des-schémas-sans-détails-pt-journée-de-la-psychothérapie.pdf")
    
    # Mock handler to return content with accents
    mock_handler.extract_text.return_value = """
    Présentation sur la thérapie des schémas
    Une journée de la psychothérapie
    Concepts théoriques et pratiques
    """
    processor.handlers = [mock_handler]
    
    # Process the document
    processor._process_file_internal(
        str(test_file),
        "COACHING",
        "High"
    )
    
    # Test various search queries with and without accents
    test_queries = [
        ("thérapie des schémas", "Test with accents"),
        ("therapie des schemas", "Test without accents"),
        ("JOURNÉE DE LA PSYCHOTHÉRAPIE", "Test with uppercase and accents"),
        ("journee psychotherapie", "Test without accents lowercase")
    ]
    
    # Mock search results
    mock_vector_db.search.return_value = [{
        "content": "Présentation sur la thérapie des schémas",
        "metadata": {
            "file_type": ".pdf",
            "workspace_id": "COACHING",
            "importance_level": "High"
        }
    }]
    
    for query, description in test_queries:
        results = processor.search_documents(
            query,
            "COACHING",
            n_results=5
        )
        
        assert len(results) > 0, f"No results found for query: {query} ({description})"
        
        # Verify metadata
        assert results[0]["metadata"]["file_type"] == ".pdf"
        assert results[0]["metadata"]["workspace_id"] == "COACHING"
        assert results[0]["metadata"]["importance_level"] == "High"
