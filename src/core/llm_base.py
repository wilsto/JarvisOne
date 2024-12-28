"""Base class for LLM implementations."""

from abc import ABC, abstractmethod
from typing import Optional

class LLM(ABC):
    def __init__(self):
        self._system_prompt: Optional[str] = None

    @property
    def system_prompt(self) -> Optional[str]:
        """Get the current system prompt."""
        return self._system_prompt

    @system_prompt.setter
    def system_prompt(self, value: Optional[str]):
        """Set the system prompt."""
        self._system_prompt = value

    @abstractmethod
    def generate_response(self, prompt: str) -> str:
        """Generate a response from the LLM given a prompt.
        
        The implementation should use self.system_prompt if available.
        """
        pass
