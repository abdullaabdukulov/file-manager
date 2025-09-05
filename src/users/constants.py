from enum import Enum

class Role(str, Enum):
    USER = "USER"
    MANAGER = "MANAGER"
    ADMIN = "ADMIN"