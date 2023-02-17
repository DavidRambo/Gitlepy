"""Repository module for Gitlepy.
Handles the logic for managing a Gitlepy repository.
All commands from gitlepy.main are dispatched to various functions in this module."""
from pathlib import Path
import pickle

from gitlepy import index
from gitlepy.commit import Commit


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
    new_index = index.Index()
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


# def _updateHead(branch_name: str) -> None:
#     """Truncates the HEAD files with the name of a branch."""
#     HEAD.write_text(branch_name)
