import pytest
from streamlit.testing.v1 import AppTest

@pytest.fixture
def chat_app():
    # Increase timeout to 10 seconds
    return AppTest.from_file("src/main.py", default_timeout=10)

def test_chat_welcome_message(chat_app):
    """Test that welcome message appears correctly"""
    chat_app.run()
    
    # Check for no exceptions during startup
    assert not chat_app.exception
    
    # Test presence of welcome message parts
    welcome_texts = [elem.value for elem in chat_app.markdown]
    welcome_text = "".join(welcome_texts)
    assert "JarvisOne" in welcome_text
    assert "recherche de fichiers" in welcome_text
    assert "Comment puis-je vous aider" in welcome_text

def test_chat_interface_elements(chat_app):
    """Test that chat interface elements exist"""
    chat_app.run()
    
    # Check for no exceptions
    assert not chat_app.exception
    
    # Check for chat input
    chat_inputs = chat_app.text_input
    assert len(chat_inputs) > 0  # At least one text input should exist
