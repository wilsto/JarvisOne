"""Workspace type definitions for testing."""

from enum import Enum, auto

class SpaceType(Enum):
    """Enum for workspace types."""
    AGNOSTIC = auto()
    COACHING = auto()
    DEV = auto()
    PERSONAL = auto()
    WORK = auto()
