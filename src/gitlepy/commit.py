"""src/gitlepy/commit.py
Represents a Gitlepy repository's commit object.
"""
from datetime import datetime

from typing import Optional


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
        else:
            self.parent_one = parent_one
            self.timestamp = datetime.now()
        self.message = message
        self.commit_id = str(hash(self.message + str(self.timestamp)))

    def __repr__(self):
        return f"{type(self).__name__}"
