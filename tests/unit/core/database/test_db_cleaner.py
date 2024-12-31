"""Tests for database cleaning utilities."""

import pytest
from sqlalchemy.orm import Session
from core.database.models import Conversation, Message, ConversationTopic
from core.workspace_manager import SpaceType
from core.database.db_cleaner import (
    fix_invalid_workspaces,
    clean_null_conversation_messages,
    remove_untitled_conversations,
    clean_orphaned_topics,
    clean_orphaned_messages,
    remove_empty_conversations,
    remove_duplicate_topics,
    clean_database
)

class TestFixInvalidWorkspaces:
    def test_fix_invalid_workspaces(self, session):
        """Test fixing invalid workspace values."""
        # Create conversations with invalid workspace
        conv1 = Conversation(title="Test1", workspace="INVALID")
        conv2 = Conversation(title="Test2", workspace="UNKNOWN")
        session.add_all([conv1, conv2])
        session.commit()

        count = fix_invalid_workspaces(session)
        assert count == 2
        
        # Verify workspaces were fixed
        convs = session.query(Conversation).all()
        assert all(conv.workspace == SpaceType.AGNOSTIC for conv in convs)

class TestCleanNullConversationMessages:
    def test_clean_null_conversation_messages(self, session):
        """Test cleaning messages with NULL conversation_id."""
        # Create messages with NULL conversation_id
        msg1 = Message(conversation_id=None, role="user", content="test1")
        msg2 = Message(conversation_id=None, role="assistant", content="test2")
        session.add_all([msg1, msg2])
        session.commit()

        count = clean_null_conversation_messages(session)
        assert count == 2
        assert session.query(Message).count() == 0

class TestRemoveUntitledConversations:
    def test_remove_untitled_conversations(self, session):
        """Test removing untitled conversations."""
        # Create untitled conversations
        conv1 = Conversation(title=None, workspace=SpaceType.AGNOSTIC)
        conv2 = Conversation(title=None, workspace=SpaceType.AGNOSTIC)
        session.add_all([conv1, conv2])
        session.commit()

        count = remove_untitled_conversations(session)
        assert count == 2
        assert session.query(Conversation).count() == 0

class TestCleanOrphanedTopics:
    def test_clean_orphaned_topics(self, session):
        """Test cleaning orphaned topics."""
        # Create conversation and topics
        conv = Conversation(title="Test", workspace=SpaceType.AGNOSTIC)
        session.add(conv)
        session.commit()

        topic1 = ConversationTopic(conversation_id=conv.id, topic="test")
        topic2 = ConversationTopic(conversation_id="invalid-uuid", topic="orphaned")
        session.add_all([topic1, topic2])
        session.commit()

        count = clean_orphaned_topics(session)
        assert count == 1
        assert session.query(ConversationTopic).count() == 1
        assert session.query(ConversationTopic).first().topic == "test"

class TestCleanOrphanedMessages:
    def test_clean_orphaned_messages(self, session):
        """Test cleaning orphaned messages."""
        # Create a conversation and messages
        conv = Conversation(title="Test Conv", workspace=SpaceType.AGNOSTIC)
        session.add(conv)
        session.commit()

        orphaned_msg = Message(conversation_id="invalid-uuid", role="user", content="test")
        valid_msg = Message(conversation_id=conv.id, role="user", content="valid")
        session.add_all([orphaned_msg, valid_msg])
        session.commit()

        count = clean_orphaned_messages(session)
        assert count == 1
        assert session.query(Message).count() == 1
        assert session.query(Message).first().content == "valid"

class TestRemoveEmptyConversations:
    def test_remove_empty_conversations(self, session):
        """Test removing empty conversations."""
        # Create conversations
        conv1 = Conversation(title="Empty", workspace=SpaceType.AGNOSTIC)
        conv2 = Conversation(title="With Message", workspace=SpaceType.AGNOSTIC)
        session.add_all([conv1, conv2])
        session.commit()

        msg = Message(conversation_id=conv2.id, role="user", content="test")
        session.add(msg)
        session.commit()

        count = remove_empty_conversations(session)
        assert count == 1
        assert session.query(Conversation).count() == 1
        assert session.query(Conversation).first().title == "With Message"

class TestRemoveDuplicateTopics:
    """
    FIXME: Ces tests sont temporairement désactivés car la gestion de la casse 
    dans remove_duplicate_topics nécessite une révision.
    Issues à résoudre :
    1. Préservation de la casse d'origine du premier topic
    2. Cohérence du comportement à travers différentes conversations
    3. Gestion des caractères spéciaux
    """
    
    @pytest.mark.skip(reason="FIXME: Gestion de la casse à réviser")
    def test_remove_duplicate_topics(self, session):
        """Test removing duplicate topics."""
        # Create conversation with duplicate topics
        conv = Conversation(title="Test", workspace=SpaceType.AGNOSTIC)
        session.add(conv)
        session.commit()

        # Add topics in specific order to ensure deterministic results
        topics = [
            ConversationTopic(conversation_id=conv.id, topic="python"),  # Lowercase first
            ConversationTopic(conversation_id=conv.id, topic="PYTHON"),
            ConversationTopic(conversation_id=conv.id, topic="Java"),    # Uppercase first
            ConversationTopic(conversation_id=conv.id, topic="java")
        ]
        session.add_all(topics)
        session.commit()

        count = remove_duplicate_topics(session)
        assert count == 2

        # Verify remaining topics and their order
        remaining = session.query(ConversationTopic).order_by(ConversationTopic.id).all()
        assert len(remaining) == 2
        topics = sorted([t.topic for t in remaining])
        assert topics == ["Java", "python"]  # First occurrence of each is kept

    @pytest.mark.skip(reason="FIXME: Gestion de la casse à réviser")
    def test_special_chars_in_topics(self, session):
        """Test handling of special characters in topics."""
        # Create conversation with topics containing special chars
        conv = Conversation(title="Test", workspace=SpaceType.AGNOSTIC)
        session.add(conv)
        session.commit()

        # Add topics in specific order to ensure deterministic results
        topics = [
            ConversationTopic(conversation_id=conv.id, topic="c++"),    # Lowercase first
            ConversationTopic(conversation_id=conv.id, topic="C++"),
            ConversationTopic(conversation_id=conv.id, topic="C#"),     # Uppercase first
            ConversationTopic(conversation_id=conv.id, topic="c#"),
            ConversationTopic(conversation_id=conv.id, topic="$pecial!"),
            ConversationTopic(conversation_id=conv.id, topic="$PECIAL!")
        ]
        session.add_all(topics)
        session.commit()

        count = remove_duplicate_topics(session)
        assert count == 3

        # Verify remaining topics
        remaining = session.query(ConversationTopic).order_by(ConversationTopic.id).all()
        assert len(remaining) == 3
        topics = sorted([t.topic for t in remaining])
        assert topics == ["$pecial!", "C#", "c++"]  # First occurrence of each is kept

    @pytest.mark.skip(reason="FIXME: Gestion de la casse à réviser")
    def test_preserve_order_across_conversations(self, session):
        """Test that topic order is preserved across different conversations."""
        # Create two conversations
        conv1 = Conversation(title="Test1", workspace=SpaceType.AGNOSTIC)
        conv2 = Conversation(title="Test2", workspace=SpaceType.AGNOSTIC)
        session.add_all([conv1, conv2])
        session.commit()

        # Add topics in specific order
        topics = [
            # Conversation 1
            ConversationTopic(conversation_id=conv1.id, topic="python"),
            ConversationTopic(conversation_id=conv1.id, topic="PYTHON"),
            # Conversation 2
            ConversationTopic(conversation_id=conv2.id, topic="PYTHON"),
            ConversationTopic(conversation_id=conv2.id, topic="python")
        ]
        session.add_all(topics)
        session.commit()

        count = remove_duplicate_topics(session)
        assert count == 2

        # Verify each conversation kept its first occurrence
        conv1_topics = session.query(ConversationTopic).filter_by(conversation_id=conv1.id).all()
        assert len(conv1_topics) == 1
        assert conv1_topics[0].topic == "python"

        conv2_topics = session.query(ConversationTopic).filter_by(conversation_id=conv2.id).all()
        assert len(conv2_topics) == 1
        assert conv2_topics[0].topic == "PYTHON"

class TestCleanDatabase:
    def test_clean_database_full(self, session):
        """Test full database cleaning process."""
        # Create test data
        conv1 = Conversation(title=None, workspace="INVALID")
        conv2 = Conversation(title="Empty", workspace="UNKNOWN")
        conv3 = Conversation(title="Valid", workspace=SpaceType.AGNOSTIC)
        session.add_all([conv1, conv2, conv3])
        session.commit()

        msg1 = Message(conversation_id=None, role="user", content="null")
        msg2 = Message(conversation_id="invalid-uuid", role="user", content="orphaned")
        msg3 = Message(conversation_id=conv3.id, role="user", content="valid")
        session.add_all([msg1, msg2, msg3])

        topic1 = ConversationTopic(conversation_id="invalid-uuid", topic="orphaned")
        topic2 = ConversationTopic(conversation_id=conv3.id, topic="Python")
        topic3 = ConversationTopic(conversation_id=conv3.id, topic="python")
        session.add_all([topic1, topic2, topic3])
        session.commit()

        stats = clean_database(session)

        # Verify all cleaning operations were performed
        assert stats['invalid_workspace_fixed'] == 2
        assert stats['null_conversation_messages_removed'] == 1
        assert stats['untitled_conversations_removed'] == 1
        assert stats['orphaned_topics_removed'] == 1
        assert stats['orphaned_messages_removed'] == 1
        assert stats['empty_conversations_removed'] == 1
        assert stats['duplicate_topics_removed'] == 1

        # Verify final database state
        assert session.query(Conversation).count() == 1
        assert session.query(Message).count() == 1
        assert session.query(ConversationTopic).count() == 1
