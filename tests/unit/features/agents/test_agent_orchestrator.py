"""Tests for AgentOrchestrator."""

import pytest
from unittest.mock import patch, MagicMock, Mock
import streamlit as st
from src.core.core_agent import CoreAgent
from src.core.config_manager import ConfigManager
from src.features.agents.agent_orchestrator import AgentOrchestrator
from tests.mocks.session_state import SessionStateMock

@pytest.fixture
def mock_llm():
    """Mock LLM model."""
    return MagicMock()

@pytest.fixture
def mock_config():
    """Mock configuration."""
    return {
        "provider": "test_provider",
        "model": "test_model"
    }

@pytest.fixture
def mock_agents():
    """Mock available agents."""
    chat_agent = Mock(spec=CoreAgent)
    chat_agent.agent_name = "chat"
    chat_agent.run.return_value = {"response": "chat response"}
    
    file_agent = Mock(spec=CoreAgent)
    file_agent.agent_name = "file"
    file_agent.run.return_value = {"response": "file response"}
    
    return {
        "chat": chat_agent,
        "file": file_agent
    }

@pytest.fixture
def mock_query_analyzer():
    """Mock query analyzer agent."""
    analyzer = Mock()
    analyzer.analyze_query = Mock()
    return analyzer

@pytest.fixture
def orchestrator(mock_llm, mock_config, mock_agents, mock_query_analyzer):
    """Create AgentOrchestrator with mocked dependencies."""
    with patch("src.features.agents.agent_orchestrator.get_llm_model", return_value=mock_llm), \
         patch("src.features.agents.agent_orchestrator.ConfigManager.load_llm_preferences", return_value=mock_config), \
         patch("src.features.agents.agent_orchestrator.query_analyzer_agent", mock_query_analyzer), \
         patch.object(AgentOrchestrator, "_load_agents", return_value=mock_agents):
        with SessionStateMock():
            return AgentOrchestrator()

def test_initialization(orchestrator, mock_llm, mock_config):
    """Test orchestrator initialization."""
    assert orchestrator.llm == mock_llm
    assert st.session_state.llm_provider == mock_config["provider"]
    assert st.session_state.llm_model == mock_config["model"]

def test_agent_selection_success(orchestrator, mock_agents):
    """Test successful agent selection."""
    orchestrator.query_analyzer.analyze_query.return_value = "file_agent"
    agent = orchestrator._select_agent("find file test.txt")
    assert agent == mock_agents["file"]

def test_agent_selection_fallback(orchestrator, mock_agents):
    """Test agent selection fallback to chat agent."""
    orchestrator.query_analyzer.analyze_query.return_value = "unknown_agent"
    agent = orchestrator._select_agent("unknown command")
    assert agent == mock_agents["chat"]

def test_agent_selection_error(orchestrator, mock_agents):
    """Test agent selection error handling."""
    orchestrator.query_analyzer.analyze_query.side_effect = Exception("test error")
    agent = orchestrator._select_agent("test query")
    assert agent == mock_agents["chat"]

def test_process_query_success(orchestrator, mock_agents):
    """Test successful query processing."""
    orchestrator.query_analyzer.analyze_query.return_value = "file_agent"
    response = orchestrator.process_query("find file test.txt")
    assert response == {"response": "file response"}
    mock_agents["file"].run.assert_called_once_with("find file test.txt")

def test_process_query_error(orchestrator):
    """Test query processing error handling."""
    error_message = "test error"
    with patch.object(orchestrator, "_select_agent", side_effect=Exception(error_message)):
        response = orchestrator.process_query("test query")
        assert response == {"error": True, "message": error_message}

def test_no_preferences(mock_llm, mock_agents):
    """Test initialization without preferences."""
    with patch("src.features.agents.agent_orchestrator.get_llm_model", return_value=mock_llm), \
         patch("src.features.agents.agent_orchestrator.ConfigManager.load_llm_preferences", return_value=None), \
         patch.object(AgentOrchestrator, "_load_agents", return_value=mock_agents):
        with SessionStateMock():
            orchestrator = AgentOrchestrator()
            assert orchestrator.llm == mock_llm
            assert st.session_state.llm_provider is None
            assert st.session_state.llm_model is None

def test_load_agents(mock_llm):
    """Test loading of agents."""
    # Create mock agents
    chat_agent = Mock(spec=CoreAgent)
    chat_agent.agent_name = "chat"
    file_agent = Mock(spec=CoreAgent)
    file_agent.agent_name = "file"
    
    # Mock the package walk
    mock_walk = [
        (None, "chat_agent", False),
        (None, "file_agent", False),
        (None, "__init__", False)
    ]
    
    # Mock the module imports
    mock_chat_module = MagicMock()
    mock_chat_module.chat_agent = chat_agent
    mock_file_module = MagicMock()
    mock_file_module.file_agent = file_agent
    
    mock_modules = {
        "src.features.agents": MagicMock(__path__=["mock_path"]),
        "src.features.agents.chat_agent": mock_chat_module,
        "src.features.agents.file_agent": mock_file_module
    }
    
    def mock_import_module(name):
        if name == "src.features.agents":
            mock_pkg = MagicMock()
            mock_pkg.__path__ = ["mock_path"]
            return mock_pkg
        return mock_modules[name]
    
    with patch("pkgutil.walk_packages", return_value=mock_walk), \
         patch("importlib.import_module", side_effect=mock_import_module):
        with SessionStateMock():
            orchestrator = AgentOrchestrator()
            agents = orchestrator.available_agents
            
            # Verify agents were loaded
            assert "chat" in agents
            assert "file" in agents
            assert agents["chat"] == chat_agent
            assert agents["file"] == file_agent
            
            # Verify LLM was passed to agents
            assert agents["chat"].llm == orchestrator.llm
            assert agents["file"].llm == orchestrator.llm

def test_load_agents_with_package(mock_llm):
    """Test loading of agents when a package is encountered."""
    chat_agent = Mock(spec=CoreAgent)
    chat_agent.agent_name = "chat"
    
    # Mock walk_packages to include a package
    mock_walk = [
        (None, "chat_agent", False),
        (None, "submodule", True),  # This is a package
        (None, "__init__", False)
    ]
    
    # Mock the module imports
    mock_chat_module = MagicMock()
    mock_chat_module.chat_agent = chat_agent
    
    mock_modules = {
        "src.features.agents": MagicMock(__path__=["mock_path"]),
        "src.features.agents.chat_agent": mock_chat_module
    }
    
    def mock_import_module(name):
        if name == "src.features.agents":
            mock_pkg = MagicMock()
            mock_pkg.__path__ = ["mock_path"]
            return mock_pkg
        return mock_modules[name]
    
    with patch("pkgutil.walk_packages", return_value=mock_walk), \
         patch("importlib.import_module", side_effect=mock_import_module):
        with SessionStateMock():
            orchestrator = AgentOrchestrator()
            agents = orchestrator.available_agents
            
            # Verify only non-package modules were processed
            assert "chat" in agents
            assert "submodule" not in agents

def test_load_agents_non_agent_items(mock_llm):
    """Test loading of agents when module contains non-agent items."""
    chat_agent = Mock(spec=CoreAgent)
    chat_agent.agent_name = "chat"
    
    # Mock module with both agent and non-agent items
    mock_chat_module = MagicMock()
    mock_chat_module.chat_agent = chat_agent
    mock_chat_module.non_agent = "some value"
    mock_chat_module.another_non_agent = 123
    
    mock_modules = {
        "src.features.agents": MagicMock(__path__=["mock_path"]),
        "src.features.agents.chat_agent": mock_chat_module
    }
    
    with patch("pkgutil.walk_packages", return_value=[(None, "chat_agent", False)]), \
         patch("importlib.import_module", side_effect=lambda name: mock_modules[name]):
        with SessionStateMock():
            orchestrator = AgentOrchestrator()
            agents = orchestrator.available_agents
            
            # Verify only agent items were loaded
            assert "chat" in agents
            assert len(agents) == 1
            assert agents["chat"] == chat_agent
