"""Data access layer for persisting domain objects."""

from datetime import datetime
from typing import Generic, TypeVar

from sqlalchemy import select

from ai_scout.storage.models import (
    Base,
    Source,
    SourceCandidate,
    Topic,
    get_engine,
    get_session,
)

ModelT = TypeVar("ModelT", bound=Base)


class BaseRepository(Generic[ModelT]):
    """Generic repository providing common CRUD operations for SQLAlchemy models.

    Subclasses must set *model_class* to the ORM model type they manage.
    Models with an ``archived_at`` column get automatic soft-delete support
    via :meth:`archive` and conditional filtering in :meth:`get_all`.
    """

    model_class: type[ModelT]

    def __init__(self, db_path: str):
        self._engine = get_engine(db_path)

    # ------------------------------------------------------------------
    # Introspection helpers
    # ------------------------------------------------------------------

    @property
    def _has_archived_at(self) -> bool:
        return hasattr(self.model_class, "archived_at")

    # ------------------------------------------------------------------
    # Generic CRUD
    # ------------------------------------------------------------------

    def add(self, **kwargs: object) -> ModelT:
        """Create and persist a new instance of *model_class*."""
        session = get_session(self._engine)
        try:
            obj = self.model_class(**kwargs)
            session.add(obj)
            session.commit()
            session.refresh(obj)
            return obj
        finally:
            session.close()

    def get_by_id(self, id: str) -> ModelT | None:
        """Fetch a single record by primary key, or *None* if not found."""
        session = get_session(self._engine)
        try:
            return session.get(self.model_class, id)
        finally:
            session.close()

    def get_all(self, include_archived: bool = False) -> list[ModelT]:
        """Return all records, optionally including soft-deleted ones.

        Models without an ``archived_at`` column always return every row.
        """
        session = get_session(self._engine)
        try:
            stmt = select(self.model_class)
            if self._has_archived_at and not include_archived:
                stmt = stmt.where(self.model_class.archived_at.is_(None))
            return list(session.execute(stmt).scalars().all())
        finally:
            session.close()

    def archive(self, id: str) -> bool:
        """Soft-delete a record by setting ``archived_at``.

        Returns *True* when the record was found and archived, *False*
        when no record matches *id*.

        Raises :class:`TypeError` when the model does not have an
        ``archived_at`` column.
        """
        if not self._has_archived_at:
            raise TypeError(
                f"{self.model_class.__name__} does not support soft-delete "
                "(no archived_at column)"
            )
        session = get_session(self._engine)
        try:
            obj = session.get(self.model_class, id)
            if obj is None:
                return False
            obj.archived_at = datetime.utcnow()
            session.commit()
            return True
        finally:
            session.close()


# ======================================================================
# Topic repository
# ======================================================================


class TopicsRepository(BaseRepository[Topic]):
    """Repository for managing Topic records."""

    model_class = Topic

    def add_topic(self, value: str, weight: float = 1.0) -> Topic:
        """Insert a single topic (delegates to the generic :meth:`add`)."""
        return self.add(value=value, weight=weight)

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

    def archive_topic(self, topic_id: str) -> bool:
        """Soft-delete a topic (delegates to the generic :meth:`archive`)."""
        return self.archive(topic_id)


# ======================================================================
# Source Candidate repository
# ======================================================================


class SourceCandidatesRepository(BaseRepository[SourceCandidate]):
    """Repository for managing source candidates awaiting validation."""

    model_class = SourceCandidate

    DUPLICATE_REASON = "duplicate"
    MANUAL_REASON = "manual"

    def add(
        self,
        name: str,
        url: str,
        source_type: str,
        discovered_by: str,
    ) -> SourceCandidate:
        """Record a newly discovered source candidate."""
        return super().add(
            name=name,
            url=url,
            source_type=source_type,
            status="pending",
            discovered_by=discovered_by,
            discovered_at=datetime.utcnow(),
        )

    def get_by_status(self, status: str) -> list[SourceCandidate]:
        """Return candidates filtered by *status* (pending | validated | rejected)."""
        session = get_session(self._engine)
        try:
            stmt = select(SourceCandidate).where(SourceCandidate.status == status)
            return list(session.execute(stmt).scalars().all())
        finally:
            session.close()

    def validate(self, id: str, reason: str | None = None) -> SourceCandidate | None:
        """Mark a candidate as validated, optionally recording a reason.

        Sets ``validated_at`` to the current timestamp. Returns the updated
        record, or *None* if no candidate matches *id*.
        """
        session = get_session(self._engine)
        try:
            obj = session.get(SourceCandidate, id)
            if obj is None:
                return None
            obj.status = "validated"
            obj.validation_reason = reason
            obj.validated_at = datetime.utcnow()
            session.commit()
            session.refresh(obj)
            return obj
        finally:
            session.close()

    def reject(self, id: str, reason: str) -> SourceCandidate | None:
        """Mark a candidate as rejected with a required reason."""
        session = get_session(self._engine)
        try:
            obj = session.get(SourceCandidate, id)
            if obj is None:
                return None
            obj.status = "rejected"
            obj.validation_reason = reason
            session.commit()
            session.refresh(obj)
            return obj
        finally:
            session.close()


# ======================================================================
# Source repository
# ======================================================================


class SourcesRepository(BaseRepository[Source]):
    """Repository for managing validated content sources."""

    model_class = Source

    def add(
        self,
        name: str,
        url: str,
        source_type: str,
        priority: float = 0.5,
        weight: float = 1.0,
    ) -> Source:
        """Register a new validated source."""
        return super().add(
            name=name,
            url=url,
            source_type=source_type,
            priority=priority,
            weight=weight,
        )