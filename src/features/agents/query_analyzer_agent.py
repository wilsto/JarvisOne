import logging
from core.core_agent import CoreAgent
from core.llm_base import LLM
import streamlit as st
from datetime import datetime
import uuid
from .confidence_verifier_agent import agent as confidence_verifier_agent

# Configure logger
logger = logging.getLogger(__name__)


AGENT_SELECTION_PROMPT = """You are AgentMatcher, a precise agent selector that must analyze queries and provide THREE pieces of information:
1. The selected agent name (EXACTLY one of: file_search_agent, feynman_agent, chat_agent)
2. Your confidence score (a number between 0-100)
3. A brief reason for your selection (one line, starting with "Reason: ")

Format your response EXACTLY like this:
[agent_name]
Confidence: [0-100]
Reason: [your brief explanation]

Examples:
file_search_agent
Confidence: 95
Reason: Query explicitly asks to find or locate specific files containing "report"

feynman_agent
Confidence: 85
Reason: Request to explain quantum computing using simple analogies

chat_agent
Confidence: 70
Reason: General information request about project details

Here are the rules for selecting the appropriate agent:

1. file_search_agent (STRICT MATCHING REQUIRED):
   - Query MUST explicitly request file operations: find, search, locate, open, read, write
   - OR contain file-specific terms: folder, directory, extension, document
   - OR mention specific file patterns: *.py, *.txt, etc.
   - Examples:
     "find files modified today"
     "search for python files containing 'main'"
     "what is the project ID" (use chat_agent instead)
     "show me information about X" (use chat_agent instead)

2. feynman_agent (REQUIRES LEARNING INTENT):
   - Query MUST request understanding or explanation of complex concepts
   - MUST use educational keywords: explain, understand, teach, learn, how does it work
   - AND involve technical/scientific topics requiring analogies
   - Examples:
     "explain how neural networks work using simple analogies"
     "help me understand blockchain technology"
     "what is the time" (use chat_agent instead)
     "find information about AI" (use chat_agent instead)

3. chat_agent (DEFAULT CHOICE):
   - General questions and information requests
   - Project-related queries without file operations
   - Simple facts or data retrieval
   - Any query not EXPLICITLY matching other agents
   - Examples:
     "what is the project ID"
     "tell me about the system status"
     "get information about X"
     "show me the configuration"

Confidence Scoring Guidelines:
- High (80-100): Clear match with agent's expertise, exact keyword matches
- Medium (50-79): Partial match, some ambiguity but clear intent
- Low (0-49): Unclear match, multiple possible interpretations

IMPORTANT: Your response MUST follow the exact format shown in the examples:
- First line: ONLY the agent name
- Second line: "Confidence: " followed by a number 0-100
- Third line: "Reason: " followed by your explanation
"""

class QueryAnalyzerAgent(CoreAgent):
    """Agent responsible for analyzing queries and determining which agent should handle them."""
    
    def __init__(self):
        super().__init__(
            agent_name="Query Analyzer Agent",
            system_instructions=AGENT_SELECTION_PROMPT,
            interactions=self.handle_query_interaction
        )
    
    def analyze_query(self, query: str) -> str:
        """
        Analyze query to determine appropriate agent with confidence score.
        
        Args:
            query: The user's query
            
        Returns:
            str: Name of the agent to handle the query
        """
        # Get agent selection and reason
        response = self.llm.generate_response(
            f"{self.system_instructions}\n\nQuery: {query}\n\n"
        ).strip()
        
        # Parse response
        lines = response.lower().split('\n')
        selected_agent = lines[0].strip()
        
        # Extract confidence
        agent_confidence = 50  # Default
        if len(lines) > 1 and lines[1].startswith('confidence:'):
            try:
                agent_confidence = float(lines[1].replace('confidence:', '').strip())
            except ValueError:
                logger.warning(f"Invalid agent confidence value: {lines[1]}")
        
        # Extract reason
        reason = "No reason provided"
        if len(lines) > 2 and lines[2].startswith('reason:'):
            reason = lines[2].replace('reason:', '').strip()
        
        # Extract the relevant part of the query after "=== End of History ==="
        query_parts = query.split("=== End of History ===")
        relevant_query = query_parts[-1].strip() if len(query_parts) > 1 else query
        
        logger.info(f"Query: '{relevant_query}' → Agent: '{selected_agent}' → Confidence: {agent_confidence} → Reason: {reason}")
        # Get confidence score from verifier agent
        confidence_score, confidence_level, verifier_reason = confidence_verifier_agent.verify_confidence(
            query=query,
            selected_agent=selected_agent,
            agent_confidence=agent_confidence,
            agent_reason=reason
        )
        
        # Create analysis for UI
        analysis = {
            'agent_selected': selected_agent,
            'agent': {
                'name': selected_agent,
                'confidence': agent_confidence,
                'reason': reason
            },
            'verifier': {
                'confidence': confidence_score,
                'level': confidence_level,
                'reason': verifier_reason
            },
            'confidence': confidence_score,
            'reason': f"{reason} (Confidence: {confidence_level} - {confidence_score:.0f}%)"
        }
        
        # Create interaction
        self.interactions(query, analysis)
        
        # Return appropriate agent name
        if selected_agent in ['file_search_agent', 'chat_agent', 'feynman_agent']:
            return selected_agent
            
        logger.warning(f"Unrecognized agent '{selected_agent}', defaulting to chat_agent")
        return "chat_agent"

    def handle_query_interaction(self, query: str, analysis: dict) -> str:
        """Handle the display of query analysis in the interface.
        
        Args:
            query: The analyzed query
            analysis: The analysis result including confidence
        
        Returns:
            str: The ID of the created interaction
        """
        if "interactions" not in st.session_state:
            st.session_state.interactions = []
        
        interaction_id = str(uuid.uuid4())
        st.session_state.interactions.append({
            'id': interaction_id,
            'type': 'query_analyzer',
            'query': query,
            'analysis': analysis,
            'timestamp': datetime.now().strftime("%H:%M:%S")
        })
        
        return interaction_id

# Create singleton instance
agent = QueryAnalyzerAgent()

if __name__ == '__main__':
    from core.llm_manager import get_llm_model
    agent.llm = get_llm_model()
    query = "find a pdf file"
    response = agent.analyze_query(query)
    print(f"Selected agent: {response}")