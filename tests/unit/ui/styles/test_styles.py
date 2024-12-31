"""Tests for UI styles management."""

import os
import pytest
from unittest.mock import mock_open, patch
from src.ui.styles import load_css, get_all_styles

# Get the absolute path to the styles directory
STYLES_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../src/ui/styles'))

@pytest.fixture
def mock_css_files():
    """Mock CSS files content."""
    css_files = {
        'base.css': """
            .block-container { padding: 2rem; }
            .stTabs { background-color: #f8f9fa; }
        """,
        'logs.css': """
            .log-entry { font-family: 'Consolas'; }
            .filter-button { float: right; }
        """,
        'interactions.css': """
            .result-row { display: flex; }
            .file-name { font-weight: bold; }
        """,
        'sidebar.css': """
            .sidebar { width: 300px; }
            .workspace-selector { margin-top: 1rem; }
        """
    }
    return css_files

def test_load_css(mock_css_files):
    """Test loading a single CSS file."""
    test_css = mock_css_files['base.css']
    
    with patch('builtins.open', mock_open(read_data=test_css)) as mock_file:
        css_content = load_css('base.css')
        
        # Verify file was opened correctly
        mock_file.assert_called_once()
        assert 'base.css' in str(mock_file.call_args[0][0])
        
        # Verify content was loaded
        assert '.block-container' in css_content
        assert '.stTabs' in css_content

def test_load_css_file_not_found():
    """Test loading a non-existent CSS file."""
    with pytest.raises(FileNotFoundError):
        load_css('nonexistent.css')

def test_get_all_styles(mock_css_files):
    """Test loading all CSS styles."""
    # Create mock for each CSS file
    mock_files = {}
    for filename, content in mock_css_files.items():
        mock_files[os.path.join(STYLES_DIR, filename)] = mock_open(read_data=content).return_value
    
    def mock_open_factory(filename, *args, **kwargs):
        return mock_files[filename]
    
    with patch('builtins.open', side_effect=mock_open_factory):
        styles = get_all_styles()
        
        # Verify all styles were loaded
        for content in mock_css_files.values():
            for line in content.splitlines():
                if line.strip():
                    assert line.strip() in styles

def test_css_files_exist():
    """Test that all required CSS files exist."""
    required_files = ["base.css", "logs.css", "interactions.css", "sidebar.css"]
    
    for filename in required_files:
        file_path = os.path.join(STYLES_DIR, filename)
        assert os.path.exists(file_path), f"Missing CSS file: {filename}"

def test_css_files_not_empty():
    """Test that CSS files have content."""
    required_files = ["base.css", "logs.css", "interactions.css", "sidebar.css"]
    
    for filename in required_files:
        file_path = os.path.join(STYLES_DIR, filename)
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read().strip()
            assert content, f"Empty CSS file: {filename}"
