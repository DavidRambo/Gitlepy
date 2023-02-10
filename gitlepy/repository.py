"""Repository module for Gitlepy.
Handles the logic for managing a Gitlepy repository.
All commands from gitlepy.main are dispatched to various functions in this module."""
from pathlib import Path


# filesystem constants
WORK_DIR = Path(Path.cwd() / "work")
GITLET_DIR = Path(WORK_DIR / ".gitlet")
BLOBS_DIR = Path(GITLET_DIR / "blobs")
COMMITS_DIR = Path(GITLET_DIR / "commits")
BRANCHES = Path(GITLET_DIR / "refs")
INDEX = Path(GITLET_DIR / "index")
HEAD = Path(GITLET_DIR / "HEAD")


def init() -> None:
    """Initializes a new Gitlepy repository unless one already exists."""
    if GITLET_DIR.exists():
        print("Gitlepy repository already exists.")
        return

    print("Initializing gitlepy repository.")
    # Create directories
    if not WORK_DIR.exists():
        WORK_DIR.mkdir()
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
