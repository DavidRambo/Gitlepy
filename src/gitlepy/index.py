"""src/gitlepy/index.py
Handles a Gitlepy repository's staging area.
"""
from typing import Dict
from typing import Set


class Index:
    """The Index class handles the Gitlepy repository's staging area.

    It uses two data structures to manage it: additions are implemented with a
    dictionary {"filename": "file contents"}, and removals with a set of
    filenames.
    """

    def __init__(
        self, additions: Dict[str, str] = {}, removals: Set[str] = set()
    ) -> None:
        """Initializes the staging area by creating an empty dict.

        Args:
            additions (dict[str, str]): Maps filenames to their blobs.
            removals (set): Set of the names of files staged for removal.
        """
        self.additions = additions
        self.removals = removals

    def __repr__(self):
        return f"{type(self).__name__}"

    def getAdditions(self) -> Dict[str, str]:
        """Provides access to the mapping of files staged for addition."""
        return self.additions

    def getRemovals(self) -> Set[str]:
        """Provides access to the names of files staged for removal."""
        return self.removals

    def stage(self, filename: str, blobID: str) -> None:
        """Stages the file with the given filename for addition.
        If the file was already staged, then it updates its corresponding blob.

        Args:
            filename (str): Name of the file being staged.
            blobID (str): Name of the blob file that stores the tracked
            contents of the named file.
        """
        self.additions[filename] = blobID
