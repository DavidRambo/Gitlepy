"""Repository module for Gitlepy.
Handles the logic for managing a Gitlepy repository.
All commands from gitlepy.main are dispatched to various functions in this module."""
from pathlib import Path
import pickle
from queue import SimpleQueue
import sys
import tempfile
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
        checkout_branch
        checkout_commit
        merge
    """

    def __init__(self, repo_path: Path):
        self.work_dir: Path = repo_path
        self.gitlepy_dir: Path = Path(self.work_dir / ".gitlepy")
        self.blobs_dir: Path = Path(self.gitlepy_dir / "blobs")
        self.commits_dir: Path = Path(self.gitlepy_dir, "commits")
        self.branches_dir: Path = Path(self.gitlepy_dir, "refs")
        self.index: Path = Path(self.gitlepy_dir, "index")
        self.head: Path = Path(self.gitlepy_dir, "HEAD")

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

    def current_branch(self) -> str:
        """Returns the name of the currently checked out branch."""
        return self.head.read_text()

    def head_commit_id(self) -> str:
        """Returns the ID of the currrently checked out commit."""
        return Path(self.branches_dir / self.current_branch()).read_text()

    def get_branch_head(self, branch: str) -> str:
        """Returns the head commit ID of the given branch."""
        assert branch in self.branches(), "Not a valid branch name."
        # Define Path object for the branch reference file.
        p = Path(self.branches_dir / branch)
        return p.read_text()

    def load_commit(self, commit_id: str) -> Commit:
        """Returns the Commit object with the specified ID."""
        commit_path = Path(self.commits_dir / commit_id)
        with commit_path.open("rb") as file:
            return pickle.load(file)

    def load_index(self) -> Index:
        """Loads the staging area, i.e. the Index object."""
        with self.index.open("rb") as file:
            return pickle.load(file)

    def load_blob(self, blob_id: str) -> Blob:
        p = Path(self.blobs_dir / blob_id)
        with p.open("rb") as file:
            return pickle.load(file)

    def get_blobs(self, commit_id: str) -> Dict[str, str]:
        """Returns the dictionary of blobs belonging to the commit object with the
        specified commit_id.

        Args:
            commit_id: Name of the commit.
        """
        commit_obj = self.load_commit(commit_id)
        return commit_obj.blobs

    def working_files(self) -> list[str]:
        """Returns a list of non-hidden files in the working directory."""
        all_paths: list[Path] = list(self.work_dir.glob("*"))
        working_files = [
            file.name for file in all_paths if not file.name.startswith(".")
        ]
        return working_files

    def untracked_files(self) -> list[str]:
        """Returns a list of files in the working directory that are neither
        tracked by the current commit nor staged for addition; also includes
        files staged for removal and then recreated.
        """
        untracked_files: list[str] = []

        # Create a set of all tracked or staged files.
        tracked_files: set = set(self.get_blobs(self.head_commit_id()).keys())

        index = self.load_index()
        staged_files: set = set(index.additions.keys())

        tracked_files = tracked_files.union(staged_files)

        for file in self.working_files():
            if file not in tracked_files or file in index.removals:
                untracked_files.append(file)

        untracked_files.sort()

        return untracked_files

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

        working_files: list = self.working_files()
        tracked_blobs: dict = self.get_blobs(self.head_commit_id())

        index: Index = self.load_index()

        for filename in tracked_blobs.keys():
            # File was deleted but not staged for removal
            if filename not in working_files and filename not in index.removals:
                unstaged_files.append(f"{filename} (deleted)")
                continue

            # File exists
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
            tracked_blobs: dict = self.get_blobs(self.head_commit_id())
            tracked_blob: Blob = self.load_blob(tracked_blobs[filename])
            tracked_contents = tracked_blob.file_contents
            file = Path(self.work_dir / filename)
            current_contents = file.read_text()
            if current_contents != tracked_contents:
                return True
        return False

    def new_commit(
        self, parent: str, message: str, merge_parent: Optional[str] = None
    ) -> None:
        """Creates a new Commit object and saves to the repostiory.

        Args:
            parent: ID of the parent commit.
            message: Commit message.
        """
        c = Commit(parent, message, merge_parent)
        c_file = Path.joinpath(self.commits_dir, c.commit_id)

        if parent == "":  # initial commit can be saved immediately
            with c_file.open("wb") as f:
                pickle.dump(c, f)
            self.update_branch_head(self.current_branch(), c.commit_id)
            return

        # Load the index and ensure files are staged for commit.
        index = self.load_index()
        if not index.additions and not index.removals:
            print("No changes staged for commit.")
            sys.exit(0)

        # Begin with parent commit's blobs
        c.blobs = self.get_blobs(parent)

        # Remove files staged for removal.
        for key in index.removals:
            c.blobs.pop(key, None)

        # Record files staged for addition.
        c.blobs.update(index.additions)

        # Clear and save index to file system.
        index.clear()
        index.save()

        # Save the commit
        with c_file.open("wb") as f:
            pickle.dump(c, f)

        self.update_branch_head(self.current_branch(), c.commit_id)
        return

    def update_branch_head(self, branch: str, commit_id: str) -> None:
        """Updates the HEAD reference of the specified branch."""
        Path(self.branches_dir / branch).write_text(commit_id)
        return

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
        if (
            not filename not in head_commit.blobs.keys()
            and new_blob.id == head_commit.blobs[filename]
        ):
            # Yes -> Do not stage, and remove if already staged.
            print("No changes have been made to that file.")
            if index.is_staged(filename):
                index.unstage(filename)
            return
        # Check whether file is already staged as well as since changed.
        elif (
            filename in index.additions.keys()
            and new_blob.id == index.additions[filename]
        ):
            print("File is already staged in present state.")
            return
        else:
            # Stage file with blob in the staging area.
            index.stage(filename, new_blob.id)

            # Save the blob.
            blob_path = Path(self.blobs_dir / new_blob.id)
            with blob_path.open("wb") as f:
                pickle.dump(new_blob, f)

        # Save the staging area.
        index.save()

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

        tracked_files = list(self.get_blobs(self.head_commit_id()).keys())

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
            commit = self.load_commit(self.head_commit_id())
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
        if target not in self.branches():  # Validate target is a branch.
            print(f"{target} is not a valid branch name.")
        # Don't checkout current branch.
        if target == self.current_branch():
            print(f"Already on '{target}'")
            return

        if self._validate_checkout():
            print("There are unstaged modifications in the way; stage and commit them.")
            return

        old_head: str = self.head_commit_id()
        # Update HEAD to reference target branch
        self.head.write_text(target)
        # Checkout the head commit for target branch.
        self._checkout_commit(old_head, self.get_branch_head(target))

    def _validate_checkout(self) -> bool:
        """Makes sure the working directory allows for checkout.
        Returns True if there is a problem.
        """
        if self.unstaged_modifications():
            return True

        return False

    def reset(self, target_id: str) -> None:
        """Resets the current branch to the specified commit."""
        # Validate target as commit id
        target_commit_id = self._match_commit_id(target_id)
        if not target_commit_id:
            print("No commit with that id exists.")
            return

        self._checkout_commit(self.head_commit_id(), target_commit_id)

        # Update current branch HEAD to reference checked out commit.
        current_branch_path = Path(self.branches_dir / self.current_branch())
        current_branch_path.write_text(target_commit_id)

    def _checkout_commit(self, old_head_id: str, target_id: str) -> None:
        """Checks out the given commit.

        This serves both the `gitlepy reset` and the `gitlepy checkout branch`
        commands.

        Unlike git, gitlepy does not allow for a detached HEAD state.
        Instead, checking out an arbitrary commit (via `reset`) resets the
        HEAD of the current branch to that commit.

        Args:
            target_id: id of the commit, can be abbreviated.
        """
        target_blobs: dict = self.get_blobs(target_id)

        # Delete files tracked by current commit and untracked by target commit.
        current_blobs: dict = self.get_blobs(old_head_id)
        for filename in current_blobs.keys():
            if filename not in target_blobs.keys():
                Path(self.work_dir / filename).unlink()

        # Load file contents from blobs.
        for filename in target_blobs.keys():
            file = Path(self.work_dir / filename)
            blob: Blob = self.load_blob(target_blobs[filename])
            file.write_text(blob.file_contents)

        # Update current branch's HEAD ref
        self.update_branch_head(self.current_branch(), target_id)

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
        if target in self.commits():
            return target
        # else try to find a match for abbreviate commit id
        elif len(target) < 40:
            matches = []
            for id in self.commits():
                if id.startswith(target):
                    matches.append(id)
            if len(matches) > 1:
                print("Ambiguous commit abbreviation.")
            elif len(matches) == 1:
                return matches[0]
        # else return None
        return None

    def log(self) -> None:
        """Returns a log of the current branch's commit history."""
        history = self._history(self.head_commit_id())
        for id in history:
            commit = self.load_commit(id)
            print(commit)

    def status(self) -> str:
        """Returns a string representation of the repository's current status."""
        output: str = ""
        # Branches
        output = "=== Branches ===\n"
        for branch in self.branches():
            if branch == self.current_branch():
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

        # Modifications Not Staged For Commit
        output += "\n=== Modifications Not Staged For Commit ===\n"
        for file in self.unstaged_modifications():
            output += f"{file}\n"
        # Untracked Files
        output += "\n=== Untracked Files ===\n"
        for file in self.untracked_files():
            output += f"{file}\n"

        return output

    def merge(self, target: str) -> None:
        """Merges the current branch with the specified `target` branch.
        It treats the current branch head as the parent commit, and then
        by comparing files between the split-point commit, the HEAD commit,
        and the head of the given branch, it stages files for addition or
        removal before creating a new commit.
        """
        # Validate the merge: True means invalid.
        if self._validate_merge(target):
            return

        # Get target branch's head commit id.
        target_commit_id = self.get_branch_head(target)

        # Get each branch's history and validate.
        current_history: list = self._history(self.head_commit_id())
        target_history: list = self._history(target_commit_id)
        if self._validate_history(target_commit_id, current_history, target_history):
            return

        # Find most recent common ancestor.
        split_id: str = self._find_split(current_history, target_history)
        if split_id == "":
            print("No common ancestor found.")
            return

        # Populate the staging area for the merge commit, and checkout
        # files as necessary. Returns a list of merge conflicts.
        conflicts: list[str] = self._prepare_merge(target_commit_id, split_id)

        if conflicts:
            self._merge_conflict(conflicts, target)
        else:
            merge_message = f"Merged {target} into {self.current_branch()}"
            self.new_commit(self.head_commit_id(), merge_message, target_commit_id)

    def _validate_merge(self, target: str) -> bool:
        """Error checking for merge method. Returns True if invalid.

        Unlike Gitlet, Gitlepy does not overwrite untracked files during
        a merge. Therefore, it does not consider untracked files to be
        in the way of a merge.
        """
        # Check for unstaged modifications files.
        if self.unstaged_modifications():
            print(
                "There is a file with unstaged changes;"
                + " delete it, or add and commit it first."
            )
            return True

        # Check whether staging area is clear.
        index: Index = self.load_index()
        if index.additions or index.removals:
            print("You have uncommitted changes.")
            return True
        # Ensure not already checked out.
        if target == self.current_branch():
            print("Cannot merge a branch with itself.")
            return True
        # Check that the specified branch exists.
        if target not in self.branches():
            print("A branch with that name does not exist.")
            return True

        return False

    def _history(self, head_id: str) -> list[str]:
        """Returns a list of commit IDs composing the specified commit's
        history.

        In order to accommodate merge commits, which have two parents,
        this method uses a queue to interlink divergent branch histories.
        """
        history = []
        q: SimpleQueue = SimpleQueue()
        q.put(head_id)

        while not q.empty():
            current_id = q.get()
            if current_id not in history:
                history.append(current_id)
                current_commit: Commit = self.load_commit(current_id)
                if current_commit.parent_two:
                    q.put(current_commit.parent_two)
                if current_commit.parent_one:
                    q.put(current_commit.parent_one)

        return history

    def _validate_history(
        self, target_head: str, current_history: list[str], target_history: list[str]
    ) -> bool:
        """Returns True if merge should be cancelled. First checks whether the
        target branch is an unmodified ancestor of the current branch. If the
        target branch history contains the current HEAD, then the current
        branch is fast-forwarded by checking out the target branch.

        Args:
            target_head: head commit id of the branch being merged.
            current_history: commit history of the currently checked out branch.
            target_history: commit history of the branch being merged.
        """
        if target_head in current_history:
            print("Target branch is an ancestor of the current branch.")
            return True
        if self.head_commit_id() in target_history:
            print("Current branch is fast-forwarded.")
            self._checkout_commit(self.head_commit_id(), target_head)
            return True
        return False

    def _find_split(self, current_history: list[str], target_history: list[str]) -> str:
        """Returns the most recent common ancestor of the two specified
        commit histories.
        """
        for id in target_history:
            if id in current_history:
                return id

        return ""

    def _prepare_merge(self, target_commit_id: str, split_id: str) -> list[str]:
        """Prepares the staging area for a merge commit and returns a list
        of conflicted files.

        Args:
            target_commit_id: ID of the commit at the head of the branch to be merged.
            split_id: ID of the most recent commont ancestor commit.
        """
        conflicts: list[str] = []
        head_blobs: Dict[str, str] = self.get_blobs(self.head_commit_id())
        target_blobs: Dict[str, str] = self.get_blobs(target_commit_id)
        split_blobs: Dict[str, str] = self.get_blobs(split_id)

        for filename in head_blobs:
            head_blob: Blob = self.load_blob(head_blobs[filename])

            if filename in target_blobs:  # file tracked by target branch
                self._merge_head_target(
                    conflicts,
                    filename,
                    head_blobs[filename],
                    target_blobs[filename],
                    split_blobs,
                )
            elif filename in split_blobs:
                # Not in target branch and present at split means
                # removed from target branch.
                split_blob: Blob = self.load_blob(split_blobs[filename])
                # If unmodified in HEAD since split, then remove.
                if head_blob == split_blob:
                    index: Index = self.load_index()
                    index.remove(filename)
                    index.save()
                    Path(self.work_dir / filename).unlink()
            # Remove file from target_blobs
            target_blobs.pop(filename, None)

        # Check files in target branch, which are not in current branch's HEAD.
        # (I.e. all [filename, blob_id] pairs remaining.)
        self._merge_target_blobs(target_blobs, split_blobs, target_commit_id)

        return conflicts

    def _merge_head_target(
        self,
        conflicts: list[str],
        filename: str,
        head_blob_id: str,
        target_blob_id: str,
        split_blobs: dict[str, str],
    ) -> None:
        """Helper method for _prepare_merge() that handles files tracked
        by both the current branch and the target branch.
        """
        index: Index = self.load_index()
        # head_blob: Blob = self.load_blob(head_blob_id)
        # target_blob: Blob = self.load_blob(target_blob_id)
        # Check for file at split point
        if filename in split_blobs:
            # split_blob: Blob = self.load_blob(split_blobs[filename])
            split_blob_id: str = split_blobs[filename]
            if split_blob_id != target_blob_id:  # Modified in target branch.
                # Not modified in current HEAD -> keep target version.
                if head_blob_id == split_blob_id:
                    index.stage(filename, target_blob_id)
                # Modified in HEAD -> check for conflict.
                elif head_blob_id != target_blob_id:
                    conflicts.append(filename)
        elif head_blob_id != target_blob_id:  # Not in split commit.
            conflicts.append(filename)

        index.save()

    def _merge_target_blobs(
        self,
        target_blobs: dict[str, str],
        split_blobs: dict[str, str],
        target_commit_id: str,
    ) -> None:
        index: Index = self.load_index()
        for filename in target_blobs:
            target_blob_id = target_blobs[filename]
            if filename not in split_blobs:  # Only present in target branch.
                self.checkout_file(filename, target_commit_id)
                index.stage(filename, target_blob_id)
            elif target_blob_id != split_blobs[filename]:
                index.stage(filename, target_blob_id)

        index.save()

    def _merge_conflict(self, conflicts: list[str], target_branch: str) -> None:
        """Resolves files in conflict by concatenating the two, stages them,
        and then creates a merge commit.
        """
        start = "<<<<<<< HEAD\n"
        middle = "=======\n"
        end = ">>>>>>>\n"

        target_blobs: Dict[str, str] = self.get_blobs(
            self.get_branch_head(target_branch)
        )

        for filename in conflicts:
            head_file = Path(self.work_dir / filename)
            # head_blob: Blob = self.load_blob(head_blobs[filename])
            target_blob: Blob = self.load_blob(target_blobs[filename])

            with tempfile.SpooledTemporaryFile(mode="w+t") as temp:
                temp.write(start)
                temp.write(head_file.read_text())
                temp.write(middle)
                temp.write(target_blob.file_contents)
                temp.write(end)
                temp.seek(0)
                head_file.write_text(temp.read())

            self.add(filename)

        merge_message = f"Merged f{self.current_branch()} into {target_branch}."
        self.new_commit(
            self.head_commit_id(), merge_message, self.get_branch_head(target_branch)
        )
        print("Encountered a merge conflict.")
