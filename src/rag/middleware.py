"""
RAG Middleware for enhancing prompts with relevant document context.
"""

import logging
from typing import Optional, List, Dict, Any
from dataclasses import dataclass
import os
from datetime import datetime
import uuid

from .document_processor import DocumentProcessor, ImportanceLevelType

logger = logging.getLogger(__name__)

@dataclass
class RAGConfig:
    """Configuration for RAG middleware."""
    max_results: int = 3
    min_similarity: float = 0.7
    importance_filter: Optional[ImportanceLevelType] = None
    max_tokens: int = 4000
    context_template: str = "Relevant context:\n{context}\n\nUser query: {query}"
    
    def __post_init__(self):
        """Log configuration after initialization."""
        logger.info(f"Initializing RAGConfig with: max_results={self.max_results}, "
                   f"min_similarity={self.min_similarity}, "
                   f"importance_filter={self.importance_filter}, "
                   f"max_tokens={self.max_tokens}")

class RAGMiddleware:
    """Middleware for adding document context to prompts."""
    
    def __init__(self, document_processor: DocumentProcessor, config: Optional[RAGConfig] = None):
        """
        Initialize the RAG middleware.
        
        Args:
            document_processor: Document processor instance for searching
            config: Optional configuration, uses defaults if not provided
        """
        self.processor = document_processor
        self.config = config or RAGConfig()
        logger.info("Initialized RAG middleware with config: %s", self.config)
    
    def _format_context(self, results: List[Dict]) -> str:
        """Format results into a context string for prompt enhancement."""
        if not results:
            return ""
            
        context_parts = []
        for result in results:
            metadata = result.get('metadata', {})
            source = metadata.get('source', 'Unknown source')
            file_name = os.path.basename(source)
            context_parts.append(
                f"[Source: {file_name} | Score: {result['similarity_score']:.2f}]\n{result['content'].strip()}"
            )
        
        return "\n\n".join(context_parts)
    
    def _get_search_results(self, query: str, workspace_id: str) -> List[Dict]:
        """Get and format search results."""
        logger.debug(f"Searching documents for query: {query[:100]}...")
        
        # Search for relevant documents
        documents = self.processor.search_documents(
            query=query,
            workspace_id=workspace_id,
            n_results=self.config.max_results,
            importance_filter=self.config.importance_filter
        )
        
        logger.debug(f"Found {len(documents)} documents")
        
        # Filter and format results
        results = [
            {
                'content': doc['content'].strip(),
                'similarity_score': doc['similarity_score'],
                'metadata': {
                    'source': doc.get('source', 'Unknown'),
                    'created_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
            }
            for doc in documents 
            if doc['similarity_score'] >= self.config.min_similarity
        ]
        
        logger.info(f"Returning {len(results)} relevant results after filtering")
        return results

    async def get_interaction_data(self, query: str, workspace_id: str) -> Optional[Dict[str, Any]]:
        """Get RAG results formatted for UI interaction display."""
        try:
            logger.info(f"Getting RAG results for query: {query[:100]}...")
            results = self._get_search_results(query, workspace_id)
            
            if results:
                logger.info(f"Found {len(results)} relevant documents")
                interaction_data = {
                    'id': str(uuid.uuid4()),  # Add unique ID
                    'type': 'rag_search',
                    'query': query,
                    'results': results,
                    'timestamp': datetime.now().strftime("%H:%M:%S")
                }
                logger.debug(f"Created interaction data: {interaction_data}")
                return interaction_data
            
            logger.info("No relevant documents found")
            return None
            
        except Exception as e:
            logger.error(f"Error getting interaction data: {str(e)}", exc_info=True)
            return None
    
    async def enhance_prompt(self, query: str, workspace_id: str) -> str:
        """
        Enhance a prompt with relevant document context.
        
        Args:
            query: The user's query
            workspace_id: ID of the workspace to search in
            
        Returns:
            Enhanced prompt with relevant context
        """
        try:
            logger.info("Enhancing prompt for query in workspace %s", workspace_id)
            results = self._get_search_results(query, workspace_id)
            
            if results:
                logger.info("Found relevant context from %d documents", len(results))
                context = self._format_context(results)
                return self.config.context_template.format(
                    context=context,
                    query=query
                )
            
            logger.info("No relevant context found, returning original query")
            return query
            
        except Exception as e:
            logger.error("Error enhancing prompt: %s", str(e))
            return query
