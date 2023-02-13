# gitletpy/main.py
"""Handles command-line arguments and dispatches to appropriate command."""
import click

# from typing import Optional
from typing import Sequence

from gitlepy import repository


@click.command()
@click.argument("command")
def main(command: Sequence[str] = None) -> None:
    if command == "init":
        # click.echo("Initializing gitlepy repository.")
        repository.init()
    elif len(command) > 0 and not repository.GITLEPY_DIR.exists():
        # For all other commands, ensure gitlepy repo exists.
        click.echo("Not a Gitlepy repository.")
    else:
        click.echo("Incorrect operands.")


if __name__ == "__main__":
    main()
