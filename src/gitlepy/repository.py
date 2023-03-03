"""Repository module for Gitlepy.
Handles the logic for managing a Gitlepy repository.
All commands from gitlepy.main are dispatched to various functions in this module."""
from pathlib import Path
import pickle
import sys
from typing import Dict
from typing import Optional

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
    def branches(self) -> list:
        """Returns a list of branch names."""
        assert (
            self.branches_dir.exists()
        ), "Error: Gitlepy's branches directory does not exist."
        path_list = list(self.branches_dir.glob("*"))
        result = []
        for file in path_list:
            result.append(file.name)
        return result

    @property
    def commits(self) -> list:
        """Returns a list of commit ids."""
        assert (
            self.commits_dir.exists()
        ), "Error: Gitlepy's commits directory does not exist."
        path_list = list(self.commits_dir.glob("*"))
        result = []
        for file in path_list:
            result.append(file.name)
        return result

    def current_branch(self) -> str:
        """Returns the name of the currently checked out branch."""
        return self.head.read_text()

    def head_commit_id(self) -> str:
        """Returns the ID of the currrently checked out commit."""
        return Path(self.branches_dir / self.current_branch()).read_text()

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

    def new_commit(self, parent: str, message: str) -> str:
        """Creates a new Commit object and saves to the repostiory.

        Args:
            parent: ID of the parent commit.
            message: Commit message.
        """
        c = Commit(parent, message)
        c_file = Path.joinpath(self.commits_dir, c.commit_id)

        if parent == "":  # initial commit can be saved immediately
            with open(c_file, "wb") as f:
                pickle.dump(c, f)
            return c.commit_id

        # Load the index and ensure files are staged for commit.
        index = self.load_index()
        if not index.additions and not index.removals:
            print("No changes staged for commit.")
            sys.exit(0)

        # Begin with parent commit's blobs
        c.blobs = self.get_blobs(parent)

        # Record files staged for addition.
        c.blobs.update(index.additions)

        # Remove files staged for remaval.
        for key in index.removals:
            del c.blobs[key]

        # Clear and save index to file system.
        index.clear()
        index.save()

        # Save the commit
        with open(c_file, "wb") as f:
            pickle.dump(c, f)
        return c.commit_id

    def add(self, filename: str) -> None:
        """Stages a file in the working directory for addition.

        If the file to be staged is identical to the one recorded by the
        current commit, then do not stage it.

        Args:
            filename: Name of the file in the working directory to be staged.
        """
        # Create Path object and associated blob
        filepath = Path(self.work_dir / filename)
        new_blob = Blob(filepath)

        # Load the staging area.
        index = self.load_index()

        # Is it unchanged since most recent commit?
        head_commit = self.load_commit(self.head_commit_id())
        if new_blob.id in head_commit.blobs.keys():
            # Yes -> Do not stage, and remove if already staged.
            if index.is_staged(filename):
                index.unstage(filename)
        else:
            # Stage file with blob in the staging area.
            index.stage(filename, new_blob.id)

        # Save the staging area.
        index.save()

        # Save the blob.
        blob_path = Path(self.blobs_dir / new_blob.id)
        with open(blob_path, "wb") as f:
            pickle.dump(new_blob, f)

    # TODO:
    def checkout_file(self, filename: str, target: str = "") -> None:
        if target == "":
            # Checkout the file from HEAD.
            # Validate file exists in HEAD commit.
            head_commit = self.load_commit(self.head_commit_id())
            if filename not in head_commit.blobs:
                print(f"{filename} is not a valid file for the current HEAD.")
                return
        else:
            # Parse target for valid branch or commit id.
            # Is target in branches?
            # If not, then is it a commit id?
            print(f"{target} is neither a valid branch nor a valid commit.")
            return

        return

    # TODO:
    def checkout(self, target: str) -> None:
        """Checks out the given branch or commit.

        target: Either the name of a branch or the id for a commit.
        """
        return

    def _parse_target(self, target: str) -> Optional[str]:
        """Determines whether the <target> string is a valid branch name or
        commit. Called by the checkout_file and checkout methods.
        """
        # if target in branches, then return "branch"
        if target in self.branches:
            return "branch"
        # elif target in commit ids, then return "commit"
        elif target in self.commits:
            return "commit"
        # else return None
        return None
