"""Tests for file search agent."""

import pytest
from unittest.mock import Mock, patch, MagicMock
import streamlit as st
from datetime import datetime
import uuid
from src.features.agents.file_search_agent import (
    agent, clean_llm_response, execute_search,
    launch_everything_gui, handle_search_interaction,
    format_result
)
from tests.utils import mock_session_state  # Import the centralized fixture

@pytest.fixture
def mock_llm():
    """Mock LLM model."""
    mock = Mock()
    mock.generate_response.return_value = "ext:py dm:today"
    return mock

@pytest.fixture
def mock_subprocess():
    """Mock subprocess for testing execute_search."""
    with patch('subprocess.run') as mock_run:
        # Configure the mock
        mock_process = Mock()
        mock_process.returncode = 0
        mock_process.stdout = "file1.py\nfile2.py\n"
        mock_process.stderr = ""
        mock_run.return_value = mock_process
        yield mock_run

@pytest.fixture
def mock_streamlit():
    """Mock Streamlit for testing."""
    # Create context manager mock
    container_mock = MagicMock()
    container_mock.__enter__ = Mock(return_value=container_mock)
    container_mock.__exit__ = Mock(return_value=None)
    
    empty_mock = MagicMock()
    empty_mock.__enter__ = Mock(return_value=empty_mock)
    empty_mock.__exit__ = Mock(return_value=None)
    
    with patch('streamlit.empty', return_value=empty_mock) as mock_empty, \
         patch('streamlit.container', return_value=container_mock) as mock_container, \
         patch('streamlit.session_state', new_callable=dict) as mock_state, \
         patch('streamlit.markdown') as mock_markdown:
        yield {
            'empty': mock_empty,
            'container': mock_container,
            'session_state': mock_state,
            'markdown': mock_markdown
        }

def test_file_search_agent_initialization():
    """Test file search agent initialization."""
    assert agent.agent_name == "File Search Agent"
    assert "Everything search engine" in agent.system_instructions[0]
    assert agent.tools == [execute_search]
    assert agent.output_formatter is not None

def test_clean_llm_response():
    """Test LLM response cleaning."""
    test_cases = [
        ("user query: ext:py", "ext:py"),
        ("output: ext:py", "ext:py"),
        ("query: ext:py", "ext:py"),
        ("`ext:py`", "ext:py"),
        ("'ext:py'", "ext:py"),
        ('"ext:py"', "ext:py"),
        ("formatted query: ext:py", "ext:py"),
        ("everything query: ext:py", "ext:py"),
        ("EXT:PY", "ext:py"),
        ("  ext:py  ", "ext:py"),
    ]
    
    for input_str, expected in test_cases:
        assert clean_llm_response(input_str) == expected

def test_execute_search_success(mock_subprocess):
    """Test successful file search execution."""
    results = execute_search("ext:py")
    
    # Verify subprocess was called correctly
    mock_subprocess.assert_called_once()
    command = mock_subprocess.call_args[0][0]
    assert "es.exe" in command
    assert "ext:py" in command
    
    # Verify results
    assert len(results) == 2
    assert "file1.py" in results
    assert "file2.py" in results

def test_execute_search_error(mock_subprocess):
    """Test file search execution with error."""
    # Configure mock for error
    mock_subprocess.return_value.returncode = 1
    mock_subprocess.return_value.stderr = "Error message"
    
    results = execute_search("invalid:query")
    
    # Verify subprocess was called
    mock_subprocess.assert_called_once()
    
    # Verify empty results on error
    assert results == []

def test_execute_search_exception(mock_subprocess):
    """Test file search execution with exception."""
    # Configure mock to raise exception
    mock_subprocess.side_effect = Exception("Test error")
    
    results = execute_search("ext:py")
    
    # Verify subprocess was called
    mock_subprocess.assert_called_once()
    
    # Verify empty results on exception
    assert results == []

def test_docs_loading_error():
    """Test error handling when loading documentation."""
    with patch('builtins.open', side_effect=Exception("Test error")):
        # Re-import to trigger docs loading
        import importlib
        import src.features.agents.file_search_agent
        importlib.reload(src.features.agents.file_search_agent)
        
        # Verify default value is set
        assert src.features.agents.file_search_agent.everything_docs == "Documentation not available"

def test_launch_everything_gui_success():
    """Test successful launch of Everything GUI."""
    with patch('subprocess.Popen') as mock_popen:
        launch_everything_gui("test query")
        
        # Verify Popen was called with correct command
        mock_popen.assert_called_once()
        command = mock_popen.call_args[0][0]
        assert "Everything.exe" in command
        assert "test query" in command

def test_launch_everything_gui_error():
    """Test error handling when launching Everything GUI."""
    with patch('subprocess.Popen', side_effect=Exception("Test error")):
        # Should not raise exception
        launch_everything_gui("test query")

def test_handle_search_interaction_new_session(mock_session_state):
    """Test handling search interaction with new session."""
    transformed_query = "ext:py"
    results = ["file1.py", "file2.py"]
    
    mock_datetime = Mock()
    mock_datetime.strftime.return_value = "15:30:00"
    
    with patch('uuid.uuid4', return_value='test-id-123'), \
         patch('src.features.agents.file_search_agent.datetime') as mock_dt:
        mock_dt.now.return_value = mock_datetime
        
        interaction_id = handle_search_interaction(transformed_query, results)
        
        # Verify interaction was created correctly
        assert interaction_id == 'test-id-123'
        assert len(st.session_state.interactions) == 1
        
        interaction = st.session_state.interactions[0]
        assert interaction['id'] == 'test-id-123'
        assert interaction['type'] == 'file_search'
        assert interaction['query'] == transformed_query
        assert interaction['results'] == results
        assert interaction['timestamp'] == "15:30:00"

def test_handle_search_interaction_existing_session(mock_session_state):
    """Test handling search interaction with existing session."""
    # Setup existing interactions
    st.session_state.interactions = []
    
    transformed_query = "ext:py"
    results = ["file1.py", "file2.py"]
    
    interaction_id = handle_search_interaction(transformed_query, results)
    
    # Verify interaction was added to existing list
    assert len(st.session_state.interactions) == 1
    assert st.session_state.interactions[0]['id'] == interaction_id

def test_format_result_empty():
    """Test result formatting with no results."""
    message = format_result([], "ext:py")
    assert "no files" in message.lower()

def test_format_result_with_files():
    """Test result formatting with files found."""
    results = ["file1.py", "file2.py"]
    transformed_query = "ext:py"
    
    # Get the message formatter function
    message_formatter = format_result(results, transformed_query)
    
    # Format message with an interaction ID
    message = message_formatter("test-id-123")
    
    assert "2 files" in message.lower()
    assert "ext:py" in message
    assert "#test-id-123" in message

# def test_file_search_agent_run(mock_llm, mock_subprocess, mock_streamlit):
#     """Test file search agent run method."""
#     # Set the mock LLM
#     agent.llm = mock_llm
    
#     # Configure subprocess mock for success
#     mock_subprocess.return_value.stdout = "test1.py\ntest2.py"
    
#     # Test query
#     query = "trouve des fichiers python modifiés aujourd'hui"
#     response = agent.run(query)
    
#     # Verify LLM was called with correct system instructions
#     expected_prompt = f"{agent.system_instructions}\n\nUser Query: {query}"
#     mock_llm.generate_response.assert_called_once_with(expected_prompt)
    
#     # Verify search was executed with cleaned LLM response
#     mock_subprocess.assert_called_once()
#     command = mock_subprocess.call_args[0][0]
#     assert "ext:py dm:today" in command
    
#     # Verify Streamlit calls
#     mock_streamlit['markdown'].assert_called()  # CSS styles
#     mock_streamlit['container'].assert_called_once()
    
#     # Verify response format
#     assert isinstance(response, dict)
#     assert "content" in response
#     assert isinstance(response["content"], list)
#     assert len(response["content"]) == 2  # Two files in results
#     assert "test1.py" in response["content"]
#     assert "test2.py" in response["content"]
