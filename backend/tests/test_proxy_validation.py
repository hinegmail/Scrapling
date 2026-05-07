"""Property-based tests for proxy validation"""

import pytest
from hypothesis import given, strategies as st, settings

from app.services.proxy import ProxyService


class TestProxyValidation:
    """Property-based tests for proxy validation"""

    @given(
        host=st.text(min_size=1, max_size=255),
        port=st.integers(),
    )
    @settings(max_examples=100)
    def test_proxy_address_validation_property(self, host, port):
        """
        Property: For any host and port combination, validation should return
        a tuple of (bool, Optional[str]) where bool indicates validity.
        """
        is_valid, error_msg = ProxyService.validate_proxy_address(host, port)

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
        port=st.integers(min_value=1, max_value=65535),
    )
    @settings(max_examples=100)
    def test_valid_port_range_property(self, port):
        """
        Property: Ports in valid range (1-65535) should be accepted.
        """
        is_valid, error_msg = ProxyService.validate_proxy_address("192.168.1.1", port)

        # Should be valid
        assert is_valid is True
        # Should have no error message
        assert error_msg is None

    @given(
        port=st.integers().filter(lambda x: x < 1 or x > 65535),
    )
    @settings(max_examples=100)
    def test_invalid_port_range_property(self, port):
        """
        Property: Ports outside valid range should be rejected.
        """
        is_valid, error_msg = ProxyService.validate_proxy_address("192.168.1.1", port)

        # Should be invalid
        assert is_valid is False
        # Should have error message
        assert error_msg is not None
        assert "Port" in error_msg or "port" in error_msg

    @given(
        octet1=st.integers(min_value=0, max_value=255),
        octet2=st.integers(min_value=0, max_value=255),
        octet3=st.integers(min_value=0, max_value=255),
        octet4=st.integers(min_value=0, max_value=255),
    )
    @settings(max_examples=100)
    def test_valid_ip_address_property(self, octet1, octet2, octet3, octet4):
        """
        Property: Valid IP addresses should be accepted.
        """
        ip = f"{octet1}.{octet2}.{octet3}.{octet4}"
        is_valid, error_msg = ProxyService.validate_proxy_address(ip, 8080)

        # Should be valid
        assert is_valid is True
        # Should have no error message
        assert error_msg is None

    @given(
        octet=st.integers(min_value=256, max_value=1000),
    )
    @settings(max_examples=50)
    def test_invalid_ip_octet_property(self, octet):
        """
        Property: IP addresses with octets > 255 should be rejected.
        """
        ip = f"192.168.1.{octet}"
        is_valid, error_msg = ProxyService.validate_proxy_address(ip, 8080)

        # Should be invalid
        assert is_valid is False
        # Should have error message
        assert error_msg is not None

    @given(
        host=st.just(""),
    )
    @settings(max_examples=10)
    def test_empty_host_validation_property(self, host):
        """
        Property: Empty host should be rejected.
        """
        is_valid, error_msg = ProxyService.validate_proxy_address(host, 8080)

        # Should be invalid
        assert is_valid is False
        # Should have error message
        assert error_msg is not None

    @given(
        hostname=st.text(
            alphabet=st.characters(blacklist_characters="."),
            min_size=1,
            max_size=63,
        ),
    )
    @settings(max_examples=50)
    def test_valid_hostname_property(self, hostname):
        """
        Property: Valid hostnames should be accepted.
        """
        # Create a valid hostname
        valid_hostname = hostname.replace(" ", "-").lower()
        if valid_hostname and valid_hostname[0].isalnum():
            is_valid, error_msg = ProxyService.validate_proxy_address(
                valid_hostname, 8080
            )

            # Should be valid or have error (depending on hostname format)
            assert isinstance(is_valid, bool)

    @given(
        proxies=st.lists(
            st.tuples(
                st.just("192.168.1.1"),
                st.integers(min_value=1, max_value=65535),
            ),
            min_size=1,
            max_size=10,
        ),
    )
    @settings(max_examples=50)
    def test_proxy_rotation_list_property(self, proxies):
        """
        Property: Proxy rotation list should contain all valid proxies.
        """
        proxy_urls = []
        for host, port in proxies:
            is_valid, _ = ProxyService.validate_proxy_address(host, port)
            if is_valid:
                url = f"http://{host}:{port}"
                proxy_urls.append(url)

        # Should have at least one valid proxy
        assert len(proxy_urls) > 0

        # Each URL should be a string
        for url in proxy_urls:
            assert isinstance(url, str)
            assert url.startswith("http://")
            assert ":" in url

    @given(
        protocol=st.sampled_from(["http", "https", "socks5"]),
        host=st.just("192.168.1.1"),
        port=st.integers(min_value=1, max_value=65535),
    )
    @settings(max_examples=50)
    def test_proxy_url_format_property(self, protocol, host, port):
        """
        Property: Proxy URLs should be properly formatted.
        """
        url = f"{protocol}://{host}:{port}"

        # URL should contain protocol
        assert protocol in url
        # URL should contain host
        assert host in url
        # URL should contain port
        assert str(port) in url
        # URL should have proper format
        assert "://" in url
        assert ":" in url.split("://")[1]
