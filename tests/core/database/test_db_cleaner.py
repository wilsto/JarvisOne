"""Tests for database cleaning utilities."""

import pytest
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.core.database.models import Base, Conversation, Message, ConversationTopic
from src.core.database.db_cleaner import clean_database
from src.core.workspace_manager import SpaceType

@pytest.fixture
def engine():
    """Create a test database engine."""
    engine = create_engine('sqlite:///:memory:')
    Base.metadata.create_all(engine)
    return engine

@pytest.fixture
def session(engine):
    """Create a new database session for testing."""
    Session = sessionmaker(bind=engine)
    return Session()

def test_clean_orphaned_messages(session):
    # Create a conversation and an orphaned message
    conv = Conversation(title="Test Conv", workspace=SpaceType.AGNOSTIC)
    session.add(conv)
    
    orphaned_msg = Message(conversation_id="non-existent", role="user", content="test")
    valid_msg = Message(conversation_id=conv.id, role="user", content="valid")
    session.add_all([orphaned_msg, valid_msg])
    session.commit()

    stats = clean_database(session)
    assert stats['orphaned_messages_removed'] == 1
    assert session.query(Message).count() == 1

def test_fix_untitled_conversations(session):
    # Create untitled conversations
    conv1 = Conversation(workspace=SpaceType.AGNOSTIC)
    conv2 = Conversation(workspace=SpaceType.AGNOSTIC)
    session.add_all([conv1, conv2])
    
    msg = Message(conversation_id=conv1.id, role="user", content="Hello world")
    session.add(msg)
    session.commit()

    stats = clean_database(session)
    assert stats['untitled_conversations_fixed'] == 2
    assert conv1.title == "Hello world"
    assert "Conversation" in conv2.title

def test_clean_empty_conversations(session):
    # Create empty and non-empty conversations
    empty_conv = Conversation(title="Empty", workspace=SpaceType.AGNOSTIC)
    valid_conv = Conversation(title="Valid", workspace=SpaceType.AGNOSTIC)
    session.add_all([empty_conv, valid_conv])
    
    msg = Message(conversation_id=valid_conv.id, role="user", content="test")
    session.add(msg)
    session.commit()

    stats = clean_database(session)
    assert stats['empty_conversations_removed'] == 1
    assert session.query(Conversation).count() == 1

def test_clean_orphaned_topics(session):
    # Create a conversation and orphaned topics
    conv = Conversation(title="Test", workspace=SpaceType.AGNOSTIC)
    session.add(conv)
    
    valid_topic = ConversationTopic(conversation_id=conv.id, topic="valid")
    orphaned_topic = ConversationTopic(conversation_id="non-existent", topic="orphaned")
    session.add_all([valid_topic, orphaned_topic])
    session.commit()

    stats = clean_database(session)
    assert stats['orphaned_topics_removed'] == 1
    assert session.query(ConversationTopic).count() == 1

def test_remove_duplicate_topics(session):
    # Create a conversation with duplicate topics
    conv = Conversation(title="Test", workspace=SpaceType.AGNOSTIC)
    session.add(conv)
    
    topic1 = ConversationTopic(conversation_id=conv.id, topic="Python")
    topic2 = ConversationTopic(conversation_id=conv.id, topic="python")  # Duplicate
    topic3 = ConversationTopic(conversation_id=conv.id, topic="Java")
    session.add_all([topic1, topic2, topic3])
    session.commit()

    stats = clean_database(session)
    assert stats['duplicate_topics_removed'] == 1
    assert session.query(ConversationTopic).count() == 2
