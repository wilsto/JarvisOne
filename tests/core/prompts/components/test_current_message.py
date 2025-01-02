"""Tests for current message component."""

import pytest
from core.prompts.components.current_message import CurrentMessageConfig, CurrentMessageBuilder

def test_current_message_config_initialization():
    """Test CurrentMessageConfig initialization with valid data."""
    config = CurrentMessageConfig(content="Hello", role="user", debug=True)
    assert config.content == "Hello"
    assert config.role == "user"
    assert config.debug is True

def test_current_message_config_empty_content():
    """Test CurrentMessageBuilder handles empty content gracefully."""
    config = CurrentMessageConfig(content="", role="user", debug=False)
    builder = CurrentMessageBuilder()
    result = builder.build(config)
    assert result == "[USER]\n"  # Empty content is stripped but role is preserved

def test_current_message_config_invalid_role():
    """Test CurrentMessageBuilder handles invalid role gracefully."""
    config = CurrentMessageConfig(content="Hello", role="invalid_role", debug=False)
    builder = CurrentMessageBuilder()
    result = builder.build(config)
    assert "[INVALID_ROLE]" in result  # Role is uppercased but preserved

def test_current_message_builder_build():
    """Test CurrentMessageBuilder builds correct format."""
    config = CurrentMessageConfig(content="What's the weather?", role="user", debug=False)
    builder = CurrentMessageBuilder()
    result = builder.build(config)
    assert result == "[USER]\nWhat's the weather?"

def test_current_message_builder_debug():
    """Test CurrentMessageBuilder in debug mode."""
    config = CurrentMessageConfig(content="Test", role="user", debug=True)
    builder = CurrentMessageBuilder()
    result = builder.build(config)
    assert "=== Current Message ===" in result

def test_current_message_builder_multiline():
    """Test CurrentMessageBuilder with multiline content."""
    content = "Line 1\nLine 2\nLine 3"
    config = CurrentMessageConfig(content=content, role="assistant", debug=False)
    builder = CurrentMessageBuilder()
    result = builder.build(config)
    assert result == f"[ASSISTANT]\n{content}"

def test_current_message_builder_special_chars():
    """Test CurrentMessageBuilder handles special characters."""
    content = "Hello\tWorld!\n:)"
    config = CurrentMessageConfig(content=content, role="user", debug=False)
    builder = CurrentMessageBuilder()
    result = builder.build(config)
    assert content in result
