from sqlalchemy import BigInteger, Column, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql.sqltypes import Enum as SQLEnum

from src.database import Base
from src.files.constants import FileType, Visibility


class File(Base):
    __tablename__ = "files"

    owner_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    department_id = Column(
        UUID(as_uuid=True), ForeignKey("departments.id"), nullable=False
    )
    filename = Column(String(255), nullable=False)
    file_type = Column(SQLEnum(FileType), nullable=False)
    visibility = Column(SQLEnum(Visibility), nullable=False)
    file_size = Column(BigInteger, nullable=False)  # Size in bytes
    s3_key = Column(String(255), nullable=False, unique=True)
    download_count = Column(Integer, default=0, nullable=False)

    owner = relationship("User", back_populates="files")
    department = relationship("Department")
    file_metadata = relationship("FileMetadata", uselist=False, back_populates="file")


class FileMetadata(Base):
    __tablename__ = "file_metadata"

    file_id = Column(
        UUID(as_uuid=True), ForeignKey("files.id"), nullable=False, unique=True
    )
    page_count = Column(Integer, nullable=True)  # For PDF
    paragraph_count = Column(Integer, nullable=True)  # For DOC/DOCX
    table_count = Column(Integer, nullable=True)  # For DOC/DOCX
    title = Column(String(255), nullable=True)
    author = Column(String(255), nullable=True)
    creation_date = Column(String(50), nullable=True)
    creator = Column(String(255), nullable=True)  # For PDF

    file = relationship("File", back_populates="file_metadata")
