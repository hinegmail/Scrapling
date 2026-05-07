"""Proxy model"""

from datetime import datetime
from typing import Optional
from uuid import UUID
from enum import Enum

from sqlalchemy import String, Boolean, DateTime, ForeignKey, Index, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, UUIDMixin, TimestampMixin


class ProxyProtocol(str, Enum):
    """Proxy protocol enum"""

    HTTP = "http"
    HTTPS = "https"
    SOCKS5 = "socks5"


class Proxy(Base, UUIDMixin, TimestampMixin):
    """Proxy model"""

    __tablename__ = "proxies"
    __table_args__ = (
        Index("idx_proxy_user_id", "user_id"),
        Index("idx_proxy_is_active", "is_active"),
    )

    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    protocol: Mapped[ProxyProtocol] = mapped_column(SQLEnum(ProxyProtocol), nullable=False)
    host: Mapped[str] = mapped_column(String(255), nullable=False)
    port: Mapped[int] = mapped_column(nullable=False)
    username: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    password: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Relationships
    user: Mapped["User"] = relationship(back_populates="proxies")

    def __repr__(self) -> str:
        return f"<Proxy(id={self.id}, name={self.name}, host={self.host}:{self.port})>"


# Import at the end to avoid circular imports
from app.models.user import User
