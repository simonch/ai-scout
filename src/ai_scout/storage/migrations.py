import os
import subprocess


def apply_migrations() -> None:
    database_url = os.environ["DATABASE_URL"]

    subprocess.run(
        [
            "yoyo",
            "apply",
            "--batch",
            "--database",
            database_url,
            "migrations",
        ],
        check=True,
    )