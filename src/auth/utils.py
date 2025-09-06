from datetime import datetime, timedelta, timezone
from typing import Dict

import jwt
from jwt.exceptions import ExpiredSignatureError, InvalidTokenError
from passlib.context import CryptContext

from src.auth.constants import TokenType
from src.auth.exceptions import InvalidToken, TokenExpired
from src.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """Hash a password using bcrypt."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against a hashed password."""
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(
    user_id: str, role: str, department_id: str, expires_delta: timedelta | None = None
) -> str:
    """Create a JWT access token with user_id, role, and department_id claims."""
    now = datetime.now(timezone.utc)
    if expires_delta:
        expire = now + expires_delta
    else:
        expire = now + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode: Dict = {
        "sub": user_id,
        "role": role,
        "department_id": department_id,
        "iat": now,
        "exp": expire,
        "type": TokenType.ACCESS.value,
    }
    encoded_jwt = jwt.encode(
        to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
    )
    return encoded_jwt


def decode_token(token: str) -> Dict:
    """Decode and validate a JWT token, raising specific exceptions for errors."""
    try:
        return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    except ExpiredSignatureError:
        raise TokenExpired()
    except InvalidTokenError:
        raise InvalidToken()
    except Exception:
        raise InvalidToken()
