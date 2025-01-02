"""Workspace context builder component."""

import logging
from dataclasses import dataclass
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

@dataclass
class WorkspaceContextConfig:
    """Configuration for workspace context building."""
    workspace_id: str
    workspace_prompt: str
    scope: str
    debug: bool = False

class WorkspaceContextBuilder:
    """Builds workspace context with consistent structure and formatting."""

    @staticmethod
    def build(config: WorkspaceContextConfig) -> str:
        """Build workspace context from the given configuration.
        
        Args:
            config: WorkspaceContextConfig containing context building parameters
            
        Returns:
            str: Formatted workspace context
        """
        try:
            if config.debug:
                logger.info("Building workspace context with config: %s", config)
                
            sections = []
            
            if config.debug:
                sections.append("=== Workspace Context ===")
                
            # Workspace identification
            if config.debug:
                sections.append(f"Active Workspace: {config.workspace_id}")
            
            # Workspace prompt
            if config.workspace_prompt:
                if config.debug:
                    sections.append("=== Workspace Instructions ===")
                sections.append(config.workspace_prompt)
            
            # Workspace scope
            if config.scope:
                if config.debug:
                    sections.append("=== Workspace Scope ===")
                sections.append(config.scope)
                    
            return "\n\n".join(sections)
            
        except Exception as e:
            logger.error("Error building workspace context: %s", e)
            return ""
