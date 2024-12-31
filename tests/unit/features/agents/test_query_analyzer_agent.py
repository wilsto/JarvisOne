"""Tests for query analyzer agent."""

import pytest
import logging
from unittest.mock import Mock, patch
from src.features.agents.query_analyzer_agent import QueryAnalyzerAgent

@pytest.fixture
def mock_llm():
    """Mock LLM model."""
    mock = Mock()
    return mock

@pytest.fixture
def agent():
    """Create a test agent instance."""
    return QueryAnalyzerAgent()

def test_query_analyzer_initialization(agent):
    """Test l'initialisation de l'agent d'analyse."""
    assert agent is not None
    assert agent.agent_name == "Query Analyzer Agent"
    assert "agentmatcher" in agent.system_instructions.lower()
    assert len(agent.tools) == 0  # No tools needed for this agent

@patch('src.features.agents.confidence_verifier_agent.agent.verify_confidence')
def test_analyze_query_file_search(mock_verify, agent, mock_llm):
    """Test query analysis for file search queries."""
    # Mock the confidence verifier
    mock_verify.return_value = (90, "high", "Good match for file search")
    
    test_cases = [
        (
            "cherche un fichier python",
            "file_search_agent\nConfidence: 95\nReason: Query explicitly asks to find python files"
        ),
        (
            "trouve les fichiers modifiés aujourd'hui",
            "file_search_agent\nConfidence: 90\nReason: Query about finding modified files"
        )
    ]
    
    for query, llm_response in test_cases:
        mock_llm.generate_response.return_value = llm_response
        agent.llm = mock_llm
        
        result = agent.analyze_query(query)
        
        # Verify result is a string and matches expected agent
        assert isinstance(result, str)
        assert result == "file_search_agent"
        
        # Verify LLM was called with correct prompt
        prompt = mock_llm.generate_response.call_args[0][0]
        assert query in prompt
        assert "file_search_agent" in prompt.lower()
        assert "chat_agent" in prompt.lower()
        mock_llm.generate_response.reset_mock()

@patch('src.features.agents.confidence_verifier_agent.agent.verify_confidence')
def test_analyze_query_chat(mock_verify, agent, mock_llm):
    """Test query analysis for chat queries."""
    # Mock the confidence verifier
    mock_verify.return_value = (80, "medium", "General chat query")
    
    query = "comment vas-tu?"
    llm_response = "chat_agent\nConfidence: 80\nReason: Simple conversational query"
    
    mock_llm.generate_response.return_value = llm_response
    agent.llm = mock_llm
    
    result = agent.analyze_query(query)
    
    # Verify result is a string and matches expected agent
    assert isinstance(result, str)
    assert result == "chat_agent"

@patch('src.features.agents.confidence_verifier_agent.agent.verify_confidence')
def test_analyze_query_invalid_response(mock_verify, agent, mock_llm):
    """Test query analysis with invalid LLM response."""
    # Mock the confidence verifier
    mock_verify.return_value = (50, "low", "Invalid response format")
    
    # Test invalid response format
    mock_llm.generate_response.return_value = "invalid format response"
    agent.llm = mock_llm
    
    result = agent.analyze_query("test query")
    
    # Should default to chat_agent
    assert isinstance(result, str)
    assert result == "chat_agent"

@patch('src.features.agents.confidence_verifier_agent.agent.verify_confidence')
def test_analyze_query_logging(mock_verify, agent, mock_llm, caplog):
    """Test logging in query analyzer."""
    # Mock the confidence verifier
    mock_verify.return_value = (90, "high", "Good match")
    
    # Set up logging capture
    caplog.set_level(logging.INFO)
    
    # Test query
    query = "cherche un fichier"
    llm_response = "file_search_agent\nConfidence: 90\nReason: File search query"
    
    mock_llm.generate_response.return_value = llm_response
    agent.llm = mock_llm
    
    result = agent.analyze_query(query)
    
    # Verify logging
    assert any("Query:" in record.message for record in caplog.records)
    assert any("file_search_agent" in record.message for record in caplog.records)
    assert any("90" in record.message for record in caplog.records)
