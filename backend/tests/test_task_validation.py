"""Property-based tests for task validation

**Validates: Requirements 2.5**

This module contains property-based tests for task configuration validation.
The tests verify that the validation system correctly identifies missing required
fields and rejects invalid configurations across various input combinations.
"""

import pytest
from hypothesis import given, strategies as st, settings, assume
from uuid import uuid4

from app.models.task import FetcherType, SelectorType, TaskStatus
from app.services.task import TaskService
from app.exceptions import ValidationError
from app.schemas.task import TaskCreate


# Strategy for generating valid task names
valid_task_names = st.text(
    alphabet=st.characters(blacklist_categories=("Cc", "Cs")),
    min_size=1,
    max_size=255
)

# Strategy for generating valid URLs
valid_urls = st.just("https://example.com") | st.just("http://example.com")

# Strategy for generating valid CSS selectors
valid_css_selectors = st.sampled_from([
    "div",
    "div.class",
    "div#id",
    "div > p",
    "div.class > p.text",
    "div[data-attr='value']",
    ".class",
    "#id",
    "div, p",
    "div.class1.class2",
])

# Strategy for generating valid XPath selectors
valid_xpath_selectors = st.sampled_from([
    "//div",
    "//div[@class='content']",
    "//div/p",
    "//div[@id='main']//p",
    "//*[@class='item']",
    "//div[contains(@class, 'active')]",
    ".//div",
    "//div[@data-id='123']",
])

# Strategy for generating invalid CSS selectors
invalid_css_selectors = st.sampled_from([
    " div",  # starts with space
    "div ",  # ends with space
    "div[[",  # invalid brackets
    "div]]",  # invalid brackets
])

# Strategy for generating invalid XPath selectors
invalid_xpath_selectors = st.sampled_from([
    "div",  # doesn't start with / or .
    "p",  # doesn't start with / or .
    "//div[",  # unbalanced brackets
    "//div]",  # unbalanced brackets
    "//div[[@attr='value']",  # unbalanced brackets
])


class TestTaskConfigurationValidation:
    """Property-based tests for task configuration validation
    
    **Validates: Requirements 2.5**
    
    These tests verify that the task validation system correctly identifies
    missing required fields and rejects invalid configurations.
    """

    @given(
        name=valid_task_names,
        url=valid_urls,
        selector=valid_css_selectors,
        fetcher_type=st.sampled_from([FetcherType.HTTP, FetcherType.DYNAMIC, FetcherType.STEALTHY]),
        timeout=st.integers(min_value=1, max_value=300),
        retry_count=st.integers(min_value=0, max_value=10),
    )
    @settings(max_examples=100)
    def test_valid_task_config_accepted(
        self,
        name,
        url,
        selector,
        fetcher_type,
        timeout,
        retry_count,
    ):
        """
        Property: For any task configuration with all valid required fields,
        the validation system should accept the configuration without raising
        an exception.
        
        **Validates: Requirements 2.5**
        """
        task_data = TaskCreate(
            name=name,
            target_url=url,
            selector=selector,
            selector_type=SelectorType.CSS,
            fetcher_type=fetcher_type,
            timeout=timeout,
            retry_count=retry_count,
        )

        # Validation should pass - no exception raised
        assert task_data.name == name
        assert task_data.target_url == url
        assert task_data.selector == selector
        assert task_data.fetcher_type == fetcher_type
        assert task_data.timeout == timeout
        assert task_data.retry_count == retry_count

    @given(
        url=st.text(min_size=1, max_size=2000).filter(
            lambda x: not x.startswith(("http://", "https://"))
        ),
    )
    @settings(max_examples=50)
    def test_invalid_url_rejected(self, url):
        """
        Property: URLs that don't start with http:// or https:// should be
        rejected with a validation error.
        
        **Validates: Requirements 2.5**
        """
        with pytest.raises(ValueError):
            TaskCreate(
                name="Test Task",
                target_url=url,
                selector="div",
                selector_type=SelectorType.CSS,
                fetcher_type=FetcherType.HTTP,
            )

    @given(
        selector=invalid_css_selectors,
    )
    @settings(max_examples=50)
    def test_invalid_css_selector_rejected(self, selector):
        """
        Property: Invalid CSS selectors should be rejected with a validation error.
        
        **Validates: Requirements 2.5**
        """
        with pytest.raises(ValueError):
            TaskCreate(
                name="Test Task",
                target_url="https://example.com",
                selector=selector,
                selector_type=SelectorType.CSS,
                fetcher_type=FetcherType.HTTP,
            )

    @given(
        selector=invalid_xpath_selectors,
    )
    @settings(max_examples=50)
    def test_invalid_xpath_selector_rejected(self, selector):
        """
        Property: Invalid XPath selectors should be rejected with a validation error.
        
        **Validates: Requirements 2.5**
        """
        with pytest.raises(ValueError):
            TaskCreate(
                name="Test Task",
                target_url="https://example.com",
                selector=selector,
                selector_type=SelectorType.XPATH,
                fetcher_type=FetcherType.HTTP,
            )

    @given(
        timeout=st.integers().filter(lambda x: x < 1 or x > 300),
    )
    @settings(max_examples=50)
    def test_invalid_timeout_rejected(self, timeout):
        """
        Property: Timeout values outside the valid range (1-300) should be rejected.
        
        **Validates: Requirements 2.5**
        """
        with pytest.raises(ValueError):
            TaskCreate(
                name="Test Task",
                target_url="https://example.com",
                selector="div",
                selector_type=SelectorType.CSS,
                fetcher_type=FetcherType.HTTP,
                timeout=timeout,
            )

    @given(
        retry_count=st.integers().filter(lambda x: x < 0 or x > 10),
    )
    @settings(max_examples=50)
    def test_invalid_retry_count_rejected(self, retry_count):
        """
        Property: Retry count values outside the valid range (0-10) should be rejected.
        
        **Validates: Requirements 2.5**
        """
        with pytest.raises(ValueError):
            TaskCreate(
                name="Test Task",
                target_url="https://example.com",
                selector="div",
                selector_type=SelectorType.CSS,
                fetcher_type=FetcherType.HTTP,
                retry_count=retry_count,
            )

    @given(
        wait_time=st.integers().filter(lambda x: x is not None and (x < 0 or x > 60)),
    )
    @settings(max_examples=50)
    def test_invalid_wait_time_rejected(self, wait_time):
        """
        Property: Wait time values outside the valid range (0-60) should be rejected.
        
        **Validates: Requirements 2.5**
        """
        with pytest.raises(ValueError):
            TaskCreate(
                name="Test Task",
                target_url="https://example.com",
                selector="div",
                selector_type=SelectorType.CSS,
                fetcher_type=FetcherType.DYNAMIC,
                wait_time=wait_time,
            )

    @given(
        viewport_width=st.integers().filter(lambda x: x < 320 or x > 1920),
    )
    @settings(max_examples=50)
    def test_invalid_viewport_width_rejected(self, viewport_width):
        """
        Property: Viewport width values outside the valid range (320-1920) should be rejected.
        
        **Validates: Requirements 2.5**
        """
        with pytest.raises(ValueError):
            TaskCreate(
                name="Test Task",
                target_url="https://example.com",
                selector="div",
                selector_type=SelectorType.CSS,
                fetcher_type=FetcherType.DYNAMIC,
                viewport_width=viewport_width,
            )

    @given(
        viewport_height=st.integers().filter(lambda x: x < 240 or x > 1080),
    )
    @settings(max_examples=50)
    def test_invalid_viewport_height_rejected(self, viewport_height):
        """
        Property: Viewport height values outside the valid range (240-1080) should be rejected.
        
        **Validates: Requirements 2.5**
        """
        with pytest.raises(ValueError):
            TaskCreate(
                name="Test Task",
                target_url="https://example.com",
                selector="div",
                selector_type=SelectorType.CSS,
                fetcher_type=FetcherType.DYNAMIC,
                viewport_height=viewport_height,
            )

    @given(
        name=st.text(min_size=1, max_size=255),
        url=valid_urls,
        selector=valid_css_selectors,
        timeout=st.integers(min_value=1, max_value=300),
        retry_count=st.integers(min_value=0, max_value=10),
        wait_time=st.one_of(st.none(), st.integers(min_value=0, max_value=60)),
        viewport_width=st.one_of(st.none(), st.integers(min_value=320, max_value=1920)),
        viewport_height=st.one_of(st.none(), st.integers(min_value=240, max_value=1080)),
    )
    @settings(max_examples=100)
    def test_optional_fields_combination(
        self,
        name,
        url,
        selector,
        timeout,
        retry_count,
        wait_time,
        viewport_width,
        viewport_height,
    ):
        """
        Property: Task configuration should accept various combinations of
        optional fields (wait_time, viewport_width, viewport_height) without
        raising validation errors when all required fields are valid.
        
        **Validates: Requirements 2.5**
        """
        task_data = TaskCreate(
            name=name,
            target_url=url,
            selector=selector,
            selector_type=SelectorType.CSS,
            fetcher_type=FetcherType.DYNAMIC,
            timeout=timeout,
            retry_count=retry_count,
            wait_time=wait_time,
            viewport_width=viewport_width,
            viewport_height=viewport_height,
        )

        # Validation should pass
        assert task_data.name == name
        assert task_data.target_url == url
        assert task_data.selector == selector
        assert task_data.wait_time == wait_time
        assert task_data.viewport_width == viewport_width
        assert task_data.viewport_height == viewport_height

    @given(
        name=st.text(min_size=1, max_size=255),
        url=valid_urls,
        selector=valid_xpath_selectors,
        timeout=st.integers(min_value=1, max_value=300),
        retry_count=st.integers(min_value=0, max_value=10),
    )
    @settings(max_examples=100)
    def test_xpath_selector_validation(
        self,
        name,
        url,
        selector,
        timeout,
        retry_count,
    ):
        """
        Property: Task configuration with valid XPath selectors should be accepted.
        
        **Validates: Requirements 2.5**
        """
        task_data = TaskCreate(
            name=name,
            target_url=url,
            selector=selector,
            selector_type=SelectorType.XPATH,
            fetcher_type=FetcherType.HTTP,
            timeout=timeout,
            retry_count=retry_count,
        )

        # Validation should pass
        assert task_data.selector == selector
        assert task_data.selector_type == SelectorType.XPATH

    @given(
        name=st.text(min_size=1, max_size=255),
        url=valid_urls,
        selector=valid_css_selectors,
        timeout=st.integers(min_value=1, max_value=300),
        retry_count=st.integers(min_value=0, max_value=10),
        use_proxy_rotation=st.booleans(),
        solve_cloudflare=st.booleans(),
    )
    @settings(max_examples=100)
    def test_advanced_options_validation(
        self,
        name,
        url,
        selector,
        timeout,
        retry_count,
        use_proxy_rotation,
        solve_cloudflare,
    ):
        """
        Property: Task configuration with various combinations of advanced options
        (proxy rotation, Cloudflare solving) should be accepted when all required
        fields are valid.
        
        **Validates: Requirements 2.5**
        """
        task_data = TaskCreate(
            name=name,
            target_url=url,
            selector=selector,
            selector_type=SelectorType.CSS,
            fetcher_type=FetcherType.STEALTHY,
            timeout=timeout,
            retry_count=retry_count,
            use_proxy_rotation=use_proxy_rotation,
            solve_cloudflare=solve_cloudflare,
        )

        # Validation should pass
        assert task_data.use_proxy_rotation == use_proxy_rotation
        assert task_data.solve_cloudflare == solve_cloudflare

    @given(
        name=st.text(min_size=1, max_size=255),
        url=valid_urls,
        selector=valid_css_selectors,
        timeout=st.integers(min_value=1, max_value=300),
        retry_count=st.integers(min_value=0, max_value=10),
        custom_headers=st.one_of(
            st.none(),
            st.dictionaries(
                keys=st.text(min_size=1, max_size=50),
                values=st.text(min_size=1, max_size=100),
                min_size=0,
                max_size=5,
            ),
        ),
        cookies=st.one_of(
            st.none(),
            st.dictionaries(
                keys=st.text(min_size=1, max_size=50),
                values=st.text(min_size=1, max_size=100),
                min_size=0,
                max_size=5,
            ),
        ),
    )
    @settings(max_examples=100)
    def test_custom_headers_and_cookies_validation(
        self,
        name,
        url,
        selector,
        timeout,
        retry_count,
        custom_headers,
        cookies,
    ):
        """
        Property: Task configuration with custom headers and cookies should be
        accepted when all required fields are valid.
        
        **Validates: Requirements 2.5**
        """
        task_data = TaskCreate(
            name=name,
            target_url=url,
            selector=selector,
            selector_type=SelectorType.CSS,
            fetcher_type=FetcherType.HTTP,
            timeout=timeout,
            retry_count=retry_count,
            custom_headers=custom_headers,
            cookies=cookies,
        )

        # Validation should pass
        assert task_data.custom_headers == custom_headers
        assert task_data.cookies == cookies

    @given(
        name=st.text(min_size=1, max_size=255),
        url=valid_urls,
        selector=valid_css_selectors,
        timeout=st.integers(min_value=1, max_value=300),
        retry_count=st.integers(min_value=0, max_value=10),
        description=st.one_of(st.none(), st.text(max_size=1000)),
    )
    @settings(max_examples=100)
    def test_optional_description_field(
        self,
        name,
        url,
        selector,
        timeout,
        retry_count,
        description,
    ):
        """
        Property: Task configuration should accept optional description field
        with any valid value (including None).
        
        **Validates: Requirements 2.5**
        """
        task_data = TaskCreate(
            name=name,
            target_url=url,
            selector=selector,
            selector_type=SelectorType.CSS,
            fetcher_type=FetcherType.HTTP,
            timeout=timeout,
            retry_count=retry_count,
            description=description,
        )

        # Validation should pass
        assert task_data.description == description
