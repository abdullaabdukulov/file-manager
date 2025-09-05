from src.auth.utils import hash_password


def prepare_user_for_creation(user_data: dict) -> dict:
    """Prepare user data for creation by hashing the password."""
    user_data["hashed_password"] = hash_password(user_data.pop("password"))
    return user_data
