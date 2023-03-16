# gitletpy/__main__.py
"""Handles command-line arguments and dispatches to appropriate command."""
from pathlib import Path
import pickle
import os.path
import sys
from typing import Tuple

import click

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
def main(ctx, repo_home: str) -> None:
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
@click.argument("files", nargs=-1)
@pass_repo
def add(repo, files: Tuple[str]) -> None:
    """Add a file or files to the staging area."""
    for filename in files:
        # Validate file.
        if not os.path.isfile(os.path.join(repo.work_dir, filename)):
            click.echo(f"{filename} does not exist.")
            sys.exit(1)
        # Call repository method to stage the file.
        repo.add(filename)

    return


@main.command()
@click.argument("files", nargs=-1)
@pass_repo
def rm(repo, files: Tuple[str]) -> None:
    """Stage a file or files for removal."""
    for filename in files:
        repo.remove(filename)
    return


@main.command()
@click.argument("message")
@pass_repo
def commit(repo, message: str) -> None:
    """Commit contents in staging area to Gitlepy repository."""
    new_head_id = repo.new_commit(repo.head_commit_id, message)
    Path(repo.branches_dir / repo.current_branch).write_text(new_head_id)


@main.command()
@pass_repo
def log(repo) -> None:
    """Prints a log of commits beginning from the HEAD."""
    commit_id = repo.head_commit_id
    while commit_id != "":
        commit = repo.load_commit(commit_id)
        click.echo(commit)
        commit_id = commit.parent_one


@main.command()
@pass_repo
def status(repo) -> None:
    """Displays the status of the gitlepy repo.

    It prints lists of:
        - branches, marking the current with an asterisk,
        - staged files,
        - removed files,
        - modifications not staged for commit,
        - untracked files.
    """
    click.echo(repo.status())


@main.command()
@click.argument("branchname")
@click.option(
    "-d",
    "--delete",
    "delete",
    required=False,
    default=False,
    is_flag=True,
    help="Deletes target branch.",
)
@pass_repo
def branch(repo, branchname: str, delete: bool) -> None:
    """Creates or deletes a branch with the given name."""
    branch_path = Path(repo.branches_dir / branchname)
    if branch_path.exists() and not delete:
        click.echo("A branch with that name already exists.")
    elif branch_path.exists() and delete:
        # Cannot delete currently checked out branch.
        if repo.current_branch == branchname:
            click.echo("Cannot delete currently checked out branch.")
        else:
            branch_path.unlink()
    elif not branch_path.exists() and not delete:
        branch_path.touch()
        # Write current HEAD commit to new branch.
        branch_path.write_text(repo.head_commit_id)
    else:
        click.echo("Cannot delete: No branch with that name exists.")


@main.command()
@click.argument("target", required=False, default="")
@click.option(
    "-f",
    "--file",
    "filename",
    type=str,
    required=False,
    help="Specify the file to checkout.",
)
@pass_repo
def checkout(repo, target, filename):
    """Checkout a branch or a file from a commit.

    This command accepts five usages:\n
        gitlepy checkout -f <file name> : checks out the given file from the HEAD commit\n
        gitlepy checkout <commit id> -f <file name> : checks out the given file from
            the given commit\n
        gitlepy checkout <branch name> : checks out the given branch\n
            the given branch\n
    """
    # Parse arguments
    if filename:
        repo.checkout_file(filename, target)
    elif target:
        repo.checkout_branch(target)
    else:
        click.echo("Incorrect operands.")


@main.command()
@click.argument("target", required=True)
@pass_repo
def reset(repo, target: str):
    """Reset the working directory to target commit.

    Usage:
        gitlepy reset <commit id>\n
    """
    repo.checkout_commit(target)


@main.command()
@click.argument("target", required=True)
@pass_repo
def merge(repo, target: str):
    """Merge the current branch with the specified branch.

    Usage:
        gitlepy merge <branch name>\n
    """
    repo.merge(target)


if __name__ == "__main__":
    main()
