"""Core agent implementation."""

from .llm_base import LLM
from .llm_manager import get_llm_model
from core.workspace_manager import WorkspaceManager
import logging
from typing import List
from pathlib import Path

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

class CoreAgent:
    def __init__(self, agent_name: str, system_instructions: str, 
                 tools: list = None, output_formatter: callable = None,
                 interactions: callable = None,
                 llm: LLM = None, workspace_manager: WorkspaceManager = None):
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
        """
        self.agent_name = agent_name
        self.system_instructions = system_instructions
        self.tools = tools if tools else []
        self.output_formatter = output_formatter
        self.interactions = interactions
        self.llm = llm if llm else ManagedLLM()
        self.workspace_manager = workspace_manager

    def _build_prompt(self, user_query: str) -> str:
        """Construit le prompt pour le LLM."""
        prompt_parts = []
        
        # Ajouter le system prompt du workspace s'il existe
        if self.workspace_manager:
            context_prompt = self.workspace_manager.get_current_context_prompt()
            prompt_parts.append(context_prompt)
        else:
            logger.warning("No workspace_manager available, using base prompt only")
        
        # Ajouter les instructions système de l'agent
        prompt_parts.append(self.system_instructions)
        
        # Ajouter la requête utilisateur
        prompt_parts.append(f"User Query: {user_query}")
        
        # Combiner tous les éléments avec des sauts de ligne
        return "\n\n".join(prompt_parts)

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

    def run(self, user_query: str) -> dict:
        """
        Exécute l'agent.

        Args:
            user_query: La requête de l'utilisateur.

        Returns:
            Un dictionnaire contenant la réponse de l'agent.
        """
        # On construit le prompt pour le LLM
        prompt = self._build_prompt(user_query)
        logger.info(f"##DEBUG## Using final prompt: {prompt}...")
        
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

        # Gérer l'interaction UI si définie - utiliser la requête transformée
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