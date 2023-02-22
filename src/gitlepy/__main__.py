# gitletpy/main.py
"""Handles command-line arguments and dispatches to appropriate command."""
from dataclasses import dataclass
from pathlib import Path
import pickle
import os.path
import sys
from typing import Optional

import click

from gitlepy import repository
from gitlepy.commit import Commit
from gitlepy.index import Index


class Repo:
    """A Gitlepy repository object.

    This dataclass provides the variables that represent the repository's
    directory structure within the file system.
    """

    def __init__(self, repo_path: Path):
        self.work_dir: Path = repo_path
        self.gitlepy_dir: Path = Path(self.work_dir / ".gitlepy")
        self.blobs_dir: Path = Path(self.gitlepy_dir / "blobs")
        self.commits_dir: Path = Path(self.gitlepy_dir, "commits")
        self.branches_dir: Path = Path(self.gitlepy_dir, "refs")
        self.index: Path = Path(self.gitlepy_dir, "index")
        self.head: Path = Path(self.gitlepy_dir, "HEAD")


pass_repo = click.make_pass_decorator(Repo)


@click.group(invoke_without_command=True)
@click.option(
    "--repo-home",
    # default=".gitlepy",
    metavar="PATH",
    help="Changes the location of the repository folder.",
)
@click.pass_context
def main(ctx, repo_home: str):
    if ctx.invoked_subcommand is None:
        click.echo("Incorrect operands.")
        return

    if repo_home:
        repo_path = Path(os.path.abspath(repo_home))
    else:
        repo_path = Path(os.path.abspath("."))

    ctx.obj = Repo(repo_path)
    # ctx.obj.work_dir = Path(repo_path)

    repo_exists = ctx.obj.gitlepy_dir.exists()

    if ctx.invoked_subcommand != "init" and not repo_exists:
        click.echo("Not a Gitlepy repository.")
        sys.exit(0)


@main.command()
@pass_repo
def init(repo) -> None:
    """Initialize new Gitlepy repository if one does not already exist."""

    if repo.gitlepy_dir.exists():
        click.echo("Gitlepy repository already exists.")
        return
    # else:
    #     return repository.init()
    click.echo("Initializing gitlepy repository.")
    repo.gitlepy_dir.mkdir()
    repo.blobs_dir.mkdir()
    repo.commits_dir.mkdir()
    repo.branches_dir.mkdir()

    # create staging area
    repo.index.touch()
    new_index = Index()
    with open(repo.index, "wb") as file:
        pickle.dump(new_index, file)

    # Create initial commit.
    initial_commit = Commit("", "Initial commit.")
    init_commit_file = Path.joinpath(repo.commits_dir, initial_commit.commit_id)
    with open(init_commit_file, "wb") as file:
        pickle.dump(initial_commit, file)

    # create a file representing the "main" branch
    branch = Path(repo.branches_dir / "main")
    with open(branch, "w") as file:
        file.write(initial_commit.commit_id)

    # create HEAD file and set current branch to "main"
    repo.head.touch()
    repo.head.write_text("main")

    return


@main.command()
@click.argument("filename")
@pass_repo
def add(repo, filename: str) -> None:
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
@pass_repo
def commit(repo, message: str) -> None:
    """Commit contents in staging area to Gitlepy repository."""
    repository.commit(message)


if __name__ == "__main__":
    main()
