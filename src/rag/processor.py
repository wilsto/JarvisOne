"""
Interfaces for RAG message processing.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any

class MessageProcessor(ABC):
    """Interface for any component that can process messages."""
    
    @abstractmethod
    async def process_message(
        self,
        message: str,
        workspace_id: str,
        **kwargs: Dict[str, Any]
    ) -> str:
        """
        Process a message and return a response.
        
        Args:
            message: The message to process
            workspace_id: ID of the current workspace
            **kwargs: Additional processing parameters
            
        Returns:
            The processed response
        """
        pass
