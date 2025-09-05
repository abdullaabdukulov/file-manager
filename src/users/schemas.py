from pydantic import BaseModel, EmailStr, Field
from uuid import UUID

from src.schemas import CustomModel
from src.users.constants import Role

class DepartmentBase(CustomModel):
    name: str = Field(..., min_length=3, max_length=100)

class DepartmentResponse(DepartmentBase):
    id: UUID

class UserCreate(CustomModel):
    username: str = Field(..., min_length=3, max_length=50, pattern=r"^[a-zA-Z0-9_]+$")
    email: EmailStr
    password: str = Field(..., min_length=8)
    role: Role = Role.USER
    department_id: UUID

class UserUpdateRole(CustomModel):
    role: Role

class UserResponse(CustomModel):
    id: UUID
    username: str
    email: EmailStr
    role: Role
    department_id: UUID
    is_active: bool