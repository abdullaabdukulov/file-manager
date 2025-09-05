from src.exceptions import DetailedHTTPException


class InvalidCredentials(DetailedHTTPException):
    STATUS_CODE = 401
    DETAIL = "Invalid username or password"


class TokenExpired(DetailedHTTPException):
    STATUS_CODE = 401
    DETAIL = "Token has expired"


class InvalidToken(DetailedHTTPException):
    STATUS_CODE = 401
    DETAIL = "Invalid token"
