"""Chat agent with RAG capabilities."""

import logging
import streamlit as st
from typing import Optional, Dict, Any
from datetime import datetime
import uuid

from core.core_agent import CoreAgent
from rag.document_processor import DocumentProcessor
from rag.enhancer import RAGEnhancer, RAGConfig

logger = logging.getLogger(__name__)

def handle_chat_interaction(query: str, response: str) -> str:
    """Handle the display of chat response in the interface.
    
    Args:
        query: The user's query
        response: The agent's response
        
    Returns:
        str: The ID of the created interaction
    """
    if "interactions" not in st.session_state:
        st.session_state.interactions = []
    
    interaction_id = str(uuid.uuid4())
    logger.debug(f"Creating chat interaction with ID: {interaction_id}")
    logger.debug(f"Query: {query[:100]}...")
    
    interaction_data = {
        'id': interaction_id,
        'type': 'chat_response',
        'timestamp': datetime.now().strftime("%H:%M:%S"),
        'data': {
            'query': query,
            'response': response
        }
    }
    
    logger.debug(f"Adding chat interaction to session: {interaction_data}")
    st.session_state.interactions.append(interaction_data)
    return interaction_id

def handle_rag_interaction(query: str, results: list) -> str:
    """Handle the display of RAG results in the interface."""
    if "interactions" not in st.session_state:
        st.session_state.interactions = []
    
    interaction_id = str(uuid.uuid4())
    logger.debug(f"Creating RAG interaction with ID: {interaction_id}")
    
    # Convertir les résultats au bon format
    formatted_results = []
    for doc in results:
        # Convertir la distance en score de similarité (1 - distance normalisée)
        distance = doc.get('distance', 0)
        similarity_score = 1 - distance if distance <= 1 else 0
        
        formatted_results.append({
            'content': doc.get('content', '').strip(),
            'similarity_score': similarity_score,
            'metadata': doc.get('metadata', {})  # Utiliser les métadonnées telles quelles
        })
    
    interaction_data = {
        'id': interaction_id,
        'type': 'rag_search',
        'query': query,
        'results': formatted_results,
        'timestamp': datetime.now().strftime("%H:%M:%S")
    }
    
    logger.debug(f"Adding RAG interaction: {interaction_data}")
    st.session_state.interactions.append(interaction_data)
    return interaction_id

class ChatAgent:
    """Chat agent with RAG capabilities."""
    
    def __init__(self, base_agent: CoreAgent):
        """Initialize the chat agent.
        
        Args:
            base_agent: The base CoreAgent instance to use
        """
        self.base_agent = base_agent
        self.doc_processor = None
        self.rag_enhancer = None
        logger.info("Initialized ChatAgent with base agent")
        
    def configure_rag(self, config: RAGConfig):
        """Configure RAG capabilities for the agent.
        
        Args:
            config: RAG configuration settings
        """
        logger.info("Configuring RAG for chat agent")
        self.doc_processor = DocumentProcessor()
        self.rag_enhancer = RAGEnhancer(
            processor=self.base_agent,
            document_processor=self.doc_processor,
            rag_config=config,
            interaction_manager=handle_rag_interaction
        )
        logger.info("RAG configuration complete")
        
    async def process_message(self, message: str, workspace_id: str, **kwargs) -> str:
        """Process a user message.
        
        Args:
            message: The user's message
            workspace_id: ID of the current workspace
            **kwargs: Additional arguments
            
        Returns:
            str: The agent's response
        """
        try:
            # If RAG is configured, use it
            if self.rag_enhancer:
                logger.info(f"Processing message with RAG enhancement: {message[:100]}...")
                response = await self.rag_enhancer.process_message(message, workspace_id, **kwargs)
                logger.debug(f"RAG enhanced response: {response[:100]}...")
                return response
            else:
                # Otherwise use base agent and create chat interaction
                logger.info(f"Processing message with base agent: {message[:100]}...")
                response = await self.base_agent.process_message(message, workspace_id, **kwargs)
                logger.debug(f"Base agent response: {response[:100]}...")
                interaction_id = handle_chat_interaction(message, response)
                logger.info(f"Created chat interaction with ID: {interaction_id}")
                return response
            
        except Exception as e:
            logger.error(f"Error processing message: {str(e)}", exc_info=True)
            error_msg = f"Error processing message: {str(e)}"
            interaction_id = handle_chat_interaction(message, error_msg)
            logger.info(f"Created error chat interaction with ID: {interaction_id}")
            return error_msg

def get_base_agent() -> CoreAgent:
    """Get the base chat agent."""
    return CoreAgent(
        agent_name="Chat Agent",
        system_instructions="You are a helpful chat assistant that answers questions using available context.",
        interactions=handle_chat_interaction  # Pass the interaction handler directly
    )

# Create the base agent for discovery
base_agent = get_base_agent()

# Create the enhanced agent instance for usage
agent = ChatAgent(base_agent)
if "workspace_manager" in st.session_state:
    agent.configure_rag(RAGConfig(max_results=5, min_similarity=0.6))

if __name__ == '__main__':
    query = "Bonjour, comment allez-vous ?"
    response = agent.process_message(query, "workspace_id")
    print(response)