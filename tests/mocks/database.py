"""Database mock for testing."""

from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass

from ..types.workspace import SpaceType

@dataclass
class Conversation:
    """Mock conversation model."""
    id: str
    title: Optional[str]
    workspace: SpaceType
    created_at: str
    updated_at: str

class DatabaseMock:
    """Mock class for conversation database.
    
    Simulates a database of conversations with:
    1. A conversations table for storing conversation metadata
    2. A messages table for storing messages of each conversation
    3. Methods for creating, reading and updating conversations and messages
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
