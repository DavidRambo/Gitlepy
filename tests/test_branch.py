"""tests/test_branch.py"""
from pathlib import Path


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
    result = r.branches()
    assert len(result) == 2
    assert "main" in result
    assert "dev" in result


def test_branch_delete(runner, setup_repo):
    """Creates a branch and deletes it."""
    runner.invoke(main, ["branch", "dev"])
    dev_path = Path(setup_repo["branches"] / "dev")
    assert dev_path.exists()
    result = runner.invoke(main, ["branch", "-d", "dev"])
    assert result.output == ""
    assert not dev_path.exists()


def test_branch_delete_not_exist(runner, setup_repo):
    """Tries to delete a non-existent branch."""
    result = runner.invoke(main, ["branch", "-d", "dev"])
    assert result.output == "Cannot delete: No branch with that name exists.\n"


def test_branch_delete_current(runner, setup_repo):
    """Tries to delete currently checked out branch."""
    result = runner.invoke(main, ["branch", "-d", "main"])
    assert result.output == "Cannot delete currently checked out branch.\n"
