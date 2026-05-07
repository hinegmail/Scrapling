"""Result model"""

from datetime import datetime
from uuid import UUID

from sqlalchemy import DateTime, ForeignKey, Index, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, UUIDMixin, TimestampMixin


class Result(Base, UUIDMixin, TimestampMixin):
    """Result model"""

    __tablename__ = "results"
    __table_args__ = (
        Index("idx_result_task_id", "task_id"),
        Index("idx_result_extracted_at", "extracted_at"),
    )

    task_id: Mapped[UUID] = mapped_column(ForeignKey("tasks.id"), nullable=False)
    data: Mapped[dict] = mapped_column(JSON, nullable=False)
    source_url: Mapped[str] = mapped_column(nullable=False)
    extracted_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    # Relationships
    task: Mapped["Task"] = relationship(back_populates="results")

    def __repr__(self) -> str:
        return f"<Result(id={self.id}, task_id={self.task_id})>"


# Import at the end to avoid circular imports
from app.models.task import Task
