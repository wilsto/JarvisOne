"""Workspace context builder component."""

import logging
from dataclasses import dataclass
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

@dataclass
class WorkspaceContextConfig:
    """Configuration for workspace context building."""
    workspace_id: str
    metadata: Dict[str, Any]
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
                
            if config.workspace_id:
                sections.append(f"Active Workspace: {config.workspace_id}")
                
            if config.metadata and 'context' in config.metadata:
                sections.append(config.metadata['context'])
            elif config.metadata:
                sections.append("Workspace Configuration:")
                for key, value in config.metadata.items():
                    sections.append(f"- {key}: {value}")
                    
            return "\n".join(sections)
            
        except Exception as e:
            logger.error("Error building workspace context: %s", e)
            return ""
