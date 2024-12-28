import logging
from core.core_agent import CoreAgent
from core.llm_base import LLM
import streamlit as st
from datetime import datetime
import uuid
from .confidence_verifier_agent import agent as confidence_verifier_agent

# Configure logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

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
Reason: Query explicitly asks to find files modified today

feynman_agent
Confidence: 85
Reason: Request for deep understanding of quantum mechanics using analogies

chat_agent
Confidence: 70
Reason: Simple question about project status

Here are the rules for selecting the appropriate agent:

1. file_search_agent:
   - Query is about searching or manipulating files
   - Contains keywords: file, find, search, modified, created
   - Mentions file extensions (.py, .txt, etc.) or file types (python, text, image)
   - Includes time references (today, yesterday, last week, this month)

2. feynman_agent:
   - Requests for complex concept explanations
   - Uses keywords: explain, understand, how does it work, what is, why
   - Topics involve: scientific concepts, technical mechanisms, abstract ideas
   - Requires: metaphors, analogies, simple examples for complex topics
   - Focus on deep understanding and insights

3. chat_agent:
   - General questions and conversations
   - Basic coding help without deep concept explanations
   - Task planning and organization
   - Simple explanations without abstraction
   - Any query not clearly matching other agents

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
        
        logger.info(f"Query: '{query}' → Agent: '{selected_agent}' → Confidence: {agent_confidence} → Reason: {reason}")
        
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