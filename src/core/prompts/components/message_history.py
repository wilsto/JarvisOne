"""Message history builder component."""

import logging
from dataclasses import dataclass
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)

@dataclass
class MessageHistoryConfig:
    """Configuration for message history building."""
    messages: List[Dict[str, str]]
    max_messages: int = 50
    debug: bool = False

class MessageHistoryBuilder:
    """Builds message history with consistent structure and formatting."""

    @staticmethod
    def build(config: MessageHistoryConfig) -> str:
        """Build a message history section from the given configuration.
        
        Args:
            config: MessageHistoryConfig containing history parameters
            
        Returns:
            str: Formatted message history
        """
        try:
            if config.debug:
                logger.info("Building message history with config: %s", config)
                
            if not config.messages:
                return ""
                
            sections = []
            
            if config.debug:
                sections.append("=== Message History ===")
            
            # Limit number of messages
            recent_messages = config.messages[-config.max_messages:]
            
            # Format messages
            for msg in recent_messages:
                role = msg["role"].upper()
                content = msg["content"].strip()
                sections.append(f"[{role}]\n{content}")
                
            return "\n\n".join(sections)
            
        except Exception as e:
            logger.error("Error building message history: %s", e)
            return ""
