"""Scrapling task execution"""

import logging
from typing import Optional
from uuid import UUID

from celery import Task
from sqlalchemy.orm import Session

from app.celery_app import celery_app
from app.db.database import SessionLocal
from app.models.task import Task as TaskModel, TaskStatus, FetcherType
from app.models.result import Result
from app.models.task_log import TaskLog
from app.exceptions import NotFoundError

logger = logging.getLogger(__name__)


class ScraplingTask(Task):
    """Base Celery task with database session"""

    def __call__(self, *args, **kwargs):
        """Execute task with database session"""
        with SessionLocal() as db:
            return self.run(*args, db=db, **kwargs)


@celery_app.task(base=ScraplingTask, bind=True, name="execute_scraping_task")
def execute_scraping_task(
    self,
    task_id: str,
    db: Optional[Session] = None,
) -> dict:
    """
    Execute a scraping task.
    
    Args:
        task_id: Task ID to execute
        db: Database session
        
    Returns:
        dict: Task execution result
    """
    if db is None:
        db = SessionLocal()
    
    try:
        # Get task from database
        task = db.query(TaskModel).filter(TaskModel.id == UUID(task_id)).first()
        if not task:
            logger.error(f"Task not found: {task_id}")
            return {"status": "failed", "error": "Task not found"}
        
        # Update task status
        task.status = TaskStatus.RUNNING
        db.commit()
        
        logger.info(f"Starting task execution: {task_id}")
        
        # Execute scraping based on fetcher type
        try:
            if task.fetcher_type == FetcherType.HTTP:
                result = _execute_http_fetch(task, db, self)
            elif task.fetcher_type == FetcherType.DYNAMIC:
                result = _execute_dynamic_fetch(task, db, self)
            elif task.fetcher_type == FetcherType.STEALTHY:
                result = _execute_stealthy_fetch(task, db, self)
            else:
                raise ValueError(f"Unknown fetcher type: {task.fetcher_type}")
            
            # Update task status
            task.status = TaskStatus.COMPLETED
            task.total_runs += 1
            task.success_count += 1
            db.commit()
            
            logger.info(f"Task completed successfully: {task_id}")
            return {"status": "completed", "results_count": len(result)}
            
        except Exception as e:
            logger.error(f"Error executing task: {str(e)}")
            task.status = TaskStatus.FAILED
            task.total_runs += 1
            task.error_count += 1
            
            # Log error
            error_log = TaskLog(
                task_id=task.id,
                level="ERROR",
                message=f"Task execution failed: {str(e)}",
            )
            db.add(error_log)
            db.commit()
            
            return {"status": "failed", "error": str(e)}
    
    except Exception as e:
        logger.error(f"Unexpected error in execute_scraping_task: {str(e)}")
        return {"status": "failed", "error": str(e)}


def _execute_http_fetch(task: TaskModel, db: Session, celery_task: Task) -> list:
    """
    Execute HTTP fetch.
    
    Args:
        task: Task model
        db: Database session
        celery_task: Celery task instance
        
    Returns:
        list: Extracted results
    """
    logger.info(f"Executing HTTP fetch for task: {task.id}")
    
    try:
        from scrapling import Fetcher
        
        # Create fetcher
        fetcher = Fetcher(
            timeout=task.timeout,
            retries=task.retry_count,
        )
        
        # Add custom headers if provided
        if task.custom_headers:
            fetcher.headers.update(task.custom_headers)
        
        # Fetch content
        response = fetcher.fetch(task.target_url)
        
        # Parse content
        selector = response.select(task.selector)
        results = []
        
        for i, element in enumerate(selector):
            result = Result(
                task_id=task.id,
                data={"text": element.get_text()},
                source_url=task.target_url,
            )
            db.add(result)
            results.append(result)
            
            # Update progress
            celery_task.update_state(
                state="PROGRESS",
                meta={
                    "current": i + 1,
                    "total": len(selector),
                    "status": f"Processing {i + 1}/{len(selector)}",
                },
            )
        
        db.commit()
        logger.info(f"HTTP fetch completed: {len(results)} results")
        return results
        
    except Exception as e:
        logger.error(f"Error in HTTP fetch: {str(e)}")
        raise


def _execute_dynamic_fetch(task: TaskModel, db: Session, celery_task: Task) -> list:
    """
    Execute dynamic fetch with browser automation.
    
    Args:
        task: Task model
        db: Database session
        celery_task: Celery task instance
        
    Returns:
        list: Extracted results
    """
    logger.info(f"Executing dynamic fetch for task: {task.id}")
    
    try:
        from scrapling import DynamicFetcher
        
        # Create fetcher
        fetcher = DynamicFetcher(
            timeout=task.timeout,
            retries=task.retry_count,
        )
        
        # Set viewport if provided
        if task.viewport_width and task.viewport_height:
            fetcher.viewport = (task.viewport_width, task.viewport_height)
        
        # Set wait time if provided
        wait_time = task.wait_time or 0
        
        # Fetch content
        response = fetcher.fetch(task.target_url, wait_time=wait_time)
        
        # Parse content
        selector = response.select(task.selector)
        results = []
        
        for i, element in enumerate(selector):
            result = Result(
                task_id=task.id,
                data={"text": element.get_text()},
                source_url=task.target_url,
            )
            db.add(result)
            results.append(result)
            
            # Update progress
            celery_task.update_state(
                state="PROGRESS",
                meta={
                    "current": i + 1,
                    "total": len(selector),
                    "status": f"Processing {i + 1}/{len(selector)}",
                },
            )
        
        db.commit()
        logger.info(f"Dynamic fetch completed: {len(results)} results")
        return results
        
    except Exception as e:
        logger.error(f"Error in dynamic fetch: {str(e)}")
        raise


def _execute_stealthy_fetch(task: TaskModel, db: Session, celery_task: Task) -> list:
    """
    Execute stealthy fetch with anti-detection.
    
    Args:
        task: Task model
        db: Database session
        celery_task: Celery task instance
        
    Returns:
        list: Extracted results
    """
    logger.info(f"Executing stealthy fetch for task: {task.id}")
    
    try:
        from scrapling import StealthyFetcher
        
        # Create fetcher
        fetcher = StealthyFetcher(
            timeout=task.timeout,
            retries=task.retry_count,
            solve_cloudflare=task.solve_cloudflare,
        )
        
        # Add custom headers if provided
        if task.custom_headers:
            fetcher.headers.update(task.custom_headers)
        
        # Fetch content
        response = fetcher.fetch(task.target_url)
        
        # Parse content
        selector = response.select(task.selector)
        results = []
        
        for i, element in enumerate(selector):
            result = Result(
                task_id=task.id,
                data={"text": element.get_text()},
                source_url=task.target_url,
            )
            db.add(result)
            results.append(result)
            
            # Update progress
            celery_task.update_state(
                state="PROGRESS",
                meta={
                    "current": i + 1,
                    "total": len(selector),
                    "status": f"Processing {i + 1}/{len(selector)}",
                },
            )
        
        db.commit()
        logger.info(f"Stealthy fetch completed: {len(results)} results")
        return results
        
    except Exception as e:
        logger.error(f"Error in stealthy fetch: {str(e)}")
        raise
