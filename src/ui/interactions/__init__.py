"""Package for interaction displays."""
from .base import BaseInteractionDisplay
from .factory import InteractionDisplayFactory
from . import agents  # Import agents to register handlers

__all__ = ['BaseInteractionDisplay', 'InteractionDisplayFactory']
