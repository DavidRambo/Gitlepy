# tests/test_init.py
"""Tests the init command.
Tests for the creation of the repository directory and subdirectories,
the staging area file, the initial commit object, that the HEAD file exists
and points to the main branch, and that the main branch file exists and
points to the initial commit.
"""
from pathlib import Path
import pickle

from click.testing import CliRunner
import pytest

from gitlepy.index import Index
from gitlepy.__main__ import main
import gitlepy.repository as repo


@pytest.fixture
def runner():
    return CliRunner()


def test_main_init_new_repo(runner):
    """Creates a new repository successfully."""
    # with runner.isolated_filesystem(tmp_path):
    #     print(f"\n>>>>\n{tmp_path=}\n<<<<<\n")
    # print(f"\n<<<<\n{Path.cwd()=}\n>>>>>\n")
    result = runner.invoke(main, ["init"])
    assert repo.GITLEPY_DIR.exists()
    assert repo.BLOBS_DIR.exists()
    assert repo.COMMITS_DIR.exists()
    assert repo.INDEX.exists()

    with open(repo.INDEX, "rb") as file:
        test_index: Index = pickle.load(file)
        assert repr(test_index) == "Index"

    # Get name of commit object file. There should be only one.
    all_commits = list(repo.COMMITS_DIR.iterdir())
    if len(all_commits) > 1:
        raise Error("There should only be one commit object saved.")
    commit_file = all_commits[0]
    # Open it and unpickle it.
    with open(commit_file, "rb") as file:
        test_commit: Commit = pickle.load(file)
        assert repr(test_commit) == "Commit"
        assert test_commit.message == "Initial commit."

    main_branch = Path(repo.BRANCHES / "main")
    assert main_branch.exists()
    # Ensure main branch references initial commit.
    # with open(main_branch, "r") as file:
    #     assert file.readline() == test_commit.commit_id
    assert main_branch.read_text() == test_commit.commit_id

    assert repo.HEAD.exists()
    assert repo.HEAD.read_text() == "main"

    assert result.exit_code == 0
    assert result.output == "Initializing gitlepy repository.\n"


def test_main_init_already_exists(runner):
    """Tries to create a new repository where one already exists."""
    # with runner.isolated_filesystem():
    # print(tmp_path)
    repo.GITLEPY_DIR.mkdir()
    result = runner.invoke(main, ["init"])
    assert result.exit_code == 0
    assert result.output == "Gitlepy repository already exists.\n"
