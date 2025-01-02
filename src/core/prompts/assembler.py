"""Prompt assembly component implementing the Builder pattern.

This module is responsible for assembling the final prompt from various components
using the Builder pattern. The PromptAssembler acts as the Builder, while the
individual component builders (SystemPromptBuilder, WorkspaceContextBuilder, etc.)
act as the ConcreteBuilders.

The assembly process follows a specific order to ensure consistency:
1. System instructions (required base)
2. Preferences (optional customization)
3. Workspace context (optional workspace-specific content)
4. Role context (optional role-specific behavior)
5. Message history (previous messages)
6. Current message (user query)
7. RAG context (optional relevant documents)

Example:
    config = PromptAssemblerConfig(
        system_config=SystemPromptConfig(...),
        workspace_config=WorkspaceContextConfig(...),
        role_config=RoleContextConfig(...),
        message_history_config=MessageHistoryConfig(...),
        current_message_config=CurrentMessageConfig(...),
        rag_config=RAGContextConfig(...),
        preferences_config=PreferencesConfig(...)
    )
    final_prompt = PromptAssembler.assemble(config)
"""

import logging
from dataclasses import dataclass
from typing import Optional, List, Dict, Any
from .components import (
    SystemPromptConfig, WorkspaceContextConfig, RAGContextConfig,
    PreferencesConfig, RoleContextConfig, SystemPromptBuilder,
    WorkspaceContextBuilder, RAGContextBuilder, PreferencesBuilder,
    RoleContextBuilder, RAGDocument, CurrentMessageConfig,
    CurrentMessageBuilder, MessageHistoryConfig, MessageHistoryBuilder
)

logger = logging.getLogger(__name__)

@dataclass
class PromptAssemblerConfig:
    """Configuration for prompt assembly."""
    system_config: SystemPromptConfig
    current_message_config: CurrentMessageConfig
    workspace_config: Optional[WorkspaceContextConfig] = None
    role_config: Optional[RoleContextConfig] = None
    message_history_config: Optional[MessageHistoryConfig] = None
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
                    
            # Message history (optional)
            if config.message_history_config:
                history = MessageHistoryBuilder.build(config.message_history_config)
                if history:
                    sections.append(history)

            # RAG context (optional)
            if config.rag_config:
                rag_ctx = RAGContextBuilder.build(config.rag_config)
                if rag_ctx:
                    sections.append(rag_ctx)

            # Preferences (optional)
            if config.preferences_config:
                preferences = PreferencesBuilder.build(None)  # Force using session state
                if preferences:
                    sections.append(preferences)

            # Current message (required)
            current_msg = CurrentMessageBuilder.build(config.current_message_config)
            if current_msg:
                sections.append(current_msg)

                    
            return "\n\n".join(sections)
            
        except Exception as e:
            logger.error("Error assembling prompt: %s", e)
            return ""
