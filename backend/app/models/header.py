"""Custom header model"""

from uuid import UUID

from sqlalchemy import String, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, UUIDMixin, TimestampMixin


class Header(Base, UUIDMixin, TimestampMixin):
    """Custom header model"""

    __tablename__ = "headers"
    __table_args__ = (
        Index("idx_header_user_id", "user_id"),
    )

    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), nullable=False)
    key: Mapped[str] = mapped_column(String(255), nullable=False)
    value: Mapped[str] = mapped_column(String(1000), nullable=False)

    # Relationships
    user: Mapped["User"] = relationship(back_populates="headers")

    def __repr__(self) -> str:
        return f"<Header(id={self.id}, key={self.key})>"


# Import at the end to avoid circular imports
from app.models.user import User
