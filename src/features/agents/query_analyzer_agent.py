import logging
from core.core_agent import CoreAgent
from core.llm_base import LLM
import streamlit as st
from datetime import datetime
import uuid

# Configure logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

AGENT_SELECTION_PROMPT = """
Analyze the user query and determine which agent should handle it.

For file search agent:
- Query is about searching or manipulating files
- Contains words like: file, find, search, modified, created
- Mentions file extensions (.py, .txt, etc.) or file types (python, text, etc.)
- Contains date modifiers (today, yesterday, last week)

For chat agent:
- Not about file search
- General questions or conversations
- Code-related questions
- Task planning or organization
- Any other topic not covered by file search

Return ONLY 'file_search_agent' or 'chat_agent' based on the query.
"""

def analyze_query_tool(query: str, llm: LLM) -> str:
    """
    Query analysis tool to determine the appropriate agent.
    
    Args:
        query: The user's query.
        llm: Shared LLM instance to use.
        
    Returns:
        The name of the agent to use.
    """
    # Use shared LLM for analysis
    prompt = AGENT_SELECTION_PROMPT + f"\n\nQuery: {query}\n\n"
    response = llm.generate_response(prompt).lower().strip()
    logger.info(f"Query: '{query}' → Agent selected: '{response}'")
    
    # Create analysis
    analysis = {
        'agent_selected': response,
        'reason': 'File search' if response == 'file_search_agent' else 'General question'
    }
    
    # Create interaction
    handle_query_interaction(query, analysis)
    
    # Check if response is a valid agent
    if response in ['file_search_agent', 'chat_agent']:
        return response
    
    # Default to chat agent
    logger.warning(f"Unrecognized agent '{response}', defaulting to chat_agent")
    return "chat_agent"

def handle_query_interaction(transformed_query: str, analysis: dict) -> str:
    """Handle the display of query analysis in the interface.
    
    Args:
        transformed_query: The analyzed query
        analysis: The analysis result
        
    Returns:
        str: The ID of the created interaction
    """
    if "interactions" not in st.session_state:
        st.session_state.interactions = []
    
    interaction_id = str(uuid.uuid4())
    st.session_state.interactions.append({
        'id': interaction_id,
        'type': 'query_analyzer',
        'query': transformed_query,
        'analysis': analysis,
        'timestamp': datetime.now().strftime("%H:%M:%S")
    })
    
    return interaction_id

# Create query analyzer agent instance
agent = CoreAgent(
    agent_name="Query Analyzer Agent",
    system_instructions=[
        "You are a query analyzer that helps understand user intentions.",
        "Analyze the query and identify key components.",
        "",
        "CRITICAL OUTPUT FORMAT RULES:",
        "1. Output ONLY the raw analysis as JSON",
        "2. NO explanations or comments",
        "3. NO line breaks or extra spaces",
    ],
    output_formatter=None,  # No special formatter needed
    interactions=handle_query_interaction
)

if __name__ == '__main__':
    from core.llm_manager import get_llm_model
    llm = get_llm_model()
    query = "find a pdf file"
    response = analyze_query_tool(query, llm)
    print(f"Selected agent: {response}")