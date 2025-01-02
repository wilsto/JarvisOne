"""Core agent implementation."""

from .llm_base import LLM
from .llm_manager import get_llm_model
from core.workspace_manager import WorkspaceManager
import logging
from typing import List
from pathlib import Path
from rag.processor import MessageProcessor
from rag.query_handler import RAGQueryHandler
from .prompts.components import (
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

    def _build_prompt(self, user_query: str, workspace_id: str = None, role_id: str = None) -> str:
        """Build the prompt for the LLM using the new component-based architecture."""
        try:
            # Initialize configs
            system_config = SystemPromptConfig(
                context_prompt=self.system_prompt,
                workspace_scope=workspace_id or "",
                debug=logger.isEnabledFor(logging.DEBUG)
            )
            
            preferences_config = PreferencesConfig(
                debug=logger.isEnabledFor(logging.DEBUG)
            )
            
            # Build workspace config if available
            workspace_config = None
            if workspace_id and self.workspace_manager:
                workspace_context = self.workspace_manager.get_current_context_prompt()
                if workspace_context:
                    workspace_config = WorkspaceContextConfig(
                        workspace_id=workspace_id,
                        metadata={'context': workspace_context},
                        debug=logger.isEnabledFor(logging.DEBUG)
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
                        debug=logger.isEnabledFor(logging.DEBUG)
                    )
            
            # Assemble final prompt
            assembler_config = PromptAssemblerConfig(
                system_config=system_config,
                workspace_config=workspace_config,
                rag_config=rag_config,
                preferences_config=preferences_config,
                debug=logger.isEnabledFor(logging.DEBUG)
            )
            
            return PromptAssembler.assemble(assembler_config)
            
        except Exception as e:
            logger.error(f"Error building prompt: {str(e)}", exc_info=True)
            return self.system_prompt  # Fallback to basic system prompt

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
                        "context": workspace_config.metadata.get("context"),
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
        logger.info(f"Running agent with workspace_id={workspace_id}, role_id={role_id}")
        
        # Build prompt with all context
        prompt = self._build_prompt(user_query, workspace_id, role_id)
        logger.debug(f"##DEBUG## Using final prompt: {prompt}...")
        
        # On demande au LLM de générer une réponse
        llm_response = self.llm.generate_response(prompt)
        
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