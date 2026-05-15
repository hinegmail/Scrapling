"""Webhook model"""

from datetime import datetime
from typing import Optional
from uuid import UUID
from enum import Enum

from sqlalchemy import String, Boolean, DateTime, ForeignKey, Index, JSON, Enum as SQLEnum, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, UUIDMixin, TimestampMixin


class WebhookEvent(str, Enum):
    """Webhook event types"""

    TASK_CREATED = "task.created"
    TASK_STARTED = "task.started"
    TASK_PROGRESS = "task.progress"
    TASK_COMPLETED = "task.completed"
    TASK_FAILED = "task.failed"
    TASK_STOPPED = "task.stopped"
    RESULT_CREATED = "result.created"


class WebhookStatus(str, Enum):
    """Webhook delivery status"""

    PENDING = "pending"
    DELIVERED = "delivered"
    FAILED = "failed"
    RETRYING = "retrying"


class Webhook(Base, UUIDMixin, TimestampMixin):
    """Webhook model for event notifications"""

    __tablename__ = "webhooks"
    __table_args__ = (
        Index("idx_webhook_user_id", "user_id"),
        Index("idx_webhook_is_active", "is_active"),
    )

    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)
    
    # Webhook URL
    url: Mapped[str] = mapped_column(String(2000), nullable=False)
    
    # Events to subscribe to (stored as comma-separated string)
    events: Mapped[str] = mapped_column(String(1000), nullable=False)
    
    # Secret for HMAC signature verification
    secret: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    
    # Retry configuration
    max_retries: Mapped[int] = mapped_column(Integer, default=3, nullable=False)
    retry_delay_seconds: Mapped[int] = mapped_column(Integer, default=60, nullable=False)
    
    # Track usage
    last_triggered_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    trigger_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    
    # Relationships
    user: Mapped["User"] = relationship(back_populates="webhooks")
    deliveries: Mapped[list["WebhookDelivery"]] = relationship(
        back_populates="webhook",
        cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Webhook(id={self.id}, name={self.name}, url={self.url})>"


class WebhookDelivery(Base, UUIDMixin, TimestampMixin):
    """Webhook delivery attempt record"""

    __tablename__ = "webhook_deliveries"
    __table_args__ = (
        Index("idx_webhook_delivery_webhook_id", "webhook_id"),
        Index("idx_webhook_delivery_status", "status"),
        Index("idx_webhook_delivery_created_at", "created_at"),
    )

    webhook_id: Mapped[UUID] = mapped_column(ForeignKey("webhooks.id"), nullable=False)
    
    # Event information
    event: Mapped[WebhookEvent] = mapped_column(SQLEnum(WebhookEvent), nullable=False)
    event_data: Mapped[dict] = mapped_column(JSON, nullable=False)
    
    # Delivery status
    status: Mapped[WebhookStatus] = mapped_column(SQLEnum(WebhookStatus), default=WebhookStatus.PENDING, nullable=False)
    
    # Response information
    http_status_code: Mapped[Optional[int]] = mapped_column(nullable=True)
    response_body: Mapped[Optional[str]] = mapped_column(nullable=True)
    error_message: Mapped[Optional[str]] = mapped_column(nullable=True)
    
    # Retry information
    attempt_count: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    next_retry_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    webhook: Mapped["Webhook"] = relationship(back_populates="deliveries")

    def __repr__(self) -> str:
        return f"<WebhookDelivery(id={self.id}, webhook_id={self.webhook_id}, status={self.status})>"


# Import at the end to avoid circular imports
from app.models.user import User
