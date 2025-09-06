from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer

from src.auth.constants import TokenType
from src.auth.utils import decode_token
from src.exceptions import NotAuthenticated, PermissionDenied
from src.users.constants import Role
from src.users.service import get_user_by_id

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


async def get_current_user(token: str = Depends(oauth2_scheme)) -> dict:
    """Retrieve the current authenticated user from a JWT token."""
    token_data = decode_token(token)
    if token_data.get("type") != TokenType.ACCESS.value:
        raise NotAuthenticated(detail="Invalid token type")

    user = await get_user_by_id(token_data["sub"])
    if not user or not user["is_active"]:
        raise NotAuthenticated(detail="User not found or inactive")

    user["role"] = token_data["role"]
    user["department_id"] = token_data["department_id"]
    return user


def require_role(required_roles: list[Role]):
    """Dependency to restrict access to specified roles."""

    async def role_checker(current_user: dict = Depends(get_current_user)):
        user_role = Role(current_user["role"])
        if user_role not in required_roles:
            raise PermissionDenied(
                detail=f"Requires one of roles: {[r.value for r in required_roles]}"
            )
        return current_user

    return role_checker
