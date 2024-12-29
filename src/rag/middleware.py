"""
RAG Middleware for enhancing prompts with relevant document context.
"""

import logging
from typing import Optional, List, Dict
from dataclasses import dataclass

from .document_processor import DocumentProcessor, ImportanceLevelType

logger = logging.getLogger(__name__)

@dataclass
class RAGConfig:
    """Configuration for RAG middleware."""
    max_results: int = 3
    min_similarity: float = 0.7
    importance_filter: Optional[ImportanceLevelType] = None
    context_template: str = "Relevant context:\n{context}\n\nUser query: {query}"

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
    
    def _format_context(self, documents: List[Dict]) -> str:
        """Format document contents into a context string."""
        if not documents:
            return ""
        
        # Sort by similarity score
        sorted_docs = sorted(documents, key=lambda x: x['similarity_score'], reverse=True)
        
        # Filter by minimum similarity
        relevant_docs = [
            doc for doc in sorted_docs 
            if doc['similarity_score'] >= self.config.min_similarity
        ]
        
        # Format each document with its metadata
        context_parts = []
        for doc in relevant_docs[:self.config.max_results]:
            context_parts.append(
                f"[Score: {doc['similarity_score']:.2f}] {doc['content'].strip()}"
            )
        
        return "\n\n".join(context_parts)
    
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
            
            # Search for relevant documents
            documents = self.processor.search_documents(
                query=query,
                workspace_id=workspace_id,
                n_results=self.config.max_results,
                importance_filter=self.config.importance_filter
            )
            
            # Format context from documents
            context = self._format_context(documents)
            
            if context:
                logger.info("Found relevant context from %d documents", len(documents))
                # Return enhanced prompt
                return self.config.context_template.format(
                    context=context,
                    query=query
                )
            else:
                logger.info("No relevant context found, returning original query")
                return query
                
        except Exception as e:
            logger.error("Error enhancing prompt: %s", str(e))
            # On error, return original query
            return query
