"""
RAG-based prompt enhancement functionality.
"""

import logging
from typing import Optional, Dict, Any, Callable

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
        rag_config: Optional[RAGConfig] = None,
        interaction_manager: Optional[Callable] = None
    ):
        """
        Initialize the RAG enhancer.
        
        Args:
            processor: The message processor to enhance with RAG
            document_processor: Document processor for searching relevant context
            rag_config: Optional RAG configuration
            interaction_manager: Function to handle RAG interactions display
        """
        self.processor = processor
        self.middleware = RAGMiddleware(document_processor, rag_config)
        self.interaction_manager = interaction_manager
        logger.info("Initialized RAG enhancer with config: %s", rag_config)
    
    async def process_message(
        self,
        message: str,
        workspace_id: str,
        **kwargs: Dict[str, Any]
    ) -> str:
        """Process a message with document-enhanced context."""
        try:
            # Get interaction data for UI display
            logger.debug(f"Getting RAG interaction data for message: {message[:100]}...")
            interaction_data = await self.middleware.get_interaction_data(message, workspace_id)
            
            # If we have RAG results, create a RAG interaction first
            if interaction_data and self.interaction_manager:
                logger.info(f"Found {len(interaction_data.get('results', []))} relevant documents")
                logger.debug("Creating RAG interaction...")
                interaction_id = self.interaction_manager(message, interaction_data)
                logger.info(f"Created RAG interaction with ID: {interaction_id}")
                
                # Enhance the prompt with relevant document context
                logger.debug("Getting enhanced prompt...")
                enhanced_prompt = await self.middleware.enhance_prompt(message, workspace_id)
                
                # Process with enhanced prompt
                logger.info("Processing message with enhanced prompt")
                return await self.processor.process_message(
                    enhanced_prompt,
                    workspace_id,
                    **kwargs
                )
            
            # If no RAG results, process normally
            logger.info("No relevant documents found, processing original message")
            return await self.processor.process_message(
                message,
                workspace_id,
                **kwargs
            )
            
        except Exception as e:
            logger.error(f"Error in RAG enhancer: {str(e)}", exc_info=True)
            # Fallback to processor on error
            return await self.processor.process_message(
                message,
                workspace_id,
                **kwargs
            )
