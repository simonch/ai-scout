from datetime import datetime
from uuid import uuid4

from sqlalchemy import Column, DateTime, Float, String, create_engine
from sqlalchemy.orm import DeclarativeBase, Session


class Base(DeclarativeBase):
    pass


class Topic(Base):
    __tablename__ = "topics"

    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    value = Column(String, nullable=False)
    weight = Column(Float, nullable=False, default=1.0)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    archived_at = Column(DateTime, nullable=True)


def get_engine(db_path: str):
    """Create a SQLAlchemy engine for the given SQLite db path."""
    return create_engine(f"sqlite:///{db_path}")


def get_session(engine) -> Session:
    return Session(engine)