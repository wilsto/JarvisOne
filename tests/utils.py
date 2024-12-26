"""Utilities for testing."""

import pytest
import streamlit as st

class MockSessionState(dict):
    """Mock class for Streamlit's session_state.
    
    This class simulates the behavior of Streamlit's session_state by:
    1. Allowing attribute-style access (session_state.key)
    2. Returning None for undefined attributes
    3. Storing values in the underlying dictionary
    4. Supporting attribute deletion (del session_state.key)
    """
    def __init__(self):
        super().__init__()
        # Initialize common session state attributes
        self.interactions = []
    
    def __setattr__(self, key, value):
        self[key] = value
    
    def __getattr__(self, key):
        if key not in self:
            return None
        return self[key]
    
    def __delattr__(self, key):
        if key in self:
            del self[key]

@pytest.fixture
def mock_session_state():
    """Fixture to provide a mock Streamlit session state.
    
    This fixture:
    1. Removes any existing session_state
    2. Creates a new MockSessionState instance
    3. Restores the original session_state after the test
    """
    # Save original session state if it exists
    original_session_state = getattr(st, 'session_state', None)
    
    # Reset session state before each test
    if hasattr(st, 'session_state'):
        delattr(st, 'session_state')
    st.session_state = MockSessionState()
    
    yield st.session_state
    
    # Restore original session state
    if original_session_state is not None:
        st.session_state = original_session_state
