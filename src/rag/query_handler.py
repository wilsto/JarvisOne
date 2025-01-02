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
        self.embeddings = VectorDBManager.get_instance().embeddings  # Assuming embeddings is an attribute of VectorDBManager
        
    def verify_semantic_relevance(self, query: str, document: str) -> float:
        """Verify semantic relevance between query and document.
        
        Args:
            query: Search query
            document: Document content
        
        Returns:
            Relevance score between 0 and 1
        """
        try:
            # Use the same embeddings model for consistency
            query_embedding = self.embeddings.embed_query(query)
            doc_embedding = self.embeddings.embed_query(document)
            
            # Calculate cosine similarity
            similarity = self._cosine_similarity(query_embedding, doc_embedding)
            return float(similarity)
        except Exception as e:
            logger.error(f"Error in semantic verification: {e}")
            return 0.0
        
    def _cosine_similarity(self, vec1, vec2) -> float:
        """Calculate cosine similarity between two vectors."""
        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        norm1 = sum(a * a for a in vec1) ** 0.5
        norm2 = sum(b * b for b in vec2) ** 0.5
        return dot_product / (norm1 * norm2) if norm1 > 0 and norm2 > 0 else 0.0
        
    def query(self, query_text: str, workspace_id: str, role_id: str = None, top_k: int = 3, 
              similarity_threshold: float = 0.7) -> List[Dict]:
        """Query the vector store for relevant documents.
        
        Args:
            query_text: Text to search for
            workspace_id: Workspace identifier
            role_id: Optional role identifier
            top_k: Number of results to return
            similarity_threshold: Minimum similarity score (0-1) for results
        
        Returns:
            List of documents with their content and metadata
        """
        try:
            logger.info(f"Starting RAG query - Text: {query_text}, Workspace: {workspace_id}, Role: {role_id}")
            
            # Query through VectorDBManager
            initial_results = self.vector_db.query(
                workspace_id=workspace_id,
                query_text=query_text,
                n_results=top_k * 2  # Get more results initially for filtering
            )
            
            if not initial_results:
                logger.warning(f"No results found for query in workspace {workspace_id}")
                return []
                
            # Filter and rerank results
            filtered_results = []
            for result in initial_results:
                # Check vector similarity
                distance = result.get('distance', 1.0)
                vector_similarity = 1 - distance
                
                if vector_similarity < similarity_threshold:
                    continue
                    
                # Verify semantic relevance
                semantic_score = self.verify_semantic_relevance(query_text, result['content'])
                
                if semantic_score >= similarity_threshold:
                    # Combine scores for final ranking
                    final_score = (vector_similarity + semantic_score) / 2
                    filtered_results.append({
                        **result,
                        'semantic_score': semantic_score,
                        'final_score': final_score
                    })
            
            # Sort by final score and take top_k
            filtered_results.sort(key=lambda x: x['final_score'], reverse=True)
            final_results = filtered_results[:top_k]
            
            logger.info(f"Found {len(final_results)} relevant documents after filtering")
            for i, result in enumerate(final_results):
                logger.info(f"Document {i+1}/{len(final_results)} - "
                           f"Final Score: {result['final_score']:.3f}, "
                           f"Vector Sim: {1-result['distance']:.3f}, "
                           f"Semantic: {result['semantic_score']:.3f}")
                logger.info(f"Content preview: {result['content'][:100]}...")
                
            return final_results
            
        except Exception as e:
            logger.error(f"Error in RAG query: {e}", exc_info=True)
            return []
            
    def cleanup(self):
        """Clean up resources."""
        pass
