from datetime import datetime
from enum import Enum
from uuid import uuid4

from sqlalchemy import Column, DateTime, Float, String, create_engine
from sqlalchemy.orm import DeclarativeBase, Session


class Base(DeclarativeBase):
    pass


class SourceType(str, Enum):
    ENGINEERING_BLOG = "engineering_blog"
    PROJECT_BLOG = "project_blog"
    NEWSLETTER = "newsletter"
    RSS_FEED = "rss_feed"
    RELEASE_FEED = "release_feed"
    DOCUMENTATION = "documentation"


class Topic(Base):
    __tablename__ = "topics"

    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    value = Column(String, nullable=False)
    weight = Column(Float, nullable=False, default=1.0)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    archived_at = Column(DateTime, nullable=True)


class SourceCandidate(Base):
    __tablename__ = "source_candidates"

    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    name = Column(String, nullable=False)
    url = Column(String, nullable=False)
    source_type = Column(String, nullable=False)
    status = Column(String, nullable=False, default="pending")
    validation_reason = Column(String, nullable=True)
    discovered_by = Column(String, nullable=False)
    discovered_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    validated_at = Column(DateTime, nullable=True)


class Source(Base):
    __tablename__ = "sources"

    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    name = Column(String, nullable=False)
    url = Column(String, nullable=False)
    source_type = Column(String, nullable=False)
    priority = Column(Float, nullable=False, default=0.5)
    weight = Column(Float, nullable=False, default=1.0)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    archived_at = Column(DateTime, nullable=True)


def get_engine(db_path: str):
    """Create a SQLAlchemy engine for the given SQLite db path."""
    return create_engine(f"sqlite:///{db_path}")


def get_session(engine) -> Session:
    return Session(engine)