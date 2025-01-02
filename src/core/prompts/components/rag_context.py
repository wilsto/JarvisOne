"""RAG context builder component."""

import logging
from dataclasses import dataclass
from typing import Optional, List, Dict, Any

logger = logging.getLogger(__name__)

@dataclass
class RAGDocument:
    """Represents a document retrieved from RAG system."""
    content: str
    metadata: Dict[str, Any]

@dataclass
class RAGContextConfig:
    """Configuration for RAG context building."""
    query: str
    documents: List[RAGDocument]
    debug: bool = False

class RAGContextBuilder:
    """Builds RAG context with consistent structure and formatting."""

    @staticmethod
    def build(config: RAGContextConfig) -> str:
        """Build RAG context from the given configuration.
        
        Args:
            config: RAGContextConfig containing context building parameters
            
        Returns:
            str: Formatted RAG context
        """
        try:
            if config.debug:
                logger.info("Building RAG context with config: %s", config)
                
            sections = []
            
            if config.debug:
                sections.append("=== RAG Context ===")
                sections.append(f"Query: {config.query}")
                
            if not config.documents:
                return ""
                
            for doc in config.documents:
                source = doc.metadata.get('file_path', 'unknown source')
                sections.append(f"From {source}:")
                sections.append(doc.content)
                
            return "\n\n".join(sections)
            
        except Exception as e:
            logger.error("Error building RAG context: %s", e)
            return ""
