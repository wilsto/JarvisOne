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
    
    def process_user_input(self, user_input: str) -> str:
        """Process user input through the orchestrator and return formatted response."""
        logger.info(f"Processing user input: {user_input}")
        
        try:
            # Obtenir la réponse de l'orchestrateur
            response = self.orchestrator.process_query(user_input)
            
            # Formater la réponse pour l'affichage
            formatted_response = self._format_response(response)
            logger.info("Successfully processed and formatted response")
            
            return formatted_response
            
        except Exception as e:
            logger.error(f"Error in chat processor: {str(e)}", exc_info=True)
            return "Je suis désolé, j'ai rencontré une erreur en traitant votre demande."