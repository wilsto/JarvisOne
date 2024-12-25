"""Configuration du logging pour l'application."""

import logging
import sys
import streamlit as st
from typing import List
from datetime import datetime

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
    """Configure le logging pour l'application."""
    # Créer le handler Streamlit
    streamlit_handler = StreamlitHandler()
    streamlit_handler.setFormatter(
        logging.Formatter('%(message)s')
    )
    
    # Créer un handler pour la console
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(
        logging.Formatter('%(asctime)s - %(levelname)s - %(name)s - %(message)s')
    )
    
    # Configurer le root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)
    
    # Supprimer les handlers existants
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Ajouter nos handlers au root logger uniquement
    root_logger.addHandler(streamlit_handler)
    root_logger.addHandler(console_handler)
    
    # Configurer les loggers existants pour utiliser le root logger
    for name in logging.root.manager.loggerDict:
        logger = logging.getLogger(name)
        logger.handlers = []  # Supprimer les handlers existants
        logger.propagate = True  # Utiliser le root logger

def get_logs() -> List[dict]:
    """Récupère les logs stockés dans la session."""
    return st.session_state.get('logs', [])
