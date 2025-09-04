import uuid
from sqlalchemy import String, Enum as SqlEnum, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
import enum

from src.database import Base


class FileVisibility(str, enum.Enum):
    PRIVATE = "PRIVATE"
    DEPARTMENT = "DEPARTMENT"
    PUBLIC = "PUBLIC"


class File(Base):
    __tablename__ = "files"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)

    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    path: Mapped[str] = mapped_column(String(500), nullable=False)
    mimetype: Mapped[str] = mapped_column(String(100), nullable=True)
    size: Mapped[int] = mapped_column(Integer, nullable=False)

    visibility: Mapped[FileVisibility] = mapped_column(
        SqlEnum(FileVisibility), default=FileVisibility.PRIVATE, nullable=False
    )

    owner_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    owner: Mapped["User"] = relationship("User", back_populates="files")

    metadata: Mapped["FileMetadata"] = relationship("FileMetadata", back_populates="file", uselist=False)


class FileMetadata(Base):
    __tablename__ = "file_metadata"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)

    file_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("files.id", ondelete="CASCADE"))
    file: Mapped["File"] = relationship("File", back_populates="metadata")

    pages: Mapped[int | None]
    author: Mapped[str | None]
    title: Mapped[str | None]
    created_at: Mapped[str | None]
    creator_program: Mapped[str | None]

    paragraphs: Mapped[int | None]
    tables: Mapped[int | None]
