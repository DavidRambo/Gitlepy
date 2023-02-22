"""src/gitlepy/commit.py
Represents a Gitlepy repository's commit object.
"""
from datetime import datetime
from hashlib import sha1
from pathlib import Path
from typing import Dict
from typing import Optional

from gitlepy.index import Index


class Commit:
    """Represents a Gitlepy commit object.

    It records a snapshot of the working directory as a dict of blobs, which
    map filenames to their blob IDs. A blob ID is the name of a blob, which
    stores the contents of a file at the time it was staged.
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
        self.parent_one = parent_one
        self.message = message
        self.blobs: Dict[str, str] = {}

        if self.parent_one == "":  # initial commit
            self.timestamp = datetime.fromtimestamp(0)
        else:
            self.timestamp = datetime.now()

        self.commit_id = sha1(
            (self.message + str(self.timestamp)).encode("utf-8")
        ).hexdigest()

    def __repr__(self):
        return f"{type(self).__name__}"
