"""Base class for interaction displays."""
from abc import ABC, abstractmethod
from typing import Dict, Any

class BaseInteractionDisplay(ABC):
    """Base class for interaction displays."""
    
    @abstractmethod
    def display(self, interaction: Dict[str, Any]) -> None:
        """Display the interaction in the UI."""
        pass

    def get_expander_title(self, interaction: Dict[str, Any]) -> str:
        """Get the title for the interaction expander."""
        return f"💬 {interaction['timestamp']}"
