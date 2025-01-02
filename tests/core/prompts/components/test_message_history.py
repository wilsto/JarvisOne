"""Tests for message history component."""

import pytest
from core.prompts.components.message_history import MessageHistoryConfig, MessageHistoryBuilder

def test_message_history_config_initialization():
    """Test MessageHistoryConfig initialization with valid data."""
    messages = [
        {"role": "user", "content": "Hello"},
        {"role": "assistant", "content": "Hi there!"}
    ]
    config = MessageHistoryConfig(messages=messages, debug=True)
    assert config.messages == messages
    assert config.debug is True

def test_message_history_config_empty_messages():
    """Test MessageHistoryConfig with empty messages list."""
    config = MessageHistoryConfig(messages=[], debug=False)
    assert config.messages == []
    assert config.debug is False

def test_message_history_builder_build():
    """Test MessageHistoryBuilder builds correct format."""
    messages = [
        {"role": "user", "content": "What's the weather?"},
        {"role": "assistant", "content": "It's sunny!"},
        {"role": "user", "content": "Thanks"}
    ]
    config = MessageHistoryConfig(messages=messages, debug=False)
    builder = MessageHistoryBuilder()
    result = builder.build(config)
    
    # Verify each message is formatted correctly
    assert "[USER]\nWhat's the weather?" in result
    assert "[ASSISTANT]\nIt's sunny!" in result
    assert "[USER]\nThanks" in result
    # Verify messages are separated by newlines
    assert "\n\n" in result

def test_message_history_builder_empty():
    """Test MessageHistoryBuilder with empty messages."""
    config = MessageHistoryConfig(messages=[], debug=False)
    builder = MessageHistoryBuilder()
    result = builder.build(config)
    assert result == ""

def test_message_history_builder_debug():
    """Test MessageHistoryBuilder in debug mode."""
    messages = [{"role": "user", "content": "Test"}]
    config = MessageHistoryConfig(messages=messages, debug=True)
    builder = MessageHistoryBuilder()
    result = builder.build(config)
    assert "=== Message History ===" in result

def test_message_history_config_invalid_messages():
    """Test MessageHistoryBuilder handles invalid message format gracefully."""
    invalid_messages = [{"invalid": "format"}]
    config = MessageHistoryConfig(messages=invalid_messages, debug=False)
    builder = MessageHistoryBuilder()
    result = builder.build(config)
    assert result == ""  # Should handle invalid format gracefully

def test_message_history_builder_special_chars():
    """Test MessageHistoryBuilder handles special characters."""
    messages = [
        {"role": "user", "content": "Hello\nWorld"},
        {"role": "assistant", "content": "Hi there!\t:)"}
    ]
    config = MessageHistoryConfig(messages=messages, debug=False)
    builder = MessageHistoryBuilder()
    result = builder.build(config)
    assert "Hello\nWorld" in result
    assert "Hi there!\t:)" in result
