"""Tests the status command as well as the Repo class's methods for
determining untracked and modified files.
"""
from pathlib import Path

import pytest

from gitlepy.__main__ import main
from gitlepy.repository import Repo


def test_working_files(runner, setup_repo):
    """Tests Repo.working_files property method."""
    repo = Repo(Path.cwd())
    file_a = Path(setup_repo["work_path"] / "a.txt")
    file_a.touch()
    working_result = repo.working_files
    assert ["a.txt"] == working_result


def test_untracked_files(runner, setup_repo):
    """Tests Repo.untracked_files property method."""
    repo = Repo(Path.cwd())
    file_a = Path(setup_repo["work_path"] / "a.txt")
    file_a.touch()
    untracked_result = repo.untracked_files
    expected = ["a.txt"]
    assert type(untracked_result) == list
    assert untracked_result is not None
    assert expected == untracked_result
