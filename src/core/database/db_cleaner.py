"""Database cleaning utilities."""

from datetime import datetime
from typing import List, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import select, func, or_, text
from .models import Conversation, Message, ConversationTopic
from pathlib import Path
import json

def log_cleaning_stats(stats: dict, base_dir: Path = None) -> Path:
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

def clean_database(session: Session) -> dict:
    """
    Clean the database by removing orphaned records and fixing inconsistencies.
    
    Returns:
        dict: Statistics about the cleaning operations performed
    """
    stats = {
        'orphaned_messages_removed': 0,
        'null_conversation_messages_removed': 0,
        'untitled_conversations_removed': 0,
        'empty_conversations_removed': 0,
        'orphaned_topics_removed': 0,
        'duplicate_topics_removed': 0,
        'invalid_workspace_fixed': 0
    }
    
    # 0. Fix invalid workspace values
    result = session.execute(text("""
        UPDATE conversations 
        SET workspace = 'AGNOSTIC' 
        WHERE workspace NOT IN ('PERSONAL', 'COACHING', 'DEV', 'WORK', 'AGNOSTIC')
    """))
    stats['invalid_workspace_fixed'] = result.rowcount
    session.commit()

    # 1. Clean messages with NULL conversation_id
    result = session.execute(text("DELETE FROM messages WHERE conversation_id IS NULL"))
    stats['null_conversation_messages_removed'] = result.rowcount
    session.commit()

    # 2. Clean messages with invalid conversation_id
    result = session.execute(text("""
        DELETE FROM messages 
        WHERE conversation_id NOT IN (SELECT id FROM conversations)
        AND conversation_id IS NOT NULL
    """))
    stats['orphaned_messages_removed'] = result.rowcount
    session.commit()

    # 3. Remove conversations without title
    result = session.execute(text("DELETE FROM conversations WHERE title IS NULL"))
    stats['untitled_conversations_removed'] = result.rowcount
    session.commit()

    # 4. Remove empty conversations
    result = session.execute(text("""
        DELETE FROM conversations 
        WHERE id NOT IN (SELECT DISTINCT conversation_id FROM messages)
    """))
    stats['empty_conversations_removed'] = result.rowcount
    session.commit()

    # 5. Clean orphaned topics
    result = session.execute(text("""
        DELETE FROM conversation_topics 
        WHERE conversation_id IS NULL 
        OR conversation_id NOT IN (SELECT id FROM conversations)
    """))
    stats['orphaned_topics_removed'] = result.rowcount
    session.commit()

    # 6. Remove duplicate topics (plus complexe, gardons l'approche ORM pour celle-ci)
    all_convs = session.query(Conversation).all()
    duplicate_topics_removed = 0
    
    for conv in all_convs:
        seen_topics = set()
        for topic in conv.topics:
            if topic.topic.lower() in seen_topics:
                session.delete(topic)
                duplicate_topics_removed += 1
            else:
                seen_topics.add(topic.topic.lower())
    stats['duplicate_topics_removed'] = duplicate_topics_removed
    session.commit()
    
    # Log cleaning stats to external file
    log_file = log_cleaning_stats(stats)
    print(f"Cleaning log written to: {log_file}")
    
    return stats

def reset_database(session: Session) -> dict:
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
