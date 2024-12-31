"""Tests for document repository."""

import pytest
from datetime import datetime
from unittest.mock import Mock, patch, call
import sqlite3
import logging

from src.features.ui.document.repository import DocumentRepository
from src.rag.document_watcher.document_tracker import DocumentTracker

logger = logging.getLogger(__name__)

@pytest.fixture
def mock_tracker():
    """Create mock document tracker."""
    tracker = Mock(spec=DocumentTracker)
    
    # Mock connection and cursor
    mock_conn = Mock()
    mock_cursor = Mock()
    mock_conn.cursor.return_value = mock_cursor
    tracker._get_connection.return_value = mock_conn
    
    # Mock document data
    mock_doc = (
        'test_workspace',           # workspace_id
        '/test/workspace1/test1.pdf', # file_path
        'processed',                # status
        datetime.now().isoformat(), # last_modified
        'abc123'                    # hash
    )
    mock_docs = [
        mock_doc,
        (
            'test_workspace',
            '/test/workspace2/test2.txt',
            'processed',
            datetime.now().isoformat(),
            'def456'
        )
    ]
    
    # Set up different fetchone results for different queries
    def mock_fetchone_side_effect():
        sql = mock_cursor.execute.call_args[0][0].strip()
        if 'COUNT(*)' in sql:
            return (2,)  # For get_document_count
        else:
            return mock_doc  # For get_document_by_id
            
    # Mock query results
    mock_cursor.fetchall.return_value = mock_docs
    mock_cursor.fetchone.side_effect = mock_fetchone_side_effect
    
    return tracker

@pytest.fixture
def repository(mock_tracker):
    """Create repository with mocked tracker."""
    return DocumentRepository(mock_tracker)

def test_get_documents_by_path(repository, mock_tracker):
    """Test retrieving documents by path."""
    docs = repository.get_documents_by_path('/test/workspace1/%')
    assert len(docs) > 0
    mock_tracker._get_connection().cursor().execute.assert_called_once()
    
    doc = docs[0]
    assert doc['workspace_id'] == 'test_workspace'
    assert doc['file_path'] == '/test/workspace1/test1.pdf'
    assert doc['status'] == 'processed'
    assert 'last_modified' in doc
    assert doc['hash'] == 'abc123'

def test_search_documents(repository, mock_tracker):
    """Test document search."""
    docs = repository.search_documents('test', '/test/workspace1/%')
    assert len(docs) > 0
    mock_tracker._get_connection().cursor().execute.assert_called_once()
    
    doc = docs[0]
    assert doc['workspace_id'] == 'test_workspace'
    assert doc['file_path'] == '/test/workspace1/test1.pdf'
    assert doc['status'] == 'processed'
    assert 'last_modified' in doc
    assert doc['hash'] == 'abc123'

def test_get_document_count(repository, mock_tracker):
    """Test document count."""
    count = repository.get_document_count('/test/workspace1/%')
    assert isinstance(count, int)
    assert count == 2
    mock_tracker._get_connection().cursor().execute.assert_called_once()

def test_get_document_by_id(repository, mock_tracker):
    """Test getting single document."""
    # Set up expected SQL and params
    expected_sql = f"""
            SELECT {', '.join(DocumentRepository.COLUMNS)}
            FROM document_tracking 
            WHERE workspace_id = ? AND file_path = ?
        """
    expected_params = ('test_workspace', '/test/workspace1/test1.pdf')
    
    # Get document
    doc = repository.get_document_by_id('test_workspace|/test/workspace1/test1.pdf')
    
    # Verify SQL execution
    mock_cursor = mock_tracker._get_connection().cursor()
    mock_cursor.execute.assert_called_once_with(expected_sql, expected_params)
    
    # Verify document data
    assert doc is not None
    assert doc['workspace_id'] == 'test_workspace'
    assert doc['file_path'] == '/test/workspace1/test1.pdf'
    assert doc['status'] == 'processed'
    assert 'last_modified' in doc
    assert doc['hash'] == 'abc123'
