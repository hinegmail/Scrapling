"""Property-based tests for result pagination"""

from datetime import datetime, timezone
from uuid import uuid4
from hypothesis import given, strategies as st, settings, HealthCheck
import pytest
from sqlalchemy.orm import Session

from app.models.result import Result
from app.models.task import Task, TaskStatus, FetcherType, SelectorType
from app.models.user import User
from app.services.result_service import ResultService
from app.exceptions import NotFoundError


class TestResultPagination:
    """Property-based tests for result pagination"""

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

    @pytest.fixture
    def task(self, test_db_session: Session, user: User) -> Task:
        """Create a test task"""
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
        test_db_session.refresh(task)
        return task

    @given(
        num_results=st.integers(min_value=0, max_value=100),
        page=st.integers(min_value=1, max_value=10),
        page_size=st.integers(min_value=1, max_value=50),
    )
    @settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow])
    def test_pagination_bounds(
        self,
        test_db_session: Session,
        user: User,
        task: Task,
        num_results: int,
        page: int,
        page_size: int,
    ):
        """Test that pagination respects bounds"""
        # Create results
        for i in range(num_results):
            result = Result(
                task_id=task.id,
                data={"index": i},
                source_url=f"https://example.com/{i}",
                extracted_at=datetime.now(timezone.utc),
            )
            test_db_session.add(result)
        test_db_session.commit()

        # Get paginated results
        results, total = ResultService.get_results(
            test_db_session, user.id, task.id, page, page_size
        )

        # Verify total count
        assert total == num_results

        # Verify page size
        expected_size = min(page_size, max(0, num_results - (page - 1) * page_size))
        assert len(results) == expected_size

        # Verify no duplicate results
        result_ids = [r.id for r in results]
        assert len(result_ids) == len(set(result_ids))

    @given(
        num_results=st.integers(min_value=1, max_value=50),
        page_size=st.integers(min_value=1, max_value=20),
    )
    @settings(max_examples=50, suppress_health_check=[HealthCheck.too_slow])
    def test_pagination_coverage(
        self,
        test_db_session: Session,
        user: User,
        task: Task,
        num_results: int,
        page_size: int,
    ):
        """Test that all results are accessible through pagination"""
        # Create results
        created_ids = []
        for i in range(num_results):
            result = Result(
                task_id=task.id,
                data={"index": i},
                source_url=f"https://example.com/{i}",
                extracted_at=datetime.now(timezone.utc),
            )
            test_db_session.add(result)
            test_db_session.flush()
            created_ids.append(result.id)
        test_db_session.commit()

        # Collect all results through pagination
        collected_ids = []
        page = 1
        while True:
            results, total = ResultService.get_results(
                test_db_session, user.id, task.id, page, page_size
            )
            if not results:
                break
            collected_ids.extend([r.id for r in results])
            page += 1

        # Verify all results are collected
        assert len(collected_ids) == num_results
        assert set(collected_ids) == set(created_ids)

    @given(
        num_results=st.integers(min_value=1, max_value=50),
        page_size=st.integers(min_value=1, max_value=20),
    )
    @settings(max_examples=50, suppress_health_check=[HealthCheck.too_slow])
    def test_pagination_order_consistency(
        self,
        test_db_session: Session,
        user: User,
        task: Task,
        num_results: int,
        page_size: int,
    ):
        """Test that pagination order is consistent"""
        # Create results
        for i in range(num_results):
            result = Result(
                task_id=task.id,
                data={"index": i},
                source_url=f"https://example.com/{i}",
                extracted_at=datetime.now(timezone.utc),
            )
            test_db_session.add(result)
        test_db_session.commit()

        # Get all results through pagination twice
        collected_ids_1 = []
        page = 1
        while True:
            results, _ = ResultService.get_results(
                test_db_session, user.id, task.id, page, page_size
            )
            if not results:
                break
            collected_ids_1.extend([r.id for r in results])
            page += 1

        collected_ids_2 = []
        page = 1
        while True:
            results, _ = ResultService.get_results(
                test_db_session, user.id, task.id, page, page_size
            )
            if not results:
                break
            collected_ids_2.extend([r.id for r in results])
            page += 1

        # Verify order is consistent
        assert collected_ids_1 == collected_ids_2

    @given(
        num_results=st.integers(min_value=1, max_value=50),
        page_size=st.integers(min_value=1, max_value=20),
    )
    @settings(max_examples=50, suppress_health_check=[HealthCheck.too_slow])
    def test_pagination_no_overlap(
        self,
        test_db_session: Session,
        user: User,
        task: Task,
        num_results: int,
        page_size: int,
    ):
        """Test that pagination pages don't overlap"""
        # Create results
        for i in range(num_results):
            result = Result(
                task_id=task.id,
                data={"index": i},
                source_url=f"https://example.com/{i}",
                extracted_at=datetime.now(timezone.utc),
            )
            test_db_session.add(result)
        test_db_session.commit()

        # Get all pages
        all_pages = []
        page = 1
        while True:
            results, _ = ResultService.get_results(
                test_db_session, user.id, task.id, page, page_size
            )
            if not results:
                break
            page_ids = [r.id for r in results]
            all_pages.append(page_ids)
            page += 1

        # Verify no overlap between pages
        for i, page1 in enumerate(all_pages):
            for j, page2 in enumerate(all_pages):
                if i != j:
                    assert len(set(page1) & set(page2)) == 0

    def test_pagination_invalid_page(
        self,
        test_db_session: Session,
        user: User,
        task: Task,
    ):
        """Test pagination with invalid page number"""
        # Create a result
        result = Result(
            task_id=task.id,
            data={"test": "data"},
            source_url="https://example.com",
            extracted_at=datetime.now(timezone.utc),
        )
        test_db_session.add(result)
        test_db_session.commit()

        # Get results with page beyond available
        results, total = ResultService.get_results(
            test_db_session, user.id, task.id, page=100, page_size=10
        )

        assert len(results) == 0
        assert total == 1

    def test_pagination_with_search(
        self,
        test_db_session: Session,
        user: User,
        task: Task,
    ):
        """Test pagination with search filter"""
        # Create results
        for i in range(5):
            result = Result(
                task_id=task.id,
                data={"content": f"test{i}"},
                source_url=f"https://example.com/page{i}",
                extracted_at=datetime.now(timezone.utc),
            )
            test_db_session.add(result)
        test_db_session.commit()

        # Search for specific results
        results, total = ResultService.get_results(
            test_db_session, user.id, task.id, page=1, page_size=10, search="page2"
        )

        assert total == 1
        assert len(results) == 1
        assert "page2" in results[0].source_url

    def test_pagination_sorting(
        self,
        test_db_session: Session,
        user: User,
        task: Task,
    ):
        """Test pagination with sorting"""
        # Create results
        for i in range(5):
            result = Result(
                task_id=task.id,
                data={"index": i},
                source_url=f"https://example.com/{i}",
                extracted_at=datetime.now(timezone.utc),
            )
            test_db_session.add(result)
        test_db_session.commit()

        # Get results sorted ascending
        results_asc, _ = ResultService.get_results(
            test_db_session, user.id, task.id, page=1, page_size=10, sort_order="asc"
        )

        # Get results sorted descending
        results_desc, _ = ResultService.get_results(
            test_db_session, user.id, task.id, page=1, page_size=10, sort_order="desc"
        )

        # Verify sorting
        assert results_asc[0].id != results_desc[0].id

    def test_pagination_nonexistent_task(
        self,
        test_db_session: Session,
        user: User,
    ):
        """Test pagination with nonexistent task"""
        nonexistent_task_id = uuid4()

        with pytest.raises(NotFoundError):
            ResultService.get_results(
                test_db_session, user.id, nonexistent_task_id, page=1, page_size=10
            )

    def test_pagination_unauthorized_user(
        self,
        test_db_session: Session,
        user: User,
        task: Task,
    ):
        """Test pagination with unauthorized user"""
        other_user = User(
            email="other@example.com",
            username="otheruser",
            hashed_password="hashed_password",
        )
        test_db_session.add(other_user)
        test_db_session.commit()

        # Create result
        result = Result(
            task_id=task.id,
            data={"test": "data"},
            source_url="https://example.com",
            extracted_at=datetime.now(timezone.utc),
        )
        test_db_session.add(result)
        test_db_session.commit()

        # Try to access with different user
        with pytest.raises(NotFoundError):
            ResultService.get_results(
                test_db_session, other_user.id, task.id, page=1, page_size=10
            )
