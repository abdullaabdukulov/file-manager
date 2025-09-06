from uuid import UUID

from sqlalchemy import select, update

from src.database import execute, fetch_all, fetch_one
from src.users.constants import Role
from src.users.exceptions import (
    DepartmentNotFound,
    InvalidRole,
    NoPermissionForDepartment,
    UserAlreadyExists,
    UserNotFound,
)
from src.users.models import Department, User
from src.users.schemas import UserCreate, UserUpdateRole
from src.users.utils import prepare_user_for_creation


async def get_user_by_username(username: str) -> dict | None:
    """Retrieve a user by username."""
    query = select(User).where(User.username == username)
    return await fetch_one(query)


async def get_user_by_id(user_id: str) -> dict | None:
    """Retrieve a user by ID."""
    query = select(User).where(User.id == UUID(user_id))
    return await fetch_one(query)


async def create_user(user_create: UserCreate, current_user: dict) -> dict:
    """Create a new user with permission checks."""
    role = Role(current_user["role"])
    if role == Role.MANAGER and user_create.department_id != UUID(
        current_user["department_id"]
    ):
        raise NoPermissionForDepartment()

    existing_user = await get_user_by_username(user_create.username)
    if existing_user:
        raise UserAlreadyExists()

    dept_query = select(Department).where(Department.id == user_create.department_id)
    if not await fetch_one(dept_query):
        raise DepartmentNotFound()

    user_data = user_create.model_dump()
    user_data = prepare_user_for_creation(user_data)
    insert_query = User.__table__.insert().values(**user_data)
    await execute(insert_query, commit_after=True)

    return await get_user_by_username(user_create.username)


async def get_users(department_id: UUID | None, current_user: dict) -> list[dict]:
    """Get list of users with permission checks."""
    role = Role(current_user["role"])
    if role == Role.ADMIN:
        query = select(User).where(User.is_active)
    elif role == Role.MANAGER:
        dept_id = department_id or UUID(current_user["department_id"])
        if dept_id != UUID(current_user["department_id"]):
            raise NoPermissionForDepartment()

        query = select(User).where(User.department_id == dept_id, User.is_active)

    else:
        raise NoPermissionForDepartment()

    if department_id and role == Role.ADMIN:
        query = query.where(User.department_id == department_id)

    return await fetch_all(query)


async def get_user(user_id: UUID, current_user: dict) -> dict:
    """Get a specific user with permission checks."""
    user = await get_user_by_id(str(user_id))
    if not user:
        raise UserNotFound()

    return user


async def update_user_role(
    user_id: UUID, update_data: UserUpdateRole, current_user: dict
) -> dict:
    """Update a user's role with permission checks."""
    await get_user(user_id, current_user)

    if update_data.role not in Role:
        raise InvalidRole()

    if Role(current_user["role"]) != Role.ADMIN and update_data.role == Role.ADMIN:
        raise NoPermissionForDepartment(detail="Cannot set admin role")

    update_query = update(User).where(User.id == user_id).values(role=update_data.role)
    await execute(update_query, commit_after=True)

    return await get_user_by_id(str(user_id))
