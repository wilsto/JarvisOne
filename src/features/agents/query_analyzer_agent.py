import logging
from core.core_agent import CoreAgent
from core.llm_base import LLM
import streamlit as st
from datetime import datetime
import uuid

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
    "{query}"
    
    Règles de sélection :
    1. Utiliser 'file_search_agent' si la requête :
       - Concerne la recherche ou manipulation de fichiers
       - Contient des mots comme : fichier, file, trouve, cherche, search, modifié, créé
       - Mentionne des extensions (.py, .txt, etc.) ou types de fichiers (python, text, etc.)
       
    2. Utiliser 'chat_agent' si :
       - C'est une question générale
       - Demande des explications ou informations
       - Ne concerne pas la recherche de fichiers
    
    Répondre UNIQUEMENT avec 'file_search_agent' ou 'chat_agent'.
    """
    
    # Utiliser le LLM partagé pour analyser
    response = llm.generate_response(prompt).lower().strip()
    logger.info(f"Query: '{query}' → Agent selected: '{response}'")
    
    # Créer l'analyse
    analysis = {
        'agent_selected': response,
        'reason': 'Recherche de fichiers' if response == 'file_search_agent' else 'Question générale'
    }
    
    # Créer l'interaction
    handle_query_interaction(query, analysis)
    
    # Vérifier si la réponse est un agent valide
    if response in ['file_search_agent', 'chat_agent']:
        return response
    
    # Par défaut, utiliser l'agent de chat
    logger.warning(f"Agent non reconnu '{response}', utilisation de chat_agent par défaut")
    return "chat_agent"

def handle_query_interaction(transformed_query: str, analysis: dict) -> str:
    """Gère l'affichage de l'analyse de requête dans l'interface.
    
    Args:
        transformed_query: La requête analysée
        analysis: Le résultat de l'analyse
        
    Returns:
        str: L'ID de l'interaction créée
    """
    if "interactions" not in st.session_state:
        st.session_state.interactions = []
    
    interaction_id = str(uuid.uuid4())
    st.session_state.interactions.append({
        'id': interaction_id,
        'type': 'query_analyzer',
        'query': transformed_query,
        'analysis': analysis,
        'timestamp': datetime.now().strftime("%H:%M:%S")
    })
    
    return interaction_id

# Créer une instance de l'agent d'analyse
agent = CoreAgent(
    agent_name="Query Analyzer Agent",
    system_instructions=[
        "You are a query analyzer that helps understand user intentions.",
        "Analyze the query and identify key components.",
        "",
        "CRITICAL OUTPUT FORMAT RULES:",
        "1. Output ONLY the raw analysis as JSON",
        "2. NO explanations or comments",
        "3. NO line breaks or extra spaces",
    ],
    output_formatter=None,  # Pas besoin de formateur spécial
    interactions=handle_query_interaction
)

if __name__ == '__main__':
    from core.llm_manager import get_llm_model
    llm = get_llm_model()
    query = "cherche un fichier pdf"
    response = analyze_query_tool(query, llm)
    print(f"Agent sélectionné: {response}")