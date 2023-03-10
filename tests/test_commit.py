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


def test_head_update():
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
    assert init_commit_id == "7c5180a06061453bd4559ea0754fa4f3581d1c91"

    # create a file representing the "main" branch
    branch = Path(repo.branches_dir / "main")
    with open(branch, "w") as file:
        file.write(init_commit_id)

    # create HEAD file and set current branch to "main"
    repo.head.touch()
    repo.head.write_text("main")

    file_a = Path("a.txt")
    file_a.touch()
    file_a.write_text("hi")
    repo.add("a.txt")

    new_head_id = repo.new_commit(repo.head_commit_id, "hi > a.txt")
    assert new_head_id != init_commit_id
    Path(repo.branches_dir / repo.current_branch).write_text(new_head_id)
    current_head_id = Path(repo.branches_dir / repo.current_branch).read_text()
    assert current_head_id == new_head_id


def test_log(runner, setup_repo):
    """Checks that the HEAD file's contents are updated to reference
    the new commit.
    """
    init_id = Path(setup_repo["branches"] / "main").read_text()
    result = runner.invoke(main, ["log"])
    assert (
        result.output == f"===\n"
        f"commit {init_id}\n"
        f"Date: Wed Dec 31 16:00:00 1969\n"
        f"Initial commit.\n\n"
    )
    file_a = Path("a.txt")
    file_a.touch()
    file_a.write_text("hello")
    runner.invoke(main, ["add", "a.txt"])
    runner.invoke(main, ["commit", "hello > a.txt"])
    first_commit_id = Path(setup_repo["branches"] / "main").read_text()
    assert init_id != first_commit_id
    file_a.write_text("hello, world")
    runner.invoke(main, ["add", "a.txt"])
    runner.invoke(main, ["commit", "hello, world > a.txt"])
    second_commit_id = Path(setup_repo["branches"] / "main").read_text()
    assert second_commit_id != first_commit_id
    # Get the timestamps from those two commits
    time_2 = get_timestamp(Path(setup_repo["commits_path"] / second_commit_id))
    time_1 = get_timestamp(Path(setup_repo["commits_path"] / first_commit_id))
    # Call the log
    result = runner.invoke(main, ["log"])
    assert (
        result.output == f"===\n"
        f"commit {second_commit_id}\n"
        f"Date: {time_2}\n"
        f"hello, world > a.txt\n"
        f"\n"
        f"===\n"
        f"commit {first_commit_id}\n"
        f"Date: {time_1}\n"
        f"hello > a.txt\n"
        f"\n"
        f"===\n"
        f"commit {init_id}\n"
        f"Date: Wed Dec 31 16:00:00 1969\n"
        f"Initial commit.\n\n"
    )


def get_timestamp(c_path: Path) -> str:
    """Retrieves the timestamp of the Commit object with the given id."""
    with open(c_path, "rb") as f:
        c = pickle.load(f)
    return c.timestamp
