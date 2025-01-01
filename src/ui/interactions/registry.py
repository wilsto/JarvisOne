"""Register all interaction display handlers."""
from .factory import InteractionDisplayFactory
from .system.config_display import ConfigChangeDisplay
from .agents.file_search import FileSearchDisplay
from .agents.query_analyzer import QueryAnalyzerDisplay
from .agents.rag_display import RAGSearchDisplay

def register_handlers():
    """Register all interaction display handlers."""
    # Register system handlers
    InteractionDisplayFactory.register_handler('config_change', ConfigChangeDisplay)
    
    # Register agent handlers
    InteractionDisplayFactory.register_handler('file_search', FileSearchDisplay)
    InteractionDisplayFactory.register_handler('query_analyzer', QueryAnalyzerDisplay)
    InteractionDisplayFactory.register_handler('rag_search', RAGSearchDisplay)
