"""Tests for UI styles management."""

import os
import pytest
from unittest.mock import mock_open, patch
from src.ui.styles import load_css, get_all_styles

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
    """Test combining all CSS files."""
    # Create a mock that returns different content for different files
    def mock_open_files(*args, **kwargs):
        file_path = args[0]
        file_name = os.path.basename(file_path)
        mock_file = mock_open(read_data=mock_css_files[file_name])()
        return mock_file
    
    with patch('builtins.open', side_effect=mock_open_files):
        combined_css = get_all_styles()
        
        # Verify all styles are included
        assert '.block-container' in combined_css
        assert '.log-entry' in combined_css
        assert '.result-row' in combined_css
        
        # Verify order (base.css should be first)
        first_style = combined_css.split('{')[0].strip()
        assert '.block-container' in first_style

def test_css_files_exist():
    """Test that all required CSS files exist."""
    style_dir = os.path.dirname(os.path.abspath(__file__))
    base_dir = os.path.join(style_dir, '..', '..', '..', '..', 'src', 'ui', 'styles')
    
    required_files = ['base.css', 'logs.css', 'interactions.css']
    for file in required_files:
        file_path = os.path.join(base_dir, file)
        assert os.path.exists(file_path), f"CSS file {file} not found"

def test_css_files_not_empty():
    """Test that CSS files have content."""
    style_dir = os.path.dirname(os.path.abspath(__file__))
    base_dir = os.path.join(style_dir, '..', '..', '..', '..', 'src', 'ui', 'styles')
    
    required_files = ['base.css', 'logs.css', 'interactions.css']
    for file in required_files:
        file_path = os.path.join(base_dir, file)
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read().strip()
            assert content, f"CSS file {file} is empty"
            assert '{' in content, f"CSS file {file} has no style rules"
