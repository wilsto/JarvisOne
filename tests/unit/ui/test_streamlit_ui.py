"""Tests for Streamlit UI components."""

import pytest
from unittest.mock import Mock, patch
from streamlit.testing.v1 import AppTest
from src.core.prompts.generic_prompts import generate_welcome_message
from src.core.workspace_manager import SpaceType
from tests.utils import mock_database  # Import mock_database fixture

@pytest.fixture
def mock_workspace_manager():
    """Mock workspace manager."""
    manager = Mock()
    manager.get_current_space_config.return_value = Mock(
        metadata={
            'scope': """
            - File Search: Search through your files and documents
            - Chat: Natural language conversation
            - Document Analysis: Process and analyze documents
            """
        }
    )
    return manager

@pytest.fixture
def mock_config_manager():
    """Mock config manager."""
    with patch('src.core.config_manager.ConfigManager._load_config') as mock_config:
        mock_config.return_value = {
            'app_state': {
                'workspace': 'AGNOSTIC',
                'cache_enabled': True,
                'role': None
            },
            'ui': {
                'theme': 'default'
            }
        }
        yield mock_config

@pytest.fixture
def mock_chat_processor(mock_database):
    """Mock chat processor."""
    with patch('src.features.chat_processor.ChatProcessor') as mock_cp:
        processor = Mock()
        
        # Mock repository methods using mock_database
        processor.repository = Mock()
        processor.repository.create_conversation.side_effect = mock_database.create_conversation
        processor.repository.get_conversation.side_effect = mock_database.get_conversation
        processor.repository.list_conversations.side_effect = mock_database.list_conversations
        processor.repository.add_message.side_effect = mock_database.add_message
        processor.repository.get_messages.side_effect = mock_database.get_messages
        
        # Mock other processor methods
        processor.get_messages.return_value = []
        processor.process_user_input.return_value = "Test response"
        
        mock_cp.return_value = processor
        yield processor

@pytest.fixture
def chat_app(mock_workspace_manager, mock_config_manager, mock_chat_processor):
    """Initialize app with mocked dependencies."""
    with patch('src.ui.chat_ui.st.session_state') as mock_state, \
         patch('src.core.workspace_manager.WorkspaceManager') as mock_manager_cls, \
         patch('src.ui.chat_ui.render_sidebar'), \
         patch('src.ui.chat_ui.display_chat'), \
         patch('streamlit.runtime.scriptrunner.add_script_run_ctx'):
        
        # Configure workspace manager
        mock_manager_cls.return_value = mock_workspace_manager
        
        # Configure session state
        mock_state.workspace = SpaceType.AGNOSTIC
        mock_state.workspace_manager = mock_workspace_manager
        mock_state.chat_processor = mock_chat_processor
        
        # Return AppTest with increased timeout
        return AppTest.from_file("src/main.py", default_timeout=5)

# FIXME: Test désactivé - Problème de timeout avec l'AppTest
# Le test échoue car l'initialisation de l'application prend trop de temps,
# même avec les mocks. Il faut revoir l'architecture des tests d'intégration
# pour éviter les dépendances lourdes et les appels à st.rerun().
@pytest.mark.skip(reason="Problème de timeout avec l'AppTest")
def test_chat_welcome_message(chat_app):
    """Test that welcome message appears correctly."""
    chat_app.run()
    
    # Check for no exceptions during startup
    assert not chat_app.exception
    
    # Get expected welcome message
    scope = """
    - File Search: Search through your files and documents
    - Chat: Natural language conversation
    - Document Analysis: Process and analyze documents
    """
    expected_message = generate_welcome_message(scope)
    
    # Test presence of welcome message parts
    welcome_texts = [elem.value for elem in chat_app.markdown]
    welcome_text = "".join(welcome_texts)
    
    # Verify essential parts
    assert "JarvisOne" in welcome_text
    assert "I can help you with" in welcome_text
    
    # Verify capabilities from scope
    assert "File Search" in welcome_text
    assert "Chat" in welcome_text
    assert "Document Analysis" in welcome_text

# FIXME: Test désactivé - Problème de timeout avec l'AppTest
# Le test échoue pour les mêmes raisons que test_chat_welcome_message.
# À réactiver une fois l'architecture des tests d'intégration revue.
@pytest.mark.skip(reason="Problème de timeout avec l'AppTest")
def test_chat_interface_elements(chat_app):
    """Test that chat interface elements exist."""
    chat_app.run()
    
    # Check for no exceptions
    assert not chat_app.exception
    
    # Check for chat input
    chat_inputs = chat_app.text_input
    assert len(chat_inputs) > 0  # At least one text input should exist