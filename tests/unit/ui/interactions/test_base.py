"""Tests for base interaction display."""
import pytest
from src.ui.interactions.base import BaseInteractionDisplay
from typing import Dict, Any

class ConcreteDisplay(BaseInteractionDisplay):
    """Concrete implementation for testing."""
    def display(self, interaction: Dict[str, Any]) -> None:
        """Display the interaction."""
        pass

@pytest.fixture
def display_handler():
    """Fixture providing a concrete display handler."""
    return ConcreteDisplay()

@pytest.fixture
def sample_interaction():
    """Fixture providing a sample interaction."""
    return {
        'id': 'test-id-123',
        'type': 'test',
        'timestamp': '15:30:00'
    }

def test_get_expander_title(display_handler, sample_interaction):
    """Test default expander title formatting."""
    title = display_handler.get_expander_title(sample_interaction)
    # Test without emoji to avoid encoding issues
    assert sample_interaction['timestamp'] in title

def test_abstract_methods():
    """Test that abstract methods are enforced."""
    # Attempting to instantiate the abstract base class should raise TypeError
    with pytest.raises(TypeError):
        BaseInteractionDisplay()

def test_concrete_implementation(display_handler):
    """Test that concrete implementation can be instantiated."""
    # Should not raise any exception
    assert isinstance(display_handler, BaseInteractionDisplay)
    assert isinstance(display_handler, ConcreteDisplay)
