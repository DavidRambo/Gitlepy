# gitletpy/main.py
"""Handles command-line arguments and dispatches to appropriate command."""
import click

# from typing import Optional
from typing import Sequence

import repository


@click.command()
@click.argument("command")
def main(command: Sequence[str] = None) -> None:
    if command == "init":
        # click.echo("Initializing gitlepy repository.")
        repository.init()
    else:
        click.echo("Incorrect operands.")


if __name__ == "__main__":
    main()
