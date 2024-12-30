"""Test workspace watcher management functionality."""

import pytest
from pathlib import Path
import tempfile
from unittest.mock import Mock, patch

from src.core.workspace_manager import WorkspaceManager, SpaceType, SpaceConfig
from src.rag.document_processor import DocumentProcessor
from src.rag.document_watcher.workspace_watcher import WorkspaceWatcherManager
from src.rag.document_watcher.watcher import FileSystemWatcher

@pytest.fixture
def temp_dir():
    """Create a temporary directory for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)

@pytest.fixture
def mock_doc_processor():
    """Create a mock document processor."""
    processor = Mock(spec=DocumentProcessor)
    # Add handlers attribute with SUPPORTED_EXTENSIONS
    mock_handler = Mock()
    mock_handler.SUPPORTED_EXTENSIONS = {'.txt', '.md'}
    processor.handlers = [mock_handler]
    return processor

@pytest.fixture
def mock_workspace_manager():
    """Create a mock workspace manager."""
    manager = Mock(spec=WorkspaceManager)
    manager.spaces = {
        SpaceType.COACHING: SpaceConfig(
            name="Coaching",
            paths=["/path/to/coaching"],
            metadata={},
            search_params={},
            tags=[],
            workspace_prompt=None
        )
    }
    return manager

class TestWorkspaceWatcherManager:
    """Test workspace watcher management functionality."""
    
    def test_start_workspace_watcher(self, mock_workspace_manager, mock_doc_processor):
        """Test starting a workspace watcher."""
        manager = WorkspaceWatcherManager(mock_workspace_manager, mock_doc_processor)
        
        with patch('src.rag.document_watcher.workspace_watcher.FileSystemWatcher', autospec=True) as MockWatcher:
            # Configure the mock to return a properly configured mock instance
            mock_instance = Mock()
            MockWatcher.return_value = mock_instance
            
            # Call the method under test
            manager.start_workspace_watcher(SpaceType.COACHING)
            
            # Verify the watcher was created with correct parameters
            MockWatcher.assert_called_once_with(
                workspace_id="COACHING",
                paths=[Path("/path/to/coaching")],
                doc_processor=mock_doc_processor
            )
            
            # Verify the instance methods were called
            mock_instance.scan_existing_files.assert_called_once()
            mock_instance.start.assert_called_once()
            
    def test_stop_workspace_watcher(self, mock_workspace_manager, mock_doc_processor):
        """Test stopping a workspace watcher."""
        manager = WorkspaceWatcherManager(mock_workspace_manager, mock_doc_processor)
        
        with patch('src.rag.document_watcher.workspace_watcher.FileSystemWatcher', autospec=True) as MockWatcher:
            # Configure mock
            mock_instance = Mock()
            MockWatcher.return_value = mock_instance
            
            # Start watcher
            manager.start_workspace_watcher(SpaceType.COACHING)
            
            # Stop watcher
            manager.stop_workspace_watcher(SpaceType.COACHING)
            mock_instance.stop.assert_called_once()

    #FIXME: test_start_coaching_workspace - AssertionError: Expected 'FileSystemWatcher' to be called once. Called 0 times.  
    def test_start_coaching_workspace(self, mock_workspace_manager, mock_doc_processor):
        """Test starting the coaching workspace specifically."""
        manager = WorkspaceWatcherManager(mock_workspace_manager, mock_doc_processor)
        
        with patch('src.rag.document_watcher.workspace_watcher.FileSystemWatcher', autospec=True) as MockWatcher:
            # Configure mock
            mock_instance = Mock()
            MockWatcher.return_value = mock_instance
            
            # Start coaching workspace
            manager.start_coaching_workspace()
            
            # Verify watcher was created correctly
            MockWatcher.assert_called_once_with(
                workspace_id="COACHING",
                paths=[Path("/path/to/coaching")],
                doc_processor=mock_doc_processor
            )
            assert SpaceType.COACHING in manager.watchers
            
    def test_cleanup(self, mock_workspace_manager, mock_doc_processor):
        """Test cleaning up all watchers."""
        manager = WorkspaceWatcherManager(mock_workspace_manager, mock_doc_processor)
        
        with patch('src.rag.document_watcher.workspace_watcher.FileSystemWatcher', autospec=True) as MockWatcher:
            # Configure mock
            mock_instance = Mock()
            MockWatcher.return_value = mock_instance
            
            # Start watcher
            manager.start_workspace_watcher(SpaceType.COACHING)
            
            # Clean up
            manager.cleanup()
            mock_instance.stop.assert_called_once()
            assert not manager.watchers
