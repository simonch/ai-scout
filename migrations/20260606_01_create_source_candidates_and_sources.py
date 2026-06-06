"""
Create source_candidates and sources tables for managing content sources.
"""

from yoyo import step

__depends__ = {"20260605_01_create_topics_table"}

steps = [
    step(
        """
        CREATE TABLE source_candidates (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            url TEXT NOT NULL,
            source_type TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'pending',
            validation_reason TEXT,
            discovered_by TEXT NOT NULL,
            discovered_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            validated_at TIMESTAMP
        )
        """,
        "DROP TABLE source_candidates",
    ),
    step(
        """
        CREATE TABLE sources (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            url TEXT NOT NULL,
            source_type TEXT NOT NULL,
            priority FLOAT NOT NULL DEFAULT 0.5,
            weight FLOAT NOT NULL DEFAULT 1.0,
            created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            archived_at TIMESTAMP
        )
        """,
        "DROP TABLE sources",
    ),
]