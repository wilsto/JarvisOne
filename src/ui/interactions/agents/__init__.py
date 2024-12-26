"""Package for agent-specific display handlers."""
from .file_search import FileSearchDisplay
from .query_analyzer import QueryAnalyzerDisplay

# Register display handlers
from ..factory import InteractionDisplayFactory

InteractionDisplayFactory.register_handler('file_search', FileSearchDisplay)
InteractionDisplayFactory.register_handler('query_analyzer', QueryAnalyzerDisplay)

__all__ = ['FileSearchDisplay', 'QueryAnalyzerDisplay']
