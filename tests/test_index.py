# tests/test_index.py
"""Tests the Index class."""
import os
from pathlib import Path
import pickle

from click.testing import CliRunner
import pytest

from gitlepy.__main__ import main
from gitlepy.index import Index
from gitlepy.repository import Repo


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def setup_repo(runner):
    runner.invoke(main, ["init"])
    repo_paths = {}
    repo_paths["test_path"] = Path(Path(os.path.abspath(".")) / ".gitlepy")
    repo_paths["index_path"] = Path(repo_paths["test_path"] / "index")
    repo_paths["blobs_path"] = Path(repo_paths["test_path"] / "blobs")
    repo_paths["commits_path"] = Path(repo_paths["test_path"] / "commits")
    repo_paths["branches"] = Path(repo_paths["test_path"] / "refs")
    return repo_paths


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
            commands.
        test_index (Index): The Gitlepy repository's Index object.
    """
    # runner.invoke(main, ["init"])
    # Create a new file and write some text to it.
    file_a = Path(setup_repo["test_path"] / "a.txt")
    file_a.touch()
    file_a.write_text("hello")
    assert file_a.exists()
    # gitlepy add a.txt
    runner.invoke(main, ["add", "a.txt"])
    with open(setup_repo["index_path"], "rb") as file:
        test_index: Index = pickle.load(file)
        assert repr(test_index) == "Index"
        assert len(test_index.additions) == 1
        assert "a.txt" in test_index.additions.keys()
