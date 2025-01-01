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

def handle_chat_interaction(query: str, response: str, rag_interaction_id: str = None) -> str:
    """Handle the display of chat response in the interface.
    
    Args:
        query: The user's query
        response: The agent's response
        rag_interaction_id: Optional ID of related RAG interaction
        
    Returns:
        str: The ID of the created interaction
    """
    if "interactions" not in st.session_state:
        st.session_state.interactions = []
    
    interaction_id = str(uuid.uuid4())
    interaction_data = {
        'id': interaction_id,
        'type': 'chat_response',
        'timestamp': datetime.now().strftime("%H:%M:%S"),
        'data': {
            'query': query,
            'response': response
        }
    }
    
    # Link to RAG interaction if present
    if rag_interaction_id:
        interaction_data['data']['rag_interaction_id'] = rag_interaction_id
    
    st.session_state.interactions.append(interaction_data)
    return interaction_id

def handle_rag_interaction(query: str, results: list) -> str:
    """Handle the display of RAG results in the interface.
    
    Args:
        query: The search query
        results: List of search results with scores
        
    Returns:
        str: The ID of the created interaction
    """
    if "interactions" not in st.session_state:
        st.session_state.interactions = []
    
    interaction_id = str(uuid.uuid4())
    st.session_state.interactions.append({
        'id': interaction_id,
        'type': 'rag_search',
        'timestamp': datetime.now().strftime("%H:%M:%S"),
        'data': {
            'query': query,
            'results': results
        }
    })
    return interaction_id

# Create the base agent first as a CoreAgent instance
def get_base_agent() -> CoreAgent:
    """Get the base chat agent."""
    return CoreAgent(
        agent_name="Chat Agent",
        system_instructions="You are a helpful chat assistant that answers questions using available context.",
        interactions=handle_chat_interaction  # Pass the interaction handler directly
    )

def get_chat_agent() -> CoreAgent:
    """Get a configured chat agent with RAG capabilities."""
    
    # Get base agent
    base_agent = get_base_agent()
    
    # Initialize document processor
    doc_processor = DocumentProcessor()
    
    # Configure RAG
    rag_config = RAGConfig(
        max_results=5,
        min_similarity=0.6
    )
    
    # Enhance with RAG capabilities
    return RAGEnhancer(
        processor=base_agent,
        document_processor=doc_processor,
        rag_config=rag_config,
        interaction_manager=handle_rag_interaction  # Pass the RAG interaction handler
    )

# Create the base agent for discovery
base_agent = get_base_agent()

# Create the enhanced agent instance for usage
agent = get_chat_agent()

if __name__ == '__main__':
    query = "Bonjour, comment allez-vous ?"
    response = agent.run(query)
    print(response['content'])