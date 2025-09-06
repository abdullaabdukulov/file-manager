from datetime import timedelta

from src.auth.exceptions import InvalidCredentials
from src.auth.schemas import LoginRequest
from src.auth.utils import create_access_token, verify_password
from src.config import settings
from src.users.service import get_user_by_username


async def authenticate_user(login_data: LoginRequest) -> str:
    """Authenticate a user and return a JWT access token."""
    user = await get_user_by_username(login_data.username)
    if not user or not verify_password(login_data.password, user["hashed_password"]):
        raise InvalidCredentials()
    if not user["is_active"]:
        raise InvalidCredentials(detail="User is inactive")

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        user_id=str(user["id"]),
        role=user["role"],
        department_id=str(user["department_id"]),
        expires_delta=access_token_expires,
    )
    return access_token
