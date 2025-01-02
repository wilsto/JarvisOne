"""Tests for workspace context builder component."""

import logging
import pytest
from core.prompts.components import WorkspaceContextBuilder, WorkspaceContextConfig

def test_basic_workspace_context():
    """Test basic workspace context building."""
    config = WorkspaceContextConfig(
        workspace_id="test_workspace",
        workspace_prompt="You are in the test workspace",
        scope="Test workspace scope",
        debug=False
    )
    
    result = WorkspaceContextBuilder.build(config)
    assert "You are in the test workspace" in result
    assert "Test workspace scope" in result

def test_workspace_context_with_metadata():
    """Test workspace context with metadata - should not appear in output."""
    config = WorkspaceContextConfig(
        workspace_id="test_workspace",
        workspace_prompt="Test prompt",
        scope="Test scope",
        metadata={"description": "Test Description", "context": "Test Context"},
        debug=False
    )
    
    result = WorkspaceContextBuilder.build(config)
    assert "Test prompt" in result
    assert "Test scope" in result
    # Metadata should not appear in the output
    assert "Test Description" not in result
    assert "Test Context" not in result

def test_workspace_context_debug_mode():
    """Test workspace context in debug mode."""
    config = WorkspaceContextConfig(
        workspace_id="test_workspace",
        workspace_prompt="Test prompt",
        scope="Test scope",
        debug=True
    )
    
    result = WorkspaceContextBuilder.build(config)
    assert "=== Workspace Context ===" in result
    assert "=== Workspace Instructions ===" in result
    assert "=== Workspace Scope ===" in result
    assert "Active Workspace: test_workspace" in result  # Workspace ID only shown in debug mode

def test_workspace_context_error_handling(caplog):
    """Test error handling in workspace context building."""
    config = None
    
    with caplog.at_level(logging.ERROR):
        result = WorkspaceContextBuilder.build(config)
        
    assert result == ""
    assert "Error building workspace context" in caplog.text

def test_empty_optional_fields():
    """Test handling of empty optional fields."""
    config = WorkspaceContextConfig(
        workspace_id="test_workspace",
        workspace_prompt="",
        scope="",
        metadata={"some": "metadata"},  # Should not affect output
        debug=False
    )
    
    result = WorkspaceContextBuilder.build(config)
    # Workspace ID should not appear in non-debug mode
    assert result == ""  # Empty string when no content to display
