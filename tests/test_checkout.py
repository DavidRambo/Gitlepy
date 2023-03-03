"""tests/test_checkout.py"""
from pathlib import Path
import pickle

import pytest

from gitlepy.__main__ import main


def test_checkout_branch_does_not_exist(runner, setup_repo):
    """Tries to checkout a non-existent branch."""
    result = runner.invoke(main, ["checkout", "dev"])
    assert result.output == "No such branch exists.\n"


def test_checkout_already_on_branch(runner, setup_repo):
    """Tries to checkout currently checked out branch."""
    result = runner.invoke(main, ["checkout", "main"])
    assert result.output == "No need to checkout the current branch.\n"


def test_checkout_new_branch(runner, setup_repo):
    """Creates a new branch and checks it out."""
    runner.invoke(main, ["branch", "dev"])  # create branch called dev
    result = runner.invoke(main, ["checkout", "dev"])
    assert result.output == ""  # No stdout
    assert setup_repo["head"].read_text() == "dev"  # HEAD updated
    # dev branch is on same commit as main
    main_path = Path(setup_repo["branches"] / "main")
    main_head = main_path.read_text()
    dev_path = Path(setup_repo["branches"] / "dev")
    dev_head = dev_path.read_text()
    assert main_head == dev_head
