# gitletpy/__main__.py
"""Handles command-line arguments and dispatches to appropriate command."""
from pathlib import Path
import pickle
import os.path
import sys

# from typing import Dict

import click

from gitlepy.commit import Commit
from gitlepy.index import Index
from gitlepy.repository import Repo


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

    repo_path = Path(os.path.abspath(repo_home or "."))

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
    new_index = Index(repo.index)
    with open(repo.index, "wb") as file:
        pickle.dump(new_index, file)

    # Create initial commit.
    init_commit_id = repo.new_commit("", "Initial commit.")

    # create a file representing the "main" branch
    branch = Path(repo.branches_dir / "main")
    with open(branch, "w") as file:
        file.write(init_commit_id)

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
    if not os.path.isfile(os.path.join(repo.work_dir, filename)):
        click.echo(f"{filename} does not exist.")
        sys.exit(1)
    # Call repository method to stage the file.
    repo.add(filename)
    return


@main.command()
@click.argument("message")
@pass_repo
def commit(repo, message: str) -> None:
    """Commit contents in staging area to Gitlepy repository."""
    new_head_id = repo.new_commit(repo.head_commit_id(), message)
    Path(repo.branches_dir / repo.current_branch()).write_text(new_head_id)


@main.command()
@pass_repo
def log(repo) -> None:
    """Prints a log of commits beginning from the HEAD."""
    commit_id = repo.head_commit_id()
    while commit_id is not None:
        commit = repo.load_commit(commit_id)
        print(commit)
        commit_id = commit.parent_one


if __name__ == "__main__":
    main()
