"""Database cleaning utilities."""

from datetime import datetime
from pathlib import Path
from typing import Dict
from sqlalchemy.orm import Session
from sqlalchemy.sql import text
from .models import Conversation, Message, ConversationTopic
import json

def log_cleaning_stats(stats: Dict[str, int], base_dir: Path = None) -> Path:
    """
    Log database cleaning statistics to an external file.
    
    Args:
        stats: Dictionary containing cleaning statistics
        base_dir: Base directory for logs (default: project_root/logs/db_cleaning)
        
    Returns:
        Path: Path to the created log file
    """
    if base_dir is None:
        base_dir = Path(__file__).parent.parent.parent.parent / "logs" / "db_cleaning"
    
    # Ensure log directory exists
    base_dir.mkdir(parents=True, exist_ok=True)
    
    # Create log file with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = base_dir / f"db_cleaning_{timestamp}.json"
    
    # Add metadata to stats
    log_data = {
        "timestamp": datetime.now().isoformat(),
        "stats": stats,
        "summary": {
            "total_items_affected": sum(stats.values()),
            "operations_performed": len(stats)
        }
    }
    
    # Write to log file
    with open(log_file, 'w', encoding='utf-8') as f:
        json.dump(log_data, f, indent=2, ensure_ascii=False)
    
    return log_file

def fix_invalid_workspaces(session: Session) -> int:
    """Fix invalid workspace values to AGNOSTIC."""
    result = session.execute(text("""
        UPDATE conversations 
        SET workspace = 'AGNOSTIC' 
        WHERE workspace NOT IN ('PERSONAL', 'COACHING', 'DEV', 'WORK', 'AGNOSTIC')
    """))
    count = result.rowcount
    session.commit()
    return count

def clean_null_conversation_messages(session: Session) -> int:
    """Remove messages with NULL conversation_id."""
    result = session.execute(text("DELETE FROM messages WHERE conversation_id IS NULL"))
    count = result.rowcount
    session.commit()
    return count

def remove_untitled_conversations(session: Session) -> int:
    """Remove conversations without title."""
    result = session.execute(text("DELETE FROM conversations WHERE title IS NULL"))
    count = result.rowcount
    session.commit()
    return count

def clean_orphaned_topics(session: Session) -> int:
    """Remove topics with invalid conversation_id."""
    result = session.execute(text("""
        DELETE FROM conversation_topics 
        WHERE conversation_id IS NULL 
        OR conversation_id NOT IN (SELECT id FROM conversations)
    """))
    count = result.rowcount
    session.commit()
    return count

def clean_orphaned_messages(session: Session) -> int:
    """Remove messages with invalid conversation_id."""
    result = session.execute(text("""
        DELETE FROM messages 
        WHERE conversation_id NOT IN (SELECT id FROM conversations)
        AND conversation_id IS NOT NULL
    """))
    count = result.rowcount
    session.commit()
    return count

def remove_empty_conversations(session: Session) -> int:
    """Remove conversations without any messages."""
    result = session.execute(text("""
        DELETE FROM conversations 
        WHERE id NOT IN (SELECT DISTINCT conversation_id FROM messages)
    """))
    count = result.rowcount
    session.commit()
    return count

def remove_duplicate_topics(session: Session) -> int:
    """Remove duplicate topics (case-insensitive) while preserving original case."""
    # 1. Récupérer tous les topics groupés par conversation
    topics_by_conv = {}
    for topic in session.query(ConversationTopic).order_by(ConversationTopic.id).all():
        key = (topic.conversation_id, topic.topic.lower())
        if key not in topics_by_conv:
            topics_by_conv[key] = topic.id
    
    if not topics_by_conv:
        return 0
    
    # 2. Construire la liste des IDs à garder
    ids_list = ",".join(f"'{id}'" for id in topics_by_conv.values())
    
    # 3. Supprimer les topics qui ne sont pas les premiers de leur groupe
    result = session.execute(text(f"""
        DELETE FROM conversation_topics
        WHERE id NOT IN ({ids_list})
    """))
    
    count = result.rowcount
    session.commit()
    return count

def clean_database(session: Session) -> Dict[str, int]:
    """
    Clean the database by removing orphaned records and fixing inconsistencies.
    
    This function performs the following operations in order:
    1. Fix invalid workspace values
    2. Remove messages with NULL conversation_id
    3. Remove untitled conversations
    4. Clean orphaned topics
    5. Clean orphaned messages
    6. Remove empty conversations
    7. Remove duplicate topics
    
    Returns:
        dict: Statistics about the cleaning operations performed
    """
    stats = {
        'invalid_workspace_fixed': fix_invalid_workspaces(session),
        'null_conversation_messages_removed': clean_null_conversation_messages(session),
        'untitled_conversations_removed': remove_untitled_conversations(session),
        'orphaned_topics_removed': clean_orphaned_topics(session),
        'orphaned_messages_removed': clean_orphaned_messages(session),
        'empty_conversations_removed': remove_empty_conversations(session),
        'duplicate_topics_removed': remove_duplicate_topics(session)
    }
    
    # Log cleaning stats to external file
    log_file = log_cleaning_stats(stats)
    print(f"Cleaning log written to: {log_file}")
    
    return stats

def reset_database(session: Session) -> Dict[str, int]:
    """
    Reset the database by removing all conversations and messages.
    This is a dangerous operation that cannot be undone.
    
    Returns:
        dict: Statistics about the reset operation
    """
    stats = {
        'conversations_removed': 0,
        'messages_removed': 0,
        'topics_removed': 0
    }
    
    # Delete all topics first (due to foreign key constraints)
    result = session.execute(text("DELETE FROM conversation_topics"))
    stats['topics_removed'] = result.rowcount
    session.commit()
    
    # Delete all messages
    result = session.execute(text("DELETE FROM messages"))
    stats['messages_removed'] = result.rowcount
    session.commit()
    
    # Delete all conversations
    result = session.execute(text("DELETE FROM conversations"))
    stats['conversations_removed'] = result.rowcount
    session.commit()
    
    # Log reset stats to external file
    log_file = log_cleaning_stats(stats)
    print(f"Reset log written to: {log_file}")
    
    return stats
