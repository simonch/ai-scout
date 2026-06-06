import typer

from ai_scout.commands.topics import topics_app
from ai_scout.init.setup import run_init, CONFIG_PATH

_BANNER = r"""
#############################
#        AI-SCOUT          #
#############################
"""

app = typer.Typer()
app.add_typer(topics_app, name="topics", help="Manage interest topics")


@app.callback(invoke_without_command=True)
def _main(ctx: typer.Context):
    typer.echo(_BANNER)
    if ctx.invoked_subcommand is None:
        if not CONFIG_PATH.exists():
            run_init()
        typer.echo("Running AI Scout pipeline...")
        raise typer.Exit()


if __name__ == "__main__":
    app()