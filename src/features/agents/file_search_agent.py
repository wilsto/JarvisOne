from core.core_agent import CoreAgent
import subprocess
import logging
import os
from pathlib import Path
import streamlit as st
import pyperclip
from typing import List
from datetime import datetime
import random
import uuid
import shlex

# Configuration du logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Get the project root directory and construct the absolute path
project_root = Path(__file__).parent.parent.parent.parent
docs_path = project_root / "docs" / "everything.md"

# Read Everything search syntax documentation
try:
    with open(docs_path, "r", encoding="utf-8") as f:
        everything_docs = f.read()
    logger.info(f"Successfully loaded documentation from {docs_path}")
except Exception as e:
    logger.error(f"Error reading everything.md from {docs_path}: {str(e)}")
    everything_docs = "Documentation not available"

def get_everything_docs():
    """Get the contents of the Everything documentation."""
    try:
        with open(docs_path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        logger.error(f"Error reading everything.md from {docs_path}: {str(e)}")
        return "Documentation not available"

def query_in_context(query: str) -> str:
    """Add context paths to the query if available.
    
    Args:
        query: Base search query
        
    Returns:
        str: Query with context paths added
    """
    if 'knowledge_manager' in st.session_state:
        paths = st.session_state.knowledge_manager.get_space_paths()
        if paths:
            # Format paths for Everything search
            path_query = ' '.join([f'path:"{str(path).replace("/", "\\")}"' for path in paths])
            return f"{query} {path_query}"
    return query

def execute_search(query: str) -> List[str]:
    """Execute Everything search with the formatted query."""
    if not isinstance(query, str) or not query.strip():
        logger.warning("Invalid query provided")
        return []
        
    # Add context to query
    query = query_in_context(query)
    
    try:
        # Path to Everything CLI executable
        es_path = "C:\\Program Files\\Everything\\es.exe"
        
        # Use list of arguments instead of shell=True
        cmd = [es_path]
        cmd.extend(shlex.split(query))  # Safely split the query into arguments
        
        logger.info(f"Executing Everything search with command: {' '.join(cmd)}")
        
        # Execute search with explicit arguments
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True
        )
        
        # Process and deduplicate results
        results = result.stdout.strip().split('\n')
        results = [r for r in results if r]  # Remove empty lines
        results = list(dict.fromkeys(results))  # Remove duplicates
        
        logger.info(f"Search completed. Found {len(results)} unique results")
        return results
        
    except subprocess.CalledProcessError as e:
        logger.error(f"Error executing Everything search: {str(e)}")
        return []

def handle_search_interaction(transformed_query: str, results: List[str]) -> str:
    """Gère l'affichage des résultats de recherche dans l'interface.
    
    Args:
        transformed_query: La requête transformée par l'agent
        results: Liste des résultats de recherche
        
    Returns:
        str: L'ID de l'interaction créée
    """
    if "interactions" not in st.session_state:
        st.session_state.interactions = []
    
    transformed_query = query_in_context(transformed_query)

    interaction_id = str(uuid.uuid4())
    st.session_state.interactions.append({
        'id': interaction_id,
        'type': 'file_search',
        'query': transformed_query,  # Utiliser la requête transformée
        'results': results,
        'timestamp': datetime.now().strftime("%H:%M:%S")
    })
    
    return interaction_id

def format_result(results: List[str], transformed_query: str, interaction_id: str) -> str:
    """Format search results into a response message.
    
    Args:
        results: Liste des résultats de recherche
        transformed_query: La requête transformée par l'agent
        interaction_id: ID de l'interaction pour le lien
        
    Returns:
        str: Message de réponse formaté
    """

    transformed_query = query_in_context(transformed_query)
    nb_results = len(results)
    if nb_results == 0:
        return "Je n'ai trouvé aucun fichier correspondant à votre recherche."
    else:
        return f"J'ai trouvé {nb_results} fichiers qui correspondent à votre recherche (`{transformed_query}`). Vous pouvez les consulter dans l'[onglet Interactions](#{interaction_id})"

everything_docs = get_everything_docs()

agent = CoreAgent(
    agent_name="File Search Agent",
    system_instructions=[
        "You are a file search query analyzer for the Everything search engine.",
        "Convert natural language to Everything search syntax.",
        "Use this documentation:",
        "",
        everything_docs,
        "",
        "CRITICAL OUTPUT FORMAT RULES:",
        "1. Output ONLY the raw query string",
        "2. NO prefixes like 'Output:', 'Query:', etc.",
        "3. NO formatting (no quotes, backticks, parentheses)",
        "4. NO explanations or comments",
        "5. NO line breaks or extra spaces",
        "",
        "INCORRECT OUTPUTS:",
        "❌ Output: ext:py dm:today",
        "❌ `ext:py dm:today`",
        "❌ Query: ext:py dm:today",
        "❌ ext:py dm:today (python files from today)",
        "",
        "CORRECT OUTPUTS:",
        "✓ ext:py dm:today",
        "✓ ext:jpg;png size:>1mb",
        "✓ ext:doc;docx;pdf path:c:\\projects",
        "",
        "ANY OUTPUT NOT FOLLOWING THESE RULES EXACTLY WILL BE REJECTED.",
        "REMEMBER: RETURN ONLY THE RAW QUERY STRING."
    ],
    tools=[execute_search],
    output_formatter=lambda results, transformed_query, interaction_id: format_result(results, transformed_query, interaction_id),
    interactions=handle_search_interaction
)


if __name__ == '__main__':
    query = "cherche des fichier pdf avec le mot clé test"
    response = agent.run(query)
    print(response['content'])