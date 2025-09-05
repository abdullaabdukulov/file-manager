import uuid
from sqlalchemy import Boolean, Column, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql.sqltypes import Enum as SQLEnum

from src.database import Base
from src.users.constants import Role


class Department(Base):
    __tablename__ = "departments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), unique=True, nullable=False)

    users = relationship("User", back_populates="department")


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(120), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    role = Column(SQLEnum(Role), nullable=False, default=Role.USER)
    department_id = Column(UUID(as_uuid=True), ForeignKey("departments.id"), nullable=False)
    is_active = Column(Boolean, default=True)

    department = relationship("Department", back_populates="users")
