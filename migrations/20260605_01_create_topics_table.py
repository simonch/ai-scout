"""
Create the topics table for storing user interest topics.
"""

from yoyo import step

__depends__ = {}

steps = [
    step(
        """
        CREATE TABLE topics (
            id TEXT PRIMARY KEY,
            value TEXT NOT NULL,
            weight FLOAT NOT NULL DEFAULT 1.0,
            created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            archived_at TIMESTAMP
        )
        """,
        "DROP TABLE topics",
    )
]