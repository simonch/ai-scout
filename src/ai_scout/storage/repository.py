"""Data access layer for topic operations."""

from datetime import datetime

from sqlalchemy import select

from ai_scout.storage.models import Topic, get_engine, get_session


class TopicsRepository:
    """Repository for managing Topic records in the database."""

    def __init__(self, db_path: str):
        self._engine = get_engine(db_path)

    def add_topic(self, value: str, weight: float = 1.0) -> Topic:
        """Insert a single topic and return the ORM object."""
        session = get_session(self._engine)
        try:
            topic = Topic(value=value, weight=weight)
            session.add(topic)
            session.commit()
            session.refresh(topic)
            return topic
        finally:
            session.close()

    def add_topics(self, values: list[str], weight: float = 1.0) -> list[Topic]:
        """Insert multiple topics with the same weight."""
        session = get_session(self._engine)
        try:
            topics = [Topic(value=v, weight=weight) for v in values]
            session.add_all(topics)
            session.commit()
            for t in topics:
                session.refresh(t)
            return topics
        finally:
            session.close()

    def get_all(self, include_archived: bool = False) -> list[Topic]:
        """Return all topics, optionally including archived ones."""
        session = get_session(self._engine)
        try:
            stmt = select(Topic)
            if not include_archived:
                stmt = stmt.where(Topic.archived_at.is_(None))
            stmt = stmt.order_by(Topic.created_at.desc())
            return list(session.execute(stmt).scalars().all())
        finally:
            session.close()

    def archive_topic(self, topic_id: str) -> bool:
        """Soft-delete a topic by setting its archived_at timestamp."""
        session = get_session(self._engine)
        try:
            topic = session.get(Topic, topic_id)
            if topic is None:
                return False
            topic.archived_at = datetime.utcnow()
            session.commit()
            return True
        finally:
            session.close()