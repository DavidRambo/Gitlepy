"""Repository module for Gitlepy.
Handles the logic for managing a Gitlepy repository.
All commands from gitlepy.main are dispatched to various functions in this module."""
from pathlib import Path
import pickle
import os
from typing import Dict

from gitlepy.index import Index
from gitlepy.commit import Commit
from gitlepy.blob import Blob


# filesystem constants
WORK_DIR = Path.cwd()
GITLEPY_DIR = Path(WORK_DIR / ".gitlepy")
BLOBS_DIR = Path(GITLEPY_DIR / "blobs")
COMMITS_DIR = Path(GITLEPY_DIR / "commits")
BRANCHES = Path(GITLEPY_DIR / "refs")
INDEX = Path(GITLEPY_DIR / "index")
HEAD = Path(GITLEPY_DIR / "HEAD")


def init() -> None:
    """Initializes a new Gitlepy repository unless one already exists."""

    print("Initializing gitlepy repository.")
    # Create directories
    GITLEPY_DIR.mkdir()
    BLOBS_DIR.mkdir()
    COMMITS_DIR.mkdir()
    BRANCHES.mkdir()

    # create staging area
    INDEX.touch()
    new_index = Index()
    with open(INDEX, "wb") as file:
        pickle.dump(new_index, file)

    # Create initial commit.
    initial_commit = Commit("", "Initial commit.")
    init_commit_file = Path.joinpath(COMMITS_DIR, initial_commit.commit_id)
    with open(init_commit_file, "wb") as file:
        pickle.dump(initial_commit, file)

    # create a file representing the "main" branch
    branch = Path(BRANCHES / "main")
    with open(branch, "w") as file:
        file.write(initial_commit.commit_id)

    # create HEAD file and set current branch to "main"
    HEAD.touch()
    # updateHead("main")
    HEAD.write_text("main")

    return


def add(filename: str) -> None:
    """Stages a file in the working directory for addition.
    If the file to be staged is identical to the one recorded by the current
    commit, then do not stage it.

    Args:
        filename: Name of the file to be staged for addition.
    """
    # Create Path object
    filepath = Path(WORK_DIR / filename)
    # Read contents into new blob
    new_blob = Blob(filepath)
    # Load the staging area
    index = load_index()

    # Is it unchanged since most recent commit?
    current_commit = load_commit(get_head_commit_id())
    if new_blob.id in current_commit.blobs.keys():
        with open(Path(BLOBS_DIR / new_blob.id), "rb") as file:
            commit_blob = pickle.load(file)
        if new_blob.file_contents == commit_blob.file_contents:
            # Yes -> Do not stage, and remove if already staged.
            index.unstage(filename)

    # Stage file with blob in the staging area.
    print(f">>> {filename=}")
    print(f">>> {new_blob.id=}")
    index.stage(filename, new_blob.id)
    # Save blob.
    with open(os.path.join(BLOBS_DIR, new_blob.id), "wb") as file:
        pickle.dump(new_blob, file)


def commit(message: str) -> None:
    """Creates a new commit object and saves it to the repository.

    Args:
        message: Commit message.
    """
    # Get id of current commit -> this will be parent of new commit.
    new_commit = Commit(get_head_commit_id(), message)
    with open(os.path.join(COMMITS_DIR, new_commit.commit_id), "wb") as file:
        pickle.dump(new_commit, file)

    # Clear index
    index = load_index()
    index.additions.clear()
    index.removals.clear()
    with open(INDEX, "wb") as file:
        pickle.dump(index, file)


def get_current_branch() -> str:
    """Returns the name of the currently checked out branch."""
    return HEAD.read_text()


def get_head_commit_id() -> str:
    """Returns the ID of the currrently checked out commit."""
    return Path(BRANCHES / get_current_branch()).read_text()


def load_commit(commit_id: str) -> Commit:
    """Returns the head commit object of the given branch."""
    commit_path = Path(COMMITS_DIR / commit_id)
    with open(commit_path, "rb") as file:
        return pickle.load(file)


def load_index() -> Index:
    """Loads the staging area, i.e. the Index object."""
    with open(INDEX, "rb") as file:
        return pickle.load(file)


def get_blobs(commit_id: str) -> Dict[str, str]:
    """Returns the dictionary of blobs belonging to the commit object with the
    specified commit_id.

    Args:
        commit_id: Name of the commit.
    """
    commit_obj = load_commit(commit_id)
    return commit_obj.blobs


# def _updateHead(branch_name: str) -> None:
#     """Truncates the HEAD file with the name of a branch."""
#     HEAD.write_text(branch_name)
