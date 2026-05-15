"""Tests for dashboard statistics and monitoring"""

import pytest
from datetime import datetime, timedelta, timezone

from app.services.dashboard import DashboardService
from app.models.task import Task, TaskStatus, FetcherType
from app.models.result import Result


class TestDashboardService:
    """Test dashboard service"""

    def test_get_statistics(self, db_session, test_user):
        """Test getting dashboard statistics"""
        # Create test tasks
        for i in range(5):
            task = Task(
                user_id=test_user.id,
                name=f"Test Task {i}",
                target_url="https://example.com",
                fetcher_type=FetcherType.HTTP,
                selector="div.content",
                status=TaskStatus.COMPLETED,
                total_runs=10,
                success_count=8,
                error_count=2,
            )
            db_session.add(task)
        
        db_session.commit()
        
        stats = DashboardService.get_statistics(db_session, test_user.id)
        
        assert stats["total_tasks"] == 5
        assert stats["total_runs"] == 50
        assert stats["total_success"] == 40
        assert stats["total_errors"] == 10
        assert stats["success_rate"] == 80.0

    def test_get_statistics_empty(self, db_session, test_user):
        """Test getting statistics for user with no tasks"""
        stats = DashboardService.get_statistics(db_session, test_user.id)
        
        assert stats["total_tasks"] == 0
        assert stats["monthly_tasks"] == 0
        assert stats["success_rate"] == 0
        assert stats["total_data_count"] == 0

    def test_get_trends(self, db_session, test_user):
        """Test getting task execution trends"""
        # Create tasks for different days
        now = datetime.now(timezone.utc)
        
        for day_offset in range(7):
            task_date = now - timedelta(days=day_offset)
            task = Task(
                user_id=test_user.id,
                name=f"Test Task {day_offset}",
                target_url="https://example.com",
                fetcher_type=FetcherType.HTTP,
                selector="div.content",
                status=TaskStatus.COMPLETED,
                total_runs=10,
                success_count=8,
                error_count=2,
                created_at=task_date,
                updated_at=task_date,
            )
            db_session.add(task)
        
        db_session.commit()
        
        trends = DashboardService.get_trends(db_session, test_user.id, days=7)
        
        assert len(trends) == 7
        # Check that each day has data
        for trend in trends:
            assert "date" in trend
            assert "task_count" in trend
            assert "success_rate" in trend

    def test_get_trends_custom_days(self, db_session, test_user):
        """Test getting trends for custom number of days"""
        trends = DashboardService.get_trends(db_session, test_user.id, days=14)
        assert len(trends) == 14

    def test_get_fetcher_stats(self, db_session, test_user):
        """Test getting fetcher usage statistics"""
        # Create tasks with different fetcher types
        for fetcher_type in FetcherType:
            for i in range(3):
                task = Task(
                    user_id=test_user.id,
                    name=f"Test Task {fetcher_type.value} {i}",
                    target_url="https://example.com",
                    fetcher_type=fetcher_type,
                    selector="div.content",
                    status=TaskStatus.COMPLETED,
                    total_runs=10,
                    success_count=8,
                    error_count=2,
                )
                db_session.add(task)
        
        db_session.commit()
        
        stats = DashboardService.get_fetcher_stats(db_session, test_user.id)
        
        # Check that all fetcher types are present
        for fetcher_type in FetcherType:
            assert fetcher_type.value in stats
            assert stats[fetcher_type.value]["count"] == 3
            assert stats[fetcher_type.value]["success_rate"] == 80.0

    def test_get_fetcher_stats_empty(self, db_session, test_user):
        """Test getting fetcher stats for user with no tasks"""
        stats = DashboardService.get_fetcher_stats(db_session, test_user.id)
        
        # All fetcher types should be present with 0 count
        for fetcher_type in FetcherType:
            assert fetcher_type.value in stats
            assert stats[fetcher_type.value]["count"] == 0

    def test_get_resource_stats(self, db_session, test_user):
        """Test getting system resource statistics"""
        stats = DashboardService.get_resource_stats(db_session, test_user.id)
        
        # Check that all resource metrics are present
        assert "cpu" in stats
        assert "memory" in stats
        assert "disk" in stats
        assert "network" in stats
        
        # Check CPU stats
        assert "percent" in stats["cpu"]
        assert 0 <= stats["cpu"]["percent"] <= 100
        
        # Check memory stats
        assert "percent" in stats["memory"]
        assert "used_mb" in stats["memory"]
        assert "total_mb" in stats["memory"]
        
        # Check disk stats
        assert "percent" in stats["disk"]
        assert "used_gb" in stats["disk"]
        assert "total_gb" in stats["disk"]
        
        # Check network stats
        assert "bytes_sent" in stats["network"]
        assert "bytes_recv" in stats["network"]

    def test_monthly_tasks_count(self, db_session, test_user):
        """Test counting tasks from current month"""
        now = datetime.now(timezone.utc)
        
        # Create task in current month
        current_month_task = Task(
            user_id=test_user.id,
            name="Current Month Task",
            target_url="https://example.com",
            fetcher_type=FetcherType.HTTP,
            selector="div.content",
            status=TaskStatus.COMPLETED,
            total_runs=10,
            success_count=8,
            error_count=2,
            created_at=now,
        )
        db_session.add(current_month_task)
        
        # Create task in previous month
        previous_month = now - timedelta(days=35)
        previous_month_task = Task(
            user_id=test_user.id,
            name="Previous Month Task",
            target_url="https://example.com",
            fetcher_type=FetcherType.HTTP,
            selector="div.content",
            status=TaskStatus.COMPLETED,
            total_runs=10,
            success_count=8,
            error_count=2,
            created_at=previous_month,
        )
        db_session.add(previous_month_task)
        
        db_session.commit()
        
        stats = DashboardService.get_statistics(db_session, test_user.id)
        
        assert stats["total_tasks"] == 2
        assert stats["monthly_tasks"] == 1

    def test_success_rate_calculation(self, db_session, test_user):
        """Test success rate calculation"""
        # Create task with 50% success rate
        task = Task(
            user_id=test_user.id,
            name="Test Task",
            target_url="https://example.com",
            fetcher_type=FetcherType.HTTP,
            selector="div.content",
            status=TaskStatus.COMPLETED,
            total_runs=100,
            success_count=50,
            error_count=50,
        )
        db_session.add(task)
        db_session.commit()
        
        stats = DashboardService.get_statistics(db_session, test_user.id)
        
        assert stats["success_rate"] == 50.0

    def test_data_count_calculation(self, db_session, test_user):
        """Test total data count calculation"""
        # Create task with results
        task = Task(
            user_id=test_user.id,
            name="Test Task",
            target_url="https://example.com",
            fetcher_type=FetcherType.HTTP,
            selector="div.content",
            status=TaskStatus.COMPLETED,
        )
        db_session.add(task)
        db_session.flush()
        
        # Create results
        for i in range(10):
            result = Result(
                task_id=task.id,
                data={"index": i, "content": "test data"},
                source_url="https://example.com",
            )
            db_session.add(result)
        
        db_session.commit()
        
        stats = DashboardService.get_statistics(db_session, test_user.id)
        
        assert stats["total_data_count"] == 10
