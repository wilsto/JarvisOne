"""Tests for document interactions."""

import pytest
from datetime import datetime
from pathlib import Path
from unittest.mock import Mock, patch

from src.features.ui.document.interactions import DocumentInteractions
from src.features.ui.document.document_service import Document

@pytest.fixture
def sample_document():
    """Create a sample document for testing."""
    return Document(
        id='1',
        name='test.pdf',
        path=Path('/test/workspace/test.pdf'),
        type='.pdf',
        last_modified=datetime.now(),
        size=1024,
        workspace_id='test_workspace'
    )

def test_get_file_icon():
    """Test file icon selection."""
    doc = Mock(type='.pdf')
    assert DocumentInteractions.get_file_icon(doc) == '📕'
    
    doc.type = '.unknown'
    assert DocumentInteractions.get_file_icon(doc) == '📄'

def test_format_size():
    """Test file size formatting."""
    assert DocumentInteractions.format_size(500) == '500.0 B'
    assert DocumentInteractions.format_size(1024) == '1.0 KB'
    assert DocumentInteractions.format_size(1024 * 1024) == '1.0 MB'

@patch('subprocess.run')
def test_open_file_location(mock_run, sample_document):
    """Test opening file location."""
    DocumentInteractions.open_file_location(sample_document.path)
    mock_run.assert_called_once()

def test_create_document_row(sample_document):
    """Test document row creation."""
    row = DocumentInteractions.create_document_row(sample_document)
    assert 'Type' in row
    assert 'Name' in row
    assert 'Size' in row
    assert 'Modified' in row
    assert row['Name'] == sample_document.name
