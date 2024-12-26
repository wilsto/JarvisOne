"""Tests for the LLM base class."""

import pytest
from src.core.llm_base import LLM

def test_cannot_instantiate_abstract():
    """Test that LLM cannot be instantiated directly."""
    with pytest.raises(TypeError, match=r"Can't instantiate abstract class LLM"):
        LLM()

def test_must_implement_generate_response():
    """Test that subclasses must implement generate_response."""
    class InvalidLLM(LLM):
        pass
    
    with pytest.raises(TypeError, match=r"Can't instantiate abstract class InvalidLLM"):
        InvalidLLM()

def test_generate_response_signature():
    """Test that generate_response has correct signature."""
    class ValidLLM(LLM):
        def generate_response(self, prompt: str) -> str:
            return f"Response to: {prompt}"
    
    llm = ValidLLM()
    response = llm.generate_response("Test prompt")
    assert response == "Response to: Test prompt"

