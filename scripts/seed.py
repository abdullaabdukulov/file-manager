import asyncio
import logging
import sys
import uuid
from pathlib import Path

# Add project root to sys.path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from sqlalchemy import select
from src.auth.utils import hash_password
from src.database import async_session, execute, fetch_one
from src.users.constants import Role
from src.users.models import Department, User

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def seed_department(name: str = "Default Department") -> uuid.UUID:
    """Seed a department if it doesn't exist, return its ID."""
    async with async_session() as session:
        query = select(Department).where(Department.name == name)
        result = await fetch_one(query)
        if result:
            logger.info(f"Department '{name}' already exists with ID {result['id']}")
            return result["id"]

        dept_id = uuid.uuid4()
        insert_query = Department.__table__.insert().values(id=dept_id, name=name)
        await execute(insert_query, commit_after=True)
        logger.info(f"Created department '{name}' with ID {dept_id}")
        return dept_id

async def seed_admin(
    username: str = "admin",
    email: str = "admin@example.com",
    password: str = "admin123456",
    department_id: uuid.UUID | None = None,
) -> None:
    """Seed an admin user if it doesn't exist."""
    async with async_session() as session:
        query = select(User).where(User.username == username)
        result = await fetch_one(query)
        if result:
            logger.info(f"Admin user '{username}' already exists")
            return

        if not department_id:
            department_id = await seed_department()

        user_data = {
            "id": uuid.uuid4(),
            "username": username,
            "email": email,
            "hashed_password": hash_password(password),
            "role": Role.ADMIN,
            "department_id": department_id,
            "is_active": True,
        }
        insert_query = User.__table__.insert().values(**user_data)
        await execute(insert_query, commit_after=True)
        logger.info(f"Created admin user '{username}' with email '{email}'")

async def main():
    """Main function to run the seeder."""
    try:
        await seed_admin()
        logger.info("Seeding completed successfully")
    except Exception as e:
        logger.error(f"Seeding failed: {str(e)}")
        raise

if __name__ == "__main__":
    asyncio.run(main())