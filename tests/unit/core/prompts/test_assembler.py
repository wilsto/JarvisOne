"""Tests for the prompt assembler."""

import pytest
from core.prompts.assembler import PromptAssembler, PromptAssemblerConfig
from core.prompts.components import (
    SystemPromptConfig,
    WorkspaceContextConfig,
    RAGContextConfig,
    PreferencesConfig,
    RoleContextConfig,
    RAGDocument
)

def test_assembler_basic():
    """Test basic prompt assembly."""
    config = PromptAssemblerConfig(
        system_config=SystemPromptConfig(
            context_prompt="Test system prompt",
            workspace_scope="test_workspace",
            debug=False
        ),
        debug=False
    )
    
    result = PromptAssembler.assemble(config)
    
    assert "Test system prompt" in result
    assert "test_workspace" in result

def test_assembler_all_components():
    """Test prompt assembly with all components."""
    config = PromptAssemblerConfig(
        system_config=SystemPromptConfig(
            context_prompt="Test system prompt",
            workspace_scope="test_workspace",
            debug=False
        ),
        workspace_config=WorkspaceContextConfig(
            workspace_id="test_workspace",
            metadata={"key": "value"},
            debug=False
        ),
        rag_config=RAGContextConfig(
            query="test query",
            documents=[
                RAGDocument(
                    content="Test content",
                    metadata={"file_path": "test.txt"}
                )
            ],
            debug=False
        ),
        preferences_config=PreferencesConfig(
            creativity_level=1,
            style_level=1,
            length_level=1,
            debug=False
        ),
        debug=False
    )
    
    result = PromptAssembler.assemble(config)
    
    assert "Test system prompt" in result
    assert "test_workspace" in result
    assert "key: value" in result
    assert "Test content" in result
    assert "Core characteristics:" in result

def test_assembler_debug_mode():
    """Test prompt assembly in debug mode."""
    config = PromptAssemblerConfig(
        system_config=SystemPromptConfig(
            context_prompt="Test system prompt",
            workspace_scope="test_workspace",
            debug=True
        ),
        debug=True
    )
    
    result = PromptAssembler.assemble(config)
    
    assert "=== System Instructions ===" in result
    assert "Test system prompt" in result
    assert "test_workspace" in result

def test_assembler_error_handling(caplog):
    """Test error handling in prompt assembly."""
    config = None
    
    # Test return value
    result = PromptAssembler.assemble(config)
    assert result == ""
    
    # Test error logging
    assert "Error assembling prompt: 'NoneType' object has no attribute 'debug'" in caplog.text
    assert "ERROR" in caplog.text

def test_assembler_empty_components():
    """Test prompt assembly with empty optional components."""
    config = PromptAssemblerConfig(
        system_config=SystemPromptConfig(
            context_prompt="Test system prompt",
            workspace_scope="test_workspace",
            debug=False
        ),
        workspace_config=None,
        rag_config=None,
        preferences_config=None,
        debug=False
    )
    
    result = PromptAssembler.assemble(config)
    
    assert "Test system prompt" in result
    assert "test_workspace" in result

def test_assembler_with_role():
    """Test assembling prompt with role context."""
    config = PromptAssemblerConfig(
        system_config=SystemPromptConfig(
            context_prompt="System instructions",
            workspace_scope="test",
            debug=False
        ),
        role_config=RoleContextConfig(
            role_id="coach",
            role_name="Coach",
            role_description="Professional Coach",
            prompt_context="Coaching instructions",
            debug=False
        ),
        debug=False
    )
    
    result = PromptAssembler.assemble(config)
    assert "System instructions" in result
    assert "Active Role: Coach" in result
    assert "Coaching instructions" in result

def test_assembler_with_all_components():
    """Test assembling prompt with all components including role."""
    config = PromptAssemblerConfig(
        system_config=SystemPromptConfig(
            context_prompt="System instructions",
            workspace_scope="test",
            debug=False
        ),
        workspace_config=WorkspaceContextConfig(
            workspace_id="test",
            metadata={"key": "value"},
            debug=False
        ),
        role_config=RoleContextConfig(
            role_id="coach",
            role_name="Coach",
            role_description="Professional Coach",
            prompt_context="Coaching instructions",
            debug=False
        ),
        rag_config=RAGContextConfig(
            query="test query",
            documents=[RAGDocument("test content", {"source": "test"})],
            debug=False
        ),
        preferences_config=PreferencesConfig(
            creativity_level=1,
            style_level=1,
            length_level=1,
            debug=False
        ),
        debug=False
    )
    
    result = PromptAssembler.assemble(config)
    assert "System instructions" in result
    assert "Active Role: Coach" in result
    assert "Coaching instructions" in result
    assert "test content" in result
    assert "key: value" in result
