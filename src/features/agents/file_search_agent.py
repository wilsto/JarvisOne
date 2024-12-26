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

def clean_llm_response(response: str) -> str:
    """Clean LLM response to ensure strict format."""
    # Remove common prefixes and formatting
    response = response.lower().strip()
    prefixes_to_remove = [
        "user query:", "output:", "correct query:",
        "query:", "formatted query:", "everything query:",
        "`", "'", '"'
    ]
    
    for prefix in prefixes_to_remove:
        if response.startswith(prefix):
            response = response[len(prefix):].strip()
    
    # Remove any trailing formatting
    response = response.rstrip('`\'" ')
    
    return response

def execute_search(query: str) -> List[str]:
    """Execute Everything search with the formatted query."""
    # Clean the query first
    query = clean_llm_response(query)
    
    try:
        # Path to Everything CLI executable
        es_path = "C:\\Program Files\\Everything\\es.exe"
        
        # Construct and log the command
        command = f'"{es_path}" {query}'
        logger.info(f"Executing Everything search with command: {command}")
        
        # Execute the command
        process = subprocess.run(
            command,
            shell=True,  # Needed for quoted paths
            capture_output=True,
            text=True
        )

        # Check the return code
        if process.returncode != 0:
            logger.error(f"Search failed with return code {process.returncode}")
            logger.error(f"Error output: {process.stderr}")
            return []
        
        # Split the output into lines, remove empty lines and duplicates
        results = list(dict.fromkeys([line.strip() for line in process.stdout.split('\n') if line.strip()]))
        logger.info(f"Search completed. Found {len(results)} unique results")
        return results
        
    except Exception as e:
        logger.error(f"Search execution error: {str(e)}")
        logger.error("Exception details:", exc_info=True)
        return []

def launch_everything_gui(query: str):
    """Launch Everything GUI with the specified query."""
    try:
        everything_path = "C:\\Program Files\\Everything\\Everything.exe"
        command = f'"{everything_path}" -s "{query}"'
        subprocess.Popen(command, shell=True)
        logger.info(f"Launched Everything GUI with query: {query}")
    except Exception as e:
        logger.error(f"Failed to launch Everything GUI: {str(e)}")

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
    
    interaction_id = str(uuid.uuid4())
    st.session_state.interactions.append({
        'id': interaction_id,
        'type': 'file_search',
        'query': transformed_query,  # Utiliser la requête transformée
        'results': results,
        'timestamp': datetime.now().strftime("%H:%M:%S")
    })
    
    return interaction_id

def format_result(results: List[str], transformed_query: str) -> str:
    """Format search results into a response message.
    
    Args:
        results: Liste des résultats de recherche
        transformed_query: La requête transformée par l'agent
        
    Returns:
        str: Message de réponse formaté
    """
    nb_results = len(results)
    if nb_results == 0:
        return "Je n'ai trouvé aucun fichier correspondant à votre recherche."
    else:
        # L'ID sera fourni par CoreAgent via handle_search_interaction
        return lambda interaction_id: f"J'ai trouvé {nb_results} fichiers qui correspondent à votre recherche (`{transformed_query}`). Vous pouvez les consulter dans l'[onglet Interactions](#{interaction_id})."

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
    output_formatter=lambda results, transformed_query, interaction_id: format_result(results, transformed_query)(interaction_id),
    interactions=handle_search_interaction
)


if __name__ == '__main__':
    query = "cherche des fichier pdf avec le mot clé test"
    response = agent.run(query)
    print(response['content'])