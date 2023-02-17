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
        if parent_one == "":  # initial commit has no parent
            self.parent_one = None
        else:
            self.parent_one = parent_one
        self.message = message
        self.timestamp = datetime.now()
        self.commit_id = str(hash(self.message + str(self.timestamp)))

    def __repr__(self):
        return f"{type(self).__name__}"
