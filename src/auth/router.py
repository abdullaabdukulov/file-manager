from fastapi import APIRouter, Depends
from src.auth.dependencies import get_current_user
from src.auth.schemas import LoginRequest, TokenResponse
from src.auth.service import authenticate_user
from src.users.schemas import UserResponse

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=TokenResponse, summary="Login to the system")
async def login(login_request: LoginRequest):
    """Authenticate user with username and password in JSON body, return JWT access token."""
    access_token = await authenticate_user(login_request)
    return TokenResponse(access_token=access_token)


@router.get("/me", response_model=UserResponse, summary="Get current user information")
async def get_me(current_user: dict = Depends(get_current_user)):
    """Retrieve details of the authenticated user."""
    return UserResponse(**current_user)
