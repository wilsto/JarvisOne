"""Prompt assembler for combining prompt components."""

import logging
from dataclasses import dataclass
from typing import Optional, List, Dict, Any
from .components import (
    SystemPromptBuilder,
    WorkspaceContextBuilder,
    RAGContextBuilder,
    PreferencesBuilder,
    SystemPromptConfig,
    WorkspaceContextConfig,
    RAGContextConfig,
    PreferencesConfig,
    RAGDocument
)

logger = logging.getLogger(__name__)

@dataclass
class PromptAssemblerConfig:
    """Configuration for prompt assembly."""
    system_config: SystemPromptConfig
    workspace_config: Optional[WorkspaceContextConfig] = None
    rag_config: Optional[RAGContextConfig] = None
    preferences_config: Optional[PreferencesConfig] = None
    debug: bool = False

class PromptAssembler:
    """Assembles complete prompts from individual components."""

    @staticmethod
    def assemble(config: PromptAssemblerConfig) -> str:
        """Assemble a complete prompt from components.
        
        Args:
            config: PromptAssemblerConfig containing all component configs
            
        Returns:
            str: Complete assembled prompt
        """
        try:
            if config.debug:
                logger.info("Assembling prompt with config: %s", config)
                
            sections = []
            
            # Build system prompt
            system_prompt = SystemPromptBuilder.build(config.system_config)
            if system_prompt:
                sections.append(system_prompt)
                
            # Build preferences if configured
            if config.preferences_config:
                preferences = PreferencesBuilder.build(config.preferences_config)
                if preferences:
                    sections.append(preferences)
                    
            # Build workspace context if configured
            if config.workspace_config:
                workspace_context = WorkspaceContextBuilder.build(config.workspace_config)
                if workspace_context:
                    sections.append(workspace_context)
                    
            # Build RAG context if configured
            if config.rag_config:
                rag_context = RAGContextBuilder.build(config.rag_config)
                if rag_context:
                    sections.append(rag_context)
                    
            return "\n\n".join(sections)
            
        except Exception as e:
            logger.error("Error assembling prompt: %s", e)
            return ""
