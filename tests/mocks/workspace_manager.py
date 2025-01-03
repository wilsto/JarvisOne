"""Workspace manager mock for testing."""

import pytest
from unittest.mock import Mock
from pathlib import Path

from src.features.workspace_manager import SpaceType

@pytest.fixture
def mock_workspace_manager():
    """Mock workspace manager for testing.
    
    This fixture provides a mock workspace manager with:
    1. Basic workspace attributes (name, type, prompt)
    2. Common workspace manager methods
    3. Default test configurations
    """
    mock = Mock()
    
    # Setup basic workspace attributes
    mock.name = "test_workspace"
    mock.workspace_type = SpaceType.DEV
    mock.workspace_prompt = "Test workspace prompt"
    mock.root_path = Path("test/workspace/path")
    
    # Setup common method returns
    mock.get_current_context_prompt.return_value = "Test system prompt"
    mock.get_workspace_path.return_value = Path("test/workspace/path")
    mock.get_workspace_config.return_value = {
        "name": "test_workspace",
        "type": "DEV",
        "system_prompt": "Test system prompt",
        "root_path": "test/workspace/path"
    }
    
    return mock
