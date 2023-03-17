# tests/test_init.py
"""Tests the init command.
Tests for the creation of the repository directory and subdirectories,
the staging area file, the initial commit object, that the HEAD file exists
and points to the main branch, and that the main branch file exists and
points to the initial commit.
"""
import os.path
from pathlib import Path
import pickle

import pytest

from gitlepy.commit import Commit
from gitlepy.index import Index
from gitlepy.__main__ import main


def test_main_init_new_repo(runner):
    """Creates a new repository successfully."""
    # with runner.isolated_filesystem(tmp_path):
    #     print(f"\n>>>>\n{tmp_path=}\n<<<<<\n")
    # print(f"\n<<<<\n{Path.cwd()=}\n>>>>>\n")
    print(f"\n>>>>>>>\n{Path.cwd()}\n<<<<<<<\n")
    init_result = runner.invoke(main, ["init"])
    assert init_result.exit_code == 0
    init_expected = "Initializing gitlepy repository.\n"
    assert init_expected == init_result.output

    test_path = Path(Path(os.path.abspath(".")) / ".gitlepy")
    assert test_path.exists()
    assert Path(test_path / "blobs").exists()
    assert Path(test_path / "commits").exists()
    index_path = Path(test_path / "index")
    assert index_path.exists()
    assert Path(test_path / "refs").exists()
    assert Path(test_path / "index").exists()

    with open(index_path, "rb") as file:
        test_index: Index = pickle.load(file)
        assert repr(test_index) == "Index"

    # Get name of commit object file. There should be only one.
    all_commits = list(Path(test_path / "commits").iterdir())
    assert len(all_commits) == 1
    commit_file = all_commits[0]
    # Open it and unpickle it.
    with open(commit_file, "rb") as file:
        test_commit: Commit = pickle.load(file)
        assert repr(test_commit) == "Commit"
        assert test_commit.message == "Initial commit."

    main_branch = Path(Path(test_path / "refs") / "main")
    assert main_branch.exists()
    # Ensure main branch references initial commit.
    # with open(main_branch, "r") as file:
    #     assert file.readline() == test_commit.commit_id
    assert main_branch.read_text() == test_commit.commit_id

    head_file = Path(test_path / "HEAD")
    assert head_file.exists()
    assert head_file.read_text() == "main"


def test_main_init_already_exists(runner):
    """Tries to create a new repository where one already exists."""
    # with runner.isolated_filesystem():
    # print(tmp_path)
    result = runner.invoke(main, ["init"])
    result = runner.invoke(main, ["init"])
    assert result.exit_code == 0
    assert result.output == "Gitlepy repository already exists.\n"
