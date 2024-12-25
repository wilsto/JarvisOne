"""Base class for LLM implementations."""

from abc import ABC, abstractmethod

class LLM(ABC):
    @abstractmethod
    def generate_response(self, prompt: str) -> str:
        """Generate a response from the LLM given a prompt."""
        pass
