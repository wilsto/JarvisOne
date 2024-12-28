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
Given a user query and a list of available agents with their system prompts, determine which agent is best suited to handle the query.

For each agent, you will receive:
- agent_name: The name of the agent
- system_prompt: The agent's system prompt that defines its capabilities and purpose

Analyze the query against each agent's system prompt to determine which agent's capabilities best match the user's needs.

Return ONLY the agent's name (without '_agent' suffix) based on the query.
"""

def analyze_query_tool(query: str, llm: LLM, available_agents: dict) -> str:
    """
    Query analysis tool to determine the appropriate agent.
    
    Args:
        query: The user's query.
        llm: Shared LLM instance to use.
        available_agents: Dictionary of available agents with their system prompts
        
    Returns:
        The name of the agent to use.
    """
    # Format agents info for the prompt
    agents_info = "\nAvailable Agents:\n"
    for name, agent in available_agents.items():
        agents_info += f"\nAgent Name: {name}\n"
        agents_info += f"System Prompt:\n{agent.system_instructions}\n"
    
    # Use shared LLM for analysis
    prompt = AGENT_SELECTION_PROMPT + agents_info + f"\n\nUser Query: {query}\n\n"
    response = llm.generate_response(prompt).lower().strip()
    
    # Validate response
    if response not in available_agents:
        logger.warning(f"Invalid agent selection '{response}', defaulting to 'chat'")
        return 'chat'
    
    return response

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
    available_agents = {
        "file_search_agent": CoreAgent(
            agent_name="File Search Agent",
            system_instructions=[
                "You are a file search agent that helps find files.",
                "Analyze the query and identify file search keywords.",
                "",
                "CRITICAL OUTPUT FORMAT RULES:",
                "1. Output ONLY the raw analysis as JSON",
                "2. NO explanations or comments",
                "3. NO line breaks or extra spaces",
            ],
            output_formatter=None,  # No special formatter needed
            interactions=None
        ),
        "feynman_agent": CoreAgent(
            agent_name="Feynman Agent",
            system_instructions=[
                "You are a Feynman agent that helps explain complex concepts.",
                "Analyze the query and identify key concepts.",
                "",
                "CRITICAL OUTPUT FORMAT RULES:",
                "1. Output ONLY the raw analysis as JSON",
                "2. NO explanations or comments",
                "3. NO line breaks or extra spaces",
            ],
            output_formatter=None,  # No special formatter needed
            interactions=None
        ),
        "chat_agent": CoreAgent(
            agent_name="Chat Agent",
            system_instructions=[
                "You are a chat agent that helps with general conversations.",
                "Analyze the query and identify key topics.",
                "",
                "CRITICAL OUTPUT FORMAT RULES:",
                "1. Output ONLY the raw analysis as JSON",
                "2. NO explanations or comments",
                "3. NO line breaks or extra spaces",
            ],
            output_formatter=None,  # No special formatter needed
            interactions=None
        )
    }
    response = analyze_query_tool(query, llm, available_agents)
    print(f"Selected agent: {response}")