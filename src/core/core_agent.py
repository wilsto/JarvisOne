"""Core agent implementation."""

from .llm_base import LLM
from .llm_manager import get_llm_model
from core.workspace_manager import WorkspaceManager
import logging
from typing import List, Dict
from pathlib import Path
from rag.processor import MessageProcessor
from rag.query_handler import RAGQueryHandler
from .prompts.components import (
    SystemPromptConfig,
    WorkspaceContextConfig,
    RAGContextConfig,
    PreferencesConfig,
    RAGDocument,
    RoleContextConfig,
    CurrentMessageConfig,
    MessageHistoryConfig
)
from .prompts.assembler import PromptAssembler, PromptAssemblerConfig

logger = logging.getLogger(__name__)

# Implémentation du LLM utilisant le gestionnaire de modèles
class ManagedLLM(LLM):
    def __init__(self):
        self.model = get_llm_model()
    
    def generate_response(self, prompt: str) -> str:
        """Génère une réponse en utilisant le modèle LLM configuré."""
        try:
            response = self.model.generate_response(prompt)
            return response
        except Exception as e:
            return f"Error generating response: {str(e)}"

class CoreAgent(MessageProcessor):
    def __init__(self, agent_name: str, system_instructions: str, 
                 tools: list = None, output_formatter: callable = None,
                 interactions: callable = None,
                 llm: LLM = None, workspace_manager: WorkspaceManager = None,
                 rag_enabled: bool = False):
        """
        Initialise un CoreAgent.

        Args:
            agent_name: Le nom de l'agent.
            system_instructions: Les instructions système pour l'agent.
            tools: Liste optionnelle de fonctions externes.
            output_formatter: Fonction optionnelle pour formater la sortie.
            interactions: Fonction optionnelle pour gérer les interactions UI.
            llm : instance du LLM utilisé par l'agent
            workspace_manager: instance du gestionnaire d'espace de travail
            rag_enabled: Enable RAG functionality
        """
        self.agent_name = agent_name
        self.system_instructions = system_instructions
        self.system_prompt = system_instructions
        self.tools = tools if tools else []
        self.output_formatter = output_formatter
        self.interactions = interactions
        self.llm = llm if llm else ManagedLLM()
        self.workspace_manager = workspace_manager
        self.message_history: List[Dict[str, str]] = []
        
        # Initialize RAG handler with logging
        if rag_enabled:
            logger.info(f"Initializing RAG handler for agent: {agent_name}")
            try:
                self.rag_handler = RAGQueryHandler()
                logger.info("Successfully initialized RAG query handler")
                
                # Test collection access
                if workspace_manager and workspace_manager.current_space:
                    workspace_id = workspace_manager.current_space.name
                    logger.info(f"Testing collection access for workspace: {workspace_id}")
                    collection = self.rag_handler._get_collection(workspace_id)
                    if collection:
                        logger.info(f"Successfully accessed collection for workspace: {workspace_id}")
                    else:
                        logger.warning(f"No collection found for workspace: {workspace_id}, will be created when needed")
                else:
                    logger.info("No workspace manager or current space available")
            except Exception as e:
                logger.error(f"Failed to initialize RAG handler: {str(e)}", exc_info=True)
                self.rag_handler = None
        else:
            logger.info(f"RAG functionality is disabled for agent: {agent_name}")
            self.rag_handler = None

    def _get_rag_context(self, query: str, workspace_id: str, role_id: str = None) -> str:
        """Get relevant context from RAG system."""
        if not self.rag_handler:
            logger.warning("No RAG handler available")
            return ""
            
        try:
            logger.info(f"Getting RAG context for query: {query[:50]}... in workspace: {workspace_id}")
            
            # Query RAG system with workspace and role context
            results = self.rag_handler.query(
                query, 
                workspace_id=workspace_id,
                role_id=role_id
            )
            
            if results:
                # Create RAG interaction when documents are found
                from features.agents.chat_agent import handle_rag_interaction
                handle_rag_interaction(query, results)
                logger.info("Found RAG content from unknown source")
            
            if not results:
                logger.warning(f"No RAG results found for workspace {workspace_id}")
                return ""
                
            # Format context
            context_parts = []
            for result in results:
                content = result.get('content', '')
                metadata = result.get('metadata', {})
                source = metadata.get('file_path', 'unknown source')
                logger.info(f"Found RAG content from {source}")
                context_parts.append(f"From {source}:\n{content}")
                
            if not context_parts:
                return ""
                
            formatted_context = "\n\n".join(context_parts)
            logger.info(f"RAG context built successfully with {len(context_parts)} documents")
            return formatted_context
            
        except Exception as e:
            logger.error(f"Error getting RAG context: {str(e)}", exc_info=True)
            return ""

    def _prepare_prompt_config(self, user_query: str, workspace_id: str = None, role_id: str = None) -> PromptAssemblerConfig:
        """Prepare the configuration for prompt assembly.
        
        This method acts as a Director in the Builder pattern, preparing all necessary
        configurations that will be used by the PromptAssembler to build the final prompt.
        It does NOT build the prompt itself, but rather collects and organizes all the
        components that should be included.
        
        Args:
            user_query: The user's query to process
            workspace_id: Optional ID of the current workspace
            role_id: Optional ID of the current role
            
        Returns:
            PromptAssemblerConfig: Configuration object containing all components
            needed to build the final prompt
            
        Note:
            This method follows the Single Responsibility Principle by focusing only
            on configuration preparation, leaving the actual prompt assembly to the
            PromptAssembler class.
        """
        try:
            debug_mode = logger.isEnabledFor(logging.DEBUG)
            
            # Initialize configs
            system_config = SystemPromptConfig(
                context_prompt=self.system_prompt,
                workspace_scope=workspace_id or "",
                debug=debug_mode
            )
            
            preferences_config = PreferencesConfig(
                debug=debug_mode
            )
            
            # Build workspace config if available
            workspace_config = None
            if workspace_id and self.workspace_manager:
                space_config = self.workspace_manager.get_current_space_config()
                if space_config:
                    workspace_config = WorkspaceContextConfig(
                        workspace_id=workspace_id,
                        workspace_prompt=space_config.workspace_prompt or "",
                        scope=space_config.scope or "",
                        debug=debug_mode
                    )
                    
                    # Build role config if role_id is provided and roles exist
                    role_config = None
                    roles = space_config.roles or []
                    if role_id and roles:
                        # Find role in space config
                        role = next((r for r in roles if r['name'] == role_id), None)
                        if role:
                            logger.debug(f"Found role configuration for {role_id}")
                            role_config = RoleContextConfig(
                                role_id=role_id,
                                role_name=role['role_name'] or "",
                                role_description=role['role_description'] or "",
                                prompt_context=role['prompt_context'] or "",
                                debug=debug_mode
                            )
                        else:
                            logger.warning(f"Role {role_id} not found in workspace {workspace_id}")
            
            # Build message history config
            message_history_config = None
            if self.message_history:
                message_history_config = MessageHistoryConfig(
                    messages=self.message_history.copy(),
                    debug=debug_mode
                )
            
            # Build current message config
            current_message_config = CurrentMessageConfig(
                content=user_query,
                role="user",
                debug=debug_mode
            )
            
            # Build RAG config if available
            rag_config = None
            if workspace_id and self.rag_handler:
                rag_context = self._get_rag_context(user_query, workspace_id, role_id)
                if rag_context:
                    rag_config = RAGContextConfig(
                        query=user_query,
                        documents=[RAGDocument(
                            content=rag_context,
                            metadata={'file_path': 'RAG System'}
                        )],
                        debug=debug_mode
                    )
            
            # Assemble final config
            return PromptAssemblerConfig(
                system_config=system_config,
                current_message_config=current_message_config,
                workspace_config=workspace_config,
                role_config=role_config,
                message_history_config=message_history_config,
                rag_config=rag_config,
                preferences_config=preferences_config,
                debug=debug_mode
            )
            
        except Exception as e:
            logger.error(f"Error preparing prompt config: {str(e)}", exc_info=True)
            # Return basic config as fallback
            return PromptAssemblerConfig(
                system_config=SystemPromptConfig(
                    context_prompt=self.system_prompt,
                    workspace_scope=workspace_id or "",
                    debug=debug_mode
                ),
                current_message_config=CurrentMessageConfig(
                    content=user_query,
                    role="user",
                    debug=debug_mode
                ),
                debug=debug_mode
            )

    def _handle_interaction(self, query: str, results: any) -> str:
        """
        Gère l'ajout d'une interaction si un gestionnaire est défini.
        
        Args:
            query: La requête utilisateur
            results: Les résultats à afficher
            
        Returns:
            str: L'ID de l'interaction créée, ou None si pas de gestionnaire
        """
        if self.interactions:
            return self.interactions(query, results)
        return None

    def get_context(self) -> dict:
        """Get the current context including workspace information."""
        context = {}
        if self.workspace_manager:
            workspace_config = self.workspace_manager.get_current_space_config()
            if workspace_config:
                context.update({
                    "workspace": {
                        "name": workspace_config.name,
                        "tags": workspace_config.tags
                    }
                })
        return context

    def get_search_paths(self) -> List[Path]:
        """Get the current search paths based on active workspace."""
        if self.workspace_manager:
            return self.workspace_manager.get_space_paths()
        return []

    def run(self, user_query: str, workspace_id: str = None, role_id: str = None) -> dict:
        """
        Exécute l'agent.

        Args:
            user_query: La requête de l'utilisateur.
            workspace_id: ID of the current workspace
            role_id: ID of the current role

        Returns:
            Un dictionnaire contenant la réponse de l'agent.
        """
        try:
            # Check for empty query
            if not user_query or not user_query.strip():
                return {"content": "Please provide a valid query."}
                
            logger.info(f"Running agent with workspace_id={workspace_id}, role_id={role_id}")
            
            # Prepare prompt configuration and build final prompt
            config = self._prepare_prompt_config(user_query, workspace_id, role_id)
            prompt = PromptAssembler.assemble(config)
            
            logger.debug(f"##DEBUG## Using final prompt: {prompt}...")
            
            # On demande au LLM de générer une réponse
            llm_response = self.llm.generate_response(prompt)
            
            # Update message history
            self.message_history.append({"role": "user", "content": user_query})
            self.message_history.append({"role": "assistant", "content": llm_response})
            
            # Limit history size
            if len(self.message_history) > 50:  # Keep last 25 exchanges
                self.message_history = self.message_history[-50:]
            
            # Si pas d'outils, on utilise directement la réponse du LLM
            content = llm_response
            
            # Exécution des outils (s'il y en a)
            if self.tools:
                for tool in self.tools:
                    try:
                        content = tool(llm_response)  # Use LLM response
                    except Exception as e:
                        logger.error(f"Error while executing tool {tool.__name__} : {e}")
                        content = []

            # Gérer l'interaction UI si définie et si RAG n'est pas utilisé
            interaction_id = None
            if not (workspace_id and self.rag_handler):
                interaction_id = self._handle_interaction(llm_response, content)

            # Si on a un formateur de sortie, on l'utilise
            if self.output_formatter:
                if content is not None:
                    content = self.output_formatter(content, llm_response, interaction_id)
                else:
                    content = {"error": "No tool output available"}
            # Sinon, on retourne un dict avec la réponse du LLM
            else:
                content = {
                    "content": content,
                    "metadata": {
                        "raw_response": llm_response,
                        "interaction_id": interaction_id
                    }
                }

            return content
            
        except Exception as e:
            logger.error(f"Error in agent execution: {str(e)}", exc_info=True)
            return {"error": str(e)}

    async def process_message(
        self,
        message: str,
        workspace_id: str,
        **kwargs: dict
    ) -> str:
        """
        Process a message as required by MessageProcessor interface.
        
        Args:
            message: The message to process
            workspace_id: ID of the current workspace
            **kwargs: Additional processing parameters
            
        Returns:
            The processed response
        """
        return await self.run(message, workspace_id, **kwargs)