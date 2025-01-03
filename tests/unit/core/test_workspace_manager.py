"""Tests for workspace manager."""
import pytest
from pathlib import Path
from core.workspace_manager import WorkspaceManager, SpaceType, SpaceConfig
import tempfile
import yaml
import os

@pytest.fixture
def temp_config_dir():
    """Create a temporary config directory with test workspace files."""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create spaces directory
        spaces_dir = Path(temp_dir) / "spaces"
        spaces_dir.mkdir()
        
        # Create coaching config
        coaching_config = {
            "name": "Coaching",
            "paths": ["${TEST_PATH}"],
            "metadata": {
                "description": "Test coaching space",
                "context": "coaching"
            },
            "search_params": {},
            "tags": ["coaching"],
            "workspace_prompt": "Test workspace prompt",
            "scope": "Test coaching scope",
            "roles": [
                {
                    "name": "Coach",
                    "prompt_context": "Test coach context"
                }
            ]
        }
        
        with open(spaces_dir / "coaching_config.yaml", "w") as f:
            yaml.dump(coaching_config, f)
            
        yield Path(temp_dir)

def test_workspace_scope_loading(temp_config_dir):
    """Test that workspace scope is properly loaded."""
    manager = WorkspaceManager(temp_config_dir)
    manager.set_current_space(SpaceType.COACHING)
    
    # Get current space config
    space_config = manager.get_current_space_config()
    assert space_config is not None
    assert space_config.scope == "Test coaching scope"
    
    # Verify scope in context prompt
    context_prompt = manager.get_current_context_prompt()
    assert "Test coaching scope" in context_prompt

def test_workspace_scope_empty():
    """Test handling of missing scope."""
    with tempfile.TemporaryDirectory() as temp_dir:
        spaces_dir = Path(temp_dir) / "spaces"
        spaces_dir.mkdir()
        
        # Create config without scope
        config = {
            "name": "Test",
            "paths": [],
            "metadata": {},
            "search_params": {},
            "tags": [],
            "workspace_prompt": "Test prompt"
        }
        
        with open(spaces_dir / "coaching_config.yaml", "w") as f:
            yaml.dump(config, f)
            
        manager = WorkspaceManager(Path(temp_dir))
        manager.set_current_space(SpaceType.COACHING)
        
        space_config = manager.get_current_space_config()
        assert space_config is not None
        assert space_config.scope is None

def test_workspace_scope_in_prompt():
    """Test that scope is correctly included in the system prompt."""
    with tempfile.TemporaryDirectory() as temp_dir:
        spaces_dir = Path(temp_dir) / "spaces"
        spaces_dir.mkdir()
        
        config = {
            "name": "Test",
            "paths": [],
            "metadata": {},
            "search_params": {},
            "tags": [],
            "workspace_prompt": "Test prompt",
            "scope": "Test scope with special instructions"
        }
        
        with open(spaces_dir / "coaching_config.yaml", "w") as f:
            yaml.dump(config, f)
            
        manager = WorkspaceManager(Path(temp_dir))
        manager.set_current_space(SpaceType.COACHING)
        
        context_prompt = manager.get_current_context_prompt()
        assert "Test scope with special instructions" in context_prompt
