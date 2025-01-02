"""Role context builder component."""

import logging
from dataclasses import dataclass
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

@dataclass
class RoleContextConfig:
    """Configuration for role context building."""
    role_id: str
    role_name: str
    role_description: str
    prompt_context: str
    metadata: Dict[str, Any] = None
    debug: bool = False

class RoleContextBuilder:
    """Builds role context with consistent structure and formatting."""

    @staticmethod
    def build(config: RoleContextConfig) -> str:
        """Build role context from the given configuration.
        
        Args:
            config: RoleContextConfig containing role context parameters
            
        Returns:
            str: Formatted role context
        """
        try:
            if config.debug:
                logger.info("Building role context with config: %s", config)
                
            sections = []
            
            if config.debug:
                sections.append("=== Role Context ===")
                
            # Add role identification
            if config.role_name:
                sections.append(f"Active Role: {config.role_name}")
                if config.role_description:
                    sections.append(f"Role Purpose: {config.role_description}")
                    
            # Add role-specific prompt context
            if config.prompt_context:
                if config.debug:
                    sections.append("=== Role Instructions ===")
                sections.append(config.prompt_context)
                
            # Add any additional metadata if present
            if config.metadata:
                if config.debug:
                    sections.append("=== Role Metadata ===")
                for key, value in config.metadata.items():
                    sections.append(f"{key}: {value}")
                    
            return "\n\n".join(sections)
            
        except Exception as e:
            logger.error("Error building role context: %s", e)
            return ""
