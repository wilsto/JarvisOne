"""Migration script to add workspace field to conversations table."""

import logging
import sys
from pathlib import Path

# Add project root to Python path
project_root = str(Path(__file__).parent.parent.parent.parent.parent)
if project_root not in sys.path:
    sys.path.append(project_root)

from sqlalchemy import create_engine, text
from src.core.workspace_manager import SpaceType

logger = logging.getLogger(__name__)

def migrate_workspace_field(db_path: str):
    """Add workspace field to conversations table and set default value.
    
    Args:
        db_path: Path to SQLite database file
    """
    engine = create_engine(f'sqlite:///{db_path}')
    
    try:
        with engine.connect() as conn:
            conn.execute(text("BEGIN TRANSACTION"))
            try:
                # Check if column exists
                result = conn.execute(text(
                    "SELECT COUNT(*) FROM pragma_table_info('conversations') WHERE name='workspace'"
                )).scalar()
                
                if result == 0:
                    logger.info("Adding workspace column to conversations table")
                    
                    # Create temporary table with new schema
                    conn.execute(text("""
                        CREATE TABLE conversations_new (
                            id VARCHAR PRIMARY KEY,
                            title VARCHAR,
                            start_timestamp DATETIME,
                            last_timestamp DATETIME,
                            summary VARCHAR,
                            workspace VARCHAR NOT NULL DEFAULT 'AGNOSTIC'
                        )
                    """))
                    
                    # Copy data from old table to new table
                    conn.execute(text("""
                        INSERT INTO conversations_new 
                        SELECT id, title, start_timestamp, last_timestamp, summary, 'AGNOSTIC' as workspace
                        FROM conversations
                    """))
                    
                    # Create temporary messages table
                    conn.execute(text("""
                        CREATE TABLE messages_new (
                            id VARCHAR PRIMARY KEY,
                            conversation_id VARCHAR,
                            timestamp DATETIME,
                            role VARCHAR NOT NULL,
                            content VARCHAR NOT NULL,
                            FOREIGN KEY(conversation_id) REFERENCES conversations(id)
                        )
                    """))
                    
                    # Copy messages
                    conn.execute(text("""
                        INSERT INTO messages_new
                        SELECT * FROM messages
                    """))
                    
                    # Create temporary topics table
                    conn.execute(text("""
                        CREATE TABLE conversation_topics_new (
                            id VARCHAR PRIMARY KEY,
                            conversation_id VARCHAR,
                            topic VARCHAR NOT NULL,
                            confidence FLOAT DEFAULT 1.0,
                            FOREIGN KEY(conversation_id) REFERENCES conversations(id)
                        )
                    """))
                    
                    # Copy topics
                    conn.execute(text("""
                        INSERT INTO conversation_topics_new
                        SELECT * FROM conversation_topics
                    """))
                    
                    # Drop old tables
                    conn.execute(text("DROP TABLE conversation_topics"))
                    conn.execute(text("DROP TABLE messages"))
                    conn.execute(text("DROP TABLE conversations"))
                    
                    # Rename new tables
                    conn.execute(text("ALTER TABLE conversations_new RENAME TO conversations"))
                    conn.execute(text("ALTER TABLE messages_new RENAME TO messages"))
                    conn.execute(text("ALTER TABLE conversation_topics_new RENAME TO conversation_topics"))
                    
                    logger.info("Successfully added workspace column and preserved relationships")
                else:
                    logger.info("Workspace column already exists")
                
                conn.execute(text("COMMIT"))
            except Exception as e:
                conn.execute(text("ROLLBACK"))
                raise e
                
    except Exception as e:
        logger.error(f"Error during migration: {e}")
        raise

if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(level=logging.INFO)
    
    # Get database path
    db_path = Path(__file__).parent.parent.parent.parent.parent / "data" / "conversations.db"
    
    if db_path.exists():
        migrate_workspace_field(str(db_path))
        logger.info("Migration completed successfully")
    else:
        logger.warning(f"Database file not found at {db_path}")
