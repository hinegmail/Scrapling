"""API Key model"""

from datetime import datetime
from typing import Optional
from uuid import UUID

from sqlalchemy import String, Boolean, DateTime, ForeignKey, Index, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, UUIDMixin, TimestampMixin


class APIKey(Base, UUIDMixin, TimestampMixin):
    """API Key model for third-party integrations"""

    __tablename__ = "api_keys"
    __table_args__ = (
        Index("idx_api_key_user_id", "user_id"),
        Index("idx_api_key_key_hash", "key_hash"),
        Index("idx_api_key_is_active", "is_active"),
    )

    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)
    
    # Store only the hash of the key for security
    key_hash: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    
    # Store the last 4 characters for display purposes
    key_preview: Mapped[str] = mapped_column(String(4), nullable=False)
    
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    
    # Track usage
    last_used_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    usage_count: Mapped[int] = mapped_column(default=0, nullable=False)
    
    # Expiration
    expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    
    # Permissions (stored as comma-separated string)
    permissions: Mapped[str] = mapped_column(String(1000), default="read,write", nullable=False)
    
    # Relationships
    user: Mapped["User"] = relationship(back_populates="api_keys")

    def __repr__(self) -> str:
        return f"<APIKey(id={self.id}, name={self.name}, key_preview=...{self.key_preview})>"


# Import at the end to avoid circular imports
from app.models.user import User
