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


class ChatProcessor:
    """Main processor for chat interactions."""
    
    def __init__(self):
        """Initialize the chat processor with the orchestrator."""
        try:
            self.orchestrator = AgentOrchestrator()
            # Conservative default: 50 messages ≈ 25k tokens (assuming ~500 tokens per message)
            self.max_history_messages = 50  # TODO: Implement message history limit in add_message method
            
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
            
    def update_workspace(self):
        """Update the chat processor for workspace change."""
        # Update LLM model with new workspace configuration
        self.orchestrator.update_llm()
        logger.info("Updated chat processor for workspace change")
            
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
            error_msg = "❌ No response from agent"
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

    def process_user_input(self, user_input: str) -> str:
        """Process user input through the orchestrator and return formatted response."""
        try:
            # Get current workspace and role info
            workspace = getattr(st.session_state, 'workspace', None)
            workspace_id = workspace.name if workspace else None
            role_id = getattr(st.session_state, 'current_role', None)
            
            logger.info(f"Processing input with workspace={workspace}, workspace_id={workspace_id}, role_id={role_id}")
            
            # Create conversation if this is the first interaction
            if st.session_state.current_conversation_id is None:
                # Extract initial title from first message
                initial_title = self.analyzer.extract_title([{"role": "user", "content": user_input}])
                workspace = getattr(st.session_state, 'pending_workspace', workspace)
                conversation = self.repository.create_conversation(title=initial_title, workspace=workspace)
                st.session_state.current_conversation_id = conversation.id
                if hasattr(st.session_state, 'pending_workspace'):
                    delattr(st.session_state, 'pending_workspace')
                logger.info(f"Created new conversation {conversation.id} with title '{initial_title}' in workspace {workspace}")
            
            # Add user message to history
            self.add_message("user", user_input)
            
            # Process through orchestrator with context
            response = self.orchestrator.process_query(
                user_input,  # No need to combine with history as CoreAgent now handles it
                workspace_id=workspace_id,
                role_id=role_id
            )
            
            # Format and add response to history
            formatted_response = self._format_response(response)
            self.add_message("assistant", formatted_response)
            
            # Update conversation metadata
            self._update_conversation_metadata()
            
            return formatted_response
            
        except Exception as e:
            error_msg = f"Error processing input: {str(e)}"
            logger.error(error_msg, exc_info=True)
            return f"❌ {error_msg}"

    def load_conversation(self, conversation_id: str):
        """Load a specific conversation from the database.
        
        Args:
            conversation_id (str): ID of the conversation to load
        
        Returns:
            bool: True if conversation loaded successfully, False otherwise
        """
        try:
            # Set loading state
            st.session_state.loading_conversation = True
            
            # Load conversation from repository
            conversation = self.repository.get_conversation(conversation_id)
            if not conversation:
                logger.warning(f"Conversation {conversation_id} not found")
                return False
                
            # Update session state with conversation messages
            st.session_state.messages = [
                {"role": msg["role"], "content": msg["content"]}
                for msg in conversation["messages"]
            ]
            st.session_state.current_conversation_id = conversation_id
            
            # Force streamlit to rerun to update UI
            st.session_state.should_rerun = True
            
            logger.info(f"Loaded conversation {conversation_id}")
            return True
            
        except Exception as e:
            error_msg = f"Failed to load conversation {conversation_id}: {str(e)}"
            logger.error(error_msg, exc_info=True)
            return False
            
        finally:
            # Clear loading state
            st.session_state.loading_conversation = False

    def new_conversation(self, workspace=None):
        """Start a new conversation."""
        st.session_state.messages = []
        st.session_state.current_conversation_id = None
        st.session_state.pending_workspace = workspace if workspace is not None else st.session_state.workspace
        logger.info(f"Prepared new conversation in workspace {workspace}")

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
            
        # Prevent duplicate messages during re-runs
        if st.session_state.messages and \
           st.session_state.messages[-1]["role"] == role and \
           st.session_state.messages[-1]["content"] == content:
            logger.debug("Skipping duplicate message")
            return
            
        # Add to session state
        st.session_state.messages.append({"role": role, "content": content})
        
        # Create conversation only for user messages if none exists
        if role == "user" and (not hasattr(st.session_state, 'current_conversation_id') or st.session_state.current_conversation_id is None):
            # Create new conversation
            initial_title = self.analyzer.extract_title([{"role": role, "content": content}])
            workspace = getattr(st.session_state, 'pending_workspace', st.session_state.workspace)
            conversation = self.repository.create_conversation(title=initial_title, workspace=workspace)
            st.session_state.current_conversation_id = conversation.id
            if hasattr(st.session_state, 'pending_workspace'):
                delattr(st.session_state, 'pending_workspace')
            logger.info(f"Created new conversation {conversation.id} with title '{initial_title}' in workspace {workspace}")
            
            # Now add all previous messages to the conversation
            for msg in st.session_state.messages[:-1]:  # All messages except the current one
                self.repository.add_message(
                    conversation.id,
                    role=msg["role"],
                    content=msg["content"]
                )
        
        # Persist current message to database if we have a conversation
        if hasattr(st.session_state, 'current_conversation_id') and st.session_state.current_conversation_id:
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