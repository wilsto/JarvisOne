"""Tests for interaction display factory."""
import pytest
from unittest.mock import Mock, patch
import streamlit as st
from src.ui.interactions.factory import (
    InteractionDisplayFactory,
    DefaultDisplay,
    BaseInteractionDisplay
)

class CustomTestDisplay(BaseInteractionDisplay):
    """Custom display handler for testing."""
    def display(self, interaction):
        """Test display method."""
        pass

@pytest.fixture
def reset_factory():
    """Reset factory handlers before each test."""
    InteractionDisplayFactory._handlers = {}
    yield
    InteractionDisplayFactory._handlers = {}

@pytest.fixture
def sample_interaction():
    """Fixture providing a sample interaction."""
    return {
        'id': 'test-id-123',
        'type': 'test_type',
        'content': 'test content',
        'timestamp': '15:30:00'
    }

def test_default_handler(reset_factory, sample_interaction):
    """Test that default handler is used when no specific handler is registered."""
    handler = InteractionDisplayFactory.get_display_handler("unknown_type")
    assert isinstance(handler, DefaultDisplay)

def test_register_and_get_handler(reset_factory):
    """Test registration and retrieval of custom handlers."""
    # Register custom handler
    InteractionDisplayFactory.register_handler("custom_type", CustomTestDisplay)
    
    # Get handler
    handler = InteractionDisplayFactory.get_display_handler("custom_type")
    assert isinstance(handler, CustomTestDisplay)

def test_default_display_implementation(reset_factory, sample_interaction):
    """Test that DefaultDisplay correctly displays interaction as JSON."""
    with patch('streamlit.json') as mock_json:
        # Create and use default display
        display = DefaultDisplay()
        display.display(sample_interaction)
        
        # Verify JSON display
        mock_json.assert_called_once_with(sample_interaction)

def test_override_handler(reset_factory):
    """Test that handlers can be overridden."""
    # Register initial handler
    InteractionDisplayFactory.register_handler("test_type", CustomTestDisplay)
    
    # Create new handler class
    class NewTestDisplay(BaseInteractionDisplay):
        def display(self, interaction):
            pass
    
    # Override handler
    InteractionDisplayFactory.register_handler("test_type", NewTestDisplay)
    
    # Get handler and verify it's the new one
    handler = InteractionDisplayFactory.get_display_handler("test_type")
    assert isinstance(handler, NewTestDisplay)
    assert not isinstance(handler, CustomTestDisplay)

def test_multiple_handlers(reset_factory):
    """Test registration and retrieval of multiple handlers."""
    # Create additional test handler
    class AnotherTestDisplay(BaseInteractionDisplay):
        def display(self, interaction):
            pass
    
    # Register multiple handlers
    handlers = {
        "type1": CustomTestDisplay,
        "type2": AnotherTestDisplay
    }
    
    for type_name, handler_class in handlers.items():
        InteractionDisplayFactory.register_handler(type_name, handler_class)
    
    # Verify each handler
    for type_name, handler_class in handlers.items():
        handler = InteractionDisplayFactory.get_display_handler(type_name)
        assert isinstance(handler, handler_class)
