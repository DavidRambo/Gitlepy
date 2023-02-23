# tests/test_index.py
"""Tests the Index class."""
import os
from pathlib import Path
import pickle

import pytest

from gitlepy.__main__ import main
from gitlepy.index import Index


def test_index_file(runner, setup_repo):
    # runner.invoke(main, ["init"])
    assert setup_repo["test_path"].exists()
    assert setup_repo["index_path"].exists()
    assert setup_repo["blobs_path"].exists()
    assert setup_repo["commits_path"].exists()
    assert setup_repo["branches"].exists()


def test_commit_no_changes(runner, setup_repo):
    """Tests that a commit with nothing staged fails."""
    # runner.invoke(main, ["init"])
    result = runner.invoke(main, ["commit", "no changes"])
    assert result.exit_code == 0
    assert result.output == "No changes staged for commit.\n"


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
    # runner.invoke(main, ["init"])
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
