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


def test_index_saved(runner):
    """Creates a new Gitlepy repository and checks for the index."""
    runner.invoke(main, ["init"])
    assert repo.INDEX.exists()
    with open(repo.INDEX, "rb") as file:
        test_index: Index = pickle.load(file)
        assert repr(test_index) == "Index"
