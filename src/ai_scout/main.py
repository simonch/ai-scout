import typer

from ai_scout.init.setup import run_init

_BANNER = r"""
#############################
#        AI-SCOUT          #
#############################
"""


app = typer.Typer()


@app.callback(invoke_without_command=True)
def _banner_callback(ctx: typer.Context):
    typer.echo(_BANNER)
    if ctx.invoked_subcommand is None:
        raise typer.Exit()


@app.command()
def init():
    """
    Initialize AI Scout configuration.
    """
    run_init()


@app.command()
def run():
    """
    Placeholder for ingestion pipeline (later).
    """
    print("Running AI Scout pipeline...")


if __name__ == "__main__":
    app()