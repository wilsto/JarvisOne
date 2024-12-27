"""Analyzes conversations to extract metadata."""

import logging
from typing import List, Dict, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class ConversationAnalyzer:
    """Analyzes conversations to extract metadata like title, topics, and summaries."""

    @staticmethod
    def extract_title(messages: List[Dict]) -> str:
        """Extract a title from the conversation messages.
        
        Args:
            messages: List of message dictionaries with 'role' and 'content'
            
        Returns:
            Extracted title string
        """
        if not messages:
            return "New Conversation"
        
        # Get first user message
        first_message = next(
            (msg for msg in messages if msg['role'] == 'user'),
            messages[0]
        )
        
        # Extract first line or first N characters
        content = first_message['content']
        title = content.split('\n')[0][:50]  # First line, max 50 chars
        
        return title if title else "New Conversation"

    @staticmethod
    def extract_topics(messages: List[Dict], min_confidence: float = 0.7) -> List[Dict]:
        """Extract topics from conversation messages.
        
        Args:
            messages: List of message dictionaries
            min_confidence: Minimum confidence threshold for topics
            
        Returns:
            List of topic dictionaries with confidence scores
        """
        # TODO: Implement more sophisticated topic extraction
        # For now, just use a simple keyword-based approach
        topics = []
        
        # Combine all message content
        content = " ".join([msg['content'] for msg in messages])
        
        # Extract potential topics (placeholder implementation)
        # In a real implementation, this would use NLP techniques
        words = content.lower().split()
        potential_topics = set([word for word in words if len(word) > 5])
        
        # Convert to topic dictionaries with confidence
        topics = [
            {
                'topic': topic,
                'confidence': 0.8  # Placeholder confidence score
            }
            for topic in list(potential_topics)[:5]  # Limit to top 5 topics
        ]
        
        return topics

    @staticmethod
    def generate_summary(messages: List[Dict]) -> str:
        """Generate a summary of the conversation.
        
        Args:
            messages: List of message dictionaries
            
        Returns:
            Generated summary string
        """
        # TODO: Implement more sophisticated summarization
        # For now, just use the first few messages
        if not messages:
            return ""
        
        # Get first exchange (user message and response)
        summary_messages = []
        for msg in messages[:2]:  # First user message and assistant response
            content = msg['content']
            # Truncate long messages
            if len(content) > 100:
                content = content[:97] + "..."
            summary_messages.append(f"{msg['role']}: {content}")
        
        return "\n".join(summary_messages)
