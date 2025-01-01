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
            # Get interaction data for UI display
            interaction_data = await self.middleware.get_interaction_data(message, workspace_id)
            interaction_id = None
            
            if interaction_data and self.interaction_manager:
                # Create interaction for RAG results using the manager function
                interaction_id = self.interaction_manager(message, interaction_data)
                logger.info(f"Created RAG interaction with ID: {interaction_id}")
            
            # Enhance the prompt with relevant document context
            enhanced_prompt = await self.middleware.enhance_prompt(message, workspace_id)
            
            # Pass enhanced prompt to processor along with the interaction ID
            logger.info("Processing enhanced prompt")
            response = await self.processor.process_message(
                enhanced_prompt,
                workspace_id,
                rag_interaction_id=interaction_id,  # Pass the RAG interaction ID to the processor
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
