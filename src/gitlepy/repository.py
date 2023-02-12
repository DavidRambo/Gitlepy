"""Repository module for Gitlepy.
Handles the logic for managing a Gitlepy repository.
All commands from gitlepy.main are dispatched to various functions in this module."""
from pathlib import Path


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
    if GITLEPY_DIR.exists():
        print("Gitlepy repository already exists.")
        return

    print("Initializing gitlepy repository.")
    # Create directories
    GITLEPY_DIR.mkdir()
    BLOBS_DIR.mkdir()
    COMMITS_DIR.mkdir()
    BRANCHES.mkdir()

    # create staging area file
    INDEX.touch()

    # Create initial commit.

    # create a file representing the "main" branch
    branch = Path(BRANCHES / "main")
    branch.touch()

    # create HEAD file and set current branch to "main"
    HEAD.touch()
    # updateHead("main")
    HEAD.write_text("main")

    return


# def _updateHead(branch_name: str) -> None:
#     """Truncates the HEAD files with the name of a branch."""
#     HEAD.write_text(branch_name)
