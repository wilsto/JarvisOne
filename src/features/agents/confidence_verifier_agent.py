"""Confidence Verifier Agent for assessing agent selection confidence."""

import logging
import re
from typing import Dict, Tuple
from core.core_agent import CoreAgent

# Configure logger
logger = logging.getLogger(__name__)


CONFIDENCE_VERIFIER_PROMPT = """You are a Confidence Verifier that must provide TWO pieces of information:
1. A confidence score (number between 0-100)
2. A brief reason for your score (one line)

IMPORTANT: Your response MUST follow the exact format shown in the examples:
- First line: "Score: " followed by a number 0-100
- Second line: "Reason: " followed by your explanation

Your task is to analyze the agent's selection and provide a final confidence score based on:
1. The query content
2. The selected agent
3. The agent's own confidence score
4. The agent's reasoning

Scoring Guidelines:
1. High Confidence (80-100):
   - Clear, unambiguous requests matching agent's expertise
   - Agent's reasoning is solid and specific
   - Agent's own confidence is high (80-100)
   - Reason matches the query intent perfectly

2. Medium Confidence (50-79):
   - Requests with some ambiguity but clear intent
   - Agent's reasoning is acceptable but could be more specific
   - Agent's own confidence is medium (50-79)
   - Reason partially matches the query intent

3. Low Confidence (0-49):
   - Vague or unclear requests
   - Agent's reasoning is weak or generic
   - Agent's own confidence is low (0-49)
   - Reason doesn't clearly match the query intent

Examples of valid responses:
Score: 95
Reason: Perfect match between query and agent expertise, strong reasoning provided

Score: 75
Reason: Good agent match but reasoning could be more specific

Score: 30
Reason: Agent's confidence is low and reasoning is too generic

REMEMBER: ONLY output the score and reason in the exact format shown!"""

class ConfidenceVerifierAgent(CoreAgent):
    """Agent responsible for verifying confidence in agent selection decisions."""
    
    def __init__(self):
        super().__init__(
            agent_name="Confidence Verifier Agent",
            system_instructions=CONFIDENCE_VERIFIER_PROMPT,
            output_formatter=lambda content, query, interaction_id: self._format_confidence_output(content, query, interaction_id)
        )
    
    def verify_confidence(self, query: str, selected_agent: str, agent_confidence: float = 50, agent_reason: str = "") -> tuple[float, str, str]:
        """
        Verify confidence in agent selection.
        
        Args:
            query: The user's query
            selected_agent: The selected agent name
            agent_confidence: The agent's own confidence score (0-100)
            agent_reason: The agent's reason for selection
            
        Returns:
            tuple[float, str, str]: Confidence score (0-100), confidence level, and reason
        """
        prompt = f"""Query: {query}
        Selected Agent: {selected_agent}
        Agent Confidence: {agent_confidence}
        Agent Reason: {agent_reason}

        Based on the above, provide your confidence score and reason.
        REMEMBER: ONLY output a score and reason in the exact format shown."""

        response = self.run(prompt)
        if isinstance(response, dict) and "content" in response:
            formatted = response["content"]
        else:
            formatted = self._format_confidence_output(response, query)
            
        return formatted["score"], formatted["level"], formatted["reason"]

    def _format_confidence_output(self, content: str, transformed_query: str, interaction_id: str = None) -> Dict:
        """Format the confidence score output.
        
        Args:
            content: Raw LLM response or processed content
            transformed_query: Original or transformed query
            interaction_id: Optional interaction ID
            
        Returns:
            Dict: Formatted confidence result with score, level, and reason
        """
        try:
            # Handle dict response
            if isinstance(content, dict):
                raw_text = content.get('content', '')
            else:
                raw_text = str(content).strip()
            
            # Log the raw response
            logger.debug(f"Raw content to format: {raw_text}")

            # Split response into lines
            lines = raw_text.split('\n')
            
            # Extract score from first line
            score_line = lines[0].lower()
            logger.debug(f"Score line: {score_line}")

            if not score_line.startswith('score:'):
                raise ValueError("Response must start with 'Score: '")
            
            numbers = re.findall(r'\d+\.?\d*', score_line)
            if not numbers:
                raise ValueError("No numbers found in score line")
            
            score = float(numbers[0])
            # Ensure score is within bounds
            score = max(0, min(100, score))
            
            # Extract reason from second line
            reason = "No reason provided"
            if len(lines) > 1 and lines[1].lower().startswith('reason:'):
                reason = lines[1].replace('reason:', '', 1).strip()
            
            return {
                "content": {
                    "score": score,
                    "level": self._get_confidence_level(score),
                    "reason": reason
                },
                "metadata": {
                    "raw_response": raw_text,
                    "interaction_id": interaction_id
                }
            }
            
        except Exception as e:
            logger.warning(f"Error formatting confidence output: {str(e)}")
            return {
                "content": {
                    "score": 0.0,
                    "level": "unknown",
                    "reason": f"Error processing response: {str(e)}"
                },
                "metadata": {
                    "raw_response": str(content),
                    "error": str(e),
                    "interaction_id": interaction_id
                }
            }

    def _get_confidence_level(self, score: float) -> str:
        """Get confidence level description.
        
        Args:
            score: Confidence score (0-100)
            
        Returns:
            str: Confidence level (high/medium/low/unknown)
        """
        if score >= 80:
            return "high"
        elif score >= 50:
            return "medium"
        elif score > 0:
            return "low"
        else:
            return "unknown"

# Create singleton instance
agent = ConfidenceVerifierAgent()
