"""Repository module for Gitlepy.
Handles the logic for managing a Gitlepy repository.
All commands from gitlepy.main are dispatched to various functions in this module."""
from pathlib import Path
import pickle
import sys
from typing import Dict
from typing import List
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
        head: The file that references the currently checked out branch:
            .gitlepy/HEAD
        branches (list) : List of branch names.
        commits (list) : List of commit IDs.
        current_branch (str) : Name of the currently checked out branch.

    Methods:
        head_commit_id
        load_commit
        load_index
        load_blob
        get_blobs
        new_commit
        add
        checkout_file
        checkout
        reset
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
    def branches(self) -> List[str]:
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
    def commits(self) -> List[str]:
        """Returns a list of commit ids."""
        assert (
            self.commits_dir.exists()
        ), "Error: Gitlepy's commits directory does not exist."
        path_list = list(self.commits_dir.glob("*"))
        result = []
        for file in path_list:
            result.append(file.name)
        return result

    @property
    def current_branch(self) -> str:
        """Returns the name of the currently checked out branch."""
        return self.head.read_text()

    @property
    def head_commit_id(self) -> str:
        """Returns the ID of the currrently checked out commit."""
        return Path(self.branches_dir / self.current_branch).read_text()

    def get_branch_head(self, branch: str) -> str:
        """Returns the commit ID (the head) of the given branch."""
        assert branch in self.branches, "Not a valid branch name."
        # Define Path object for the branch reference file.
        p = Path(self.branches_dir / branch)
        return p.read_text()

    def load_commit(self, commit_id: str) -> Commit:
        """Returns the head commit object of the given branch."""
        commit_path = Path(self.commits_dir / commit_id)
        with open(commit_path, "rb") as file:
            return pickle.load(file)

    def load_index(self) -> Index:
        """Loads the staging area, i.e. the Index object."""
        with open(self.index, "rb") as file:
            return pickle.load(file)

    def load_blob(self, blob_id: str) -> Blob:
        p = Path(self.blobs_dir / blob_id)
        with open(p, "rb") as file:
            return pickle.load(file)

    def get_blobs(self, commit_id: str) -> Dict[str, str]:
        """Returns the dictionary of blobs belonging to the commit object with the
        specified commit_id.

        Args:
            commit_id: Name of the commit.
        """
        commit_obj = self.load_commit(commit_id)
        return commit_obj.blobs

    @property
    def working_files(self) -> list[str]:
        """Returns a list of non-hidden files in the working directory."""
        all_paths = list(self.work_dir.glob("*"))
        working_files = [
            file.name for file in all_paths if not file.name.startswith(".")
        ]
        return working_files

    @property
    def untracked_files(self) -> list[str]:
        """Returns a list of files in the working directory that are neither
        tracked by the current commit nor in the staging area.
        """
        untracked_files: list[str] = []

        # Create a set of all tracked or staged files.
        tracked_files: set = set(self.get_blobs(self.head_commit_id).keys())

        index = self.load_index()
        staged_files: set = set(index.additions.keys())
        staged_files = staged_files.union(index.removals)

        tracked_files = tracked_files.union(staged_files)

        for file in self.working_files:
            if file not in tracked_files:
                untracked_files.append(file)

        untracked_files.sort()

        return untracked_files

    @property
    def unstaged_modifications(self) -> list[str]:
        """Returns a list of tracked files modified but not staged,
           including a parenthetical indication of whether the file has been
           modified or deleted.

        Such a file is either:
        - tracked in current commit, changed in working directory, but not staged;
        - staged for addition, but with different contents than in the working directory;
        - staged for addition, but deleted in the working directory;
        - tracked in the current commit and deleted from the working directory,
          but not staged for removal.
        """
        unstaged_files: list[str] = []

        working_files: list = self.working_files
        tracked_blobs: dict = self.get_blobs(self.head_commit_id)

        index: Index = self.load_index()

        for filename in tracked_blobs.keys():
            # File was deleted but not staged for removal
            if filename not in working_files and filename not in index.removals:
                unstaged_files.append(f"{filename} (deleted)")
                continue

            if filename in working_files:
                # First compare with staged file
                if self._modified_since_staged(filename):
                    unstaged_files.append(f"{filename} (modified)")
                    continue
                # Then compare with tracked content
                elif self._diff_from_tracked(filename):
                    unstaged_files.append(f"{filename} (modified)")
                    continue

        # Check untracked files staged for addition.
        for filename in index.additions.keys():
            if filename not in tracked_blobs.keys():
                if filename not in working_files:
                    unstaged_files.append(f"{filename} (deleted)")
                else:
                    staged_blob: Blob = self.load_blob(index.additions[filename])
                    staged_contents = staged_blob.file_contents
                    file = Path(self.work_dir / filename)
                    current_contents = file.read_text()
                    if current_contents != staged_contents:
                        unstaged_files.append(f"{filename} (modified)")

        unstaged_files.sort()
        return unstaged_files

    def _modified_since_staged(self, filename: str) -> bool:
        """Returns True if file has been modified since staged."""
        index: Index = self.load_index()
        if filename in index.additions:
            staged_blob: Blob = self.load_blob(index.additions[filename])
            staged_contents = staged_blob.file_contents
            file = Path(self.work_dir / filename)
            current_contents = file.read_text()
            if current_contents != staged_contents:
                return True
        return False

    def _diff_from_tracked(self, filename: str) -> bool:
        """Returns True if file differs from tracked version and is not staged."""
        index: Index = self.load_index()
        if filename not in index.additions.keys():
            tracked_blobs: dict = self.get_blobs(self.head_commit_id)
            tracked_blob: Blob = self.load_blob(tracked_blobs[filename])
            tracked_contents = tracked_blob.file_contents
            file = Path(self.work_dir / filename)
            current_contents = file.read_text()
            if current_contents != tracked_contents:
                return True
        return False

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

        # Remove files staged for removal.
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
        head_commit = self.load_commit(self.head_commit_id)
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

    def remove(self, filename: str) -> None:
        """If the file is staged for addition, unstages it. Otherwise, if
        tracked and not staged, stages it file for removal. If tracked and
        in the working directory, deletes the file.

        Note: does not delete the file if it is untracked.
        """
        index: Index = self.load_index()

        # Check that file is not already staged for removal.
        if filename in index.removals:
            print("That file is already staged for removal.")
            return

        tracked_files = list(self.get_blobs(self.head_commit_id).keys())

        if filename in index.additions:
            # Stage for removal and save the index.
            index.unstage(filename)
            index.save()
        elif filename in tracked_files:
            index.remove(filename)
            index.save()
            # Delete it if not already deleted.
            file_path = Path(self.work_dir / filename)
            if file_path.exists():
                file_path.unlink()
        else:  # Neither staged nor tracked -> do nothing.
            print("No reason to remove the file.")
            return

    def checkout_file(self, filename: str, target: str = "") -> None:
        """Checks out a file from some commit.

        The default commit is the current HEAD, which is specified by a null
        target.

        Args:
            filename : name of the file to be checked out
            target : commit from which to check out the file
        """
        if target == "":  # Checkout the file from HEAD.
            commit = self.load_commit(self.head_commit_id)
        else:
            commit_id = self._match_commit_id(target)
            if not commit_id:
                print(f"{target} is not a valid commit.")
            else:
                commit = self.load_commit(commit_id)

        # Validate that file exists in HEAD commit.
        if filename not in commit.blobs:
            print(f"{filename} is not a valid file.")
        else:  # Checkout the file
            # Path for file in working directory
            filepath = Path(self.work_dir / filename)
            # Path for the blob
            blob = self.load_blob(commit.blobs[filename])
            filepath.write_text(blob.file_contents)

    def checkout_branch(self, target: str) -> None:
        """Checks out the given branch.

        target: Name of a branch.
        """
        if target in self.branches:  # Validate target is a branch.
            # Don't checkout current branch.
            if target == self.current_branch:
                print(f"Already on '{target}'")
                return

            # Update HEAD to target branch
            self.head.write_text(target)
            # Checkout the head commit for target branch.
            self.checkout_commit(self.get_branch_head(target))
        else:
            print(f"{target} is not a valid branch name.")

    def checkout_commit(self, target: str) -> None:
        """Checks out the given commit.

        target: id of the commit.
        """
        # Validate target as commit id
        target_commit_id = self._match_commit_id(target)
        if not target_commit_id:
            print("No commit with that id exists.")
        else:
            blobs: dict = self.get_blobs(target_commit_id)

            # Delete files untracked by target commit.
            for filename in self.working_files:
                if filename not in blobs:
                    Path(self.work_dir / filename).unlink()

            # Load file contents from blobs.
            for filename in blobs:
                file = Path(self.work_dir / filename)
                blob = self.load_blob(blobs[filename])
                file.write_text(blob.file_contents)

            # Update current branch HEAD to reference checked out commit.
            current_branch = Path(self.branches_dir / self.head.read_text())
            current_branch.write_text(target_commit_id)

            # clear the staging area
            index = self.load_index()
            index.clear()
            index.save()

    def _match_commit_id(self, target: str) -> Optional[str]:
        """Determines whether the `target` string is a valid commit.
        If `target` < 40 characters, then it will treat it as an abbreviation
        and try to find a matching commit.
        """
        # if target in commit ids, then return "commit"
        if target in self.commits:
            return target
        # else try to find a match for abbreviate commit id
        elif len(target) < 40:
            matches = []
            for id in self.commits:
                if id.startswith(target):
                    matches.append(id)
            if len(matches) > 1:
                print("Ambiguous commit abbreviation.")
            elif len(matches) == 1:
                return matches[0]
        # else return None
        return None

    def status(self) -> str:
        """Returns a string representation of the repository's current status."""
        output: str = ""
        # Branches
        output = "=== Branches ===\n"
        for branch in self.branches:
            if branch == self.current_branch:
                output += "*"
            output += f"{branch}\n"

        # Staging Area
        index = self.load_index()
        # Staged Files
        output += "\n=== Staged Files ===\n"
        for file in index.additions:
            output += f"{file}\n"
        # Removed Files
        output += "\n=== Removed Files ===\n"
        for file in index.removals:
            output += f"{file}\n"

        # TODO: Modifications Not Staged For Commit
        output += "\n === Modifications Not Staged For Commit ===\n"
        # TODO: Untracked Files
        output += "\n === Untracked Files ===\n"
        return output
