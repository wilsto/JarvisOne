import pytest
from src.core.core_agent import CoreAgent, ManagedLLM
from src.core.llm_base import LLM
from unittest.mock import patch, MagicMock
from core.workspace_manager import SpaceType, SpaceConfig
from pathlib import Path
from dataclasses import dataclass
from tests.mocks.session_state import SessionStateMock  # Import from new location

@dataclass
class MockRole:
    name: str
    description: str
    prompt_context: str

class MockLLM(LLM):
    def __init__(self):
        self.last_prompt = None
        self.mock_response = "Test response"
        self.should_raise = False

    def generate_response(self, prompt: str) -> str:
        if self.should_raise:
            raise Exception("Test error")
        self.last_prompt = prompt
        return self.mock_response

    def set_mock_response(self, response: str):
        self.mock_response = response
    
    def set_should_raise(self, should_raise: bool):
        self.should_raise = should_raise

class ErrorRaisingLLM(LLM):
    def generate_response(self, prompt: str) -> str:
        raise Exception("Test error")

class SuccessLLM(LLM):
    def generate_response(self, prompt: str) -> str:
        return "Success response"

@pytest.fixture
def mock_llm():
    return MockLLM()

@pytest.fixture
def core_agent(mock_llm):
    return CoreAgent(
        agent_name="test_agent",
        system_instructions="Test instructions",
        llm=mock_llm
    )

@pytest.fixture
def mock_workspace_manager():
    """Create a mock workspace manager with test data."""
    mock_manager = MagicMock()
    
    mock_space_config = SpaceConfig(
        name="Test Workspace",
        paths=[Path("test/path")],
        metadata={"description": "Test workspace"},
        search_params={},
        tags=["test"],
        workspace_prompt="Test workspace prompt",
        scope="Test workspace scope",
        roles=[
            MockRole(
                name="Coach",
                description="An AI coach that helps users achieve their goals",
                prompt_context="Test role context"
            )
        ]
    )
    
    # Setup workspace manager properties
    mock_manager.current_space = SpaceType.COACHING
    mock_manager.spaces = {SpaceType.COACHING: mock_space_config}
    mock_manager.get_current_space_config.return_value = mock_space_config
    mock_manager.current_space_config = mock_space_config
    
    return mock_manager

def test_core_agent_initialization(core_agent):
    """Test that CoreAgent can be initialized with an LLM"""
    assert core_agent is not None
    assert isinstance(core_agent.llm, LLM)
    assert core_agent.agent_name == "test_agent"
    assert core_agent.system_instructions == "Test instructions"

def test_core_agent_run(core_agent, mock_llm):
    """Test that CoreAgent can process a query"""
    mock_llm.set_mock_response("Processed response")
    response = core_agent.run("Test query")

    assert response["content"] == "Processed response"
    assert mock_llm.last_prompt is not None
    assert "Test instructions" in mock_llm.last_prompt

def test_core_agent_empty_query(core_agent):
    """Test that CoreAgent handles empty queries appropriately"""
    response = core_agent.run("")
    assert response["content"] == "Please provide a valid query."

def test_core_agent_with_tool(core_agent, mock_llm):
    """Test that CoreAgent can use tools"""
    def mock_tool(response: str) -> str:
        return f"Tool processed: {response}"
    
    # Add tool to agent
    core_agent.tools = [mock_tool]
    mock_llm.set_mock_response("LLM response")
    
    response = core_agent.run("Test with tool")
    assert response["content"] == "Tool processed: LLM response"

def test_core_agent_system_instructions(core_agent, mock_llm):
    """Test that CoreAgent properly uses system instructions"""
    mock_llm.set_mock_response("Response with instructions")
    
    # Create a new agent with specific instructions
    agent = CoreAgent(
        agent_name="test_agent",
        system_instructions="Special test instructions",
        llm=mock_llm
    )
    
    response = agent.run("Test query")
    assert "Special test instructions" in mock_llm.last_prompt
    assert response["content"] == "Response with instructions"

def test_managed_llm_error_handling():
    """Test that ManagedLLM handles errors properly"""
    error_llm = ErrorRaisingLLM()
    managed_llm = ManagedLLM()
    managed_llm.model = error_llm
    
    response = managed_llm.generate_response("Test query")
    assert "Error generating response" in response

def test_managed_llm_success():
    """Test that ManagedLLM handles successful responses"""
    success_llm = SuccessLLM()
    managed_llm = ManagedLLM()
    managed_llm.model = success_llm
    
    response = managed_llm.generate_response("Test query")
    assert response == "Success response"

def test_core_agent_tool_error():
    """Test that CoreAgent handles tool errors properly"""
    mock_llm = MockLLM()
    
    def failing_tool(response: str) -> str:
        raise Exception("Tool error")
    
    agent = CoreAgent(
        agent_name="test_agent",
        system_instructions="Test instructions",
        tools=[failing_tool],
        llm=mock_llm
    )
    
    response = agent.run("Test query")
    assert isinstance(response["content"], list)
    assert len(response["content"]) == 0  # Empty list on error

def test_core_agent_output_formatter(core_agent, mock_llm):
    """Test that CoreAgent uses output formatter properly"""
    def mock_formatter(content, raw_response, interaction_id):
        return {
            "formatted_content": content,
            "raw": raw_response,
            "interaction": interaction_id
        }

    core_agent.output_formatter = mock_formatter
    mock_llm.set_mock_response("Test response")
    
    response = core_agent.run("Test query")
    
    assert "formatted_content" in response
    assert response["raw"] == "Test response"
    assert response["interaction"] is None

def test_core_agent_output_formatter_none_content(core_agent, mock_llm):
    """Test that CoreAgent handles None content with formatter"""
    def mock_formatter(content, raw_response, interaction_id):
        return {
            "formatted_content": content,
            "raw": raw_response,
            "interaction": interaction_id
        }

    core_agent.output_formatter = mock_formatter
    mock_llm.set_mock_response("Test response")
    
    # Simulate no content output
    response = core_agent.run("Test query")
    
    assert "formatted_content" in response
    assert response["raw"] == "Test response"
    assert response["interaction"] is None

def test_core_agent_with_workspace_context(core_agent, mock_llm, mock_workspace_manager):
    """Test that CoreAgent properly includes workspace context in prompt."""
    # Set workspace manager
    core_agent.workspace_manager = mock_workspace_manager
    
    # Run query
    response = core_agent.run("Test query", workspace_id="COACHING")
    
    # Verify workspace context in prompt
    assert "Test workspace prompt" in mock_llm.last_prompt
    assert "Test workspace scope" in mock_llm.last_prompt
    assert "Working in scope: COACHING" in mock_llm.last_prompt

def test_core_agent_without_workspace_context(core_agent, mock_llm):
    """Test that CoreAgent works without workspace context."""
    response = core_agent.run("Test query")
    
    # Basic prompt should still work
    assert "Test instructions" in mock_llm.last_prompt
    assert response["content"] is not None

def test_core_agent_with_empty_workspace_context(core_agent, mock_llm, mock_workspace_manager):
    """Test that CoreAgent handles empty workspace context gracefully."""
    # Modify mock space config to have empty values
    mock_space_config = SpaceConfig(
        name="Test Workspace",
        paths=[Path("test/path")],
        metadata={},
        search_params={},
        tags=["test"],
        workspace_prompt="",
        scope="",
        roles=[]
    )
    
    mock_workspace_manager.spaces = {"COACHING": mock_space_config}
    mock_workspace_manager.current_space_config = mock_space_config
    
    # Set workspace manager
    core_agent.workspace_manager = mock_workspace_manager
    
    # Run query
    response = core_agent.run("Test query", workspace_id="COACHING")
    
    # Should still work with basic prompt
    assert "Test instructions" in mock_llm.last_prompt
    assert response["content"] is not None

def test_core_agent_workspace_debug_mode(core_agent, mock_llm, mock_workspace_manager, caplog):
    """Test that CoreAgent includes debug information in workspace context when debug is enabled."""
    import logging
    caplog.set_level(logging.DEBUG)
    
    # Set workspace manager
    core_agent.workspace_manager = mock_workspace_manager
    
    # Run query
    response = core_agent.run("Test query", workspace_id="COACHING")
    
    # Debug information should be included
    assert "=== Workspace Context ===" in mock_llm.last_prompt
    assert "Active Workspace: COACHING" in mock_llm.last_prompt

def test_core_agent_role_context(core_agent, mock_llm, mock_workspace_manager):
    """Test that CoreAgent includes role context when available."""
    # Add role to mock space config
    mock_space_config = mock_workspace_manager.current_space_config
    mock_space_config.roles = [
        MockRole(
            name="Coach",
            description="An AI coach that helps users achieve their goals",
            prompt_context="Test role context"
        )
    ]
    
    # Set workspace manager and role
    core_agent.workspace_manager = mock_workspace_manager
    
    # Run query with role
    response = core_agent.run("Test query", workspace_id="COACHING", role_id="Coach")
    
    # Basic prompt components should be present
    assert "Test instructions" in mock_llm.last_prompt
    assert "Working in scope: COACHING" in mock_llm.last_prompt
    
    # Role context should be included
    assert "Test role context" in mock_llm.last_prompt

def test_core_agent_invalid_role(core_agent, mock_llm, mock_workspace_manager):
    """Test that CoreAgent handles invalid roles gracefully."""
    # Add role to mock space config
    mock_space_config = mock_workspace_manager.current_space_config
    mock_space_config.roles = [
        MockRole(
            name="Coach",
            description="An AI coach that helps users achieve their goals",
            prompt_context="Test role context"
        )
    ]
    
    # Set workspace manager
    core_agent.workspace_manager = mock_workspace_manager
    
    # Run query with invalid role
    response = core_agent.run("Test query", workspace_id="COACHING", role_id="InvalidRole")
    
    # Basic prompt components should be present
    assert "Test instructions" in mock_llm.last_prompt
    assert "Working in scope: COACHING" in mock_llm.last_prompt
    
    # Role context should not be included
    assert "Test role context" not in mock_llm.last_prompt

def test_prepare_prompt_config(core_agent, mock_workspace_manager):
    """Test that prompt configuration preparation works correctly."""
    # Setup workspace with role
    mock_space_config = mock_workspace_manager.current_space_config
    mock_space_config.workspace_prompt = "Test workspace prompt"
    mock_space_config.scope = "Test workspace scope"
    mock_space_config.roles = [
        MockRole(
            name="Coach",
            description="An AI coach that helps users achieve their goals",
            prompt_context="Test role context"
        )
    ]
    
    # Set workspace manager
    core_agent.workspace_manager = mock_workspace_manager
    
    # Prepare config with all components
    config = core_agent._prepare_prompt_config(
        "Test query",
        workspace_id="COACHING",
        role_id="Coach"
    )
    
    # Verify system config
    assert config.system_config is not None
    assert config.system_config.context_prompt == core_agent.system_prompt
    assert config.system_config.workspace_scope == "COACHING"
    
    # Verify workspace config
    assert config.workspace_config is not None
    assert config.workspace_config.workspace_prompt == "Test workspace prompt"
    assert config.workspace_config.scope == "Test workspace scope"
    
    # Verify role config
    assert config.role_config is not None
    assert config.role_config.role_id == "Coach"
    assert config.role_config.prompt_context == "Test role context"
    
    # Verify preferences config exists
    assert config.preferences_config is not None

def test_prepare_prompt_config_fallback(core_agent):
    """Test that prompt configuration preparation provides fallback on error."""
    # Prepare config without workspace manager (should use fallback)
    config = core_agent._prepare_prompt_config("Test query")
    
    # Verify basic config is present
    assert config.system_config is not None
    assert config.system_config.context_prompt == core_agent.system_prompt
    
    # Verify optional configs are None
    assert config.workspace_config is None
    assert config.role_config is None
    assert config.rag_config is None
