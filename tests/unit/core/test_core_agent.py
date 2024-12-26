import pytest
from src.core.core_agent import CoreAgent, ManagedLLM
from src.core.llm_base import LLM
from unittest.mock import patch, MagicMock
from tests.utils import mock_session_state  # Import the common fixture

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
    assert "Test query" in mock_llm.last_prompt
    assert "Test instructions" in mock_llm.last_prompt

def test_core_agent_empty_query(core_agent):
    """Test that CoreAgent handles empty queries appropriately"""
    response = core_agent.run("")
    assert isinstance(response, dict)
    assert "content" in response

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

def test_core_agent_output_formatter():
    """Test that CoreAgent uses output formatter properly"""
    mock_llm = MockLLM()
    
    def mock_formatter(content: str, raw_response: str, interaction_id: str = None) -> dict:
        return {
            "formatted": content,
            "raw": raw_response,
            "interaction_id": interaction_id
        }
    
    agent = CoreAgent(
        agent_name="test_agent",
        system_instructions="Test instructions",
        output_formatter=mock_formatter,
        llm=mock_llm
    )
    
    response = agent.run("Test query")
    assert "formatted" in response
    assert "raw" in response
    assert response["formatted"] == "Test response"
    assert response["raw"] == "Test response"
    assert "interaction_id" in response

def test_core_agent_output_formatter_none_content():
    """Test that CoreAgent handles None content with formatter"""
    mock_llm = MockLLM()
    
    def failing_tool(response: str) -> None:
        return None
    
    def mock_formatter(content: str, raw_response: str, interaction_id: str = None) -> dict:
        return {
            "formatted": content,
            "raw": raw_response,
            "interaction_id": interaction_id
        }
    
    agent = CoreAgent(
        agent_name="test_agent",
        system_instructions="Test instructions",
        tools=[failing_tool],
        output_formatter=mock_formatter,
        llm=mock_llm
    )
    
    response = agent.run("Test query")
    assert "error" in response
    assert response["error"] == "No tool output available"
