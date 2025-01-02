"""Prompt assembly component."""

import logging
from dataclasses import dataclass
from typing import Optional, List, Dict, Any
from .components import (
    SystemPromptConfig, WorkspaceContextConfig, RAGContextConfig,
    PreferencesConfig, RoleContextConfig, SystemPromptBuilder,
    WorkspaceContextBuilder, RAGContextBuilder, PreferencesBuilder,
    RoleContextBuilder, RAGDocument
)

logger = logging.getLogger(__name__)

@dataclass
class PromptAssemblerConfig:
    """Configuration for prompt assembly."""
    system_config: SystemPromptConfig
    workspace_config: Optional[WorkspaceContextConfig] = None
    role_config: Optional[RoleContextConfig] = None
    rag_config: Optional[RAGContextConfig] = None
    preferences_config: Optional[PreferencesConfig] = None
    debug: bool = False

class PromptAssembler:
    """Assembles complete prompts from individual components."""
    
    @staticmethod
    def assemble(config: PromptAssemblerConfig) -> str:
        """Assemble a complete prompt from the provided components.
        
        Args:
            config: Configuration containing all component configs
            
        Returns:
            str: Complete assembled prompt
        """
        try:
            if config.debug:
                logger.info("Assembling prompt with config: %s", config)
                
            sections = []
            
            # System instructions (required)
            system_prompt = SystemPromptBuilder.build(config.system_config)
            if system_prompt:
                sections.append(system_prompt)
                
            # Preferences (optional)
            if config.preferences_config:
                prefs = PreferencesBuilder.build(config.preferences_config)
                if prefs:
                    sections.append(prefs)
                    
            # Workspace context (optional)
            if config.workspace_config:
                workspace_ctx = WorkspaceContextBuilder.build(config.workspace_config)
                if workspace_ctx:
                    sections.append(workspace_ctx)
                    
            # Role context (optional)
            if config.role_config:
                role_ctx = RoleContextBuilder.build(config.role_config)
                if role_ctx:
                    sections.append(role_ctx)
                    
            # RAG context (optional)
            if config.rag_config:
                rag_ctx = RAGContextBuilder.build(config.rag_config)
                if rag_ctx:
                    sections.append(rag_ctx)
                    
            return "\n\n".join(sections)
            
        except Exception as e:
            logger.error("Error assembling prompt: %s", e)
            return ""
