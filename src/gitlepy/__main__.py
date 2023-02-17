# gitletpy/main.py
"""Handles command-line arguments and dispatches to appropriate command."""
import os.path
import sys

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
        sys.exit(0)


@main.command()
@click.pass_context
def init(ctx) -> None:
    """Initialize new Gitlepy repository if one does not already exist."""

    if ctx.obj["REPO"]:
        click.echo("Gitlepy repository already exists.")
    else:
        return repository.init()


@main.command()
@click.argument("filename")
@click.pass_context
def add(ctx, filename: str) -> None:
    """Add a file to the staging area."""
    # Validate file.
    if not os.path.isfile(os.path.join(repository.WORK_DIR, filename)):
        click.echo(f"{filename} does not exist.")
        sys.exit(1)
    # Call repository method to stage the file.
    repository.add(filename)
    return


@main.command()
@click.argument("message")
@click.pass_context
def commit(ctx, message: str) -> None:
    """Commit contents in staging area to Gitlepy repository."""
    repository.commit(message)


if __name__ == "__main__":
    main()
