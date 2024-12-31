"""Test configuration and fixtures."""

import os
import sys
import pytest
import tempfile
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add project root and src directories to Python path
root_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
src_path = os.path.join(root_path, 'src')

sys.path.insert(0, root_path)  # For tests package
sys.path.insert(0, src_path)   # For src package

from core.database.models import Base

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
