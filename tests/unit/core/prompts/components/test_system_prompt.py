"""Tests for the system prompt builder component."""

import pytest
from core.prompts.components import SystemPromptBuilder, SystemPromptConfig

def test_system_prompt_basic():
    """Test basic system prompt building."""
    config = SystemPromptConfig(
        context_prompt="Test system prompt",
        workspace_scope="test_workspace",
        debug=False
    )
    
    result = SystemPromptBuilder.build(config)
    
    assert "Test system prompt" in result
    assert "test_workspace" in result

def test_system_prompt_empty():
    """Test system prompt with empty values."""
    config = SystemPromptConfig(
        context_prompt="",
        workspace_scope="",
        debug=False
    )
    
    result = SystemPromptBuilder.build(config)
    
    assert result == ""

def test_system_prompt_debug_mode():
    """Test system prompt in debug mode."""
    config = SystemPromptConfig(
        context_prompt="Test prompt",
        workspace_scope="test_scope",
        debug=True
    )
    
    result = SystemPromptBuilder.build(config)
    
    assert "=== System Instructions ===" in result
    assert "Test prompt" in result
    assert "test_scope" in result

def test_system_prompt_error_handling(caplog):
    """Test error handling in system prompt building."""
    config = None
    
    # Test return value
    result = SystemPromptBuilder.build(config)
    assert result == ""
    
    # Test error logging
    assert "Error building system prompt: 'NoneType' object has no attribute 'debug'" in caplog.text
    assert "ERROR" in caplog.text
