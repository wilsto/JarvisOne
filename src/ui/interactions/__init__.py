"""Package for interaction displays."""
from .base import BaseInteractionDisplay
from .factory import InteractionDisplayFactory
from .registry import register_handlers

# Register all handlers
register_handlers()

__all__ = ['BaseInteractionDisplay', 'InteractionDisplayFactory']
