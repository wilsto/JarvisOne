"""System prompt builder component."""

import logging
from dataclasses import dataclass
from typing import Optional

logger = logging.getLogger(__name__)

@dataclass
class SystemPromptConfig:
    """Configuration for system prompt building."""
    context_prompt: str
    workspace_scope: str
    debug: bool = False

class SystemPromptBuilder:
    """Builds system prompts with consistent structure and formatting."""

    @staticmethod
    def build(config: SystemPromptConfig) -> str:
        """Build a system prompt from the given configuration.
        
        Args:
            config: SystemPromptConfig containing prompt building parameters
            
        Returns:
            str: Formatted system prompt
        """
        try:
            if config.debug:
                logger.info("Building system prompt with config: %s", config)
                
            # Build the prompt sections
            sections = []
            
            if config.debug:
                sections.append("=== System Instructions ===")
                
            if config.context_prompt:
                sections.append(config.context_prompt)
                
            if config.workspace_scope:
                if config.debug:
                    sections.append("=== Workspace Scope ===")
                sections.append(f"Working in scope: {config.workspace_scope}")
                
            return "\n\n".join(sections)
            
        except Exception as e:
            logger.error("Error building system prompt: %s", e)
            return ""
