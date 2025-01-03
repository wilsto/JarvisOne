"""Streamlit session state mock for testing."""

from unittest.mock import Mock

class SessionStateMock:
    """Mock class for Streamlit's session_state.
    
    Simulates the behavior of Streamlit's session_state by:
    1. Allowing attribute-style access (session_state.key)
    2. Returning None for undefined attributes
    3. Storing values in the underlying dictionary
    4. Supporting attribute deletion (del session_state.key)
    """
    def __init__(self):
        super().__init__()
        # Initialize common session state attributes
        self.interactions = []
        
        # Initialize workspace manager mock
        self.workspace_manager = Mock()
        self.workspace_manager.get_current_context_prompt.return_value = "Test system prompt"
        
        # Initialize other session state variables
        self.messages = []
        self.current_conversation_id = None
        
    def __setattr__(self, key: str, value):
        """Set attribute value."""
        self.__dict__[key] = value
        
    def __getattr__(self, key: str):
        """Get attribute value, return None if not found."""
        return self.__dict__.get(key)
        
    def __delattr__(self, key: str):
        """Delete attribute if it exists."""
        if key in self.__dict__:
            del self.__dict__[key]
