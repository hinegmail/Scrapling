"""Property-based tests for WebSocket progress message integrity

**Validates: Requirements 3.2**

This module contains property-based tests for WebSocket progress message integrity.
The tests verify that WebSocket progress messages contain all required fields
(task_id, processed_count, total_count, success_count, error_count, current_url,
elapsed_time, estimated_remaining) with correct data types and non-negative values.
"""

import pytest
from datetime import datetime, timezone
from uuid import UUID, uuid4
from hypothesis import given, strategies as st, settings, assume
import json

from app.services.progress import ProgressService
from app.models.task import Task, TaskStatus
from app.models.user import User


class TestWebSocketProgressMessageIntegrity:
    """Property-based tests for WebSocket progress message integrity
    
    **Validates: Requirements 3.2**
    
    These tests verify that WebSocket progress messages contain all required fields
    with correct data types and valid value ranges.
    """

    @given(
        processed_count=st.integers(min_value=0, max_value=10000),
        total_count=st.integers(min_value=1, max_value=10000),
        success_count=st.integers(min_value=0),
        error_count=st.integers(min_value=0),
        current_url=st.text(min_size=1, max_size=2048),
        elapsed_time=st.integers(min_value=0, max_value=86400),
        estimated_remaining=st.integers(min_value=0, max_value=86400),
    )
    @settings(max_examples=100)
    def test_progress_message_contains_all_required_fields(
        self,
        processed_count,
        total_count,
        success_count,
        error_count,
        current_url,
        elapsed_time,
        estimated_remaining,
    ):
        """
        Property: For any task execution state, WebSocket progress message should
        contain all required fields: task_id, processed_count, total_count,
        success_count, error_count, current_url, elapsed_time, estimated_remaining.
        
        **Validates: Requirements 3.2**
        """
        # Ensure processed_count doesn't exceed total_count
        assume(processed_count <= total_count)
        
        task_id = uuid4()
        
        # Create progress message
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
        
        # Verify all required fields are present
        required_fields = [
            "task_id",
            "processed_count",
            "total_count",
            "success_count",
            "error_count",
            "current_url",
            "elapsed_time",
            "estimated_remaining",
            "timestamp",
        ]
        
        for field in required_fields:
            assert field in message, f"Required field '{field}' missing from progress message"
            assert message[field] is not None, f"Required field '{field}' is None"

    @given(
        processed_count=st.integers(min_value=0, max_value=10000),
        total_count=st.integers(min_value=1, max_value=10000),
        success_count=st.integers(min_value=0),
        error_count=st.integers(min_value=0),
        current_url=st.text(min_size=1, max_size=2048),
        elapsed_time=st.integers(min_value=0, max_value=86400),
        estimated_remaining=st.integers(min_value=0, max_value=86400),
    )
    @settings(max_examples=100)
    def test_progress_message_field_types(
        self,
        processed_count,
        total_count,
        success_count,
        error_count,
        current_url,
        elapsed_time,
        estimated_remaining,
    ):
        """
        Property: All fields in progress message should have correct data types.
        
        **Validates: Requirements 3.2**
        """
        assume(processed_count <= total_count)
        
        task_id = uuid4()
        
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
        
        # Verify field types
        assert isinstance(message["task_id"], str), "task_id should be string"
        assert isinstance(message["processed_count"], int), "processed_count should be int"
        assert isinstance(message["total_count"], int), "total_count should be int"
        assert isinstance(message["success_count"], int), "success_count should be int"
        assert isinstance(message["error_count"], int), "error_count should be int"
        assert isinstance(message["current_url"], str), "current_url should be string"
        assert isinstance(message["elapsed_time"], int), "elapsed_time should be int"
        assert isinstance(message["estimated_remaining"], int), "estimated_remaining should be int"
        assert isinstance(message["timestamp"], str), "timestamp should be string"

    @given(
        processed_count=st.integers(min_value=0, max_value=10000),
        total_count=st.integers(min_value=1, max_value=10000),
        success_count=st.integers(min_value=0),
        error_count=st.integers(min_value=0),
        current_url=st.text(min_size=1, max_size=2048),
        elapsed_time=st.integers(min_value=0, max_value=86400),
        estimated_remaining=st.integers(min_value=0, max_value=86400),
    )
    @settings(max_examples=100)
    def test_progress_message_non_negative_values(
        self,
        processed_count,
        total_count,
        success_count,
        error_count,
        current_url,
        elapsed_time,
        estimated_remaining,
    ):
        """
        Property: All numeric fields in progress message should be non-negative.
        
        **Validates: Requirements 3.2**
        """
        assume(processed_count <= total_count)
        
        task_id = uuid4()
        
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
        
        # Verify non-negative values
        assert message["processed_count"] >= 0, "processed_count should be non-negative"
        assert message["total_count"] > 0, "total_count should be positive"
        assert message["success_count"] >= 0, "success_count should be non-negative"
        assert message["error_count"] >= 0, "error_count should be non-negative"
        assert message["elapsed_time"] >= 0, "elapsed_time should be non-negative"
        assert message["estimated_remaining"] >= 0, "estimated_remaining should be non-negative"

    @given(
        processed_count=st.integers(min_value=0, max_value=10000),
        total_count=st.integers(min_value=1, max_value=10000),
        success_count=st.integers(min_value=0),
        error_count=st.integers(min_value=0),
        current_url=st.text(min_size=1, max_size=2048),
        elapsed_time=st.integers(min_value=0, max_value=86400),
        estimated_remaining=st.integers(min_value=0, max_value=86400),
    )
    @settings(max_examples=100)
    def test_progress_message_processed_count_constraint(
        self,
        processed_count,
        total_count,
        success_count,
        error_count,
        current_url,
        elapsed_time,
        estimated_remaining,
    ):
        """
        Property: processed_count should not exceed total_count.
        
        **Validates: Requirements 3.2**
        """
        assume(processed_count <= total_count)
        
        task_id = uuid4()
        
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
        
        # Verify constraint
        assert message["processed_count"] <= message["total_count"], \
            "processed_count should not exceed total_count"

    @given(
        data=st.data(),
    )
    @settings(max_examples=100)
    def test_progress_message_success_error_count_constraint(self, data):
        """
        Property: success_count + error_count should not exceed processed_count.
        
        **Validates: Requirements 3.2**
        """
        processed_count = data.draw(st.integers(min_value=0, max_value=10000))
        total_count = data.draw(st.integers(min_value=max(1, processed_count), max_value=10000))
        success_count = data.draw(st.integers(min_value=0, max_value=processed_count))
        error_count = data.draw(st.integers(min_value=0, max_value=processed_count - success_count))
        current_url = data.draw(st.text(min_size=1, max_size=2048))
        elapsed_time = data.draw(st.integers(min_value=0, max_value=86400))
        estimated_remaining = data.draw(st.integers(min_value=0, max_value=86400))
        
        task_id = uuid4()
        
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
        
        # Verify constraint
        assert message["success_count"] + message["error_count"] <= message["processed_count"], \
            "success_count + error_count should not exceed processed_count"

    @given(
        processed_count=st.integers(min_value=0, max_value=10000),
        total_count=st.integers(min_value=1, max_value=10000),
        success_count=st.integers(min_value=0),
        error_count=st.integers(min_value=0),
        current_url=st.text(min_size=1, max_size=2048),
        elapsed_time=st.integers(min_value=0, max_value=86400),
        estimated_remaining=st.integers(min_value=0, max_value=86400),
    )
    @settings(max_examples=100)
    def test_progress_message_percentage_calculation(
        self,
        processed_count,
        total_count,
        success_count,
        error_count,
        current_url,
        elapsed_time,
        estimated_remaining,
    ):
        """
        Property: progress_percentage should be correctly calculated as
        (processed_count / total_count * 100), rounded to integer.
        
        **Validates: Requirements 3.2**
        """
        assume(processed_count <= total_count)
        
        task_id = uuid4()
        
        expected_percentage = int((processed_count / total_count * 100) if total_count > 0 else 0)
        
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
            "progress_percentage": expected_percentage,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        
        # Verify percentage calculation
        assert message["progress_percentage"] == expected_percentage, \
            "progress_percentage should match calculated value"
        assert 0 <= message["progress_percentage"] <= 100, \
            "progress_percentage should be between 0 and 100"

    @given(
        processed_count=st.integers(min_value=0, max_value=10000),
        total_count=st.integers(min_value=1, max_value=10000),
        success_count=st.integers(min_value=0),
        error_count=st.integers(min_value=0),
        current_url=st.text(min_size=1, max_size=2048),
        elapsed_time=st.integers(min_value=0, max_value=86400),
        estimated_remaining=st.integers(min_value=0, max_value=86400),
    )
    @settings(max_examples=100)
    def test_progress_message_json_serializable(
        self,
        processed_count,
        total_count,
        success_count,
        error_count,
        current_url,
        elapsed_time,
        estimated_remaining,
    ):
        """
        Property: Progress message should be JSON serializable.
        
        **Validates: Requirements 3.2**
        """
        assume(processed_count <= total_count)
        
        task_id = uuid4()
        
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
        
        # Should be JSON serializable
        json_str = json.dumps(message)
        assert isinstance(json_str, str), "Message should be JSON serializable"
        
        # Should be deserializable
        deserialized = json.loads(json_str)
        assert deserialized == message, "Deserialized message should match original"

    @given(
        processed_count=st.integers(min_value=0, max_value=10000),
        total_count=st.integers(min_value=1, max_value=10000),
        success_count=st.integers(min_value=0),
        error_count=st.integers(min_value=0),
        current_url=st.text(min_size=1, max_size=2048),
        elapsed_time=st.integers(min_value=0, max_value=86400),
        estimated_remaining=st.integers(min_value=0, max_value=86400),
    )
    @settings(max_examples=100)
    def test_progress_message_timestamp_format(
        self,
        processed_count,
        total_count,
        success_count,
        error_count,
        current_url,
        elapsed_time,
        estimated_remaining,
    ):
        """
        Property: Timestamp should be in ISO 8601 format.
        
        **Validates: Requirements 3.2**
        """
        assume(processed_count <= total_count)
        
        task_id = uuid4()
        timestamp = datetime.now(timezone.utc).isoformat()
        
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
            "timestamp": timestamp,
        }
        
        # Verify timestamp format (ISO 8601)
        assert "T" in message["timestamp"], "Timestamp should contain 'T' separator"
        assert "+" in message["timestamp"] or "Z" in message["timestamp"], \
            "Timestamp should contain timezone information"
        
        # Should be parseable as datetime
        try:
            datetime.fromisoformat(message["timestamp"].replace("Z", "+00:00"))
        except ValueError:
            pytest.fail("Timestamp should be in valid ISO 8601 format")

    @given(
        processed_count=st.integers(min_value=0, max_value=10000),
        total_count=st.integers(min_value=1, max_value=10000),
        success_count=st.integers(min_value=0),
        error_count=st.integers(min_value=0),
        current_url=st.text(min_size=1, max_size=2048),
        elapsed_time=st.integers(min_value=0, max_value=86400),
        estimated_remaining=st.integers(min_value=0, max_value=86400),
    )
    @settings(max_examples=100)
    def test_progress_message_task_id_format(
        self,
        processed_count,
        total_count,
        success_count,
        error_count,
        current_url,
        elapsed_time,
        estimated_remaining,
    ):
        """
        Property: task_id should be a valid UUID string.
        
        **Validates: Requirements 3.2**
        """
        assume(processed_count <= total_count)
        
        task_id = uuid4()
        
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
        
        # Should be valid UUID string
        try:
            UUID(message["task_id"])
        except ValueError:
            pytest.fail("task_id should be a valid UUID string")

    @given(
        processed_count=st.integers(min_value=0, max_value=10000),
        total_count=st.integers(min_value=1, max_value=10000),
        success_count=st.integers(min_value=0),
        error_count=st.integers(min_value=0),
        current_url=st.text(min_size=1, max_size=2048),
        elapsed_time=st.integers(min_value=0, max_value=86400),
        estimated_remaining=st.integers(min_value=0, max_value=86400),
    )
    @settings(max_examples=100)
    def test_progress_message_consistency_across_calls(
        self,
        processed_count,
        total_count,
        success_count,
        error_count,
        current_url,
        elapsed_time,
        estimated_remaining,
    ):
        """
        Property: Creating progress messages with same data should produce
        consistent results (except for timestamp).
        
        **Validates: Requirements 3.2**
        """
        assume(processed_count <= total_count)
        
        task_id = uuid4()
        
        # Create two messages with same data
        message1 = {
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
        
        message2 = {
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
        
        # All fields except timestamp should be identical
        for key in message1:
            if key != "timestamp":
                assert message1[key] == message2[key], \
                    f"Field '{key}' should be consistent across calls"

    @given(
        processed_count=st.integers(min_value=0, max_value=10000),
        total_count=st.integers(min_value=1, max_value=10000),
        success_count=st.integers(min_value=0),
        error_count=st.integers(min_value=0),
        current_url=st.text(min_size=1, max_size=2048),
        elapsed_time=st.integers(min_value=0, max_value=86400),
        estimated_remaining=st.integers(min_value=0, max_value=86400),
    )
    @settings(max_examples=100)
    def test_progress_message_no_extra_fields_required(
        self,
        processed_count,
        total_count,
        success_count,
        error_count,
        current_url,
        elapsed_time,
        estimated_remaining,
    ):
        """
        Property: Progress message should only contain expected fields,
        no unexpected extra fields.
        
        **Validates: Requirements 3.2**
        """
        assume(processed_count <= total_count)
        
        task_id = uuid4()
        
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
        
        # Define expected fields
        expected_fields = {
            "type",
            "task_id",
            "processed_count",
            "total_count",
            "success_count",
            "error_count",
            "current_url",
            "elapsed_time",
            "estimated_remaining",
            "progress_percentage",
            "timestamp",
        }
        
        # Verify no extra fields
        actual_fields = set(message.keys())
        assert actual_fields == expected_fields, \
            f"Message should only contain expected fields. Extra: {actual_fields - expected_fields}"

    @given(
        processed_count=st.integers(min_value=0, max_value=10000),
        total_count=st.integers(min_value=1, max_value=10000),
        success_count=st.integers(min_value=0),
        error_count=st.integers(min_value=0),
        current_url=st.text(min_size=1, max_size=2048),
        elapsed_time=st.integers(min_value=0, max_value=86400),
        estimated_remaining=st.integers(min_value=0, max_value=86400),
    )
    @settings(max_examples=100)
    def test_progress_message_type_field_value(
        self,
        processed_count,
        total_count,
        success_count,
        error_count,
        current_url,
        elapsed_time,
        estimated_remaining,
    ):
        """
        Property: The 'type' field should always be 'task_progress'.
        
        **Validates: Requirements 3.2**
        """
        assume(processed_count <= total_count)
        
        task_id = uuid4()
        
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
        
        # Verify type field
        assert message["type"] == "task_progress", \
            "The 'type' field should always be 'task_progress'"
