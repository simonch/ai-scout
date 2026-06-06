from pathlib import Path

from yoyo import get_backend, read_migrations

_MIGRATIONS_DIR = Path(__file__).resolve().parent.parent.parent.parent / "migrations"


def apply_migrations(db_path: str) -> None:
    """Apply any pending yoyo migrations against the SQLite database.

    Args:
        db_path: Absolute path to the SQLite database file.
    """
    db_url = f"sqlite:///{db_path}"
    backend = get_backend(db_url)
    migrations = read_migrations(str(_MIGRATIONS_DIR))
    pending = backend.to_apply(migrations)

    if pending:
        backend.apply_migrations(pending)