"""tests/test_merge.py

Tests the merge command.
"""
from pathlib import Path

import pytest

from gitlepy.__main__ import main
from gitlepy.repository import Repo


@pytest.fixture(autouse=True)
def merge_setup(runner, setup_repo):
    """Basic multi-branch setup for merge tests.

    Leaves the gitlepy repository in the following state, with a clean
    working directory:
    === Branches ===
    *dev
    main

    main's a.txt = "Hello"
    dev's a.txt = "Hello, gitlepy."
    """
    file_a = Path(setup_repo["work_path"] / "a.txt")
    file_a.write_text("Hello")
    runner.invoke(main, ["add", "a.txt"])
    runner.invoke(main, ["commit", "Hello > a.txt"])

    runner.invoke(main, ["branch", "dev"])  # create branch called dev
    runner.invoke(main, ["checkout", "dev"])  # check out dev
    file_a.write_text("Hello, gitlepy.")
    runner.invoke(main, ["add", "a.txt"])
    runner.invoke(main, ["commit", "Hello, gitlepy > a.txt"])


def test_merge_uncommited_changes(runner, setup_repo):
    """Fails to merge due to staged but uncommited changes."""
    runner.invoke(main, ["checkout", "main"])
    file_a = Path(setup_repo["work_path"] / "a.txt")
    file_a.write_text("Hi\n")
    runner.invoke(main, ["add", "a.txt"])  # stage file_a
    result = runner.invoke(main, ["merge", "dev"])
    expected = "You have uncommitted changes.\n"
    assert expected == result.output


def test_merge_unstaged_changes(runner, setup_repo):
    """Merges a file with unstaged changes."""
    runner.invoke(main, ["checkout", "main"])
    file_a = Path(setup_repo["work_path"] / "a.txt")
    file_a.write_text("Hi\n")
    result = runner.invoke(main, ["merge", "dev"])
    expected = "There is a file with unstaged changes; delete it, or add and commit it first.\n"
    assert result.output == expected


def test_merge_nonexistent_branch(runner, setup_repo):
    """Tries to merge with a branch name that does not exist."""
    r = Repo(setup_repo["work_path"])
    result = r.branches()
    assert len(result) == 2
    assert "main" in result
    assert "dev" in result
    assert r.current_branch() == "dev"
    result = runner.invoke(main, ["merge", "invalid"])
    print(f"\n>>>>\n{r.branches()}\n<<<<<")
    expected = "A branch with that name does not exist.\n"
    assert expected == result.output


def test_merge_self(runner, setup_repo):
    """Tries to merge a branch with itself."""
    result = runner.invoke(main, ["merge", "dev"])
    expected = "Cannot merge a branch with itself.\n"
    assert expected == result.output


def test_merge_file_change(runner, setup_repo):
    """Fast forwards main to dev."""
    runner.invoke(main, ["checkout", "main"])
    merge_result = runner.invoke(main, ["merge", "dev"])
    merge_expected = "Current branch is fast-forwarded.\n"
    assert merge_expected == merge_result.output
    file_a = Path(setup_repo["work_path"] / "a.txt")
    expected = "Hello, gitlepy."
    assert file_a.read_text() == expected


def test_merge_head_updated(runner, setup_repo):
    """Fast forwards main to dev and checks that the HEAD reference
    for main branch is the same as dev branch."""
    repo = Repo(setup_repo["work_path"])
    dev_ref = repo.head_commit_id()

    # checkout main
    runner.invoke(main, ["checkout", "main"])
    old_main_ref = repo.head_commit_id()
    assert dev_ref != old_main_ref

    # merge with dev
    merge_result = runner.invoke(main, ["merge", "dev"])
    assert "Current branch is fast-forwarded.\n" == merge_result.output
    new_main_ref = repo.head_commit_id()
    assert old_main_ref != new_main_ref
    assert new_main_ref == dev_ref


def test_merge_ignore_untracked_file(runner, setup_repo):
    """Fast forwards main to dev, ignoring an untracked file."""
    file_b = Path(setup_repo["work_path"] / "b.txt")
    file_b.touch()
    runner.invoke(main, ["checkout", "main"])
    file_c = Path(setup_repo["work_path"] / "c.txt")
    file_c.touch()
    runner.invoke(main, ["merge", "dev"])
    assert file_b.exists()
    assert file_c.exists()


def test_merge_file_conflict(runner, setup_repo):
    """Merges a file with a conflict."""
    runner.invoke(main, ["checkout", "main"])
    file_a = Path(setup_repo["work_path"] / "a.txt")
    file_a.write_text("Hi\n")
    runner.invoke(main, ["add", "a.txt"])
    runner.invoke(main, ["commit", "Hi > a.txt"])
    result = runner.invoke(main, ["merge", "dev"])
    expected = "<<<<<<< HEAD\nHi\n=======\nHello, gitlepy.>>>>>>>\n"
    assert file_a.read_text() == expected
