"""Core agent implementation."""

from .llm_base import LLM
from .llm_manager import get_llm_model
import logging
logger = logging.getLogger(__name__)

# Implémentation du LLM utilisant le gestionnaire de modèles
class ManagedLLM(LLM):
    def __init__(self):
        self.model = get_llm_model()
    
    def generate_response(self, prompt: str) -> str:
        try:
            response = self.model.generate_response(prompt)
            return response
        except Exception as e:
            return f"Error generating response: {str(e)}"

class CoreAgent:
    def __init__(self, agent_name: str, system_instructions: str, 
                 tools: list = None, output_formatter: callable = None,
                 llm: LLM = None):
        """
        Initialise un CoreAgent.

        Args:
            agent_name: Le nom de l'agent.
            system_instructions: Les instructions système pour l'agent.
            tools: Liste optionnelle de fonctions externes.
            output_formatter: Fonction optionnelle pour formater la sortie.
            llm : instance du LLM utilisé par l'agent
        """
        self.agent_name = agent_name
        self.system_instructions = system_instructions
        self.tools = tools if tools else []
        self.output_formatter = output_formatter
        self.llm = llm if llm else ManagedLLM()

    def _build_prompt(self, user_query: str) -> str:
        """
        Construit le prompt pour le LLM.
        """
        return f"{self.system_instructions}\n\nUser Query: {user_query}"

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
        
        # On demande au LLM de générer une réponse
        formatted_query = self.llm.generate_response(prompt)
        
        # Exécution des outils (s'il y en a)
        content = None
        if self.tools:
            for tool in self.tools:
                try:
                    content = tool(formatted_query)  # Use LLM formatted query
                except Exception as e:
                    logger.error(f"Error while executing tool {tool.__name__} : {e}")
                    content = []

        if self.output_formatter:
            if content is not None:
                content = self.output_formatter(content, formatted_query)
            else:
                content = {"error": "No tool output available"}

        return content  # Return the formatted content directly