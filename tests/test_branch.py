"""tests/test_branch.py"""
from pathlib import Path
import pickle

import pytest

from gitlepy.__main__ import main
from gitlepy import repository


def test_branch_already_exists(runner, setup_repo):
    "Tries to create a branch with a name of an existing branch."
    result = runner.invoke(main, ["branch", "main"])
    assert result.output == "A branch with that name already exists.\n"


def test_branch_file(runner, setup_repo):
    """Creates a new branch and ensures its representative file exists."""
    result = runner.invoke(main, ["branch", "dev"])  # create branch called dev
    dev_path = Path(setup_repo["branches"] / "dev")
    assert dev_path.exists()
    assert result.output == ""


def test_branches_list(runner, setup_repo):
    """Creates a branch and then lists all branches."""
    result = runner.invoke(main, ["branch", "dev"])  # create branch called dev
    # Create instance of Repo class for testing.
    r = repository.Repo(setup_repo["work_path"])
    result = r.branches
    assert len(result) == 2
    assert "main" in result
    assert "dev" in result
