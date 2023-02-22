"""src/gitlepy/commit.py
Represents a Gitlepy repository's commit object.
"""
from datetime import datetime
from hashlib import sha1
from pathlib import Path
import pickle
from typing import Dict
from typing import Optional

from gitlepy.index import Index


class Commit:
    """Represents a Gitlepy commit object.
    It records a snapshot of the working directory as a dict of blobs, which
    map filenames to their blob IDs. A blob ID is the name of a blob, which
    stores the contents of a file.
    """

    def __init__(
        self,
        parent_one: str,
        message: str,
        starting_blobs: Dict[str, str],
        index_path: Path,
        parent_two: Optional[str] = None,
    ) -> None:
        """Creates a commit object.

        Args:
            parent_one: ID of the parent commit.
            parent_two: In the event of a merge, ID of the merge commit.
            message: Commit message.
        """
        if parent_one == "":
            self.parent_one = None  # initial commit has no parent
            self.timestamp = datetime.fromtimestamp(0)  # common timestamp
            self.blobs = starting_blobs  # empty dict
        else:
            self.parent_one = parent_one
            self.timestamp = datetime.now()

            # Begin with parent commit's blobs.
            self.blobs = starting_blobs

            # Record files staged for addition.
            with open(index_path, "rb") as file:
                index = pickle.load(file)

            self.blobs.update(index.additions)

            # Remove files staged for remaval.
            for key in index.removals:
                del self.blobs[key]

            # Save index to file system.
            index.save()

        self.message = message
        self.commit_id = sha1(
            (self.message + str(self.timestamp)).encode("utf-8")
        ).hexdigest()

    def __repr__(self):
        return f"{type(self).__name__}"
