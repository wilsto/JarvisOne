"""Current message builder component."""

import logging
from dataclasses import dataclass
from typing import Optional

logger = logging.getLogger(__name__)

@dataclass
class CurrentMessageConfig:
    """Configuration for current message building."""
    content: str
    role: str = "user"
    debug: bool = False

class CurrentMessageBuilder:
    """Builds current message with consistent structure and formatting."""

    @staticmethod
    def build(config: CurrentMessageConfig) -> str:
        """Build a current message section from the given configuration.
        
        Args:
            config: CurrentMessageConfig containing message parameters
            
        Returns:
            str: Formatted current message
        """
        try:
            if config.debug:
                logger.info("Building current message with config: %s", config)
                
            sections = []
            
            if config.debug:
                sections.append("=== Current Message ===")
                
            sections.append(f"[{config.role.upper()}]\n{config.content.strip()}")
                
            return "\n".join(sections)
            
        except Exception as e:
            logger.error("Error building current message: %s", e)
            return ""
