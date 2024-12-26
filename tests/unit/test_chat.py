import pytest
import streamlit as st
from src.ui.chat_ui import init_chat_session

def test_chat_initialization(monkeypatch):
    """Test that chat session is initialized with welcome message"""
    # Mock streamlit session state
    class MockSessionState(dict):
        def __init__(self):
            super().__init__()
            self._dict = {}

        def __setattr__(self, key, value):
            if key == "_dict":
                super().__setattr__(key, value)
            else:
                self._dict[key] = value
                self[key] = value

        def __getattr__(self, key):
            if key == "_dict":
                return super().__getattr__(key)
            return self._dict[key]

        def __contains__(self, key):
            return key in self._dict

    mock_state = MockSessionState()
    monkeypatch.setattr(st, "session_state", mock_state)

    # Initialize chat
    init_chat_session()

    # Check that messages list exists and contains welcome message
    assert "messages" in st.session_state
    assert len(st.session_state.messages) == 1
    assert st.session_state.messages[0]["role"] == "assistant"

    # Check welcome message content
    welcome_content = st.session_state.messages[0]["content"]
    assert "JarvisOne" in welcome_content
    assert "recherche de fichiers" in welcome_content
    assert "👋" in welcome_content
