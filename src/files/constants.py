from enum import Enum


class Visibility(str, Enum):
    PRIVATE = "PRIVATE"
    DEPARTMENT = "DEPARTMENT"
    PUBLIC = "PUBLIC"


class FileType(str, Enum):
    PDF = "PDF"
    DOC = "DOC"
    DOCX = "DOCX"
