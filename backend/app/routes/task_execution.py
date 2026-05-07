"""Task execution routes"""

import logging
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.middleware.auth import get_current_user
from app.models.task import Task, TaskStatus
from app.services.task import TaskService
from app.tasks.scrapling_tasks import execute_scraping_task
from app.exceptions import NotFoundError, ValidationError

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/tasks", tags=["task-execution"])


class TaskExecutionResponse(BaseModel):
    """Task execution response"""
    task_id: UUID
    status: str
    message: str


@router.post("/{task_id}/run", response_model=TaskExecutionResponse)
async def run_task(
    task_id: UUID,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Start executing a task.
    
    - **task_id**: Task ID to execute
    """
    try:
        # Get task
        task = TaskService.get_task(db, current_user["id"], task_id)
        
        # Check if task is already running
        if task.status == TaskStatus.RUNNING:
            raise ValidationError("Task is already running")
        
        # Update task status
        task.status = TaskStatus.RUNNING
        db.commit()
        
        # Queue task for execution
        celery_task = execute_scraping_task.delay(str(task_id))
        
        logger.info(f"Task execution started: {task_id}, celery_task_id: {celery_task.id}")
        
        return TaskExecutionResponse(
            task_id=task_id,
            status="running",
            message="Task execution started",
        )
    except NotFoundError as e:
        logger.warning(f"Task not found: {task_id}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ValidationError as e:
        logger.warning(f"Validation error: {str(e)}")
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))
    except Exception as e:
        logger.error(f"Error running task: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to run task")


@router.post("/{task_id}/pause", response_model=TaskExecutionResponse)
async def pause_task(
    task_id: UUID,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Pause a running task.
    
    - **task_id**: Task ID to pause
    """
    try:
        # Get task
        task = TaskService.get_task(db, current_user["id"], task_id)
        
        # Check if task is running
        if task.status != TaskStatus.RUNNING:
            raise ValidationError("Task is not running")
        
        # Update task status
        task.status = TaskStatus.PAUSED
        db.commit()
        
        logger.info(f"Task paused: {task_id}")
        
        return TaskExecutionResponse(
            task_id=task_id,
            status="paused",
            message="Task paused",
        )
    except NotFoundError as e:
        logger.warning(f"Task not found: {task_id}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ValidationError as e:
        logger.warning(f"Validation error: {str(e)}")
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))
    except Exception as e:
        logger.error(f"Error pausing task: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to pause task")


@router.post("/{task_id}/resume", response_model=TaskExecutionResponse)
async def resume_task(
    task_id: UUID,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Resume a paused task.
    
    - **task_id**: Task ID to resume
    """
    try:
        # Get task
        task = TaskService.get_task(db, current_user["id"], task_id)
        
        # Check if task is paused
        if task.status != TaskStatus.PAUSED:
            raise ValidationError("Task is not paused")
        
        # Update task status
        task.status = TaskStatus.RUNNING
        db.commit()
        
        # Queue task for execution
        celery_task = execute_scraping_task.delay(str(task_id))
        
        logger.info(f"Task resumed: {task_id}, celery_task_id: {celery_task.id}")
        
        return TaskExecutionResponse(
            task_id=task_id,
            status="running",
            message="Task resumed",
        )
    except NotFoundError as e:
        logger.warning(f"Task not found: {task_id}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ValidationError as e:
        logger.warning(f"Validation error: {str(e)}")
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))
    except Exception as e:
        logger.error(f"Error resuming task: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to resume task")


@router.post("/{task_id}/stop", response_model=TaskExecutionResponse)
async def stop_task(
    task_id: UUID,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Stop a running or paused task.
    
    - **task_id**: Task ID to stop
    """
    try:
        # Get task
        task = TaskService.get_task(db, current_user["id"], task_id)
        
        # Check if task is running or paused
        if task.status not in [TaskStatus.RUNNING, TaskStatus.PAUSED]:
            raise ValidationError("Task is not running or paused")
        
        # Update task status
        task.status = TaskStatus.STOPPED
        db.commit()
        
        logger.info(f"Task stopped: {task_id}")
        
        return TaskExecutionResponse(
            task_id=task_id,
            status="stopped",
            message="Task stopped",
        )
    except NotFoundError as e:
        logger.warning(f"Task not found: {task_id}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ValidationError as e:
        logger.warning(f"Validation error: {str(e)}")
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))
    except Exception as e:
        logger.error(f"Error stopping task: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to stop task")
