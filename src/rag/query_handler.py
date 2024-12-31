"""RAG query handler for retrieving relevant context."""

import logging
from typing import List, Dict, Optional
from pathlib import Path

from vector_db.manager import VectorDBManager

# Configure logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

if not logger.handlers:
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
    logger.addHandler(handler)

class RAGQueryHandler:
    """Handles RAG queries to retrieve relevant context."""
    
    def __init__(self):
        """Initialize query handler."""
        logger.info("Initializing RAGQueryHandler")
        self.vector_db = VectorDBManager.get_instance()
        
    def query(self, query_text: str, workspace_id: str, role_id: str = None, top_k: int = 3) -> List[Dict]:
        """Query the vector store for relevant documents.
        
        Args:
            query_text: Text to search for
            workspace_id: Workspace identifier
            role_id: Optional role identifier
            top_k: Number of results to return
            
        Returns:
            List of documents with their content and metadata
        """
        try:
            logger.info(f"Starting RAG query - Text: {query_text}, Workspace: {workspace_id}, Role: {role_id}")
            
            # Query through VectorDBManager
            results = self.vector_db.query(
                workspace_id=workspace_id,
                query_text=query_text,
                n_results=top_k
            )
            
            if not results:
                logger.warning(f"No results found for query in workspace {workspace_id}")
                return []
                
            logger.info(f"Found {len(results)} documents")
            for i, result in enumerate(results):
                logger.info(f"Document {i+1}/{len(results)} - Distance: {result.get('distance')}")
                logger.info(f"Content preview: {result['content'][:100]}...")
                
            return results
            
        except Exception as e:
            logger.error(f"Error in RAG query: {e}", exc_info=True)
            return []
            
    def cleanup(self):
        """Clean up resources."""
        pass
