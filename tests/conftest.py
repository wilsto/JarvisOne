"""Test configuration and fixtures."""

import os
import sys
import pytest
import logging
import tempfile
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from pathlib import Path
import streamlit as st

# Add project root and src directories to Python path
root_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
src_path = os.path.join(root_path, 'src')

sys.path.insert(0, root_path)  # For tests package
sys.path.insert(0, src_path)   # For src package

from core.database.models import Base
from .mocks.database import DatabaseMock
from .mocks.session_state import SessionStateMock

# Configure logging for all tests
@pytest.fixture(autouse=True)
def configure_logging():
    """Configure logging for all tests."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        stream=sys.stdout
    )

@pytest.fixture(scope="function")
def engine():
    """Create a test database engine."""
    # Use a temporary file for SQLite
    db_fd, db_path = tempfile.mkstemp(suffix='.db')
    os.close(db_fd)  # Close the file descriptor immediately
    
    # Create engine with foreign key support
    engine = create_engine(f'sqlite:///{db_path}?foreign_keys=1')
    Base.metadata.create_all(engine)
    
    yield engine
    
    engine.dispose()  # Ensure all connections are closed
    try:
        os.unlink(db_path)  # Clean up after test
    except PermissionError:
        pass  # Ignore if file is still locked

@pytest.fixture(scope="function")
def session(engine):
    """Create a new database session for testing."""
    Session = sessionmaker(bind=engine)
    session = Session()
    
    yield session
    
    session.close()  # Ensure session is closed

@pytest.fixture(scope="function")
def temp_db_path():
    """Create a temporary database path for testing.
    
    This fixture creates a temporary SQLite database file and ensures proper cleanup.
    Used by document tracking and other database-dependent tests.
    """
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
        db_path = f.name
    yield db_path
    # Clean up
    try:
        Path(db_path).unlink(missing_ok=True)
    except PermissionError:
        # Ensure all connections are closed
        import gc
        gc.collect()  # Force garbage collection
        import time
        time.sleep(0.1)  # Wait a bit
        try:
            Path(db_path).unlink(missing_ok=True)
        except PermissionError:
            pass  # Let the OS clean it up later

@pytest.fixture(scope="function")
def mock_database():
    """Fixture to provide a mock database.
    
    This fixture:
    1. Creates a new DatabaseMock instance
    2. Yields it for the test
    3. Clears all data after the test
    """
    db = DatabaseMock()
    yield db
    db.clear()

@pytest.fixture(scope="function")
def mock_session_state():
    """Fixture to provide a mock Streamlit session state.
    
    This fixture:
    1. Removes any existing session_state
    2. Creates a new SessionStateMock instance
    3. Restores the original session_state after the test
    """
    # Store original session state
    original_session_state = st._get_session()
    
    # Create mock session state
    mock_state = SessionStateMock()
    st._set_session(mock_state)
    
    yield mock_state
    
    # Restore original session state
    st._set_session(original_session_state)
