import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import CursorResult, Insert, MetaData, Select, Update
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.asyncio import AsyncConnection, create_async_engine
from sqlalchemy.orm import DeclarativeBase, declared_attr, Mapped, mapped_column

from src.config import settings
from src.constants import DB_NAMING_CONVENTION

DATABASE_URL = str(settings.DATABASE_ASYNC_URL)

metadata = MetaData(naming_convention=DB_NAMING_CONVENTION)

engine = create_async_engine(
    DATABASE_URL,
    pool_size=settings.DATABASE_POOL_SIZE,
    pool_recycle=settings.DATABASE_POOL_TTL,
    pool_pre_ping=settings.DATABASE_POOL_PRE_PING,
)


class Base(DeclarativeBase):
    metadata = metadata

    @declared_attr.directive
    def __tablename__(cls) -> str:
        return cls.__name__.lower() + "s"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )


async def fetch_one(
        query: Select | Insert | Update,
        connection: AsyncConnection | None = None,
        commit_after: bool = False,
) -> dict[str, Any] | None:
    if not connection:
        async with engine.connect() as conn:
            cursor = await _execute_query(query, conn, commit_after)
            row = cursor.mappings().first()
            return dict(row) if row else None

    cursor = await _execute_query(query, connection, commit_after)
    row = cursor.mappings().first()
    return dict(row) if row else None


async def fetch_all(
        query: Select | Insert | Update,
        connection: AsyncConnection | None = None,
        commit_after: bool = False,
) -> list[dict[str, Any]]:
    if not connection:
        async with engine.connect() as conn:
            cursor = await _execute_query(query, conn, commit_after)
            return [dict(r) for r in cursor.mappings().all()]

    cursor = await _execute_query(query, connection, commit_after)
    return [dict(r) for r in cursor.mappings().all()]


async def execute(
        query: Insert | Update,
        connection: AsyncConnection | None = None,
        commit_after: bool = False,
) -> None:
    if not connection:
        async with engine.connect() as conn:
            await _execute_query(query, conn, commit_after)
            return

    await _execute_query(query, connection, commit_after)


async def _execute_query(
        query: Select | Insert | Update,
        connection: AsyncConnection,
        commit_after: bool = False,
) -> CursorResult:
    result = await connection.execute(query)
    if commit_after:
        await connection.commit()
    return result


async def get_connection() -> AsyncConnection:
    async with engine.connect() as connection:
        yield connection
