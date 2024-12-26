from core.core_agent import CoreAgent
import subprocess
import logging
import os
from pathlib import Path
import streamlit as st
import pyperclip
from typing import List

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

def format_result(results: List[str], query: str) -> List[str]:
    """Format and display search results using Streamlit."""
    
    # Style CSS pour les résultats
    st.markdown("""
        <style>
        .result-row {
            display: flex;
            align-items: center;
            padding: 4px 0;
            margin: 2px 0;
        }
        .result-number {
            min-width: 40px;
            font-weight: bold;
            color: #555;
        }
        .result-content {
            flex-grow: 1;
            margin-left: 10px;
        }
        .file-name {
            font-weight: bold;
            color: #1f1f1f;
        }
        .file-path {
            color: #666;
            font-size: 0.85em;
        }
        </style>
    """, unsafe_allow_html=True)
    
    # Conteneur principal avec padding minimal
    with st.container():
        # En-tête compact
        col1, col2 = st.columns([9, 1])
        with col1:
            with st.expander("ℹ️ Informations de recherche", expanded=False):
                st.code(query, language="text")
        with col2:
            st.metric("Résultats", len(results), label_visibility="visible")
        
        # Affichage des résultats
        for i, result in enumerate(results, 1):
            file_path = result.strip()
            file_name = os.path.basename(file_path)
            dir_path = os.path.dirname(file_path)
            
            # Utilisation de colonnes pour un layout horizontal
            cols = st.columns([0.4, 5, 0.6])
            
            with cols[0]:
                # Numéro plus grand pour les 10 premiers résultats
                if i <= 10:
                    st.markdown(f"<h3 style='margin: 0; color: #555;'>#{i}</h3>", unsafe_allow_html=True)
                else:
                    st.markdown(f"<div style='color: #666;'>#{i}</div>", unsafe_allow_html=True)
            
            with cols[1]:
                # Nom de fichier et chemin sur une seule ligne
                st.markdown(
                    f"<div style='line-height: 1.2;'>"
                    f"<span class='file-name'>{file_name}</span><br/>"
                    f"<span class='file-path'>{dir_path}</span>"
                    f"</div>",
                    unsafe_allow_html=True
                )
            
            with cols[2]:
                if st.button("📋", key=f"copy_{i}", help="Copier le chemin"):
                    pyperclip.copy(file_path)
                    st.toast("Chemin copié !", icon="✅")
        
        # Bouton Everything en bas
        st.button("🔍 Ouvrir dans Everything", 
                 key="open_everything", 
                 use_container_width=True,
                 on_click=launch_everything_gui,
                 args=(query,))
    
    # Return the results for CoreAgent
    return results

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
    output_formatter=format_result
)


if __name__ == '__main__':
    query = "cherche des fichier pdf avec le mot clé test"
    response = agent.run(query)
    print(response['content'])