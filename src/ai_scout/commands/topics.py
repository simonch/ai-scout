from pathlib import Path

import typer
import yaml

from ai_scout.storage.repository import TopicsRepository

topics_app = typer.Typer()


def _get_repo() -> TopicsRepository:
    """Load the config and return a TopicsRepository bound to the configured DB."""
    config_path = Path.home() / ".ai-scout" / "config.yaml"
    config = yaml.safe_load(config_path.read_text()) or {}
    db_path = str(Path(config["storage"]["db_file_path"]).expanduser())
    return TopicsRepository(db_path)


@topics_app.command()
def list():
    """List all active (non-archived) topics."""
    repo = _get_repo()
    topics = repo.get_all(include_archived=False)

    if not topics:
        typer.echo("No topics found.")
        raise typer.Exit()

    typer.echo("\nActive topics:")
    typer.echo("─" * 60)
    for t in topics:
        typer.echo(f"  {t.id[:8]}  {t.value:<40}  weight={t.weight}")
    typer.echo("─" * 60)
    typer.echo(f"  {len(topics)} topic(s) total")


@topics_app.command()
def add(
    value: str = typer.Argument(..., help="Topic value"),
    weight: float = typer.Option(1.0, "--weight", "-w", help="Topic weight"),
):
    """Add a new topic."""
    repo = _get_repo()
    topic = repo.add_topic(value=value, weight=weight)
    typer.echo(f"Added topic: {topic.value} (id={topic.id[:8]}, weight={topic.weight})")


@topics_app.command()
def remove(
    value: str = typer.Argument(..., help="Topic value to remove"),
):
    """Remove (archive) all topics matching the given value."""
    repo = _get_repo()
    topics = repo.get_all(include_archived=False)
    matching = [t for t in topics if t.value == value]

    if not matching:
        typer.echo(f"No active topic found with value '{value}'.")
        raise typer.Exit()

    for t in matching:
        repo.archive_topic(t.id)
    typer.echo(f"Archived {len(matching)} topic(s) with value '{value}'.")