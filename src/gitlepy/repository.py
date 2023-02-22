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


class Repo:
    """A Gitlepy repository object.

    This dataclass provides the variables that represent the repository's
    directory structure within the file system. Its methods further this
    role by serving up various strings and objects constitutive of a repo.

    Args:
        repo_path: Path object representing the working directory.

    Attributes:
        work_dir: The working directory tracked by the repository.
        gitlepy_dir: The gitlepy repository main directory.
        blobs_dir: Where blobs are stored: .gitlepy/blobs
        commits_dir: Where commits are stored: .gitlepy/commits
        branches_dir: Where branch names and their head commits are stored:
            .gitlepy/refs
        index: The file that represents the staging area: .gitlepy/index
        head: The file that stores the currently checked out commit:
            .gitlepy/HEAD

    Methods:
        current_branch
        head_commit_id
        load_commit
        load_index
        get_blobs
    """

    def __init__(self, repo_path: Path):
        self.work_dir: Path = repo_path
        self.gitlepy_dir: Path = Path(self.work_dir / ".gitlepy")
        self.blobs_dir: Path = Path(self.gitlepy_dir / "blobs")
        self.commits_dir: Path = Path(self.gitlepy_dir, "commits")
        self.branches_dir: Path = Path(self.gitlepy_dir, "refs")
        self.index: Path = Path(self.gitlepy_dir, "index")
        self.head: Path = Path(self.gitlepy_dir, "HEAD")

    @property
    def current_branch(self) -> str:
        """Returns the name of the currently checked out branch."""
        return self.head.read_text()

    @property
    def head_commit_id(self) -> str:
        """Returns the ID of the currrently checked out commit."""
        return Path(self.branches_dir / self.current_branch).read_text()

    def load_commit(self, commit_id: str) -> Commit:
        """Returns the head commit object of the given branch."""
        commit_path = Path(self.commits_dir / commit_id)
        with open(commit_path, "rb") as file:
            return pickle.load(file)

    def load_index(self) -> Index:
        """Loads the staging area, i.e. the Index object."""
        with open(self.index, "rb") as file:
            return pickle.load(file)

    def get_blobs(self, commit_id: str) -> Dict[str, str]:
        """Returns the dictionary of blobs belonging to the commit object with the
        specified commit_id.

        Args:
            commit_id: Name of the commit.
        """
        commit_obj = self.load_commit(commit_id)
        return commit_obj.blobs


# def add(filename: str) -> None:
#     """Stages a file in the working directory for addition.
#     If the file to be staged is identical to the one recorded by the current
#     commit, then do not stage it.

#     Args:
#         filename: Name of the file to be staged for addition.
#     """
#     # Create Path object
#     filepath = Path(WORK_DIR / filename)
#     # Read contents into new blob
#     new_blob = Blob(filepath)
#     # Load the staging area
#     index = load_index()

#     # Is it unchanged since most recent commit?
#     current_commit = load_commit(get_head_commit_id())
#     if new_blob.id in current_commit.blobs.keys():
#         with open(Path(BLOBS_DIR / new_blob.id), "rb") as file:
#             commit_blob = pickle.load(file)
#         if new_blob.file_contents == commit_blob.file_contents:
#             # Yes -> Do not stage, and remove if already staged.
#             index.unstage(filename)

#     # Stage file with blob in the staging area.
#     print(f">>> {filename=}")
#     print(f">>> {new_blob.id=}")
#     index.stage(filename, new_blob.id)
#     for key in index.additions.keys():
#         print(f"{key=}")
#     # Save blob.
#     with open(os.path.join(BLOBS_DIR, new_blob.id), "wb") as file:
#         pickle.dump(new_blob, file)


# def commit(message: str) -> None:
#     """Creates a new commit object and saves it to the repository.

#     Args:
#         message: Commit message.
#     """
#     # Check for changes staged for commit.
#     index = load_index()
#     if not index.additions and not index.removals:
#         print("No changes staged for commit.")
#         return

#     # Get id of current commit -> this will be parent of new commit.
#     new_commit = Commit(get_head_commit_id(), message)
#     with open(os.path.join(COMMITS_DIR, new_commit.commit_id), "wb") as file:
#         pickle.dump(new_commit, file)

#     # Clear index
#     index.additions.clear()
#     index.removals.clear()
#     with open(INDEX, "wb") as file:
#         pickle.dump(index, file)


# def _updateHead(branch_name: str) -> None:
#     """Truncates the HEAD file with the name of a branch."""
#     HEAD.write_text(branch_name)
