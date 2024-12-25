import logging
from core.core_agent import CoreAgent
from core.llm_base import LLM

# Configuration du logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

def analyze_query_tool(query: str, llm: LLM) -> str:
    """
    Outil d'analyse de requête pour déterminer l'agent approprié.
    
    Args:
        query: La requête de l'utilisateur.
        llm: Instance LLM partagée à utiliser.
        
    Returns:
        Le nom de l'agent à utiliser.
    """
    # Créer un prompt pour l'analyse
    prompt = f"""Analyser la requête suivante et déterminer l'agent le plus approprié:
    {query}
    
    Si la requête concerne la recherche de fichiers, répondre 'file_search_agent'.
    Sinon, répondre 'chat_agent'.
    """
    
    # Utiliser le LLM partagé pour analyser
    response = llm.generate_response(prompt).lower().strip()
    
    # Vérifier si la réponse est un agent valide
    if response in ['file_search_agent', 'chat_agent']:
        return response
    
    # Par défaut, utiliser l'agent de chat
    logger.info(f"Agent non reconnu '{response}', utilisation de chat_agent par défaut")
    return "chat_agent"

# Créer une instance de l'agent d'analyse
agent = CoreAgent(
    agent_name="Query Analyzer",
    system_instructions="""Je suis un agent d'analyse de requêtes.
    Mon rôle est d'analyser les requêtes des utilisateurs et de déterminer l'agent le plus approprié pour y répondre."""
)

if __name__ == '__main__':
    from core.llm_manager import get_llm_model
    llm = get_llm_model()
    query = "cherche un fichier pdf"
    response = analyze_query_tool(query, llm)
    print(f"Agent sélectionné: {response}")