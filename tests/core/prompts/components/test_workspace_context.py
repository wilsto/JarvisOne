"""Tests for the workspace context builder component."""

import pytest
from core.prompts.components import WorkspaceContextBuilder, WorkspaceContextConfig

def test_workspace_context_basic():
    """Test basic workspace context building."""
    config = WorkspaceContextConfig(
        workspace_id="test_workspace",
        metadata={"key": "value"},
        debug=False
    )
    
    result = WorkspaceContextBuilder.build(config)
    
    assert "Active Workspace: test_workspace" in result
    assert "key: value" in result

def test_workspace_context_with_raw_context():
    """Test workspace context with raw context string."""
    config = WorkspaceContextConfig(
        workspace_id="test_workspace",
        metadata={"context": "Raw workspace context"},
        debug=False
    )
    
    result = WorkspaceContextBuilder.build(config)
    
    assert "Raw workspace context" in result
    assert "Workspace Configuration" not in result

def test_workspace_context_empty():
    """Test workspace context with empty values."""
    config = WorkspaceContextConfig(
        workspace_id="",
        metadata={},
        debug=False
    )
    
    result = WorkspaceContextBuilder.build(config)
    
    assert result == ""

def test_workspace_context_debug_mode():
    """Test workspace context in debug mode."""
    config = WorkspaceContextConfig(
        workspace_id="test_workspace",
        metadata={"key": "value"},
        debug=True
    )
    
    result = WorkspaceContextBuilder.build(config)
    
    assert "=== Workspace Context ===" in result
    assert "Active Workspace: test_workspace" in result
    assert "key: value" in result

def test_workspace_context_error_handling(caplog):
    """Test error handling in workspace context building."""
    config = None
    
    # Test return value
    result = WorkspaceContextBuilder.build(config)
    assert result == ""
    
    # Test error logging
    assert "Error building workspace context: 'NoneType' object has no attribute 'debug'" in caplog.text
    assert "ERROR" in caplog.text
