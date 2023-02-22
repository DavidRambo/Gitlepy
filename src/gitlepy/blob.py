"""src/gitlepy/blob.py
Represents a blob object.
"""
from hashlib import sha1
from pathlib import Path


class Blob:
    """Represents a blob object in the Gitlepy repository.
    Blobs are stored in the BLOBS_DIR, as defined in gitlepy.repository.
    A blob records the contents of a file in the working directory, and its
    filename is the hash of this content. A blob is created when a file is
    staged for addition.
    """

    def __init__(self, filepath: Path):
        """Creates a new blob object from the contents of a file.

        The name for the blob is the hash of the file's contents.
        See the following two SO posts for info on chunking a file for
        space-efficient hashing: https://stackoverflow.com/a/22058673
        and https://stackoverflow.com/a/44873382

        Args:
            filename: Name of the file to be recorded as a blob.
        """
        self.file_contents = filepath.read_text()

        self.sha = sha1()
        BUF_SIZE: int = 64 * 1024  # 65_536
        mv = memoryview(bytearray(BUF_SIZE))
        with open(filepath, "rb", buffering=0) as f:
            while chunk := f.readinto(mv):
                self.sha.update(mv[:chunk])

        self.id = self.sha.hexdigest()
