"""Task service"""

from datetime import datetime, timezone
from typing import Optional
from uuid import UUID

from sqlalchemy import and_
from sqlalchemy.orm import Session

from app.models.task import Task, TaskStatus, FetcherType, SelectorType
from app.models.user import User
from app.exceptions import NotFoundError, ValidationError, AuthorizationError
from app.schemas.task import TaskCreate, TaskUpdate


class TaskService:
    """Task service for business logic"""

    @staticmethod
    def create_task(db: Session, user_id: UUID, task_data: TaskCreate) -> Task:
        """Create a new task"""
        # Validate required fields
        if not task_data.name or not task_data.target_url or not task_data.selector:
            raise ValidationError("Missing required fields: name, target_url, selector")

        # Validate URL format
        if not task_data.target_url.startswith(("http://", "https://")):
            raise ValidationError("Invalid URL format")

        # Validate selector based on type
        TaskService._validate_selector(task_data.selector, task_data.selector_type)

        # Validate fetcher-specific configuration
        TaskService._validate_fetcher_config(task_data)

        # Create task
        task = Task(
            user_id=user_id,
            name=task_data.name,
            description=task_data.description,
            target_url=task_data.target_url,
            fetcher_type=task_data.fetcher_type,
            selector=task_data.selector,
            selector_type=task_data.selector_type,
            timeout=task_data.timeout,
            retry_count=task_data.retry_count,
            use_proxy_rotation=task_data.use_proxy_rotation,
            solve_cloudflare=task_data.solve_cloudflare,
            custom_headers=task_data.custom_headers,
            cookies=task_data.cookies,
            wait_time=task_data.wait_time,
            viewport_width=task_data.viewport_width,
            viewport_height=task_data.viewport_height,
            status=TaskStatus.DRAFT,
        )

        db.add(task)
        db.commit()
        db.refresh(task)
        return task

    @staticmethod
    def get_task(db: Session, user_id: UUID, task_id: UUID) -> Task:
        """Get a task by ID"""
        task = db.query(Task).filter(
            and_(Task.id == task_id, Task.user_id == user_id)
        ).first()

        if not task:
            raise NotFoundError("Task not found")

        return task

    @staticmethod
    def get_tasks(
        db: Session,
        user_id: UUID,
        page: int = 1,
        page_size: int = 10,
        status: Optional[TaskStatus] = None,
        search: Optional[str] = None,
    ) -> tuple[list[Task], int]:
        """Get tasks with pagination and filtering"""
        query = db.query(Task).filter(Task.user_id == user_id)

        # Filter by status
        if status:
            query = query.filter(Task.status == status)

        # Search by name or description
        if search:
            search_term = f"%{search}%"
            query = query.filter(
                (Task.name.ilike(search_term)) | (Task.description.ilike(search_term))
            )

        # Get total count
        total = query.count()

        # Apply pagination
        offset = (page - 1) * page_size
        tasks = query.offset(offset).limit(page_size).all()

        return tasks, total

    @staticmethod
    def update_task(db: Session, user_id: UUID, task_id: UUID, task_data: TaskUpdate) -> Task:
        """Update a task"""
        task = TaskService.get_task(db, user_id, task_id)

        # Validate selector if provided
        if task_data.selector and task_data.selector_type:
            TaskService._validate_selector(task_data.selector, task_data.selector_type)

        # Validate fetcher config if fetcher type changed
        if task_data.fetcher_type:
            TaskService._validate_fetcher_config(task_data)

        # Update fields
        update_data = task_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(task, field, value)

        task.updated_at = datetime.now(timezone.utc)

        db.commit()
        db.refresh(task)
        return task

    @staticmethod
    def delete_task(db: Session, user_id: UUID, task_id: UUID) -> None:
        """Delete a task"""
        task = TaskService.get_task(db, user_id, task_id)

        db.delete(task)
        db.commit()

    @staticmethod
    def clone_task(db: Session, user_id: UUID, task_id: UUID) -> Task:
        """Clone a task"""
        original_task = TaskService.get_task(db, user_id, task_id)

        # Create new task with same configuration
        new_task = Task(
            user_id=user_id,
            name=f"{original_task.name} (Copy)",
            description=original_task.description,
            target_url=original_task.target_url,
            fetcher_type=original_task.fetcher_type,
            selector=original_task.selector,
            selector_type=original_task.selector_type,
            timeout=original_task.timeout,
            retry_count=original_task.retry_count,
            use_proxy_rotation=original_task.use_proxy_rotation,
            solve_cloudflare=original_task.solve_cloudflare,
            custom_headers=original_task.custom_headers,
            cookies=original_task.cookies,
            wait_time=original_task.wait_time,
            viewport_width=original_task.viewport_width,
            viewport_height=original_task.viewport_height,
            status=TaskStatus.DRAFT,
        )

        db.add(new_task)
        db.commit()
        db.refresh(new_task)
        return new_task

    @staticmethod
    def _validate_selector(selector: str, selector_type: SelectorType) -> None:
        """Validate selector syntax"""
        if not selector:
            raise ValidationError("Selector cannot be empty")

        if selector_type == SelectorType.CSS:
            # Basic CSS selector validation
            if selector.startswith(" ") or selector.endswith(" "):
                raise ValidationError("CSS selector cannot start or end with space")
            # Check for invalid characters
            if "[[" in selector or "]]" in selector:
                raise ValidationError("Invalid CSS selector syntax")

        elif selector_type == SelectorType.XPATH:
            # Basic XPath validation
            if not (selector.startswith("/") or selector.startswith(".")):
                raise ValidationError("XPath must start with / or .")
            # Check for balanced brackets
            if selector.count("[") != selector.count("]"):
                raise ValidationError("XPath has unbalanced brackets")

    @staticmethod
    def rerun_task(db: Session, user_id: UUID, task_id: UUID) -> Task:
        """Rerun a task with existing configuration"""
        original_task = TaskService.get_task(db, user_id, task_id)

        # Create new task with same configuration
        new_task = Task(
            user_id=user_id,
            name=original_task.name,
            description=original_task.description,
            target_url=original_task.target_url,
            fetcher_type=original_task.fetcher_type,
            selector=original_task.selector,
            selector_type=original_task.selector_type,
            timeout=original_task.timeout,
            retry_count=original_task.retry_count,
            use_proxy_rotation=original_task.use_proxy_rotation,
            solve_cloudflare=original_task.solve_cloudflare,
            custom_headers=original_task.custom_headers,
            cookies=original_task.cookies,
            wait_time=original_task.wait_time,
            viewport_width=original_task.viewport_width,
            viewport_height=original_task.viewport_height,
            status=TaskStatus.DRAFT,
        )

        db.add(new_task)
        db.commit()
        db.refresh(new_task)
        return new_task

    @staticmethod
    def _validate_selector(selector: str, selector_type: SelectorType) -> None:
        """Validate selector syntax"""
        if not selector:
            raise ValidationError("Selector cannot be empty")

        if selector_type == SelectorType.CSS:
            # Basic CSS selector validation
            if selector.startswith(" ") or selector.endswith(" "):
                raise ValidationError("CSS selector cannot start or end with space")
            # Check for invalid characters
            if "[[" in selector or "]]" in selector:
                raise ValidationError("Invalid CSS selector syntax")

        elif selector_type == SelectorType.XPATH:
            # Basic XPath validation
            if not (selector.startswith("/") or selector.startswith(".")):
                raise ValidationError("XPath must start with / or .")
            # Check for balanced brackets
            if selector.count("[") != selector.count("]"):
                raise ValidationError("XPath has unbalanced brackets")

    @staticmethod
    def _validate_fetcher_config(task_data) -> None:
        """Validate fetcher-specific configuration"""
        if hasattr(task_data, "fetcher_type"):
            fetcher_type = task_data.fetcher_type
        else:
            return

        if fetcher_type == FetcherType.DYNAMIC:
            # Dynamic fetcher requires wait_time
            if hasattr(task_data, "wait_time") and task_data.wait_time is not None:
                if task_data.wait_time < 0 or task_data.wait_time > 60:
                    raise ValidationError("Wait time must be between 0 and 60 seconds")

        elif fetcher_type == FetcherType.STEALTHY:
            # Stealthy fetcher can have solve_cloudflare option
            pass

        # HTTP fetcher has no special requirements
