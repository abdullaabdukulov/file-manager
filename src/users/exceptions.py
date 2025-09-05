from src.exceptions import BadRequest, NotFound, PermissionDenied


class UserNotFound(NotFound):
    DETAIL = "User not found"


class UserAlreadyExists(BadRequest):
    DETAIL = "User already exists"


class InvalidRole(BadRequest):
    DETAIL = "Invalid role"


class DepartmentNotFound(NotFound):
    DETAIL = "Department not found"


class NoPermissionForDepartment(PermissionDenied):
    DETAIL = "No permission for this department"
