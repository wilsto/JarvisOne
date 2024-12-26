"""Factory for creating display handlers."""
from typing import Dict, Type, Any
from .base import BaseInteractionDisplay

class DefaultDisplay(BaseInteractionDisplay):
    """Default display handler when no specific handler is found."""
    
    def display(self, interaction: Dict[str, Any]) -> None:
        """Display interaction in a generic way."""
        import streamlit as st
        st.json(interaction)

class InteractionDisplayFactory:
    """Factory for creating appropriate display handlers."""
    
    _handlers: Dict[str, Type[BaseInteractionDisplay]] = {}
    _default_handler = DefaultDisplay
    
    @classmethod
    def get_display_handler(cls, interaction_type: str) -> BaseInteractionDisplay:
        """Get the appropriate display handler for the interaction type."""
        handler_class = cls._handlers.get(interaction_type, cls._default_handler)
        return handler_class()
    
    @classmethod
    def register_handler(cls, interaction_type: str, handler_class: Type[BaseInteractionDisplay]) -> None:
        """Register a new display handler."""
        cls._handlers[interaction_type] = handler_class
