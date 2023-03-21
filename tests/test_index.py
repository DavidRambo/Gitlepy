# tests/test_index.py
"""Tests the Index class."""
from pathlib import Path
import pickle

import pytest

from gitlepy.__main__ import main
from gitlepy.index import Index
from gitlepy.repository import Repo


def test_index_file(runner, setup_repo):
    # runner.invoke(main, ["init"])
    assert setup_repo["test_path"].exists()
    assert setup_repo["index_path"].exists()
    assert setup_repo["blobs_path"].exists()
    assert setup_repo["commits_path"].exists()
    assert setup_repo["branches"].exists()


def test_add_no_file(runner, setup_repo):
    """Tries to add a non-existent file to the staging area."""
    # runner.invoke(main, ["init"])
    result = runner.invoke(main, ["add", "nofile"])
    assert result.exit_code == 1
    assert result.output == "nofile does not exist.\n"


def test_add(runner, setup_repo):
    """Adds a file to the staging area.

    Args:
        runner (CliRunner): This is the click.testing object used to invoke
            commands. (See above for the runner fixture.)
        setup_repo (dict): A dict containing Path objects to the repository's
            file structure. (See above for the setup_repo fixture.)
    """
    # Create a new file and write some text to it.
    file_a = Path("a.txt")
    file_a.touch()
    file_a.write_text("hello")
    assert file_a.exists()
    # gitlepy add a.txt
    result = runner.invoke(main, ["add", "a.txt"])
    assert result.output == ""

    with open(setup_repo["index_path"], "rb") as file:
        test_index: Index = pickle.load(file)

    assert repr(test_index) == "Index"
    assert len(test_index.additions) == 1
    assert "a.txt" in test_index.additions.keys()


def test_rm_none(runner, setup_repo):
    """Tries to remove an untracked, unstaged file."""
    file_a = Path("a.txt")
    file_a.touch()
    assert file_a.exists()
    result = runner.invoke(main, ["rm", "a.txt"])
    assert result.output == "No reason to remove the file.\n"


def test_rm_unstage(runner, setup_repo):
    """Removes a file from the stagind area."""
    file_a = Path("a.txt")
    file_a.touch()
    assert file_a.exists()
    runner.invoke(main, ["add", "a.txt"])
    result = runner.invoke(main, ["rm", "a.txt"])
    assert result.output == ""


def test_rm_removal_already_deleted(runner, setup_repo):
    """Stages a file for removal."""
    file_a = Path("a.txt")
    file_a.touch()
    assert file_a.exists()
    runner.invoke(main, ["add", "a.txt"])
    runner.invoke(main, ["commit", "Add a.txt"])
    file_a.unlink()
    result = runner.invoke(main, ["rm", "a.txt"])
    assert not file_a.exists()
    assert result.output == ""


def test_rm_removal_and_delete(runner, setup_repo):
    """Stages a file for removal."""
    file_a = Path("a.txt")
    file_a.touch()
    assert file_a.exists()
    runner.invoke(main, ["add", "a.txt"])
    runner.invoke(main, ["commit", "Add a.txt"])
    result = runner.invoke(main, ["rm", "a.txt"])

    repo = Repo(Path.cwd())
    index = repo.load_index()
    assert "a.txt" in index.removals
    assert not file_a.exists()
    assert result.output == ""


def test_rm_already_staged_removal(runner, setup_repo):
    """Tries to remove a file already staged for removal."""
    file_a = Path("a.txt")
    file_a.touch()
    assert file_a.exists()
    runner.invoke(main, ["add", "a.txt"])
    runner.invoke(main, ["commit", "Add a.txt"])
    runner.invoke(main, ["rm", "a.txt"])
    result = runner.invoke(main, ["rm", "a.txt"])
    expected = "That file is already staged for removal.\n"
    assert result.output == expected


def test_add_revert_add(runner, setup_repo):
    """Stages a file, then changes it to original state and adds, which
    unstages the file.
    """
    file_a = Path("a.txt")
    file_a.write_text("Some text.")
    runner.invoke(main, ["add", "a.txt"])
    runner.invoke(main, ["commit", "Add a.txt"])

    file_a.write_text("Different text.")
    runner.invoke(main, ["add", "a.txt"])
    file_a.write_text("Some text.")
    result = runner.invoke(main, ["add", "a.txt"])
    assert result.exit_code == 0
    assert result.output == ""
    repo = Repo(setup_repo["work_path"])
    index = repo.load_index()
    assert "a.txt" not in index.additions.keys()
