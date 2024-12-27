"""Repository for database operations."""

import logging
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Dict

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import SQLAlchemyError

from .models import Base, Conversation, Message, ConversationTopic
from core.knowledge_space import SpaceType

logger = logging.getLogger(__name__)

class ConversationRepository:
    """Handles all database operations for conversations."""

    def __init__(self, db_path: str):
        """Initialize the repository with database connection.
        
        Args:
            db_path: Path to SQLite database file
        """
        self.engine = create_engine(f'sqlite:///{db_path}')
        Base.metadata.create_all(self.engine)
        self.SessionLocal = sessionmaker(bind=self.engine)

    def _get_db(self) -> Session:
        """Create a new database session."""
        return self.SessionLocal()

    def create_conversation(self, title: Optional[str] = None, workspace: SpaceType = SpaceType.AGNOSTIC) -> Conversation:
        """Create a new conversation.
        
        Args:
            title: Optional title for the conversation
            workspace: Workspace type for the conversation (default: AGNOSTIC)
            
        Returns:
            Created conversation instance
        """
        db = self._get_db()
        try:
            conversation = Conversation(title=title, workspace=workspace)
            db.add(conversation)
            db.commit()
            db.refresh(conversation)
            return conversation
        except SQLAlchemyError as e:
            logger.error(f"Error creating conversation: {e}")
            db.rollback()
            raise
        finally:
            db.close()

    def add_message(self, conversation_id: str, role: str, content: str) -> Message:
        """Add a message to a conversation.
        
        Args:
            conversation_id: ID of the conversation
            role: Role of the message sender ('user' or 'assistant')
            content: Content of the message
            
        Returns:
            Created message instance
        """
        db = self._get_db()
        try:
            message = Message(
                conversation_id=conversation_id,
                role=role,
                content=content
            )
            db.add(message)
            
            # Update conversation last_timestamp
            conversation = db.query(Conversation).filter_by(id=conversation_id).first()
            if conversation:
                conversation.last_timestamp = datetime.utcnow()
            
            db.commit()
            db.refresh(message)
            return message
        except SQLAlchemyError as e:
            logger.error(f"Error adding message: {e}")
            db.rollback()
            raise
        finally:
            db.close()

    def get_conversation(self, conversation_id: str) -> Optional[Dict]:
        """Get a conversation by ID with all its messages.
        
        Args:
            conversation_id: ID of the conversation
            
        Returns:
            Dictionary containing conversation details and messages
        """
        db = self._get_db()
        try:
            conversation = db.query(Conversation).filter_by(id=conversation_id).first()
            if not conversation:
                return None
            
            return {
                'id': conversation.id,
                'title': conversation.title,
                'start_timestamp': conversation.start_timestamp,
                'last_timestamp': conversation.last_timestamp,
                'summary': conversation.summary,
                'messages': [
                    {
                        'role': msg.role,
                        'content': msg.content,
                        'timestamp': msg.timestamp
                    }
                    for msg in conversation.messages
                ],
                'topics': [
                    {
                        'topic': topic.topic,
                        'confidence': topic.confidence
                    }
                    for topic in conversation.topics
                ]
            }
        finally:
            db.close()

    def get_recent_conversations(self, limit: int = 10, workspace: Optional[SpaceType] = None) -> List[Dict]:
        """Get recent conversations with their latest messages.
        
        Args:
            limit: Maximum number of conversations to return
            workspace: Optional workspace filter
            
        Returns:
            List of conversations with their messages
        """
        db = self._get_db()
        try:
            query = db.query(Conversation)
            
            if workspace is not None:
                query = query.filter(Conversation.workspace == workspace)
                
            conversations = (
                query.order_by(Conversation.last_timestamp.desc())
                .limit(limit)
                .all()
            )
            
            return [
                {
                    "id": conv.id,
                    "title": conv.title,
                    "last_timestamp": conv.last_timestamp,
                    "messages": [
                        {
                            "role": msg.role,
                            "content": msg.content,
                            "timestamp": msg.timestamp
                        }
                        for msg in conv.messages
                    ],
                    "workspace": conv.workspace
                }
                for conv in conversations
            ]
        except SQLAlchemyError as e:
            logger.error(f"Error getting recent conversations: {e}")
            raise
        finally:
            db.close()

    def update_conversation_metadata(
        self,
        conversation_id: str,
        title: Optional[str] = None,
        summary: Optional[str] = None,
        topics: Optional[List[Dict]] = None
    ):
        """Update conversation metadata.
        
        Args:
            conversation_id: ID of the conversation
            title: New title for the conversation
            summary: New summary for the conversation
            topics: List of topics with confidence scores
        """
        db = self._get_db()
        try:
            conversation = db.query(Conversation).filter_by(id=conversation_id).first()
            if not conversation:
                return
            
            if title is not None:
                conversation.title = title
            if summary is not None:
                conversation.summary = summary
            
            if topics is not None:
                # Remove existing topics
                db.query(ConversationTopic).filter_by(conversation_id=conversation_id).delete()
                
                # Add new topics
                for topic_data in topics:
                    topic = ConversationTopic(
                        conversation_id=conversation_id,
                        topic=topic_data['topic'],
                        confidence=topic_data.get('confidence', 1.0)
                    )
                    db.add(topic)
            
            db.commit()
        except SQLAlchemyError as e:
            logger.error(f"Error updating conversation metadata: {e}")
            db.rollback()
            raise
        finally:
            db.close()

    def delete_conversation(self, conversation_id: str):
        """Delete a conversation and its messages from the database."""
        db = self._get_db()
        try:
            # Delete messages first due to foreign key constraint
            db.query(Message).filter_by(conversation_id=conversation_id).delete()
            # Then delete the conversation
            db.query(Conversation).filter_by(id=conversation_id).delete()
            db.commit()
        except Exception as e:
            logger.error(f"Error deleting conversation {conversation_id}: {str(e)}")
            db.rollback()
            raise
        finally:
            db.close()
