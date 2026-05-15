"""Dashboard service for statistics and monitoring"""

from datetime import datetime, timedelta, timezone
from typing import Optional
from uuid import UUID

from sqlalchemy import and_, func
from sqlalchemy.orm import Session

from app.models.task import Task, TaskStatus, FetcherType
from app.models.result import Result
from app.exceptions import NotFoundError


class DashboardService:
    """Service for dashboard statistics and monitoring"""

    @staticmethod
    def get_statistics(db: Session, user_id: UUID) -> dict:
        """
        Get dashboard statistics for a user.
        
        Returns:
            dict: Statistics including total tasks, monthly tasks, success rate, total data
        """
        # Get total tasks
        total_tasks = db.query(func.count(Task.id)).filter(
            Task.user_id == user_id
        ).scalar() or 0

        # Get tasks from current month
        now = datetime.now(timezone.utc)
        month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        monthly_tasks = db.query(func.count(Task.id)).filter(
            and_(
                Task.user_id == user_id,
                Task.created_at >= month_start
            )
        ).scalar() or 0

        # Get success rate
        total_runs = db.query(func.sum(Task.total_runs)).filter(
            Task.user_id == user_id
        ).scalar() or 0
        
        total_success = db.query(func.sum(Task.success_count)).filter(
            Task.user_id == user_id
        ).scalar() or 0
        
        success_rate = (total_success / total_runs * 100) if total_runs > 0 else 0

        # Get total extracted data (count of results)
        total_data_count = db.query(func.count(Result.id)).join(
            Task, Result.task_id == Task.id
        ).filter(Task.user_id == user_id).scalar() or 0

        # Get total data size (estimate based on JSON data)
        total_data_size = db.query(func.sum(func.length(func.cast(Result.data, str)))).join(
            Task, Result.task_id == Task.id
        ).filter(Task.user_id == user_id).scalar() or 0

        return {
            "total_tasks": total_tasks,
            "monthly_tasks": monthly_tasks,
            "success_rate": round(success_rate, 2),
            "total_data_count": total_data_count,
            "total_data_size_bytes": total_data_size or 0,
            "total_runs": total_runs,
            "total_success": total_success,
            "total_errors": db.query(func.sum(Task.error_count)).filter(
                Task.user_id == user_id
            ).scalar() or 0,
        }

    @staticmethod
    def get_trends(db: Session, user_id: UUID, days: int = 7) -> list[dict]:
        """
        Get task execution trends for the last N days.
        
        Args:
            db: Database session
            user_id: User ID
            days: Number of days to retrieve (default 7)
            
        Returns:
            list: Daily trend data with task counts and success rates
        """
        trends = []
        now = datetime.now(timezone.utc)
        
        for i in range(days - 1, -1, -1):
            day_start = (now - timedelta(days=i)).replace(
                hour=0, minute=0, second=0, microsecond=0
            )
            day_end = day_start + timedelta(days=1)
            
            # Get tasks completed on this day
            completed_tasks = db.query(Task).filter(
                and_(
                    Task.user_id == user_id,
                    Task.status == TaskStatus.COMPLETED,
                    Task.updated_at >= day_start,
                    Task.updated_at < day_end
                )
            ).all()
            
            # Calculate daily statistics
            daily_total_runs = sum(task.total_runs for task in completed_tasks)
            daily_success = sum(task.success_count for task in completed_tasks)
            daily_errors = sum(task.error_count for task in completed_tasks)
            
            daily_success_rate = (
                (daily_success / daily_total_runs * 100) 
                if daily_total_runs > 0 else 0
            )
            
            # Get daily result count
            daily_results = db.query(func.count(Result.id)).join(
                Task, Result.task_id == Task.id
            ).filter(
                and_(
                    Task.user_id == user_id,
                    Result.extracted_at >= day_start,
                    Result.extracted_at < day_end
                )
            ).scalar() or 0
            
            trends.append({
                "date": day_start.isoformat(),
                "task_count": len(completed_tasks),
                "total_runs": daily_total_runs,
                "success_count": daily_success,
                "error_count": daily_errors,
                "success_rate": round(daily_success_rate, 2),
                "result_count": daily_results,
            })
        
        return trends

    @staticmethod
    def get_fetcher_stats(db: Session, user_id: UUID) -> dict:
        """
        Get statistics about fetcher usage.
        
        Returns:
            dict: Fetcher type usage statistics
        """
        fetcher_stats = {}
        
        for fetcher_type in FetcherType:
            count = db.query(func.count(Task.id)).filter(
                and_(
                    Task.user_id == user_id,
                    Task.fetcher_type == fetcher_type
                )
            ).scalar() or 0
            
            # Get success rate for this fetcher type
            total_runs = db.query(func.sum(Task.total_runs)).filter(
                and_(
                    Task.user_id == user_id,
                    Task.fetcher_type == fetcher_type
                )
            ).scalar() or 0
            
            total_success = db.query(func.sum(Task.success_count)).filter(
                and_(
                    Task.user_id == user_id,
                    Task.fetcher_type == fetcher_type
                )
            ).scalar() or 0
            
            success_rate = (
                (total_success / total_runs * 100) 
                if total_runs > 0 else 0
            )
            
            fetcher_stats[fetcher_type.value] = {
                "count": count,
                "total_runs": total_runs,
                "success_count": total_success,
                "success_rate": round(success_rate, 2),
            }
        
        return fetcher_stats

    @staticmethod
    def get_resource_stats(db: Session, user_id: UUID) -> dict:
        """
        Get system resource usage statistics.
        
        Note: This is a placeholder for actual system monitoring.
        In production, this would integrate with system monitoring tools.
        
        Returns:
            dict: Resource usage statistics
        """
        import psutil
        
        # Get CPU usage
        cpu_percent = psutil.cpu_percent(interval=1)
        
        # Get memory usage
        memory = psutil.virtual_memory()
        memory_percent = memory.percent
        memory_used_mb = memory.used / (1024 * 1024)
        memory_total_mb = memory.total / (1024 * 1024)
        
        # Get disk usage
        disk = psutil.disk_usage('/')
        disk_percent = disk.percent
        disk_used_gb = disk.used / (1024 * 1024 * 1024)
        disk_total_gb = disk.total / (1024 * 1024 * 1024)
        
        # Get network stats
        net_io = psutil.net_io_counters()
        
        return {
            "cpu": {
                "percent": round(cpu_percent, 2),
            },
            "memory": {
                "percent": round(memory_percent, 2),
                "used_mb": round(memory_used_mb, 2),
                "total_mb": round(memory_total_mb, 2),
            },
            "disk": {
                "percent": round(disk_percent, 2),
                "used_gb": round(disk_used_gb, 2),
                "total_gb": round(disk_total_gb, 2),
            },
            "network": {
                "bytes_sent": net_io.bytes_sent,
                "bytes_recv": net_io.bytes_recv,
                "packets_sent": net_io.packets_sent,
                "packets_recv": net_io.packets_recv,
            },
        }
