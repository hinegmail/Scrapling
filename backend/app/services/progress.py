"""Progress tracking service"""

import logging
from datetime import datetime, timezone
from typing import Optional
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.task import Task
from app.models.task_log import TaskLog
from app.websocket_manager import manager

logger = logging.getLogger(__name__)


class ProgressService:
    """Service for tracking and broadcasting task progress"""

    @staticmethod
    async def update_progress(
        db: Session,
        task_id: UUID,
        processed_count: int,
        total_count: int,
        success_count: int,
        error_count: int,
        current_url: str,
        elapsed_time: int,
        estimated_remaining: int,
    ):
        """
        Update task progress and broadcast to WebSocket clients.
        
        Args:
            db: Database session
            task_id: Task ID
            processed_count: Number of items processed
            total_count: Total number of items
            success_count: Number of successful items
            error_count: Number of failed items
            current_url: Current URL being processed
            elapsed_time: Elapsed time in seconds
            estimated_remaining: Estimated remaining time in seconds
        """
        try:
            # Get task
            task = db.query(Task).filter(Task.id == task_id).first()
            if not task:
                logger.warning(f"Task not found for progress update: {task_id}")
                return
            
            # Prepare progress message
            message = {
                "type": "task_progress",
                "task_id": str(task_id),
                "processed_count": processed_count,
                "total_count": total_count,
                "success_count": success_count,
                "error_count": error_count,
                "current_url": current_url,
                "elapsed_time": elapsed_time,
                "estimated_remaining": estimated_remaining,
                "progress_percentage": int((processed_count / total_count * 100) if total_count > 0 else 0),
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
            
            # Broadcast to WebSocket clients
            await manager.broadcast_task_update(task_id, message)
            
            logger.debug(f"Progress updated for task {task_id}: {processed_count}/{total_count}")
            
        except Exception as e:
            logger.error(f"Error updating progress: {str(e)}")

    @staticmethod
    async def log_message(
        db: Session,
        task_id: UUID,
        level: str,
        message: str,
    ):
        """
        Log a message and broadcast to WebSocket clients.
        
        Args:
            db: Database session
            task_id: Task ID
            level: Log level (DEBUG, INFO, WARNING, ERROR)
            message: Log message
        """
        try:
            # Create log entry
            task_log = TaskLog(
                task_id=task_id,
                level=level,
                message=message,
            )
            db.add(task_log)
            db.commit()
            
            # Prepare log message
            log_message = {
                "type": "task_log",
                "task_id": str(task_id),
                "level": level,
                "message": message,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
            
            # Broadcast to WebSocket clients
            await manager.broadcast_task_update(task_id, log_message)
            
            logger.debug(f"Log message for task {task_id}: [{level}] {message}")
            
        except Exception as e:
            logger.error(f"Error logging message: {str(e)}")

    @staticmethod
    async def task_started(db: Session, task_id: UUID):
        """
        Notify that task has started.
        
        Args:
            db: Database session
            task_id: Task ID
        """
        try:
            message = {
                "type": "task_started",
                "task_id": str(task_id),
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
            
            await manager.broadcast_task_update(task_id, message)
            logger.info(f"Task started: {task_id}")
            
        except Exception as e:
            logger.error(f"Error notifying task start: {str(e)}")

    @staticmethod
    async def task_completed(
        db: Session,
        task_id: UUID,
        status: str,
        total_time: int,
        results_count: int,
        error_message: Optional[str] = None,
    ):
        """
        Notify that task has completed.
        
        Args:
            db: Database session
            task_id: Task ID
            status: Completion status (success, failed, stopped)
            total_time: Total execution time in seconds
            results_count: Number of results collected
            error_message: Error message if failed
        """
        try:
            message = {
                "type": "task_completed",
                "task_id": str(task_id),
                "status": status,
                "total_time": total_time,
                "results_count": results_count,
                "error_message": error_message,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
            
            await manager.broadcast_task_update(task_id, message)
            logger.info(f"Task completed: {task_id} - status={status}")
            
        except Exception as e:
            logger.error(f"Error notifying task completion: {str(e)}")

    @staticmethod
    async def task_paused(db: Session, task_id: UUID):
        """
        Notify that task has been paused.
        
        Args:
            db: Database session
            task_id: Task ID
        """
        try:
            message = {
                "type": "task_paused",
                "task_id": str(task_id),
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
            
            await manager.broadcast_task_update(task_id, message)
            logger.info(f"Task paused: {task_id}")
            
        except Exception as e:
            logger.error(f"Error notifying task pause: {str(e)}")

    @staticmethod
    async def task_resumed(db: Session, task_id: UUID):
        """
        Notify that task has been resumed.
        
        Args:
            db: Database session
            task_id: Task ID
        """
        try:
            message = {
                "type": "task_resumed",
                "task_id": str(task_id),
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
            
            await manager.broadcast_task_update(task_id, message)
            logger.info(f"Task resumed: {task_id}")
            
        except Exception as e:
            logger.error(f"Error notifying task resume: {str(e)}")

    @staticmethod
    async def task_stopped(db: Session, task_id: UUID):
        """
        Notify that task has been stopped.
        
        Args:
            db: Database session
            task_id: Task ID
        """
        try:
            message = {
                "type": "task_stopped",
                "task_id": str(task_id),
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
            
            await manager.broadcast_task_update(task_id, message)
            logger.info(f"Task stopped: {task_id}")
            
        except Exception as e:
            logger.error(f"Error notifying task stop: {str(e)}")
