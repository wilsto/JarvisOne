"""Tests for document service."""

import pytest
from datetime import datetime
from pathlib import Path
from unittest.mock import Mock

from src.features.ui.document.models import Document
from src.features.ui.document.document_service import DocumentService
from src.features.ui.document.repository import DocumentRepository
from src.core.workspace_manager import WorkspaceManager

@pytest.fixture
def mock_workspace_manager():
    """Create mock workspace manager."""
    manager = Mock(spec=WorkspaceManager)
    manager.get_current_space_config.return_value = {
        'paths': ['/test/workspace1', '/test/workspace2']
    }
    return manager

@pytest.fixture
def mock_repository():
    """Create mock document repository."""
    repository = Mock(spec=DocumentRepository)
    
    # Mock document data
    mock_docs = [
        {
            'id': '1',
            'filename': 'test1.pdf',
            'filepath': '/test/workspace1/test1.pdf',
            'last_modified': datetime.now(),
            'file_size': 1024
        },
        {
            'id': '2',
            'filename': 'test2.txt',
            'filepath': '/test/workspace2/test2.txt',
            'last_modified': datetime.now(),
            'file_size': 2048
        }
    ]
    
    repository.get_documents_by_path.return_value = mock_docs
    repository.search_documents.return_value = mock_docs
    repository.get_document_count.return_value = len(mock_docs)
    repository.get_document_by_id.return_value = mock_docs[0]
    
    return repository

@pytest.fixture
def document_service(mock_repository, mock_workspace_manager):
    """Create document service with mocked dependencies."""
    return DocumentService(mock_repository, mock_workspace_manager)

def test_get_documents_for_workspace(document_service):
    """Test retrieving documents for workspace."""
    docs = document_service.get_documents_for_workspace('test_workspace')
    assert len(docs) > 0
    assert all(isinstance(doc, Document) for doc in docs)

def test_search_documents(document_service):
    """Test document search functionality."""
    docs = document_service.search_documents('test', 'test_workspace')
    assert len(docs) > 0
    assert all(isinstance(doc, Document) for doc in docs)

def test_get_document_count(document_service):
    """Test document count retrieval."""
    count = document_service.get_document_count('test_workspace')
    assert isinstance(count, int)
    assert count >= 0

def test_get_document_metadata(document_service):
    """Test metadata retrieval."""
    metadata = document_service.get_document_metadata('1')
    assert metadata is not None
    assert 'filename' in metadata
    assert 'filepath' in metadata
