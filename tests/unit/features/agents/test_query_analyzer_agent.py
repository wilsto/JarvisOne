"""Tests for query analyzer agent."""

import pytest
import logging
from unittest.mock import Mock, patch
from src.features.agents.query_analyzer_agent import agent, analyze_query_tool

@pytest.fixture
def mock_llm():
    """Mock LLM model."""
    mock = Mock()
    return mock

def test_query_analyzer_initialization():
    """Test query analyzer agent initialization."""
    assert agent.agent_name == "Query Analyzer"
    assert "analyse de requêtes" in agent.system_instructions.lower()
    assert len(agent.tools) == 0  # No tools needed for this agent

def test_analyze_query_file_search():
    """Test query analysis for file search queries."""
    mock = Mock()
    test_cases = [
        ("cherche un fichier python", "file_search_agent"),
        ("trouve les fichiers modifiés aujourd'hui", "file_search_agent"),
        ("liste les .txt", "file_search_agent"),
        ("search for python files", "file_search_agent"),
        ("fichiers créés hier", "file_search_agent")
    ]
    
    for query, expected in test_cases:
        mock.generate_response.return_value = expected
        result = analyze_query_tool(query, mock)
        assert result == expected
        
        # Verify LLM was called with correct prompt
        prompt = mock.generate_response.call_args[0][0]
        assert query in prompt
        assert "file_search_agent" in prompt
        assert "chat_agent" in prompt
        mock.generate_response.reset_mock()

def test_analyze_query_chat():
    """Test query analysis for chat queries."""
    mock = Mock()
    test_cases = [
        ("explique-moi python", "chat_agent"),
        ("quelle est la météo ?", "chat_agent"),
        ("comment vas-tu ?", "chat_agent"),
        ("aide-moi avec git", "chat_agent")
    ]
    
    for query, expected in test_cases:
        mock.generate_response.return_value = expected
        result = analyze_query_tool(query, mock)
        assert result == expected
        
        # Verify LLM was called with correct prompt
        prompt = mock.generate_response.call_args[0][0]
        assert query in prompt
        mock.generate_response.reset_mock()

def test_analyze_query_invalid_response():
    """Test query analysis with invalid LLM response."""
    mock = Mock()
    test_cases = [
        "invalid_agent",
        "unknown",
        "",
        "test_agent",
        "none"
    ]
    
    for invalid_response in test_cases:
        mock.generate_response.return_value = invalid_response
        result = analyze_query_tool("test query", mock)
        assert result == "chat_agent"  # Should default to chat_agent
        mock.generate_response.reset_mock()

def test_analyze_query_logging(caplog):
    """Test logging in query analyzer."""
    mock = Mock()
    query = "test query"
    
    # Test successful case
    mock.generate_response.return_value = "chat_agent"
    with caplog.at_level(logging.INFO):
        analyze_query_tool(query, mock)
    assert "Agent selected: 'chat_agent'" in caplog.text
    
    # Test warning case
    caplog.clear()
    mock.generate_response.return_value = "invalid_agent"
    with caplog.at_level(logging.WARNING):
        analyze_query_tool(query, mock)
    assert "Agent non reconnu" in caplog.text
