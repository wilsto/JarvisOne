from core.core_agent import CoreAgent
import subprocess
import logging
import os
from pathlib import Path
import streamlit as st

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

def execute_search(query: str) -> list:
    """Execute an Everything search command and return the results."""
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
        
        # Log output details
        logger.info(f"Raw stdout: {process.stdout}")
        logger.info(f"Raw stderr: {process.stderr}")
        logger.info(f"Return code: {process.returncode}")
        
        if process.returncode != 0:
            logger.error(f"Search failed with return code {process.returncode}")
            logger.error(f"Error output: {process.stderr}")
            return []
            
        # Split the output into lines, remove empty lines and duplicates
        results = list(dict.fromkeys([line.strip() for line in process.stdout.split('\n') if line.strip()]))
        logger.info(f"Search completed. Found {len(results)} unique results")
        if results:
            logger.info("Results found:")
            for i, r in enumerate(results, 1):
                logger.info(f"{i}. {r}")
        else:
            logger.info("No results found")
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

def format_result(content: list, formatted_query: str) -> dict:
    """Format search results for display.
    
    Args:
        content: List of search results from execute_search
        formatted_query: The query formatted by the LLM
        
    Returns:
        dict: Formatted response with content and metadata
    """
    if not content:
        logger.info("No results found")
        return {
            "content": "Aucun résultat trouvé.",
            "metadata": {
                "total_results": 0,
                "has_more": False,
                "formatted_query": formatted_query
            }
        }
    
    total_results = len(content)
    displayed_results = [f"\n• {file_path}" for file_path in content[:10]]
    
    # Format response
    formatted = [
        f"\nRecherche effectuée : {formatted_query}",
        f"\nNombre total de résultats : {total_results}",
        "\n"
    ]
    
    formatted.extend(displayed_results)
    
    if total_results > 10:
        formatted.append(f"\n... et {total_results - 10} autres résultats")
    
    logger.info(f"Formatted {total_results} results for query: {formatted_query}")
    for i, file_path in enumerate(content[:10], 1):
        logger.info(f"{i}. {file_path}")
    
    # Add Everything GUI button with formatted query
    st.button("🔍 Ouvrir dans Everything", 
             on_click=launch_everything_gui, 
             args=(formatted_query,),
             help="Ouvre Everything avec cette recherche")
    
    return {
        "content": "\n".join(formatted),
        "metadata": {
            "total_results": total_results,
            "has_more": total_results > 10,
            "results": content,
            "formatted_query": formatted_query
        }
    }

agent = CoreAgent(
    agent_name="File Search Agent",
    system_instructions=[
        "You are a file search query analyzer. Format search queries for Everything search engine.",
        "Convert natural language to Everything syntax using the following documentation:",
        "",
        everything_docs,
        "",
        "After formatting the query, I will execute it using Everything search engine.",
        "Return ONLY the formatted query, nothing else."
    ],
    tools=[execute_search],
    output_formatter=format_result
)


if __name__ == '__main__':
    query = "cherche des fichier pdf avec le mot clé test"
    response = agent.run(query)
    print(response['content'])