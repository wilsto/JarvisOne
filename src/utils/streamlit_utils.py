"""Utilities for handling Streamlit-specific functionality."""

import warnings
import logging
import functools
import threading
from contextlib import contextmanager

logger = logging.getLogger(__name__)

class StreamlitThread(threading.Thread):
    """Thread class that suppresses Streamlit context warnings."""
    
    def run(self):
        """Override run to suppress warnings."""
        with warnings.catch_warnings():
            warnings.filterwarnings(
                "ignore",
                message=".*missing ScriptRunContext.*",
                category=Warning
            )
            super().run()

def suppress_streamlit_warnings(func):
    """Decorator to suppress Streamlit warnings in background threads."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        with warnings.catch_warnings():
            warnings.filterwarnings(
                "ignore",
                message=".*missing ScriptRunContext.*",
                category=Warning
            )
            return func(*args, **kwargs)
    return wrapper

@contextmanager
def streamlit_warning_suppressor():
    """Context manager to suppress Streamlit warnings."""
    with warnings.catch_warnings():
        warnings.filterwarnings(
            "ignore",
            message=".*missing ScriptRunContext.*",
            category=Warning
        )
        yield
