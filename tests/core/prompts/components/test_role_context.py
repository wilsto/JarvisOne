"""Tests for role context builder component."""

import logging
import pytest
from core.prompts.components import RoleContextBuilder, RoleContextConfig

def test_basic_role_context():
    """Test basic role context building."""
    config = RoleContextConfig(
        role_id="coach",
        role_name="Coach",
        role_description="Professional Coach Role",
        prompt_context="You are a professional coach focused on development",
        debug=False
    )
    
    result = RoleContextBuilder.build(config)
    assert "Active Role: Coach" in result
    assert "Role Purpose: Professional Coach Role" in result
    assert "You are a professional coach" in result
    
def test_role_context_with_metadata():
    """Test role context with additional metadata."""
    config = RoleContextConfig(
        role_id="coach",
        role_name="Coach",
        role_description="Professional Coach Role",
        prompt_context="Base prompt",
        metadata={"expertise": "Leadership", "approach": "Solution-focused"},
        debug=False
    )
    
    result = RoleContextBuilder.build(config)
    assert "expertise: Leadership" in result
    assert "approach: Solution-focused" in result
    
def test_role_context_debug_mode():
    """Test role context building in debug mode."""
    config = RoleContextConfig(
        role_id="coach",
        role_name="Coach",
        role_description="Professional Coach Role",
        prompt_context="Debug test prompt",
        debug=True
    )
    
    result = RoleContextBuilder.build(config)
    assert "=== Role Context ===" in result
    assert "=== Role Instructions ===" in result
    
def test_role_context_error_handling(caplog):
    """Test error handling in role context building."""
    config = None
    
    with caplog.at_level(logging.ERROR):
        result = RoleContextBuilder.build(config)
        
    assert result == ""
    assert "Error building role context" in caplog.text
    
def test_empty_optional_fields():
    """Test handling of empty optional fields."""
    config = RoleContextConfig(
        role_id="coach",
        role_name="Coach",
        role_description="",
        prompt_context="",
        metadata=None,
        debug=False
    )
    
    result = RoleContextBuilder.build(config)
    assert "Active Role: Coach" in result
    assert "Role Purpose" not in result
