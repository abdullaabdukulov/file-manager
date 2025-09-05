import os
from src.files.constants import FileType
from src.files.exceptions import InvalidFileType


def get_file_type(filename: str) -> FileType:
    """Determine the file type from the filename extension."""
    ext = os.path.splitext(filename)[1].lower()
    if ext == ".pdf":
        return FileType.PDF
    elif ext in (".doc", ".docx"):
        return FileType.DOCX
    else:
        raise InvalidFileType()
