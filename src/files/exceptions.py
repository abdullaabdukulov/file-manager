from src.exceptions import BadRequest, NotFound, PermissionDenied

class FileNotFound(NotFound):
    DETAIL = "File not found"

class InvalidFileType(BadRequest):
    DETAIL = "Invalid file type"

class FileSizeExceeded(BadRequest):
    DETAIL = "File size exceeds role limit"

class InvalidVisibility(BadRequest):
    DETAIL = "Invalid visibility for role"

class FileAccessDenied(PermissionDenied):
    DETAIL = "No access to this file"