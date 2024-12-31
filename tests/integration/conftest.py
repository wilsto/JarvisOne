"""Configuration for integration tests."""

import pytest
import logging
import sys
from pathlib import Path

# Configure logging for tests
@pytest.fixture(autouse=True)
def configure_logging():
    """Configure logging for all tests."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        stream=sys.stdout
    )

# Add project root to Python path
@pytest.fixture(autouse=True)
def add_project_root_to_path():
    """Add project root to Python path."""
    project_root = Path(__file__).parent.parent.parent
    sys.path.insert(0, str(project_root))
