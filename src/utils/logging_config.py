"""Logging configuration for the application."""

import logging
import sys
import streamlit as st
from typing import List
from datetime import datetime
from core.config_manager import ConfigManager

class StreamlitHandler(logging.Handler):
    """Custom handler to store logs in st.session_state."""
    
    def __init__(self) -> None:
        super().__init__()
        
    def emit(self, record: logging.LogRecord) -> None:
        try:
            # Check if we are in a valid Streamlit context
            try:
                from streamlit.runtime.scriptrunner import get_script_run_ctx
                if get_script_run_ctx() is None:
                    return  # No Streamlit context, silently ignore
            except:
                return  # In case of error, silently ignore
                
            # Initialize logs if necessary
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
            # Get config instance
            config = ConfigManager._load_config()
            # Keep only the latest logs based on configured limit
            max_entries = config.get('logging', {}).get('max_log_entries', 1000)
            if len(st.session_state.logs) > max_entries:
                st.session_state.logs = st.session_state.logs[-max_entries:]
        except Exception as e:
            # Silently handle errors to avoid infinite loops in logging
            # This is intentional as logging failures should not break the application
            sys.stderr.write(f"Error in StreamlitHandler: {str(e)}\n")

def setup_logging() -> None:
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
    
    # Suppress specific warnings
    logging.getLogger('streamlit.runtime.scriptrunner_utils.script_run_context').setLevel(logging.ERROR)

def get_logs() -> List[dict]:
    """Retrieve logs stored in the session."""
    return st.session_state.get('logs', [])
