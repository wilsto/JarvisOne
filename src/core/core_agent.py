from abc import ABC, abstractmethod

# Définition d'une classe abstraite pour les modèles LLM
class LLM(ABC):
    @abstractmethod
    def generate_response(self, prompt: str) -> str:
        pass

# Implémentation basique d'un LLM qui ne fait qu'echo
class DummyLLM(LLM):
    def generate_response(self, prompt: str) -> str:
        return f"Réponse du DummyLLM:\n{prompt}"

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
        self.llm = llm if llm else DummyLLM()


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
        content = self.llm.generate_response(prompt)

        # Exécution des outils (s'il y en a)
        if self.tools:
            for tool in self.tools:
                try:
                   tool_output = tool(user_query)
                   content = f"{content}\n\n Output from tool {tool.__name__}:\n {tool_output}"
                except Exception as e:
                    content = f"{content}\n\n Error while executing tool {tool.__name__} : {e}"


        if self.output_formatter:
             content = self.output_formatter(content)
        return {"content": content}