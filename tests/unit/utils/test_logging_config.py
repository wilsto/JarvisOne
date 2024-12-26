"""Tests for logging configuration."""

import pytest
import logging
import streamlit as st
from datetime import datetime
from src.utils.logging_config import StreamlitHandler, setup_logging, get_logs
from unittest.mock import patch, MagicMock
from tests.utils import MockSessionState

@pytest.fixture
def mock_session_state():
    """Mock Streamlit's session state."""
    with patch('streamlit.session_state', new_callable=MockSessionState) as mock_state:
        yield mock_state

@pytest.fixture
def mock_script_run_ctx():
    """Mock Streamlit's script run context."""
    with patch('streamlit.runtime.scriptrunner.get_script_run_ctx') as mock_ctx:
        mock_ctx.return_value = MagicMock()  # Simule un contexte Streamlit valide
        yield mock_ctx

def test_streamlit_handler_init():
    """Test StreamlitHandler initialization."""
    handler = StreamlitHandler()
    assert isinstance(handler, logging.Handler)

def test_streamlit_handler_emit_no_context(mock_session_state, mock_script_run_ctx):
    """Test StreamlitHandler.emit when no Streamlit context."""
    mock_script_run_ctx.return_value = None  # Simule l'absence de contexte Streamlit
    
    handler = StreamlitHandler()
    record = logging.LogRecord(
        name="test_logger",
        level=logging.INFO,
        pathname="test.py",
        lineno=1,
        msg="Test message",
        args=(),
        exc_info=None
    )
    
    handler.emit(record)
    assert 'logs' not in mock_session_state  # Pas de logs stockés sans contexte

def test_streamlit_handler_emit_with_context(mock_session_state, mock_script_run_ctx):
    """Test StreamlitHandler.emit with valid Streamlit context."""
    handler = StreamlitHandler()
    record = logging.LogRecord(
        name="test_logger",
        level=logging.INFO,
        pathname="test.py",
        lineno=1,
        msg="Test message",
        args=(),
        exc_info=None
    )
    
    handler.emit(record)
    
    assert 'logs' in mock_session_state
    assert len(mock_session_state['logs']) == 1
    log_entry = mock_session_state['logs'][0]
    assert log_entry['level'] == 'INFO'
    assert log_entry['message'] == 'Test message'
    assert isinstance(log_entry['timestamp'], str)

def test_streamlit_handler_emit_max_logs(mock_session_state, mock_script_run_ctx):
    """Test StreamlitHandler.emit respects max logs limit."""
    handler = StreamlitHandler()
    
    # Créer 1100 logs (au-delà de la limite de 1000)
    for i in range(1100):
        record = logging.LogRecord(
            name="test_logger",
            level=logging.INFO,
            pathname="test.py",
            lineno=1,
            msg=f"Test message {i}",
            args=(),
            exc_info=None
        )
        handler.emit(record)
    
    assert len(mock_session_state['logs']) == 1000  # Vérifie la limite
    assert mock_session_state['logs'][-1]['message'] == 'Test message 1099'  # Vérifie que c'est le dernier message

def test_setup_logging():
    """Test setup_logging configuration."""
    setup_logging()
    
    root_logger = logging.getLogger()
    assert root_logger.level == logging.DEBUG
    
    # Vérifie les handlers
    handler_types = [type(h) for h in root_logger.handlers]
    assert StreamlitHandler in handler_types
    assert logging.StreamHandler in handler_types
    
    # Vérifie que les autres loggers propagent au root logger
    test_logger = logging.getLogger('test')
    assert len(test_logger.handlers) == 0
    assert test_logger.propagate is True

def test_get_logs_empty(mock_session_state):
    """Test get_logs with no logs."""
    logs = get_logs()
    assert logs == []

def test_get_logs_with_data(mock_session_state):
    """Test get_logs with existing logs."""
    test_logs = [
        {
            'timestamp': '2024-01-01 12:00:00',
            'level': 'INFO',
            'message': 'Test message'
        }
    ]
    mock_session_state['logs'] = test_logs
    
    logs = get_logs()
    assert logs == test_logs
