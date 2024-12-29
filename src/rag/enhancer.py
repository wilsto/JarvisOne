"""
RAG-based prompt enhancement functionality.
"""

import logging
from typing import Optional, Dict, Any

from .middleware import RAGMiddleware, RAGConfig
from .document_processor import DocumentProcessor
from .processor import MessageProcessor

logger = logging.getLogger(__name__)

class RAGEnhancer:
    """
    Enhances prompts with relevant document context.
    Wraps any message processor to add RAG capabilities without modifying its behavior.
    """
    
    def __init__(
        self,
        processor: MessageProcessor,
        document_processor: DocumentProcessor,
        rag_config: Optional[RAGConfig] = None
    ):
        """
        Initialize the RAG enhancer.
        
        Args:
            processor: The message processor to enhance with RAG
            document_processor: Document processor for searching relevant context
            rag_config: Optional RAG configuration
        """
        self.processor = processor
        self.middleware = RAGMiddleware(document_processor, rag_config)
        logger.info("Initialized RAG enhancer with config: %s", rag_config)
    
    async def process_message(
        self,
        message: str,
        workspace_id: str,
        **kwargs: Dict[str, Any]
    ) -> str:
        """
        Process a message with document-enhanced context.
        
        Args:
            message: The message to process
            workspace_id: ID of the current workspace
            **kwargs: Additional arguments passed to the processor
            
        Returns:
            The processed response
        """
        try:
            # Enhance the prompt with relevant document context
            enhanced_prompt = await self.middleware.enhance_prompt(message, workspace_id)
            
            # Pass enhanced prompt to processor
            logger.info("Processing enhanced prompt")
            response = await self.processor.process_message(
                enhanced_prompt,
                workspace_id,
                **kwargs
            )
            
            return response
            
        except Exception as e:
            logger.error("Error in RAG enhancer: %s", str(e))
            # Fallback to processor on error
            return await self.processor.process_message(
                message,
                workspace_id,
                **kwargs
            )
