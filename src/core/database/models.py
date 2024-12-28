"""SQLAlchemy models for conversation persistence."""

from datetime import datetime
import uuid
from sqlalchemy import Column, String, DateTime, Float, ForeignKey, create_engine, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from core.workspace_manager import SpaceType

Base = declarative_base()

class Conversation(Base):
    """Represents a chat conversation."""
    __tablename__ = 'conversations'

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String, nullable=True)
    start_timestamp = Column(DateTime, default=datetime.utcnow)
    last_timestamp = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    summary = Column(String, nullable=True)
    workspace = Column(Enum(SpaceType), default=SpaceType.AGNOSTIC, nullable=False)

    # Relationships
    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan")
    topics = relationship("ConversationTopic", back_populates="conversation", cascade="all, delete-orphan")

class Message(Base):
    """Represents a single message in a conversation."""
    __tablename__ = 'messages'

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    conversation_id = Column(String, ForeignKey('conversations.id'))
    timestamp = Column(DateTime, default=datetime.utcnow)
    role = Column(String, nullable=False)  # 'user' or 'assistant'
    content = Column(String, nullable=False)

    # Relationship
    conversation = relationship("Conversation", back_populates="messages")

class ConversationTopic(Base):
    """Represents topics identified in a conversation."""
    __tablename__ = 'conversation_topics'

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    conversation_id = Column(String, ForeignKey('conversations.id'))
    topic = Column(String, nullable=False)
    confidence = Column(Float, default=1.0)

    # Relationship
    conversation = relationship("Conversation", back_populates="topics")

def init_database(db_path: str):
    """Initialize the database and create tables if they don't exist."""
    engine = create_engine(f'sqlite:///{db_path}')
    Base.metadata.create_all(engine)
    return engine
