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

        # Si on a un formateur de sortie, on l'utilise
        if self.output_formatter:
            if content is not None:
                content = self.output_formatter(content, llm_response)
            else:
                content = {"error": "No tool output available"}
        # Sinon, on retourne un dict avec la réponse du LLM
        else:
            content = {
                "content": content,
                "metadata": {
                    "raw_response": llm_response
                }
            }

        return content