import uuid
from sqlalchemy import String, Enum as SqlEnum, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database import Base
import enum


class UserRole(str, enum.Enum):
    USER = "USER"
    MANAGER = "MANAGER"
    ADMIN = "ADMIN"


class Group(Base):
    __tablename__ = "groups"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)

    users: Mapped[list["User"]] = relationship("User", back_populates="group")


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)

    role: Mapped[UserRole] = mapped_column(SqlEnum(UserRole), nullable=False, default=UserRole.USER)

    group_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("groups.id"), nullable=True)
    group: Mapped["Group"] = relationship("Group", back_populates="users")

    files: Mapped[list["File"]] = relationship("File", back_populates="owner")
