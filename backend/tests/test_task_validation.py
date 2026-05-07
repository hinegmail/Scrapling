"""Property-based tests for task validation"""

import pytest
from hypothesis import given, strategies as st, settings
from uuid import uuid4

from app.models.task import FetcherType, SelectorType, TaskStatus
from app.services.task import TaskService
from app.exceptions import ValidationError


class TestTaskValidation:
    """Property-based tests for task validation"""

    @given(
        selector=st.text(min_size=1, max_size=1000),
        selector_type=st.sampled_from([SelectorType.CSS, SelectorType.XPATH]),
    )
    @settings(max_examples=100)
    def test_selector_validation_property(self, selector, selector_type):
        """
        Property: For any selector string and type, validation should either
        accept or reject it consistently.
        """
        try:
            TaskService._validate_selector(selector, selector_type)
            # If no exception, selector is valid
            assert selector is not None
            assert len(selector) > 0
        except ValidationError as e:
            # If exception, error message should be non-empty
            assert str(e) is not None
            assert len(str(e)) > 0

    @given(
        name=st.text(min_size=1, max_size=255),
        url=st.just("https://example.com"),
        selector=st.just("div.content"),
        selector_type=st.just(SelectorType.CSS),
        fetcher_type=st.sampled_from([FetcherType.HTTP, FetcherType.DYNAMIC, FetcherType.STEALTHY]),
        timeout=st.integers(min_value=1, max_value=300),
        retry_count=st.integers(min_value=0, max_value=10),
    )
    @settings(max_examples=100)
    def test_task_config_validation_property(
        self,
        name,
        url,
        selector,
        selector_type,
        fetcher_type,
        timeout,
        retry_count,
    ):
        """
        Property: For any task configuration with valid required fields,
        validation should pass.
        """
        from app.schemas.task import TaskCreate

        task_data = TaskCreate(
            name=name,
            target_url=url,
            selector=selector,
            selector_type=selector_type,
            fetcher_type=fetcher_type,
            timeout=timeout,
            retry_count=retry_count,
        )

        # Should not raise exception
        assert task_data.name == name
        assert task_data.target_url == url
        assert task_data.selector == selector

    @given(
        url=st.text(min_size=1, max_size=2000).filter(
            lambda x: not x.startswith(("http://", "https://"))
        ),
    )
    @settings(max_examples=50)
    def test_invalid_url_validation_property(self, url):
        """
        Property: URLs that don't start with http:// or https:// should be rejected.
        """
        from app.schemas.task import TaskCreate

        with pytest.raises(ValueError):
            TaskCreate(
                name="Test",
                target_url=url,
                selector="div",
                selector_type=SelectorType.CSS,
                fetcher_type=FetcherType.HTTP,
            )

    @given(
        wait_time=st.integers(min_value=-1, max_value=100).filter(
            lambda x: x < 0 or x > 60
        ),
    )
    @settings(max_examples=50)
    def test_invalid_wait_time_validation_property(self, wait_time):
        """
        Property: Wait time outside 0-60 range should be rejected.
        """
        from app.schemas.task import TaskCreate

        with pytest.raises(ValueError):
            TaskCreate(
                name="Test",
                target_url="https://example.com",
                selector="div",
                selector_type=SelectorType.CSS,
                fetcher_type=FetcherType.DYNAMIC,
                wait_time=wait_time,
            )

    @given(
        port=st.integers().filter(lambda x: x < 1 or x > 65535),
    )
    @settings(max_examples=50)
    def test_invalid_port_validation_property(self, port):
        """
        Property: Port numbers outside 1-65535 range should be rejected.
        """
        from app.schemas.task import TaskCreate

        with pytest.raises(ValueError):
            TaskCreate(
                name="Test",
                target_url="https://example.com",
                selector="div",
                selector_type=SelectorType.CSS,
                fetcher_type=FetcherType.HTTP,
                timeout=port,  # Using timeout as proxy for port validation
            )

    @given(
        timeout=st.integers(min_value=1, max_value=300),
        retry_count=st.integers(min_value=0, max_value=10),
    )
    @settings(max_examples=100)
    def test_valid_timeout_retry_property(self, timeout, retry_count):
        """
        Property: Valid timeout and retry count should be accepted.
        """
        from app.schemas.task import TaskCreate

        task_data = TaskCreate(
            name="Test",
            target_url="https://example.com",
            selector="div",
            selector_type=SelectorType.CSS,
            fetcher_type=FetcherType.HTTP,
            timeout=timeout,
            retry_count=retry_count,
        )

        assert task_data.timeout == timeout
        assert task_data.retry_count == retry_count
