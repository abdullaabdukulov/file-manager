import uuid
from datetime import datetime
from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database import Base


class RefreshToken(Base):
    __tablename__ = "refresh_tokens"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    token: Mapped[str] = mapped_column(String(500), unique=True, nullable=False)
    expires_at: Mapped[datetime]

    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    user: Mapped["User"] = relationship("User")
