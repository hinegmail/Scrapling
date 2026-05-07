"""Celery tasks"""

from app.tasks.scrapling_tasks import execute_scraping_task

__all__ = ["execute_scraping_task"]
