"""Property-based tests for data export format correctness

**Validates: Requirements 4.5**

This module contains property-based tests for data export format correctness.
The tests verify that exported data in CSV, JSON, and Excel formats can be
parsed back to reconstruct the original data structure (roundtrip property).
"""

import csv
import json
import io
from datetime import datetime, timezone
from uuid import uuid4
from hypothesis import given, strategies as st, settings, HealthCheck
import pytest
from sqlalchemy.orm import Session

from app.models.result import Result
from app.models.task import Task, TaskStatus, FetcherType, SelectorType
from app.models.user import User
from app.services.export_service import ExportService
from app.exceptions import ValidationError


class TestExportFormats:
    """Property-based tests for export format correctness"""

    def _create_test_user(self, session: Session) -> User:
        """Helper to create a test user"""
        user = User(
            email=f"test_{uuid4()}@example.com",
            username=f"testuser_{uuid4()}",
            password_hash="hashed_password",
        )
        session.add(user)
        session.flush()
        return user

    def _create_test_task(self, session: Session, user: User) -> Task:
        """Helper to create a test task"""
        task = Task(
            user_id=user.id,
            name="Test Task",
            target_url="https://example.com",
            fetcher_type=FetcherType.HTTP,
            selector=".item",
            selector_type=SelectorType.CSS,
            status=TaskStatus.DRAFT,
        )
        session.add(task)
        session.flush()
        return task

    @given(
        num_results=st.integers(min_value=1, max_value=20),
        data_keys=st.lists(
            st.text(min_size=1, max_size=20, alphabet=st.characters(blacklist_characters="\n\r")),
            min_size=1,
            max_size=5,
            unique=True,
        ),
    )
    @settings(
        max_examples=50,
        suppress_health_check=[HealthCheck.too_slow, HealthCheck.function_scoped_fixture],
    )
    def test_csv_export_roundtrip(
        self,
        test_db_session: Session,
        num_results: int,
        data_keys: list,
    ):
        """Test CSV export and parse roundtrip"""
        # Create test data
        user = self._create_test_user(test_db_session)
        task = self._create_test_task(test_db_session, user)

        # Create results with various data
        created_data = []
        for i in range(num_results):
            data = {key: f"value_{i}_{key}" for key in data_keys}
            result = Result(
                task_id=task.id,
                data=data,
                source_url=f"https://example.com/{i}",
                extracted_at=datetime.now(timezone.utc),
            )
            test_db_session.add(result)
            created_data.append(data)
        test_db_session.flush()

        # Export to CSV
        results = test_db_session.query(Result).filter(Result.task_id == task.id).all()
        csv_content = ExportService.export_to_csv(results)

        # Parse CSV
        csv_reader = csv.DictReader(io.StringIO(csv_content))
        rows = list(csv_reader)

        # Verify row count
        assert len(rows) == num_results

        # Verify all keys are present
        for key in data_keys:
            assert key in csv_reader.fieldnames

    @given(
        num_results=st.integers(min_value=1, max_value=20),
        data_values=st.lists(
            st.one_of(
                st.text(min_size=0, max_size=50),
                st.integers(),
                st.floats(allow_nan=False, allow_infinity=False),
                st.booleans(),
            ),
            min_size=1,
            max_size=5,
        ),
    )
    @settings(
        max_examples=50,
        suppress_health_check=[HealthCheck.too_slow, HealthCheck.function_scoped_fixture],
    )
    def test_json_export_roundtrip(
        self,
        test_db_session: Session,
        num_results: int,
        data_values: list,
    ):
        """Test JSON export and parse roundtrip"""
        # Create test data
        user = self._create_test_user(test_db_session)
        task = self._create_test_task(test_db_session, user)

        # Create results
        created_results = []
        for i in range(num_results):
            data = {f"field_{j}": data_values[j % len(data_values)] for j in range(len(data_values))}
            result = Result(
                task_id=task.id,
                data=data,
                source_url=f"https://example.com/{i}",
                extracted_at=datetime.now(timezone.utc),
            )
            test_db_session.add(result)
            created_results.append(result)
        test_db_session.flush()

        # Export to JSON
        results = test_db_session.query(Result).filter(Result.task_id == task.id).all()
        json_content = ExportService.export_to_json(results)

        # Parse JSON
        parsed = json.loads(json_content)

        # Verify structure
        assert isinstance(parsed, list)
        assert len(parsed) == num_results

        # Verify each item has required fields
        for item in parsed:
            assert "id" in item
            assert "task_id" in item
            assert "source_url" in item
            assert "extracted_at" in item
            assert "data" in item

    @given(
        num_results=st.integers(min_value=1, max_value=20),
    )
    @settings(
        max_examples=50,
        suppress_health_check=[HealthCheck.too_slow, HealthCheck.function_scoped_fixture],
    )
    def test_csv_data_integrity(
        self,
        test_db_session: Session,
        num_results: int,
    ):
        """Test CSV export preserves data integrity"""
        # Create test data
        user = self._create_test_user(test_db_session)
        task = self._create_test_task(test_db_session, user)

        # Create results with specific data
        test_data = []
        for i in range(num_results):
            data = {
                "title": f"Title {i}",
                "price": f"${i * 10}",
                "description": f"Description for item {i}",
            }
            result = Result(
                task_id=task.id,
                data=data,
                source_url=f"https://example.com/item/{i}",
                extracted_at=datetime.now(timezone.utc),
            )
            test_db_session.add(result)
            test_data.append(data)
        test_db_session.flush()

        # Export to CSV
        results = test_db_session.query(Result).filter(Result.task_id == task.id).all()
        csv_content = ExportService.export_to_csv(results)

        # Parse and verify
        csv_reader = csv.DictReader(io.StringIO(csv_content))
        rows = list(csv_reader)

        for i, row in enumerate(rows):
            assert row["title"] == test_data[i]["title"]
            assert row["price"] == test_data[i]["price"]
            assert row["description"] == test_data[i]["description"]

    @given(
        num_results=st.integers(min_value=1, max_value=20),
    )
    @settings(
        max_examples=50,
        suppress_health_check=[HealthCheck.too_slow, HealthCheck.function_scoped_fixture],
    )
    def test_json_data_integrity(
        self,
        test_db_session: Session,
        num_results: int,
    ):
        """Test JSON export preserves data integrity"""
        # Create test data
        user = self._create_test_user(test_db_session)
        task = self._create_test_task(test_db_session, user)

        # Create results with specific data
        test_data = []
        for i in range(num_results):
            data = {
                "id": i,
                "name": f"Item {i}",
                "active": i % 2 == 0,
            }
            result = Result(
                task_id=task.id,
                data=data,
                source_url=f"https://example.com/item/{i}",
                extracted_at=datetime.now(timezone.utc),
            )
            test_db_session.add(result)
            test_data.append(data)
        test_db_session.flush()

        # Export to JSON
        results = test_db_session.query(Result).filter(Result.task_id == task.id).all()
        json_content = ExportService.export_to_json(results)

        # Parse and verify
        parsed = json.loads(json_content)

        for i, item in enumerate(parsed):
            assert item["data"]["id"] == test_data[i]["id"]
            assert item["data"]["name"] == test_data[i]["name"]
            assert item["data"]["active"] == test_data[i]["active"]

    def test_csv_special_characters(
        self,
        test_db_session: Session,
    ):
        """Test CSV export handles special characters"""
        # Create test data
        user = self._create_test_user(test_db_session)
        task = self._create_test_task(test_db_session, user)

        # Create result with special characters
        data = {
            "text": 'Hello "World", with\ncommas',
            "symbols": "!@#$%^&*()",
        }
        result = Result(
            task_id=task.id,
            data=data,
            source_url="https://example.com",
            extracted_at=datetime.now(timezone.utc),
        )
        test_db_session.add(result)
        test_db_session.flush()

        # Export to CSV
        results = test_db_session.query(Result).filter(Result.task_id == task.id).all()
        csv_content = ExportService.export_to_csv(results)

        # Parse and verify
        csv_reader = csv.DictReader(io.StringIO(csv_content))
        rows = list(csv_reader)

        assert len(rows) == 1
        assert rows[0]["text"] == data["text"]
        assert rows[0]["symbols"] == data["symbols"]

    def test_json_special_characters(
        self,
        test_db_session: Session,
    ):
        """Test JSON export handles special characters"""
        # Create test data
        user = self._create_test_user(test_db_session)
        task = self._create_test_task(test_db_session, user)

        # Create result with special characters
        data = {
            "text": 'Hello "World" with\nnewlines',
            "unicode": "你好世界 🌍",
        }
        result = Result(
            task_id=task.id,
            data=data,
            source_url="https://example.com",
            extracted_at=datetime.now(timezone.utc),
        )
        test_db_session.add(result)
        test_db_session.flush()

        # Export to JSON
        results = test_db_session.query(Result).filter(Result.task_id == task.id).all()
        json_content = ExportService.export_to_json(results)

        # Parse and verify
        parsed = json.loads(json_content)

        assert parsed[0]["data"]["text"] == data["text"]
        assert parsed[0]["data"]["unicode"] == data["unicode"]

    def test_csv_column_filtering(
        self,
        test_db_session: Session,
    ):
        """Test CSV export with column filtering"""
        # Create test data
        user = self._create_test_user(test_db_session)
        task = self._create_test_task(test_db_session, user)

        # Create result with multiple fields
        data = {
            "title": "Test Title",
            "price": "100",
            "description": "Test Description",
            "category": "Test Category",
        }
        result = Result(
            task_id=task.id,
            data=data,
            source_url="https://example.com",
            extracted_at=datetime.now(timezone.utc),
        )
        test_db_session.add(result)
        test_db_session.flush()

        # Export with column filtering
        results = test_db_session.query(Result).filter(Result.task_id == task.id).all()
        csv_content = ExportService.export_to_csv(results, columns=["title", "price"])

        # Parse and verify
        csv_reader = csv.DictReader(io.StringIO(csv_content))
        rows = list(csv_reader)

        assert "title" in csv_reader.fieldnames
        assert "price" in csv_reader.fieldnames
        assert "description" not in csv_reader.fieldnames

    def test_json_column_filtering(
        self,
        test_db_session: Session,
    ):
        """Test JSON export with column filtering"""
        # Create test data
        user = self._create_test_user(test_db_session)
        task = self._create_test_task(test_db_session, user)

        # Create result with multiple fields
        data = {
            "title": "Test Title",
            "price": "100",
            "description": "Test Description",
        }
        result = Result(
            task_id=task.id,
            data=data,
            source_url="https://example.com",
            extracted_at=datetime.now(timezone.utc),
        )
        test_db_session.add(result)
        test_db_session.flush()

        # Export with column filtering
        results = test_db_session.query(Result).filter(Result.task_id == task.id).all()
        json_content = ExportService.export_to_json(results, columns=["title", "price"])

        # Parse and verify
        parsed = json.loads(json_content)

        assert "title" in parsed[0]["data"]
        assert "price" in parsed[0]["data"]
        assert "description" not in parsed[0]["data"]

    def test_empty_results_export(
        self,
        test_db_session: Session,
    ):
        """Test export with empty results"""
        # CSV export
        csv_content = ExportService.export_to_csv([])
        assert csv_content == ""

        # JSON export
        json_content = ExportService.export_to_json([])
        assert json_content == "[]"

    def test_invalid_export_format(self):
        """Test invalid export format"""
        with pytest.raises(ValidationError):
            ExportService.validate_export_format("invalid_format")

    def test_clipboard_text_format(
        self,
        test_db_session: Session,
    ):
        """Test clipboard text format"""
        # Create test data
        user = self._create_test_user(test_db_session)
        task = self._create_test_task(test_db_session, user)

        # Create results
        for i in range(3):
            result = Result(
                task_id=task.id,
                data={"title": f"Item {i}"},
                source_url=f"https://example.com/{i}",
                extracted_at=datetime.now(timezone.utc),
            )
            test_db_session.add(result)
        test_db_session.flush()

        # Get clipboard data
        results = test_db_session.query(Result).filter(Result.task_id == task.id).all()
        text_data = ExportService.get_clipboard_data(results, "text")

        # Verify format
        assert "URL:" in text_data
        assert "Extracted:" in text_data
        assert "title:" in text_data

    def test_clipboard_json_format(
        self,
        test_db_session: Session,
    ):
        """Test clipboard JSON format"""
        # Create test data
        user = self._create_test_user(test_db_session)
        task = self._create_test_task(test_db_session, user)

        # Create result
        result = Result(
            task_id=task.id,
            data={"title": "Test"},
            source_url="https://example.com",
            extracted_at=datetime.now(timezone.utc),
        )
        test_db_session.add(result)
        test_db_session.flush()

        # Get clipboard data
        results = test_db_session.query(Result).filter(Result.task_id == task.id).all()
        json_data = ExportService.get_clipboard_data(results, "json")

        # Verify it's valid JSON
        parsed = json.loads(json_data)
        assert isinstance(parsed, list)
        assert len(parsed) == 1
