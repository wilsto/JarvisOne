"""SQLAlchemy models for conversation persistence."""

from datetime import datetime, UTC
import uuid
from sqlalchemy import Column, String, DateTime, Float, ForeignKey, create_engine, Enum, TypeDecorator
from sqlalchemy.orm import relationship, declarative_base
from core.workspace_manager import SpaceType

# Use the new declarative_base from sqlalchemy.orm
Base = declarative_base()

class ISODateTime(TypeDecorator):
    """Platform-independent ISO8601 DateTime type."""
    impl = String
    cache_ok = True

    def process_bind_param(self, value, dialect):
        """Convert DateTime to ISO8601 string."""
        if value is None:
            return None
        if isinstance(value, str):
            return value
        return value.isoformat()

    def process_result_value(self, value, dialect):
        """Convert ISO8601 string to DateTime."""
        if value is None:
            return None
        if isinstance(value, datetime):
            return value
        return datetime.fromisoformat(value)

class Conversation(Base):
    """Represents a chat conversation."""
    __tablename__ = 'conversations'

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String, nullable=True)
    start_timestamp = Column(ISODateTime, default=lambda: datetime.now(UTC))
    last_timestamp = Column(ISODateTime, default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC))
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
    timestamp = Column(ISODateTime, default=lambda: datetime.now(UTC))
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
