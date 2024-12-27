"""Process and route user chat inputs to appropriate agents."""

import logging
from typing import Any
import streamlit as st

from .agents.agent_orchestrator import AgentOrchestrator

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
            logger.info("AgentOrchestrator initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize AgentOrchestrator: {str(e)}", exc_info=True)
            raise
        self._initialize_session_state()
    
    def _initialize_session_state(self):
        """Initialize session state for chat history."""
        if "messages" not in st.session_state:
            st.session_state.messages = []
            logger.info("Created new messages list in session state")
    
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

    def process_user_input(self, user_input: str) -> str:
        """Process user input through the orchestrator and return formatted response."""
        logger.info(f"Processing user input: {user_input}")
        
        try:
            # Add conversation history to context
            context = self._format_conversation_history()
            
            # Create system context to help LLM understand the conversation format
            system_context = (
                "You are JarvisOne, an AI assistant. Below is the conversation history "
                "followed by the current user input. Use this context to provide a relevant "
                "and contextually appropriate response."
            )
            
            # Combine all context elements
            enriched_input = (
                f"{system_context}\n\n"
                f"{context}\n"
                f"[CURRENT USER INPUT]\n{user_input}\n"
            )
            
            # Get response from orchestrator
            response = self.orchestrator.process_query(enriched_input)
            
            # Format the response for display
            formatted_response = self._format_response(response)
            logger.info("Successfully processed and formatted response")
            
            return formatted_response
            
        except Exception as e:
            logger.error(f"Error in chat processor: {str(e)}", exc_info=True)
            return "Je suis désolé, j'ai rencontré une erreur en traitant votre demande."