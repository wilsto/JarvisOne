"""Configuration du logging pour l'application."""

import logging
import sys
import streamlit as st
from typing import List
from datetime import datetime
from core.config_manager import ConfigManager

class StreamlitHandler(logging.Handler):
    """Handler personnalisé pour stocker les logs dans st.session_state."""
    
    def __init__(self):
        super().__init__()
        
    def emit(self, record):
        try:
            # Vérifier si nous sommes dans un contexte Streamlit valide
            try:
                from streamlit.runtime.scriptrunner import get_script_run_ctx
                if get_script_run_ctx() is None:
                    return  # Pas de contexte Streamlit, on ignore silencieusement
            except:
                return  # En cas d'erreur, on ignore silencieusement
                
            # Initialiser les logs si nécessaire
            if "logs" not in st.session_state:
                st.session_state.logs = []
                
            msg = self.format(record)
            timestamp = datetime.fromtimestamp(record.created).strftime('%Y-%m-%d %H:%M:%S')
            log_entry = {
                'timestamp': timestamp,
                'level': record.levelname,
                'message': msg
            }
            st.session_state.logs.append(log_entry)
            # Keep only the last 1000 logs
            if len(st.session_state.logs) > 1000:
                st.session_state.logs = st.session_state.logs[-1000:]
        except Exception:
            # En cas d'erreur, on ne fait rien pour éviter les boucles infinies
            pass

def setup_logging():
    """Configure logging for the application."""
    # Load logging configuration
    config = ConfigManager._load_config()
    log_level = config.get("logging", {}).get("level", "INFO")
    log_level = getattr(logging, log_level.upper(), logging.INFO)
    
    # Create Streamlit handler
    streamlit_handler = StreamlitHandler()
    streamlit_handler.setFormatter(
        logging.Formatter('%(message)s')
    )
    
    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(
        logging.Formatter('%(asctime)s - %(levelname)s - %(name)s - %(message)s')
    )
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    
    # Remove existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Add our handlers to root logger only
    root_logger.addHandler(streamlit_handler)
    root_logger.addHandler(console_handler)
    
    # Configure existing loggers to use root logger
    for name in logging.root.manager.loggerDict:
        logger = logging.getLogger(name)
        logger.handlers = []  # Remove existing handlers
        logger.propagate = True  # Use root logger

def get_logs() -> List[dict]:
    """Récupère les logs stockés dans la session."""
    return st.session_state.get('logs', [])
