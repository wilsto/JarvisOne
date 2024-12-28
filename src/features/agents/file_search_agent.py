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

# Configure logger
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
    if 'workspace_manager' in st.session_state:
        paths = st.session_state.workspace_manager.get_space_paths()
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
    """Handle the display of search results in the interface.
    
    Args:
        transformed_query: The query transformed by the agent
        results: List of search results
        
    Returns:
        str: The ID of the created interaction
    """
    if "interactions" not in st.session_state:
        st.session_state.interactions = []
    
    transformed_query = query_in_context(transformed_query)

    interaction_id = str(uuid.uuid4())
    st.session_state.interactions.append({
        'id': interaction_id,
        'type': 'file_search',
        'query': transformed_query,  # Use the transformed query
        'results': results,
        'timestamp': datetime.now().strftime("%H:%M:%S")
    })
    
    return interaction_id

def format_result(results: List[str], transformed_query: str, interaction_id: str) -> str:
    """Format search results into a response message.
    
    Args:
        results: List of search results
        transformed_query: The query transformed by the agent
        interaction_id: Interaction ID for the link
        
    Returns:
        str: Formatted response message
    """

    transformed_query = query_in_context(transformed_query)
    nb_results = len(results)
    if nb_results == 0:
        return "No files found matching your search."
    else:
        return f"I found {nb_results} files matching your search (`{transformed_query}`). You can view them in the [Interactions tab](#{interaction_id})"

everything_docs = get_everything_docs()

agent = CoreAgent(
    agent_name="File Search Agent",
    system_instructions="\n".join([
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
    ]),
    tools=[execute_search],
    output_formatter=lambda results, transformed_query, interaction_id: format_result(results, transformed_query, interaction_id),
    interactions=handle_search_interaction
)


if __name__ == '__main__':
    query = "search for pdf files with keyword test"
    response = agent.run(query)
    print(response['content'])