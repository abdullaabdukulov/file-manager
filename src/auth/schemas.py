from pydantic import Field

from src.schemas import CustomModel


class LoginRequest(CustomModel):
    username: str = Field(..., min_length=3, max_length=50, pattern=r"^[a-zA-Z0-9_]+$")
    password: str = Field(..., min_length=8)


class TokenResponse(CustomModel):
    access_token: str
    token_type: str = "bearer"
