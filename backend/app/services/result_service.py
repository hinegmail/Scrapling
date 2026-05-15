"""Result service for business logic"""

import json
from datetime import datetime, timezone
from typing import Optional
from uuid import UUID

from sqlalchemy import and_, or_, desc, asc
from sqlalchemy.orm import Session

from app.models.result import Result
from app.models.task import Task
from app.exceptions import NotFoundError, ValidationError


class ResultService:
    """Result service for managing results"""

    @staticmethod
    def create_result(
        db: Session,
        task_id: UUID,
        data: dict,
        source_url: str,
        extracted_at: datetime,
    ) -> Result:
        """Create a new result"""
        # Verify task exists
        task = db.query(Task).filter(Task.id == task_id).first()
        if not task:
            raise NotFoundError("Task not found")

        result = Result(
            task_id=task_id,
            data=data,
            source_url=source_url,
            extracted_at=extracted_at,
        )

        db.add(result)
        db.commit()
        db.refresh(result)
        return result

    @staticmethod
    def get_result(db: Session, user_id: UUID, task_id: UUID, result_id: UUID) -> Result:
        """Get a specific result"""
        # Verify user owns the task
        task = db.query(Task).filter(
            and_(Task.id == task_id, Task.user_id == user_id)
        ).first()
        if not task:
            raise NotFoundError("Task not found")

        result = db.query(Result).filter(
            and_(Result.id == result_id, Result.task_id == task_id)
        ).first()

        if not result:
            raise NotFoundError("Result not found")

        return result

    @staticmethod
    def get_results(
        db: Session,
        user_id: UUID,
        task_id: UUID,
        page: int = 1,
        page_size: int = 10,
        search: Optional[str] = None,
        sort_by: str = "extracted_at",
        sort_order: str = "desc",
    ) -> tuple[list[Result], int]:
        """Get results with pagination, filtering, and sorting"""
        # Verify user owns the task
        task = db.query(Task).filter(
            and_(Task.id == task_id, Task.user_id == user_id)
        ).first()
        if not task:
            raise NotFoundError("Task not found")

        query = db.query(Result).filter(Result.task_id == task_id)

        # Search in data fields
        if search:
            search_term = f"%{search}%"
            # Search in source_url and data (as JSON string)
            query = query.filter(
                or_(
                    Result.source_url.ilike(search_term),
                    Result.data.astext.ilike(search_term),
                )
            )

        # Get total count
        total = query.count()

        # Apply sorting
        sort_column = getattr(Result, sort_by, Result.extracted_at)
        if sort_order.lower() == "asc":
            query = query.order_by(asc(sort_column))
        else:
            query = query.order_by(desc(sort_column))

        # Apply pagination
        offset = (page - 1) * page_size
        results = query.offset(offset).limit(page_size).all()

        return results, total

    @staticmethod
    def delete_result(db: Session, user_id: UUID, task_id: UUID, result_id: UUID) -> None:
        """Delete a result"""
        result = ResultService.get_result(db, user_id, task_id, result_id)
        db.delete(result)
        db.commit()

    @staticmethod
    def delete_results_by_task(db: Session, task_id: UUID) -> None:
        """Delete all results for a task"""
        db.query(Result).filter(Result.task_id == task_id).delete()
        db.commit()

    @staticmethod
    def search_results(
        db: Session,
        user_id: UUID,
        task_id: UUID,
        search_term: str,
        page: int = 1,
        page_size: int = 10,
    ) -> tuple[list[Result], int]:
        """Search results by content"""
        return ResultService.get_results(
            db, user_id, task_id, page, page_size, search_term
        )

    @staticmethod
    def filter_results(
        db: Session,
        user_id: UUID,
        task_id: UUID,
        filters: dict,
        page: int = 1,
        page_size: int = 10,
    ) -> tuple[list[Result], int]:
        """Filter results by various criteria"""
        # Verify user owns the task
        task = db.query(Task).filter(
            and_(Task.id == task_id, Task.user_id == user_id)
        ).first()
        if not task:
            raise NotFoundError("Task not found")

        query = db.query(Result).filter(Result.task_id == task_id)

        # Apply filters
        if "source_url" in filters and filters["source_url"]:
            query = query.filter(Result.source_url.ilike(f"%{filters['source_url']}%"))

        if "date_from" in filters and filters["date_from"]:
            query = query.filter(Result.extracted_at >= filters["date_from"])

        if "date_to" in filters and filters["date_to"]:
            query = query.filter(Result.extracted_at <= filters["date_to"])

        # Get total count
        total = query.count()

        # Apply pagination
        offset = (page - 1) * page_size
        results = query.offset(offset).limit(page_size).all()

        return results, total

    @staticmethod
    def get_results_for_export(
        db: Session,
        user_id: UUID,
        task_id: UUID,
        filters: Optional[dict] = None,
    ) -> list[Result]:
        """Get all results for export (without pagination)"""
        # Verify user owns the task
        task = db.query(Task).filter(
            and_(Task.id == task_id, Task.user_id == user_id)
        ).first()
        if not task:
            raise NotFoundError("Task not found")

        query = db.query(Result).filter(Result.task_id == task_id)

        # Apply filters if provided
        if filters:
            if "source_url" in filters and filters["source_url"]:
                query = query.filter(Result.source_url.ilike(f"%{filters['source_url']}%"))

            if "date_from" in filters and filters["date_from"]:
                query = query.filter(Result.extracted_at >= filters["date_from"])

            if "date_to" in filters and filters["date_to"]:
                query = query.filter(Result.extracted_at <= filters["date_to"])

        return query.order_by(desc(Result.extracted_at)).all()
