"""src/gitlepy/blob.py
Represents a blob object.
"""


class Blob:
    """Represents a blob object in the Gitlepy repository.
    Blobs are stored in the BLOBS_DIR, as defined in gitlepy.repository.
    A blob records the contents of a file in the working directory, and its
    filename is the hash of this content. A blob is created when a file is
    staged for addition.
    """

    def __init__(self, file_contents: str):
        """Creates a new blob object from the contents of a file.

        The name for the blob is the hash of the file's contents.

        Args:
            filename: Name of the file to be recorded as a blob.
        """
        self.file_contents = file_contents
        self.id = hash(file_contents)
