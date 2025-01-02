"""Tests for the RAG context builder component."""

import pytest
from core.prompts.components import RAGContextBuilder, RAGContextConfig, RAGDocument

def test_rag_context_basic():
    """Test basic RAG context building."""
    config = RAGContextConfig(
        query="test query",
        documents=[
            RAGDocument(
                content="Test content",
                metadata={"file_path": "test.txt"}
            )
        ],
        debug=False
    )
    
    result = RAGContextBuilder.build(config)
    
    assert "From test.txt:" in result
    assert "Test content" in result

def test_rag_context_multiple_documents():
    """Test RAG context with multiple documents."""
    config = RAGContextConfig(
        query="test query",
        documents=[
            RAGDocument(
                content="Content 1",
                metadata={"file_path": "file1.txt"}
            ),
            RAGDocument(
                content="Content 2",
                metadata={"file_path": "file2.txt"}
            )
        ],
        debug=False
    )
    
    result = RAGContextBuilder.build(config)
    
    assert "From file1.txt:" in result
    assert "Content 1" in result
    assert "From file2.txt:" in result
    assert "Content 2" in result

def test_rag_context_empty():
    """Test RAG context with no documents."""
    config = RAGContextConfig(
        query="test query",
        documents=[],
        debug=False
    )
    
    result = RAGContextBuilder.build(config)
    
    assert result == ""

def test_rag_context_debug_mode():
    """Test RAG context in debug mode."""
    config = RAGContextConfig(
        query="test query",
        documents=[
            RAGDocument(
                content="Test content",
                metadata={"file_path": "test.txt"}
            )
        ],
        debug=True
    )
    
    result = RAGContextBuilder.build(config)
    
    assert "=== RAG Context ===" in result
    assert "Query: test query" in result
    assert "From test.txt:" in result
    assert "Test content" in result

def test_rag_context_error_handling(caplog):
    """Test error handling in RAG context building."""
    config = None
    
    # Test return value
    result = RAGContextBuilder.build(config)
    assert result == ""
    
    # Test error logging
    assert "Error building RAG context: 'NoneType' object has no attribute 'debug'" in caplog.text
    assert "ERROR" in caplog.text
