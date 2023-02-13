# gitletpy/main.py
"""Handles command-line arguments and dispatches to appropriate command."""
import click

# from typing import Optional
from typing import Sequence

from gitlepy import repository


@click.command()
@click.argument("command")  # TODO: handle additional arguments
def main(command: Sequence[str] = None) -> None:
    if command == "init":
        # click.echo("Initializing gitlepy repository.")
        return repository.init()
    elif len(command) > 0 and not repository.GITLEPY_DIR.exists():
        # For all other commands, ensure gitlepy repo exists.
        click.echo("Not a Gitlepy repository.")
        return
    if command == "add":
        pass
        return
    if command == "rm":
        pass
    if command == "commit":
        pass
    if command == "checkout":
        pass
    if command == "log":
        pass
    if command == "status":
        pass
    if command == "branch":
        pass
    if command == "rm-branch":
        pass
    else:
        click.echo("Incorrect operands.")


if __name__ == "__main__":
    main()
