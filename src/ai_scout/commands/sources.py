from pathlib import Path

import typer
import yaml

from ai_scout.storage.models import SourceType
from ai_scout.storage.repository import SourcesRepository

sources_app = typer.Typer()


def _get_repo() -> SourcesRepository:
    """Load the config and return a SourcesRepository bound to the configured DB."""
    config_path = Path.home() / ".ai-scout" / "config.yaml"
    config = yaml.safe_load(config_path.read_text()) or {}
    db_path = str(Path(config["storage"]["db_file_path"]).expanduser())
    return SourcesRepository(db_path)


@sources_app.command()
def list():
    """List all active (non-archived) sources."""
    repo = _get_repo()
    sources = repo.get_all(include_archived=False)

    if not sources:
        typer.echo("No sources found.")
        raise typer.Exit()

    typer.echo("\nActive sources:")
    typer.echo("─" * 80)
    for s in sources:
        typer.echo(
            f"  {s.id[:8]}  {s.name:<30} {s.source_type:<20}  "
            f"pri={s.priority}  wt={s.weight}"
        )
    typer.echo("─" * 80)
    typer.echo(f"  {len(sources)} source(s) total")


@sources_app.command()
def add(
    name: str = typer.Argument(..., help="Source name"),
    url: str = typer.Argument(..., help="Source URL"),
    source_type: str = typer.Argument(
        ..., help=f"Source type ({', '.join(e.value for e in SourceType)})"
    ),
    priority: float = typer.Option(0.5, "--priority", "-p", help="Source priority"),
    weight: float = typer.Option(1.0, "--weight", "-w", help="Source weight"),
):
    """Register a new validated source."""
    # Validate source_type against the enum
    valid_types = {e.value for e in SourceType}
    if source_type not in valid_types:
        typer.echo(
            f"Invalid source_type '{source_type}'. "
            f"Must be one of: {', '.join(sorted(valid_types))}",
            err=True,
        )
        raise typer.Exit(code=1)

    repo = _get_repo()
    source = repo.add(
        name=name,
        url=url,
        source_type=source_type,
        priority=priority,
        weight=weight,
    )
    typer.echo(
        f"Added source: {source.name} (id={source.id[:8]}, "
        f"type={source.source_type})"
    )


@sources_app.command()
def remove(
    name: str = typer.Argument(..., help="Source name to archive"),
):
    """Archive (soft-delete) all active sources matching the given name."""
    repo = _get_repo()
    sources = repo.get_all(include_archived=False)
    matching = [s for s in sources if s.name == name]

    if not matching:
        typer.echo(f"No active source found with name '{name}'.")
        raise typer.Exit()

    for s in matching:
        repo.archive(s.id)
    typer.echo(f"Archived {len(matching)} source(s) with name '{name}'.")