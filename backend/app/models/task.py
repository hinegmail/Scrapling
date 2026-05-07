"""Task model"""

from datetime import datetime
from typing import Optional
from uuid import UUID
from enum import Enum

from sqlalchemy import String, Integer, Boolean, DateTime, ForeignKey, Index, JSON, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, UUIDMixin, TimestampMixin


class FetcherType(str, Enum):
    """Fetcher type enum"""

    HTTP = "http"
    DYNAMIC = "dynamic"
    STEALTHY = "stealthy"


class SelectorType(str, Enum):
    """Selector type enum"""

    CSS = "css"
    XPATH = "xpath"


class TaskStatus(str, Enum):
    """Task status enum"""

    DRAFT = "draft"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    STOPPED = "stopped"


class Task(Base, UUIDMixin, TimestampMixin):
    """Task model"""

    __tablename__ = "tasks"
    __table_args__ = (
        Index("idx_task_user_id", "user_id"),
        Index("idx_task_status", "status"),
        Index("idx_task_created_at", "created_at"),
        Index("idx_task_user_status", "user_id", "status"),
    )

    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)
    target_url: Mapped[str] = mapped_column(String(2000), nullable=False)
    fetcher_type: Mapped[FetcherType] = mapped_column(SQLEnum(FetcherType), nullable=False)
    selector: Mapped[str] = mapped_column(String(1000), nullable=False)
    selector_type: Mapped[SelectorType] = mapped_column(SQLEnum(SelectorType), nullable=False)
    timeout: Mapped[int] = mapped_column(Integer, default=30, nullable=False)
    retry_count: Mapped[int] = mapped_column(Integer, default=3, nullable=False)
    status: Mapped[TaskStatus] = mapped_column(SQLEnum(TaskStatus), default=TaskStatus.DRAFT, nullable=False)

    # Advanced options
    use_proxy_rotation: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    solve_cloudflare: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    custom_headers: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    cookies: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)

    # Browser configuration (for dynamic fetcher)
    wait_time: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    viewport_width: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    viewport_height: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    # Statistics
    last_run_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    total_runs: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    success_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    error_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # Relationships
    user: Mapped["User"] = relationship(back_populates="tasks")
    results: Mapped[list["Result"]] = relationship(back_populates="task", cascade="all, delete-orphan")
    logs: Mapped[list["TaskLog"]] = relationship(back_populates="task", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Task(id={self.id}, name={self.name}, status={self.status})>"


# Import at the end to avoid circular imports
from app.models.user import User
from app.models.result import Result
from app.models.task_log import TaskLog
