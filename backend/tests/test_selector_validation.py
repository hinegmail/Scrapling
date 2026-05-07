"""Property-based tests for selector validation"""

import pytest
from hypothesis import given, strategies as st, settings

from app.services.selector_validator import SelectorValidator


class TestSelectorValidation:
    """Property-based tests for selector validation"""

    @given(
        selector=st.text(min_size=1, max_size=1000),
    )
    @settings(max_examples=100)
    def test_css_selector_validation_property(self, selector):
        """
        Property: For any CSS selector string, validation should return
        a tuple of (bool, Optional[str]) where bool indicates validity.
        """
        is_valid, error_msg = SelectorValidator.validate_css_selector(selector)

        # Result should be a boolean
        assert isinstance(is_valid, bool)

        # If invalid, error message should be non-empty
        if not is_valid:
            assert error_msg is not None
            assert len(error_msg) > 0
        else:
            # If valid, error message should be None
            assert error_msg is None

    @given(
        selector=st.text(min_size=1, max_size=1000),
    )
    @settings(max_examples=100)
    def test_xpath_selector_validation_property(self, selector):
        """
        Property: For any XPath selector string, validation should return
        a tuple of (bool, Optional[str]) where bool indicates validity.
        """
        is_valid, error_msg = SelectorValidator.validate_xpath_selector(selector)

        # Result should be a boolean
        assert isinstance(is_valid, bool)

        # If invalid, error message should be non-empty
        if not is_valid:
            assert error_msg is not None
            assert len(error_msg) > 0
        else:
            # If valid, error message should be None
            assert error_msg is None

    @given(
        selector=st.just("div.content"),
        selector_type=st.sampled_from(["css", "xpath"]),
    )
    @settings(max_examples=50)
    def test_selector_type_dispatch_property(self, selector, selector_type):
        """
        Property: validate_selector should dispatch to correct validator
        based on selector_type.
        """
        is_valid, error_msg = SelectorValidator.validate_selector(selector, selector_type)

        # Result should be a boolean
        assert isinstance(is_valid, bool)

        # If invalid, error message should be non-empty
        if not is_valid:
            assert error_msg is not None

    @given(
        selector=st.text(min_size=1, max_size=1000),
        selector_type=st.text(min_size=1, max_size=50).filter(
            lambda x: x not in ["css", "xpath"]
        ),
    )
    @settings(max_examples=50)
    def test_unknown_selector_type_property(self, selector, selector_type):
        """
        Property: Unknown selector types should return invalid with error message.
        """
        is_valid, error_msg = SelectorValidator.validate_selector(selector, selector_type)

        # Should be invalid
        assert is_valid is False
        # Should have error message
        assert error_msg is not None
        assert "Unknown" in error_msg or "unknown" in error_msg

    @given(
        selector=st.just(""),
    )
    @settings(max_examples=10)
    def test_empty_selector_validation_property(self, selector):
        """
        Property: Empty selectors should be rejected.
        """
        is_valid_css, _ = SelectorValidator.validate_css_selector(selector)
        is_valid_xpath, _ = SelectorValidator.validate_xpath_selector(selector)

        # Both should be invalid
        assert is_valid_css is False
        assert is_valid_xpath is False

    @given(
        selector=st.text(min_size=1, max_size=1000),
    )
    @settings(max_examples=100)
    def test_selector_suggestions_property(self, selector):
        """
        Property: For invalid selectors, suggestions should be a non-empty list.
        """
        is_valid, error_msg = SelectorValidator.validate_css_selector(selector)

        if not is_valid and error_msg:
            suggestions = SelectorValidator.get_selector_suggestions(
                selector, "css", error_msg
            )

            # Suggestions should be a list
            assert isinstance(suggestions, list)
            # Should have at least one suggestion
            assert len(suggestions) > 0
            # Each suggestion should be a string
            for suggestion in suggestions:
                assert isinstance(suggestion, str)
                assert len(suggestion) > 0

    @given(
        html=st.just("<div class='content'>Test</div>"),
        selector=st.just("div.content"),
        selector_type=st.just("css"),
    )
    @settings(max_examples=10)
    def test_selector_test_property(self, html, selector, selector_type):
        """
        Property: Testing a valid selector against HTML should return
        a tuple of (int, list) where int is match count.
        """
        try:
            match_count, preview_data = SelectorValidator.test_selector(
                html, selector, selector_type
            )

            # Match count should be non-negative integer
            assert isinstance(match_count, int)
            assert match_count >= 0

            # Preview data should be a list
            assert isinstance(preview_data, list)

            # Preview data length should not exceed match count
            assert len(preview_data) <= match_count
            assert len(preview_data) <= 5  # Max 5 previews

            # Each preview should have required fields
            for preview in preview_data:
                assert isinstance(preview, dict)
                assert "index" in preview
                assert "text" in preview
                assert "tag" in preview
        except Exception as e:
            # If error, it should be a string
            assert isinstance(str(e), str)
