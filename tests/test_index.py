# src/gitlepy/index.py
"""Tests the Index class."""
from pathlib import Path
import pickle

from click.testing import CliRunner
import pytest

from gitlepy.__main__ import main
from gitlepy.index import Index
import gitlepy.repository as repo


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def test_index(runner):
    runner.invoke(main, ["init"])
    assert repo.INDEX.exists()
    with open(repo.INDEX, "rb") as file:
        test_index: Index = pickle.load(file)
        assert repr(test_index) == "Index"
    return test_index


def test_add(runner, test_index):
    """Adds a file to the staging area.

    Args:
        runner (CliRunner): This is the click.testing object used to invoke
            commands.
        test_index (Index): The Gitlepy repository's Index object.
    """
    # Create a new file and write some text to it.
    file_a = Path(Path.cwd() / "a.txt")
    file_a.touch()
    file_a.write_text("hello")
    # gitlepy add a.txt
    runner.invoke(main, ["add", "a.txt"])
    adds = test_index.additions
    assert len(adds) == 1
    assert "a.txt" in adds.keys()


def test_add_no_file(runner, test_index):
    """Tries to add a non-existent file to the staging area."""
    result = runner.invoke(main, ["add", "nofile"])
    assert result.exit_code == 1
    assert result.output == "nofile does not exist.\n"
