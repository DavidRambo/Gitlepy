# gitletpy/main.py
"""Handles command-line arguments and dispatches to appropriate command."""
import click

# from typing import Optional
# from typing import Sequence

from gitlepy import repository


@click.group(invoke_without_command=True)
@click.pass_context
def main(ctx):
    ctx.ensure_object(dict)

    if ctx.invoked_subcommand is None:
        click.echo("Incorrect operands.")
        return

    ctx.obj["REPO"] = repository.GITLEPY_DIR.exists()

    if (
        ctx.invoked_subcommand is not None
        and ctx.invoked_subcommand != "init"
        and not ctx.obj["REPO"]
    ):
        click.echo("Not a Gitlepy repository.")


@main.command()
@click.pass_context
def init(ctx):
    """Initialize new Gitlepy repository if one does not already exist."""

    if ctx.obj["REPO"]:
        click.echo("Gitlepy repository already exists.")
    else:
        return repository.init()


@main.command()
@click.argument("filename")
@click.pass_context
def add(ctx, filename: str):
    """Add a file to the staging area."""
    pass


@main.command()
@click.argument("message")
@click.pass_context
def commit(ctx, message: str):
    """Commit contents in staging area to Gitlepy repository."""
    pass


if __name__ == "__main__":
    main()
