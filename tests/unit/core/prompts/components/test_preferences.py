"""Tests for the preferences builder component."""

import pytest
from unittest.mock import patch
from core.prompts.components import PreferencesBuilder, PreferencesConfig

def test_preferences_basic():
    """Test basic preferences building."""
    config = PreferencesConfig(
        creativity_level=1,
        style_level=1,
        length_level=1,
        debug=False
    )
    
    result = PreferencesBuilder.build(config)
    
    assert "Core characteristics:" in result
    assert "Communication style:" in result
    assert "Response length guideline:" in result

def test_preferences_strict_mode():
    """Test preferences in strict mode."""
    config = PreferencesConfig(
        creativity_level=0,
        style_level=0,
        length_level=0,
        debug=False
    )
    
    result = PreferencesBuilder.build(config)
    
    assert "Strict" in result
    assert "Professional" in result
    assert "Be extremely concise" in result

def test_preferences_creative_mode():
    """Test preferences in creative mode."""
    config = PreferencesConfig(
        creativity_level=2,
        style_level=2,
        length_level=2,
        debug=False
    )
    
    result = PreferencesBuilder.build(config)
    
    assert "Creative" in result
    assert "Fun" in result
    assert "Provide comprehensive explanations" in result

@patch('streamlit.session_state')
def test_preferences_from_session_state(mock_session_state):
    """Test preferences building from session state."""
    mock_session_state.get.side_effect = lambda key, default: {
        'llm_creativity': 1,
        'llm_style': 1,
        'llm_length': 1
    }.get(key, default)
    
    result = PreferencesBuilder.build()
    
    assert "Core characteristics:" in result
    assert "Communication style:" in result
    assert "Response length guideline:" in result

def test_preferences_debug_mode():
    """Test preferences in debug mode."""
    config = PreferencesConfig(
        creativity_level=1,
        style_level=1,
        length_level=1,
        debug=True
    )
    
    result = PreferencesBuilder.build(config)
    
    assert "=== Preferences ===" in result
    assert "Core characteristics:" in result
    assert "Communication style:" in result
    assert "Response length guideline:" in result

def test_preferences_error_handling(caplog):
    """Test error handling in preferences building."""
    config = PreferencesConfig(
        creativity_level=999,  # Invalid level
        style_level=1,
        length_level=1,
        debug=False
    )
    
    # Test return value
    result = PreferencesBuilder.build(config)
    assert result == ""
    
    # Test error logging
    assert "Error building preferences: 999" in caplog.text
    assert "ERROR" in caplog.text
