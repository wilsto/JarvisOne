"""Test utilities."""

import pytest
from unittest.mock import Mock, patch
import streamlit as st
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum, auto

class SpaceType(Enum):
    """Enum for workspace types."""
    AGNOSTIC = auto()
    COACHING = auto()
    DEV = auto()
    PERSONAL = auto()
    WORK = auto()

@dataclass
class Conversation:
    """Mock conversation model."""
    id: str
    title: Optional[str]
    workspace: SpaceType
    created_at: str
    updated_at: str

class MockDatabase:
    """Mock class for conversation database.
    
    Cette classe simule une base de données de conversations avec :
    1. Une table conversations pour stocker les métadonnées des conversations
    2. Une table messages pour stocker les messages de chaque conversation
    3. Des méthodes pour créer, lire et mettre à jour les conversations et messages
    """
    def __init__(self):
        self.conversations: Dict[str, Conversation] = {}
        self.messages: Dict[str, List[Dict]] = {}
        self._next_conversation_id = 1
        self._next_message_id = 1
    
    def create_conversation(self, title: Optional[str] = None, workspace: SpaceType = SpaceType.AGNOSTIC) -> Conversation:
        """Create a new conversation."""
        conversation_id = str(self._next_conversation_id)
        self._next_conversation_id += 1
        
        conversation = Conversation(
            id=conversation_id,
            title=title or "New Conversation",
            workspace=workspace,
            created_at=datetime.now().isoformat(),
            updated_at=datetime.now().isoformat()
        )
        
        self.conversations[conversation_id] = conversation
        self.messages[conversation_id] = []
        return conversation
    
    def get_conversation(self, conversation_id: str) -> Optional[Conversation]:
        """Get conversation by ID."""
        return self.conversations.get(conversation_id)
    
    def list_conversations(self, workspace: Optional[SpaceType] = None) -> List[Conversation]:
        """List all conversations, optionally filtered by workspace."""
        conversations = list(self.conversations.values())
        if workspace:
            conversations = [c for c in conversations if c.workspace == workspace]
        return sorted(conversations, key=lambda x: x.updated_at, reverse=True)
    
    def add_message(self, conversation_id: str, role: str, content: str) -> str:
        """Add a message to a conversation."""
        if conversation_id not in self.conversations:
            raise ValueError(f"Conversation {conversation_id} not found")
            
        message_id = str(self._next_message_id)
        self._next_message_id += 1
        
        message = {
            "id": message_id,
            "conversation_id": conversation_id,
            "role": role,
            "content": content,
            "created_at": datetime.now().isoformat()
        }
        
        self.messages[conversation_id].append(message)
        
        # Update conversation
        conversation = self.conversations[conversation_id]
        conversation.updated_at = datetime.now().isoformat()
        
        return message_id
    
    def get_messages(self, conversation_id: str) -> List[Dict]:
        """Get all messages for a conversation."""
        if conversation_id not in self.conversations:
            raise ValueError(f"Conversation {conversation_id} not found")
        return self.messages[conversation_id]
    
    def clear(self):
        """Clear all data."""
        self.conversations.clear()
        self.messages.clear()
        self._next_conversation_id = 1
        self._next_message_id = 1

@pytest.fixture
def mock_database():
    """Fixture to provide a mock database.
    
    This fixture:
    1. Creates a new MockDatabase instance
    2. Yields it for the test
    3. Clears all data after the test
    """
    db = MockDatabase()
    yield db
    db.clear()

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
        
        # Initialize workspace manager mock
        self.workspace_manager = Mock()
        self.workspace_manager.get_current_context_prompt.return_value = "Test system prompt"
        
        # Initialize other session state variables
        self.messages = []
        self.current_conversation_id = None
    
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
    
    # Create new mock session state
    st.session_state = MockSessionState()
    
    yield st.session_state
    
    # Restore original session state
    if original_session_state is not None:
        st.session_state = original_session_state

@dataclass
class MockRAGDocument:
    """Mock RAG document for testing."""
    content: str
    metadata: dict
    distance: float
    
    def to_dict(self) -> dict:
        """Convert to dictionary format."""
        return {
            "content": self.content,
            "metadata": self.metadata,
            "distance": self.distance
        }

class RAGTestUtils:
    """Utility class for RAG testing."""
    @staticmethod
    def create_mock_embeddings(dimensions: int = 3) -> List[float]:
        """Create mock embeddings vector."""
        return [1.0] + [0.0] * (dimensions - 1)
        
    @staticmethod
    def create_mock_documents(count: int = 1, base_similarity: float = 0.9) -> List[dict]:
        """Create mock RAG documents with decreasing similarity."""
        return [
            MockRAGDocument(
                content=f"test document {i}",
                metadata={"source": "test"},
                distance=1 - (base_similarity - (0.1 * i))
            ).to_dict() for i in range(count)
        ]
