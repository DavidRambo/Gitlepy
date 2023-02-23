"""tests/test_commit.py

Tests the commit command.

The first two tests each create a new commit and ensure their attributes
(message, blobs) are correct. I can try to check the timestamp; however,
this may be difficult depending on how exact it is. One way around exact
matches of timestamps is to do a range between two times taken just before
and just after the commit. To check the commit_ID, I will simply assert
its length is 40.

The third test checks that the log command works, which in turn entails
that the Commit.__str__() method works.
"""
from pathlib import Path
import pickle

import pytest

from gitlepy.__main__ import main
from gitlepy.index import Index
from gitlepy.repository import Repo


def test_commit_no_changes(runner, setup_repo):
    """Tests that a commit with nothing staged fails."""
    # runner.invoke(main, ["init"])
    result = runner.invoke(main, ["commit", "no changes"])
    assert result.exit_code == 0
    assert result.output == "No changes staged for commit.\n"


def test_successful_commit(runner, setup_repo):
    file_a = Path("a.txt")
    file_a.touch()
    file_a.write_text("hello")
    runner.invoke(main, ["add", "a.txt"])
    result = runner.invoke(main, ["commit", "Write hello to a."])
    assert result.output == ""


def test_commit_hash():
    """This test circumvents the click interface in __main__ in order
    to test the Repo class's own new_commit method.
    """
    # Initialize
    repo = Repo(Path.cwd())
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
    assert len(init_commit_id) == "026a95e8b538e97b46567dfb94b61730dc9bc004"


def test_head_update(runner, setup_repo):
    """Checks that the HEAD file's contents are updated to reference
    the new commit.
    """
    init_id = Path(setup_repo["branches"] / "main").read_text()
    file_a = Path("a.txt")
    file_a.touch()
    file_a.write_text("hello")
    runner.invoke(main, ["add", "a.txt"])
    runner.invoke(main, ["commit", "hello > a.txt"])
    first_commit_id = Path(setup_repo["branches"] / "main").read_text()
    assert init_id != first_commit_id


# def test_log(runner, setup_repo):
#     file_a = Path("a.txt")
#     file_a.touch()
#     file_a.write_text("hello")
#     runner.invoke(main, ["add", "a.txt"])
#     runner.invoke(main, ["commit", "hello > a.txt"])
#     file_a.write_text("hello, world")
#     runner.invoke(main, ["add", "a.txt"])
#     runner.invoke(main, ["commit", "hello, world > a.txt"])
