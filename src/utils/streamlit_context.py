"""Streamlit context management utilities."""

import logging
import warnings

def suppress_streamlit_context_warnings():
    """Suppress Streamlit context warnings by setting log level."""
    # Suppress Streamlit context warnings
    streamlit_logger = logging.getLogger('streamlit.runtime.scriptrunner_utils.script_run_context')
    streamlit_logger.setLevel(logging.ERROR)
    
    # Suppress PyTorch path warnings in Streamlit
    streamlit_watcher_logger = logging.getLogger('streamlit.watcher.local_sources_watcher')
    streamlit_watcher_logger.setLevel(logging.ERROR)
    
    # Suppress torch path warnings
    warnings.filterwarnings('ignore', message='.*torch.classes.*')
