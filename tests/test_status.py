"""Tests the status command as well as the Repo class's methods for
determining untracked and modified files.
"""
from pathlib import Path

import pytest

from gitlepy.__main__ import main
from gitlepy.repository import Repo


def test_working_files(setup_repo):
    """Tests Repo.working_files property method."""
    repo = Repo(Path.cwd())
    file_a = Path(setup_repo["work_path"] / "a.txt")
    file_a.touch()
    working_result = repo.working_files
    assert ["a.txt"] == working_result


def test_untracked_files(setup_repo):
    """Tests Repo.untracked_files property method."""
    repo = Repo(Path.cwd())
    file_a = Path(setup_repo["work_path"] / "a.txt")
    file_a.touch()
    untracked_result = repo.untracked_files
    expected = ["a.txt"]
    assert type(untracked_result) == list
    assert untracked_result is not None
    assert expected == untracked_result


def test_unstaged_modifications_modified(runner, setup_repo):
    """Tests Repo.unstaged_modifications property method by modifying a
    tracked file without staging for addition.
    """
    repo = Repo(Path.cwd())
    file_a = Path(setup_repo["work_path"] / "a.txt")
    file_a.touch()
    runner.invoke(main, ["add", "a.txt"])
    runner.invoke(main, ["commit", "Add a.txt"])
    file_a.write_text("hello")
    result = repo.unstaged_modifications
    expected = ["a.txt (modified)"]
    assert expected == result


def test_unstaged_modifications_deleted(runner, setup_repo):
    """Tests Repo.unstaged_modifications property method by deleting
    a tracked file without staging for removal.
    """
    repo = Repo(Path.cwd())
    file_a = Path(setup_repo["work_path"] / "a.txt")
    file_a.touch()
    runner.invoke(main, ["add", "a.txt"])
    runner.invoke(main, ["commit", "Add a.txt"])
    file_a.unlink()
    result = repo.unstaged_modifications
    expected = ["a.txt (deleted)"]
    assert expected == result


def test_unstaged_modifications_untracked_staged_modified(runner, setup_repo):
    """Tests Repo.unstaged_modifications property method by modifying
    an untracked file after it was staged for addition.
    """
    repo = Repo(Path.cwd())
    file_a = Path(setup_repo["work_path"] / "a.txt")
    file_a.touch()
    runner.invoke(main, ["add", "a.txt"])
    file_a.write_text("hello")
    result = repo.unstaged_modifications
    expected = ["a.txt (modified)"]
    assert expected == result


def test_unstaged_modifications_tracked_staged_modified(runner, setup_repo):
    """Tests Repo.unstaged_modifications property method by modifying
    a file tracked by the current commit and already staged for addition.
    """
    repo = Repo(Path.cwd())
    file_a = Path(setup_repo["work_path"] / "a.txt")
    file_a.touch()
    runner.invoke(main, ["add", "a.txt"])
    runner.invoke(main, ["commit", "Add a.txt"])
    file_a.write_text("hello")
    runner.invoke(main, ["add", "a.txt"])
    file_a.write_text("hello, world")
    result = repo.unstaged_modifications
    expected = ["a.txt (modified)"]
    assert expected == result


def test_unstaged_modifications_none(runner, setup_repo):
    """Tests Repo.unstaged_modifications property method when no modifications
    are unstaged.
    """
    repo = Repo(Path.cwd())
    file_a = Path(setup_repo["work_path"] / "a.txt")
    file_a.touch()
    runner.invoke(main, ["add", "a.txt"])
    runner.invoke(main, ["commit", "Add a.txt"])
    file_a.write_text("hello")
    runner.invoke(main, ["add", "a.txt"])
    result = repo.unstaged_modifications
    expected = []
    assert expected == result


def test_unstaged_modifications_removal_readded(runner, setup_repo):
    """Tests Repo.unstaged_modifications property method by staging a file
    for removal and then adding it back to the working directory. It is now
    considered to be untracked.
    """
    repo = Repo(Path.cwd())
    file_a = Path(setup_repo["work_path"] / "a.txt")
    file_a.touch()
    runner.invoke(main, ["add", "a.txt"])
    runner.invoke(main, ["commit", "Add a.txt"])
    runner.invoke(main, ["rm", "a.txt"])
    file_a.touch()
    assert file_a.exists()

    result_1 = repo.unstaged_modifications
    expected_1 = []
    assert expected_1 == result_1

    expected_2 = ["a.txt"]
    result_2 = repo.untracked_files
    assert expected_2 == result_2
