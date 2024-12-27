"""Process and route user chat inputs to appropriate agents."""

import logging
from typing import Any, Optional
from pathlib import Path
import streamlit as st

from .agents.agent_orchestrator import AgentOrchestrator
from core.database.repository import ConversationRepository
from core.analysis.conversation_analyzer import ConversationAnalyzer

# Configuration du logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

class ChatProcessor:
    """Main processor for chat interactions."""
    
    def __init__(self):
        """Initialize the chat processor with the orchestrator."""
        try:
            self.orchestrator = AgentOrchestrator()
            # Conservative default: 50 messages ≈ 25k tokens (assuming ~500 tokens per message)
            self.max_history_messages = 50
            
            # Initialize database
            db_path = Path(__file__).parent.parent.parent / "data" / "conversations.db"
            db_path.parent.mkdir(exist_ok=True)
            self.repository = ConversationRepository(str(db_path))
            self.analyzer = ConversationAnalyzer()
            
            logger.info("ChatProcessor initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize ChatProcessor: {str(e)}", exc_info=True)
            raise
        self._initialize_session_state()
    
    def _initialize_session_state(self):
        """Initialize session state for chat history."""
        if "messages" not in st.session_state:
            st.session_state.messages = []
        if "current_conversation_id" not in st.session_state:
            st.session_state.current_conversation_id = None
        logger.info("Session initialized")
            
    def _format_response(self, response: Any) -> str:
        """Format the response for display in chat.
        
        Args:
            response: Response from agent, can be:
                - Dict with 'content' or 'error' key
                - String (direct LLM response)
                - None (error case)
        
        Returns:
            str: Formatted response ready for display
        """
        # Handle None case
        if response is None:
            error_msg = "❌ Pas de réponse de l'agent"
            logger.warning("Agent returned None response")
            return error_msg
            
        # Handle dict case
        if isinstance(response, dict):
            if "error" in response:
                error_msg = f"❌ {response['error']}"
                logger.warning(f"Error in response: {error_msg}")
                return error_msg
            
            if "content" in response:
                return str(response["content"])
                
        # Handle string or other cases
        return str(response)
    
    def _format_conversation_history(self) -> str:
        """Format conversation history for context."""
        if not st.session_state.messages:
            return ""
        
        # Use configurable number of recent messages
        recent_messages = st.session_state.messages[-self.max_history_messages:]
        
        # Format messages with clear separation and metadata
        formatted_messages = []
        for msg in recent_messages:
            role = msg["role"].upper()
            content = msg["content"].strip()
            formatted_messages.append(f"[{role}]\n{content}\n")
        
        formatted_history = "\n".join(formatted_messages)
        
        return (
            "\n=== Conversation History ===\n"
            f"{formatted_history}\n"
            "=== End of History ===\n"
        )

    def set_history_limit(self, limit: int) -> None:
        """Set the maximum number of messages to include in conversation history.
        
        Args:
            limit (int): Maximum number of messages to keep in history
        """
        if limit < 1:
            logger.warning(f"Invalid history limit: {limit}. Using default.")
            return
            
        self.max_history_messages = limit
        logger.info(f"Updated conversation history limit to {limit} messages")

    def _combine_history_with_input(self, user_input: str) -> str:
        """Combine conversation history with new user input.
        
        Args:
            user_input: New user input to process
        
        Returns:
            str: Combined history and input ready for processing
        """
        history = self._format_conversation_history()
        if not history:
            return user_input
            
        return f"{history}\n[USER]\n{user_input}"

    def process_user_input(self, user_input: str) -> str:
        """Process user input through the orchestrator and return formatted response."""
        try:
            # Create conversation if this is the first interaction
            if st.session_state.current_conversation_id is None:
                conversation = self.repository.create_conversation()
                st.session_state.current_conversation_id = conversation.id
                logger.info(f"Created new conversation {conversation.id} on first interaction")
            
            # Combine history with input
            combined_input = self._combine_history_with_input(user_input)
            
            # Process through orchestrator
            response = self.orchestrator.process_query(combined_input)
            
            return self._format_response(response)
            
        except Exception as e:
            error_msg = f"Error processing input: {str(e)}"
            logger.error(error_msg, exc_info=True)
            return f"❌ {error_msg}"

    def load_conversation(self, conversation_id: str):
        """Load a specific conversation from the database."""
        conversation = self.repository.get_conversation(conversation_id)
        if conversation:
            st.session_state.messages = [
                {"role": msg["role"], "content": msg["content"]}
                for msg in conversation["messages"]
            ]
            st.session_state.current_conversation_id = conversation_id
            logger.info(f"Loaded conversation {conversation_id}")
        else:
            logger.warning(f"Conversation {conversation_id} not found")

    def new_conversation(self, workspace=None):
        """Start a new conversation."""
        st.session_state.messages = []
        if workspace is None:
            workspace = st.session_state.knowledge_space
        conversation = self.repository.create_conversation(workspace=workspace)
        st.session_state.current_conversation_id = conversation.id
        logger.info(f"Created new conversation {conversation.id} in workspace {workspace}")

    def get_recent_conversations(self, workspace=None, limit: int = 10):
        """Get recent conversations for display in sidebar."""
        return self.repository.get_recent_conversations(limit=limit, workspace=workspace)

    def _update_conversation_metadata(self):
        """Update conversation metadata based on current messages."""
        if not st.session_state.messages:
            return

        messages = [
            {
                "role": msg["role"],
                "content": msg["content"]
            }
            for msg in st.session_state.messages
        ]

        # Extract metadata
        title = self.analyzer.extract_title(messages)
        topics = self.analyzer.extract_topics(messages)
        summary = self.analyzer.generate_summary(messages)

        # Update in database
        self.repository.update_conversation_metadata(
            st.session_state.current_conversation_id,
            title=title,
            summary=summary,
            topics=topics
        )

    def add_message(self, role: str, content: str):
        """Add a message to the current conversation."""
        # Initialize messages list if needed
        if "messages" not in st.session_state:
            st.session_state.messages = []
            
        # Add to session state
        st.session_state.messages.append({"role": role, "content": content})
        
        # Persist to database
        self.repository.add_message(
            st.session_state.current_conversation_id,
            role=role,
            content=content
        )
        
        # Update metadata periodically (every 5 messages)
        if len(st.session_state.messages) % 5 == 0:
            self._update_conversation_metadata()

    def get_messages(self):
        """Get all messages in the current conversation."""
        return st.session_state.messages

    def delete_conversation(self, conversation_id: str):
        """Delete a conversation from the database."""
        try:
            self.repository.delete_conversation(conversation_id)
            if st.session_state.current_conversation_id == conversation_id:
                st.session_state.current_conversation_id = None
                st.session_state.messages = []
            logger.info(f"Deleted conversation {conversation_id}")
        except Exception as e:
            logger.error(f"Error deleting conversation: {str(e)}", exc_info=True)
            raise