"""Tests for document processor."""

import os
import pytest
from pathlib import Path
from unittest.mock import Mock, patch, AsyncMock
import chromadb
import tempfile
import shutil
import asyncio
from typing import Dict, Any

from src.rag.document_processor import DocumentProcessor, ImportanceLevelType

# Test workspaces
TEST_WORKSPACES = {
    "coaching": {"description": "Coaching workspace"},
    "dev": {"description": "Development workspace"},
    "personal": {"description": "Personal workspace"}
}

@pytest.fixture
def test_docs():
    """Test documents for each workspace."""
    return {
        "coaching": [
            ("doc1.txt", "This is a coaching document about leadership", "High"),
            ("doc2.txt", "Another coaching document about management", "Medium")
        ],
        "dev": [
            ("code1.txt", "Python code example with classes", "High"),
            ("code2.txt", "JavaScript tutorial document", "Medium")
        ],
        "personal": [
            ("note1.txt", "Personal notes about goals", "High")
        ]
    }

@pytest.fixture
def temp_dir():
    """Create a temporary directory for test files."""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    try:
        shutil.rmtree(temp_dir)
    except PermissionError:
        pass  # Ignore permission errors during cleanup

@pytest.fixture
def doc_processor(temp_dir):
    """Create DocumentProcessor instance with temp directory."""
    processor = None
    try:
        processor = DocumentProcessor(vector_db_path=temp_dir)
        yield processor
    finally:
        if processor:
            processor.cleanup()

def create_test_file(temp_dir: str, filename: str, content: str) -> str:
    """Create a test file with given content."""
    file_path = os.path.join(temp_dir, filename)
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)
    return file_path

def test_collection_isolation(doc_processor, temp_dir, test_docs):
    """Test that collections are properly isolated by workspace."""
    # Create test documents for each workspace
    for workspace, docs in test_docs.items():
        for filename, content, importance in docs:
            file_path = create_test_file(temp_dir, filename, content)
            doc_processor._process_file_internal(
                file_path,
                workspace,
                importance
            )
    
    # Test search in each workspace
    for workspace in TEST_WORKSPACES:
        results = doc_processor.search_documents(
            "document",
            workspace,
            n_results=5
        )
        # Verify results only contain documents from this workspace
        for result in results:
            assert result["metadata"]["workspace_id"] == workspace

def test_importance_filtering(doc_processor, temp_dir):
    """Test filtering by importance level."""
    # Create documents with different importance levels
    docs = [
        ("high.txt", "High importance document", "High"),
        ("medium.txt", "Medium importance document", "Medium"),
        ("low.txt", "Low importance document", "Low")
    ]
    
    for filename, content, importance in docs:
        file_path = create_test_file(temp_dir, filename, content)
        doc_processor._process_file_internal(
            file_path,
            "test_workspace",
            importance
        )
    
    # Search with importance filter
    results = doc_processor.search_documents(
        "document",
        "test_workspace",
        importance_filter="High"
    )
    
    assert len(results) > 0
    for result in results:
        assert result["metadata"]["importance_level"] == "High"

def test_collection_persistence(temp_dir):
    """Test that collections persist between processor instances."""
    # First processor instance
    processor1 = DocumentProcessor(vector_db_path=temp_dir)
    
    try:
        # Add document
        file_path = create_test_file(temp_dir, "test.txt", "Test document")
        processor1._process_file_internal(
            file_path,
            "test_workspace",
            "High"
        )
        
        # Cleanup first instance
        processor1.cleanup()
        
        # Create new processor instance with same path
        processor2 = DocumentProcessor(vector_db_path=temp_dir)
        
        # Search should find document
        results = processor2.search_documents(
            "test",
            "test_workspace",
            n_results=1
        )
        
        assert len(results) > 0
        assert "Test document" in results[0]["content"]
        
    finally:
        processor1.cleanup()
        if 'processor2' in locals():
            processor2.cleanup()

def test_empty_and_invalid_cases(doc_processor, temp_dir):
    """Test handling of empty files and invalid queries."""
    # Empty file
    empty_path = create_test_file(temp_dir, "empty.txt", "")
    doc_processor._process_file_internal(
        empty_path,
        "test_workspace",
        "High"
    )
    
    # Non-existent file
    with pytest.raises(FileNotFoundError):
        doc_processor._process_file_internal(
            "nonexistent.txt",
            "test_workspace",
            "High"
        )
    
    # Empty query
    results = doc_processor.search_documents(
        "",
        "test_workspace",
        n_results=1
    )
    assert len(results) == 0

def test_cross_workspace_search(doc_processor, temp_dir):
    """Test that searches don't leak across workspaces."""
    # Add same content to different workspaces
    content = "Unique test content"
    for workspace in ["workspace1", "workspace2"]:
        file_path = create_test_file(temp_dir, f"{workspace}.txt", content)
        doc_processor._process_file_internal(
            file_path,
            workspace,
            "High"
        )
    
    # Search in workspace1
    results1 = doc_processor.search_documents(
        "unique",
        "workspace1",
        n_results=5
    )
    
    # Search in workspace2
    results2 = doc_processor.search_documents(
        "unique",
        "workspace2",
        n_results=5
    )
    
    # Verify no cross-contamination
    assert len(results1) == 1
    assert len(results2) == 1
    assert results1[0]["metadata"]["workspace_id"] == "workspace1"
    assert results2[0]["metadata"]["workspace_id"] == "workspace2"

def test_process_document_basic(doc_processor, temp_dir):
    """Test basic document processing."""
    content = "Test document content"
    test_file = create_test_file(temp_dir, "test.md", content)
    
    doc_processor.process_document(
        str(test_file),
        "test_workspace",
        temp_dir,
        importance_level="High"
    )
    
    # Verify document was added to collection
    collection = doc_processor._get_collection("test_workspace")
    results = collection.query(
        query_texts=["test"],
        n_results=1
    )
    assert len(results['documents']) > 0
    assert "Test document content" in results['documents'][0][0]
