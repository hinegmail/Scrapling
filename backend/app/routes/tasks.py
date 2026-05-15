"""Task routes"""

import logging
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.task import TaskStatus
from app.schemas.task import TaskCreate, TaskUpdate, TaskResponse, TaskListResponse
from app.services.task import TaskService
from app.middleware.auth import get_current_user
from app.exceptions import NotFoundError, ValidationError, AuthorizationError

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/tasks", tags=["tasks"])


@router.post("", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(
    task_data: TaskCreate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Create a new task.
    
    - **name**: Task name (required)
    - **target_url**: Target URL to scrape (required)
    - **selector**: CSS or XPath selector (required)
    - **fetcher_type**: http, dynamic, or stealthy (required)
    - **selector_type**: css or xpath (required)
    """
    try:
        task = TaskService.create_task(db, current_user["id"], task_data)
        logger.info(f"Task created: {task.id} by user {current_user['id']}")
        return task
    except ValidationError as e:
        logger.warning(f"Validation error creating task: {str(e)}")
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))
    except Exception as e:
        logger.error(f"Error creating task: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to create task")


@router.get("", response_model=TaskListResponse)
async def list_tasks(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    status: Optional[TaskStatus] = Query(None),
    search: Optional[str] = Query(None),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get tasks with pagination and filtering.
    
    - **page**: Page number (default: 1)
    - **page_size**: Items per page (default: 10, max: 100)
    - **status**: Filter by task status (optional)
    - **search**: Search by name or description (optional)
    """
    try:
        tasks, total = TaskService.get_tasks(
            db, current_user["id"], page, page_size, status, search
        )
        total_pages = (total + page_size - 1) // page_size
        
        return TaskListResponse(
            items=tasks,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
        )
    except Exception as e:
        logger.error(f"Error listing tasks: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to list tasks")


@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(
    task_id: UUID,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get a specific task by ID"""
    try:
        task = TaskService.get_task(db, current_user["id"], task_id)
        return task
    except NotFoundError as e:
        logger.warning(f"Task not found: {task_id}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        logger.error(f"Error getting task: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to get task")


@router.put("/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: UUID,
    task_data: TaskUpdate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update a task configuration"""
    try:
        task = TaskService.update_task(db, current_user["id"], task_id, task_data)
        logger.info(f"Task updated: {task_id}")
        return task
    except NotFoundError as e:
        logger.warning(f"Task not found: {task_id}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ValidationError as e:
        logger.warning(f"Validation error updating task: {str(e)}")
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))
    except Exception as e:
        logger.error(f"Error updating task: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to update task")


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    task_id: UUID,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Delete a task and its associated results"""
    try:
        TaskService.delete_task(db, current_user["id"], task_id)
        logger.info(f"Task deleted: {task_id}")
        return None
    except NotFoundError as e:
        logger.warning(f"Task not found: {task_id}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        logger.error(f"Error deleting task: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to delete task")


@router.post("/{task_id}/clone", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def clone_task(
    task_id: UUID,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Clone an existing task"""
    try:
        task = TaskService.clone_task(db, current_user["id"], task_id)
        logger.info(f"Task cloned: {task_id} -> {task.id}")
        return task
    except NotFoundError as e:
        logger.warning(f"Task not found: {task_id}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        logger.error(f"Error cloning task: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to clone task")



@router.post("/{task_id}/rerun", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def rerun_task(
    task_id: UUID,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Rerun an existing task with the same configuration"""
    try:
        task = TaskService.rerun_task(db, current_user["id"], task_id)
        logger.info(f"Task rerun: {task_id} -> {task.id}")
        return task
    except NotFoundError as e:
        logger.warning(f"Task not found: {task_id}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        logger.error(f"Error rerunning task: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to rerun task")


@router.get("/history", response_model=TaskListResponse)
async def get_task_history(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    status: Optional[TaskStatus] = Query(None),
    search: Optional[str] = Query(None),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get task history with pagination and filtering.
    
    - **page**: Page number (default: 1)
    - **page_size**: Items per page (default: 10, max: 100)
    - **status**: Filter by task status (optional)
    - **search**: Search by name or description (optional)
    """
    try:
        tasks, total = TaskService.get_tasks(
            db, current_user["id"], page, page_size, status, search
        )
        total_pages = (total + page_size - 1) // page_size
        
        return TaskListResponse(
            items=tasks,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
        )
    except Exception as e:
        logger.error(f"Error getting task history: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to get task history")
