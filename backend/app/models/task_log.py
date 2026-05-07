"""Task log model"""

from datetime import datetime
from uuid import UUID
from enum import Enum

from sqlalchemy import String, DateTime, ForeignKey, Index, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, UUIDMixin


class LogLevel(str, Enum):
    """Log level enum"""

    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"


class TaskLog(Base, UUIDMixin):
    """Task log model"""

    __tablename__ = "task_logs"
    __table_args__ = (
        Index("idx_tasklog_task_id", "task_id"),
        Index("idx_tasklog_timestamp", "timestamp"),
        Index("idx_tasklog_level", "level"),
    )

    task_id: Mapped[UUID] = mapped_column(ForeignKey("tasks.id"), nullable=False)
    level: Mapped[LogLevel] = mapped_column(SQLEnum(LogLevel), nullable=False)
    message: Mapped[str] = mapped_column(String(2000), nullable=False)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    # Relationships
    task: Mapped["Task"] = relationship(back_populates="logs")

    def __repr__(self) -> str:
        return f"<TaskLog(id={self.id}, task_id={self.task_id}, level={self.level})>"


# Import at the end to avoid circular imports
from app.models.task import Task
