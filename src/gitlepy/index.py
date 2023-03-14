"""src/gitlepy/index.py
Represents a Gitlepy repository's staging area.
"""
from pathlib import Path
import pickle
from typing import Dict
from typing import Set


class Index:
    """The Index class handles the Gitlepy repository's staging area.

    It uses two data structures to manage it: additions are implemented with a
    dictionary {"filename": "file contents"}, and removals with a set of
    filenames.
    """

    def __init__(
        self,
        index_path: Path,
        additions: Dict[str, str] = {},
        removals: Set[str] = set(),
    ) -> None:
        """Initializes the staging area by creating an empty dict.

        Args:
            additions (dict[str, str]): Maps filenames to their blobs.
            removals (set): Set of the names of files staged for removal.
        """
        self.path = index_path
        self.additions = additions
        self.removals = removals

    def __repr__(self):
        return f"{type(self).__name__}"

    def stage(self, filename: str, blob_id: str) -> None:
        """Stages the file with the given filename for addition.
        If the file was already staged, then it updates its corresponding blob.

        Args:
            filename (str): Name of the file being staged.
            blob_id (str): Name of the blob file that stores the tracked contents
                of the named file.
        """
        self.additions[filename] = blob_id

    def unstage(self, filename: str) -> None:
        """Removes the specified file from the staging area."""
        if filename in self.additions:
            del self.additions[filename]
        elif filename in self.removals:
            del self.removals[filename]

    def remove(self, filename: str) -> None:
        """Stages the specified file for removal."""
        self.removals.add(filename)

    def clear(self) -> None:
        """Clears the staging area."""
        self.additions.clear()
        self.removals.clear()

    def save(self) -> None:
        """Writes the index to the repository."""
        with open(self.path, "wb") as file:
            pickle.dump(self, file)

    def is_staged(self, filename: str) -> bool:
        """Determines whether the given file is staged for addition."""
        return filename in self.additions.keys()

    # def getAdditions(self) -> Dict[str, str]:
    #     """Provides access to the mapping of files staged for addition."""
    #     return self.additions

    # def getRemovals(self) -> Set[str]:
    #     """Provides access to the names of files staged for removal."""
    #     return self.removals
