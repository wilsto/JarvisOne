"""Reset vector and SQLite databases."""

import os
import shutil
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

def reset_vector_db(vector_db_path: Path) -> None:
    """Reset ChromaDB vector database.
    
    Args:
        vector_db_path: Path to the ChromaDB directory
    """
    try:
        if vector_db_path.exists():
            logger.info(f"Removing vector database at {vector_db_path}")
            shutil.rmtree(vector_db_path)
            vector_db_path.mkdir(parents=True, exist_ok=True)
            logger.info("Vector database reset complete")
        else:
            logger.info(f"Vector database directory {vector_db_path} does not exist")
            vector_db_path.mkdir(parents=True, exist_ok=True)
            
    except Exception as e:
        logger.error(f"Error resetting vector database: {e}")
        raise

def reset_document_tracking(db_path: Path) -> None:
    """Reset document tracking SQLite database.
    
    Args:
        db_path: Path to the SQLite database file
    """
    try:
        if db_path.exists():
            logger.info(f"Removing document tracking database at {db_path}")
            os.remove(db_path)
            logger.info("Document tracking database reset complete")
        else:
            logger.info(f"Document tracking database {db_path} does not exist")
            
    except Exception as e:
        logger.error(f"Error resetting document tracking database: {e}")
        raise

def reset_all_databases(data_dir: Path = None) -> None:
    """Reset all databases (vector and SQLite).
    
    Args:
        data_dir: Optional path to data directory. If not provided, uses default.
    """
    if data_dir is None:
        data_dir = Path("data")
        
    try:
        # Reset vector database
        vector_db_path = data_dir / "vector_db"
        reset_vector_db(vector_db_path)
        
        # Reset document tracking database
        doc_tracking_db = data_dir / "documents.db"
        reset_document_tracking(doc_tracking_db)
        
        logger.info("All databases reset successfully")
        
    except Exception as e:
        logger.error(f"Error during database reset: {e}")
        raise

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    reset_all_databases()
