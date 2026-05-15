"""Property-based tests for task list filtering"""

from datetime import datetime, timezone
from uuid import uuid4
from hypothesis import given, strategies as st, settings, HealthCheck
import pytest
from sqlalchemy.orm import Session

from app.models.task import Task, TaskStatus, FetcherType, SelectorType
from app.models.user import User
from app.services.task import TaskService
from app.exceptions import NotFoundError


class TestTaskListFiltering:
    """Property-based tests for task list filtering"""

    @pytest.fixture
    def user(self, test_db_session: Session) -> User:
        """Create a test user"""
        user = User(
            email="test@example.com",
            username="testuser",
            hashed_password="hashed_password",
        )
        test_db_session.add(user)
        test_db_session.commit()
        test_db_session.refresh(user)
        return user

    @given(
        num_tasks=st.integers(min_value=1, max_value=30),
        page_size=st.integers(min_value=1, max_value=15),
    )
    @settings(max_examples=50, suppress_health_check=[HealthCheck.too_slow])
    def test_task_list_pagination(
        self,
        test_db_session: Session,
        user: User,
        num_tasks: int,
        page_size: int,
    ):
        """Test task list pagination"""
        # Create tasks
        for i in range(num_tasks):
            task = Task(
                user_id=user.id,
                name=f"Task {i}",
                target_url=f"https://example.com/{i}",
                fetcher_type=FetcherType.HTTP,
                selector=".item",
                selector_type=SelectorType.CSS,
                status=TaskStatus.DRAFT,
            )
            test_db_session.add(task)
        test_db_session.commit()

        # Get paginated tasks
        tasks, total = TaskService.get_tasks(
            test_db_session, user.id, page=1, page_size=page_size
        )

        # Verify total count
        assert total == num_tasks

        # Verify page size
        expected_size = min(page_size, num_tasks)
        assert len(tasks) == expected_size

    @given(
        num_tasks=st.integers(min_value=1, max_value=30),
    )
    @settings(max_examples=50, suppress_health_check=[HealthCheck.too_slow])
    def test_task_list_status_filter(
        self,
        test_db_session: Session,
        user: User,
        num_tasks: int,
    ):
        """Test task list filtering by status"""
        # Create tasks with different statuses
        statuses = [TaskStatus.DRAFT, TaskStatus.RUNNING, TaskStatus.COMPLETED]
        for i in range(num_tasks):
            task = Task(
                user_id=user.id,
                name=f"Task {i}",
                target_url=f"https://example.com/{i}",
                fetcher_type=FetcherType.HTTP,
                selector=".item",
                selector_type=SelectorType.CSS,
                status=statuses[i % len(statuses)],
            )
            test_db_session.add(task)
        test_db_session.commit()

        # Filter by status
        for status in statuses:
            tasks, total = TaskService.get_tasks(
                test_db_session, user.id, page=1, page_size=100, status=status
            )

            # Verify all returned tasks have the correct status
            for task in tasks:
                assert task.status == status

            # Verify count
            expected_count = (num_tasks + len(statuses) - 1) // len(statuses)
            assert total <= expected_count + 1

    @given(
        num_tasks=st.integers(min_value=1, max_value=20),
        search_term=st.text(min_size=1, max_size=10, alphabet="abcdefghijklmnopqrstuvwxyz"),
    )
    @settings(max_examples=50, suppress_health_check=[HealthCheck.too_slow])
    def test_task_list_search_filter(
        self,
        test_db_session: Session,
        user: User,
        num_tasks: int,
        search_term: str,
    ):
        """Test task list search filtering"""
        # Create tasks with searchable names
        for i in range(num_tasks):
            name = f"Task {search_term} {i}" if i % 2 == 0 else f"Task {i}"
            task = Task(
                user_id=user.id,
                name=name,
                target_url=f"https://example.com/{i}",
                fetcher_type=FetcherType.HTTP,
                selector=".item",
                selector_type=SelectorType.CSS,
                status=TaskStatus.DRAFT,
            )
            test_db_session.add(task)
        test_db_session.commit()

        # Search for tasks
        tasks, total = TaskService.get_tasks(
            test_db_session, user.id, page=1, page_size=100, search=search_term
        )

        # Verify all returned tasks contain search term
        for task in tasks:
            assert search_term.lower() in task.name.lower()

        # Verify count is reasonable
        expected_count = (num_tasks + 1) // 2
        assert total <= expected_count

    @given(
        num_tasks=st.integers(min_value=1, max_value=30),
        page_size=st.integers(min_value=1, max_value=15),
    )
    @settings(max_examples=50, suppress_health_check=[HealthCheck.too_slow])
    def test_task_list_coverage(
        self,
        test_db_session: Session,
        user: User,
        num_tasks: int,
        page_size: int,
    ):
        """Test that all tasks are accessible through pagination"""
        # Create tasks
        created_ids = []
        for i in range(num_tasks):
            task = Task(
                user_id=user.id,
                name=f"Task {i}",
                target_url=f"https://example.com/{i}",
                fetcher_type=FetcherType.HTTP,
                selector=".item",
                selector_type=SelectorType.CSS,
                status=TaskStatus.DRAFT,
            )
            test_db_session.add(task)
            test_db_session.flush()
            created_ids.append(task.id)
        test_db_session.commit()

        # Collect all tasks through pagination
        collected_ids = []
        page = 1
        while True:
            tasks, _ = TaskService.get_tasks(
                test_db_session, user.id, page=page, page_size=page_size
            )
            if not tasks:
                break
            collected_ids.extend([t.id for t in tasks])
            page += 1

        # Verify all tasks are collected
        assert len(collected_ids) == num_tasks
        assert set(collected_ids) == set(created_ids)

    @given(
        num_tasks=st.integers(min_value=1, max_value=20),
    )
    @settings(max_examples=50, suppress_health_check=[HealthCheck.too_slow])
    def test_task_list_no_duplicates(
        self,
        test_db_session: Session,
        user: User,
        num_tasks: int,
    ):
        """Test that task list doesn't return duplicates"""
        # Create tasks
        for i in range(num_tasks):
            task = Task(
                user_id=user.id,
                name=f"Task {i}",
                target_url=f"https://example.com/{i}",
                fetcher_type=FetcherType.HTTP,
                selector=".item",
                selector_type=SelectorType.CSS,
                status=TaskStatus.DRAFT,
            )
            test_db_session.add(task)
        test_db_session.commit()

        # Get all tasks
        tasks, _ = TaskService.get_tasks(
            test_db_session, user.id, page=1, page_size=100
        )

        # Verify no duplicates
        task_ids = [t.id for t in tasks]
        assert len(task_ids) == len(set(task_ids))

    def test_task_list_user_isolation(
        self,
        test_db_session: Session,
        user: User,
    ):
        """Test that task list is isolated per user"""
        # Create another user
        other_user = User(
            email="other@example.com",
            username="otheruser",
            hashed_password="hashed_password",
        )
        test_db_session.add(other_user)
        test_db_session.commit()

        # Create tasks for both users
        for i in range(5):
            task1 = Task(
                user_id=user.id,
                name=f"User1 Task {i}",
                target_url=f"https://example.com/{i}",
                fetcher_type=FetcherType.HTTP,
                selector=".item",
                selector_type=SelectorType.CSS,
                status=TaskStatus.DRAFT,
            )
            task2 = Task(
                user_id=other_user.id,
                name=f"User2 Task {i}",
                target_url=f"https://example.com/{i}",
                fetcher_type=FetcherType.HTTP,
                selector=".item",
                selector_type=SelectorType.CSS,
                status=TaskStatus.DRAFT,
            )
            test_db_session.add(task1)
            test_db_session.add(task2)
        test_db_session.commit()

        # Get tasks for each user
        user1_tasks, user1_total = TaskService.get_tasks(
            test_db_session, user.id, page=1, page_size=100
        )
        user2_tasks, user2_total = TaskService.get_tasks(
            test_db_session, other_user.id, page=1, page_size=100
        )

        # Verify isolation
        assert user1_total == 5
        assert user2_total == 5

        user1_ids = {t.id for t in user1_tasks}
        user2_ids = {t.id for t in user2_tasks}
        assert len(user1_ids & user2_ids) == 0

    def test_task_list_combined_filters(
        self,
        test_db_session: Session,
        user: User,
    ):
        """Test task list with combined filters"""
        # Create tasks
        for i in range(10):
            status = TaskStatus.RUNNING if i % 2 == 0 else TaskStatus.DRAFT
            name = f"Important Task {i}" if i < 5 else f"Regular Task {i}"
            task = Task(
                user_id=user.id,
                name=name,
                target_url=f"https://example.com/{i}",
                fetcher_type=FetcherType.HTTP,
                selector=".item",
                selector_type=SelectorType.CSS,
                status=status,
            )
            test_db_session.add(task)
        test_db_session.commit()

        # Filter by status and search
        tasks, total = TaskService.get_tasks(
            test_db_session,
            user.id,
            page=1,
            page_size=100,
            status=TaskStatus.RUNNING,
            search="Important",
        )

        # Verify results
        for task in tasks:
            assert task.status == TaskStatus.RUNNING
            assert "Important" in task.name

    def test_task_list_empty_result(
        self,
        test_db_session: Session,
        user: User,
    ):
        """Test task list with no matching results"""
        # Create a task
        task = Task(
            user_id=user.id,
            name="Test Task",
            target_url="https://example.com",
            fetcher_type=FetcherType.HTTP,
            selector=".item",
            selector_type=SelectorType.CSS,
            status=TaskStatus.DRAFT,
        )
        test_db_session.add(task)
        test_db_session.commit()

        # Search for non-existent task
        tasks, total = TaskService.get_tasks(
            test_db_session, user.id, page=1, page_size=100, search="nonexistent"
        )

        assert total == 0
        assert len(tasks) == 0

    def test_task_list_status_filter_all_statuses(
        self,
        test_db_session: Session,
        user: User,
    ):
        """Test task list filtering with all possible statuses"""
        # Create tasks with all statuses
        all_statuses = [
            TaskStatus.DRAFT,
            TaskStatus.RUNNING,
            TaskStatus.PAUSED,
            TaskStatus.COMPLETED,
            TaskStatus.FAILED,
            TaskStatus.STOPPED,
        ]

        for status in all_statuses:
            task = Task(
                user_id=user.id,
                name=f"Task {status}",
                target_url="https://example.com",
                fetcher_type=FetcherType.HTTP,
                selector=".item",
                selector_type=SelectorType.CSS,
                status=status,
            )
            test_db_session.add(task)
        test_db_session.commit()

        # Verify each status filter works
        for status in all_statuses:
            tasks, total = TaskService.get_tasks(
                test_db_session, user.id, page=1, page_size=100, status=status
            )

            assert total == 1
            assert len(tasks) == 1
            assert tasks[0].status == status
