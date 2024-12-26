"""Tests for chat agent."""

import pytest
from unittest.mock import Mock, patch
from src.features.agents.chat_agent import agent

@pytest.fixture
def mock_llm():
    """Mock LLM model."""
    mock = Mock()
    mock.generate_response.return_value = "Test response"
    return mock

def test_chat_agent_initialization():
    """Test chat agent initialization."""
    assert agent.agent_name == "Chat Agent"
    assert "Tu es un assistant chat" in agent.system_instructions

def test_chat_agent_run(mock_llm):
    """Test chat agent run method."""
    # Set the mock LLM
    agent.llm = mock_llm
    
    # Test query
    query = "Bonjour, comment allez-vous ?"
    response = agent.run(query)
    
    # Verify LLM was called with correct system instructions
    expected_prompt = f"{agent.system_instructions}\n\nUser Query: {query}"
    mock_llm.generate_response.assert_called_once_with(expected_prompt)
    
    # Verify response format
    assert isinstance(response, dict)
    assert "content" in response
    assert response["content"] == "Test response"
    assert "metadata" in response
    assert "raw_response" in response["metadata"]
    assert response["metadata"]["raw_response"] == "Test response"

def test_chat_agent_run_error_handling(mock_llm):
    """Test chat agent error handling."""
    # Set the mock LLM to raise an exception
    error_msg = "Test error"
    mock_llm.generate_response.return_value = f"Error generating response: {error_msg}"
    agent.llm = mock_llm
    
    # Test query
    query = "Test query"
    response = agent.run(query)
    
    # Verify error response
    assert isinstance(response, dict)
    assert "content" in response
    assert error_msg in response["content"]
    assert "metadata" in response
    assert "raw_response" in response["metadata"]
    assert error_msg in response["metadata"]["raw_response"]

def test_chat_agent_no_llm():
    """Test chat agent behavior without LLM."""
    # Create a mock LLM that returns an error
    mock_llm = Mock()
    mock_llm.generate_response.return_value = "Error generating response: LLM not initialized"
    agent.llm = mock_llm
    
    # Test query
    query = "Test query"
    response = agent.run(query)
    
    # Verify error response
    assert isinstance(response, dict)
    assert "content" in response
    assert "LLM not initialized" in response["content"]
    assert "metadata" in response
    assert "raw_response" in response["metadata"]
