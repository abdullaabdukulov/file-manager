from uuid import UUID

from fastapi import APIRouter, Depends, Query

from src.auth.dependencies import get_current_user, require_role
from src.users.constants import Role
from src.users.schemas import UserCreate, UserResponse, UserUpdateRole
from src.users.service import create_user, get_user, get_users, update_user_role

router = APIRouter(prefix="/users", tags=["users"])


@router.post(
    "/",
    response_model=UserResponse,
    dependencies=[Depends(require_role([Role.MANAGER, Role.ADMIN]))],
)
async def create_new_user(
    user_create: UserCreate, current_user: dict = Depends(get_current_user)
):
    """Create a new user. Managers can only create users in their own department."""
    created_user = await create_user(user_create, current_user)
    return UserResponse(**created_user)


@router.get(
    "/",
    response_model=list[UserResponse],
    dependencies=[Depends(require_role([Role.MANAGER, Role.ADMIN]))],
)
async def list_users(
    department_id: UUID | None = Query(
        None,
        description="Optional department ID to filter users\
         (admins only for other departments)",
    ),
    current_user: dict = Depends(get_current_user),
):
    """
    List users in a department. Admins can list all or
    by department; managers only their own.
    """
    users = await get_users(department_id, current_user)
    return [UserResponse(**u) for u in users]


@router.get(
    "/{user_id}",
    response_model=UserResponse,
    dependencies=[Depends(require_role([Role.MANAGER, Role.ADMIN]))],
)
async def get_user_detail(
    user_id: UUID, current_user: dict = Depends(get_current_user)
):
    """
    Get details of a specific user.
    Permission checked based on role and department.
    """
    user = await get_user(user_id, current_user)
    return UserResponse(**user)


@router.put(
    "/{user_id}/role",
    response_model=UserResponse,
    dependencies=[Depends(require_role([Role.MANAGER, Role.ADMIN]))],
)
async def update_role(
    user_id: UUID,
    update_data: UserUpdateRole,
    current_user: dict = Depends(get_current_user),
):
    """
    Update a user's role. Managers cannot set ADMIN role and
    are limited to their department.
    """
    updated_user = await update_user_role(user_id, update_data, current_user)
    return UserResponse(**updated_user)
