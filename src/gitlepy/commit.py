"""src/gitlepy/commit.py
Represents a Gitlepy repository's commit object.
"""
from datetime import datetime
from hashlib import sha1
from typing import Dict
from typing import Optional


class Commit:
    """Represents a Gitlepy commit object.

    It records a snapshot of the working directory as a dict of blobs, which
    map filenames to their blob IDs. A blob ID is the name of a blob, which
    stores the contents of a file at the time it was staged.

    Attributes:
        parent_one (str): ID of the parent commit
        parent_two (str): If it is a merge commit, ID of the second parent.
        message (str): Commit message.
        timestamp: datetime object representing the time of the commit.
        commit_id (str): hexdigest() of the commit's SHA-1 hash.
        blobs (dict): Dictionary in the form {"file name", "blob id"}.
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
        self.parent_two = parent_two
        self.message = message
        self.blobs: Dict[str, str] = {}

        if self.parent_one == "":  # initial commit
            self.timestamp = datetime.fromtimestamp(0).ctime()
        else:
            self.timestamp = datetime.now().ctime()

        self.commit_id = sha1(
            (self.message + str(self.timestamp)).encode("utf-8")
        ).hexdigest()

    def __repr__(self):
        return f"{type(self).__name__}"

    def __str__(self):
        """Formats the commit's information for the log command.

        ===
        commit [sha1 hash]
        Date: [timestamp]
        [commit message]
        [newline]
        """
        output = (
            "===\n"
            + "commit "
            + self.commit_id
            + "\n"
            + "Date: "
            + self.timestamp
            + "\n"
            + self.message
            + "\n"
        )
        return output
