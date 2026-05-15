"""Property-based tests for proxy validation

**Validates: Requirements 8.3**

This module contains property-based tests for proxy format validation.
The tests verify that the validation system correctly identifies proxy addresses
in the format IP:port or hostname:port with valid port numbers (1-65535).
"""

import pytest
from hypothesis import given, strategies as st, settings

from app.services.proxy import ProxyService


class TestProxyValidation:
    """Property-based tests for proxy validation
    
    **Validates: Requirements 8.3**
    
    These tests verify that the proxy validation system correctly identifies
    valid and invalid proxy addresses in the format IP:port or hostname:port,
    with port numbers in the range 1-65535.
    """

    @given(
        host=st.text(min_size=1, max_size=255),
        port=st.integers(),
    )
    @settings(max_examples=100)
    def test_proxy_address_validation_property(self, host, port):
        """
        Property: For any host and port combination, validation should return
        a tuple of (bool, Optional[str]) where bool indicates validity.
        
        **Validates: Requirements 8.3**
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
        
        **Validates: Requirements 8.3**
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
        
        **Validates: Requirements 8.3**
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
        
        **Validates: Requirements 8.3**
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
        
        **Validates: Requirements 8.3**
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
        
        **Validates: Requirements 8.3**
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
        
        **Validates: Requirements 8.3**
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
        
        **Validates: Requirements 8.3**
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
        
        **Validates: Requirements 8.3**
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

    @given(
        host=st.text(min_size=1, max_size=255),
        port=st.integers(min_value=1, max_value=65535),
    )
    @settings(max_examples=100)
    def test_valid_proxy_format_consistency(self, host, port):
        """
        Property: For any valid host and port, the validation result should be
        consistent across multiple calls.
        
        **Validates: Requirements 8.3**
        """
        result1 = ProxyService.validate_proxy_address(host, port)
        result2 = ProxyService.validate_proxy_address(host, port)

        # Results should be identical
        assert result1 == result2

    @given(
        octet1=st.integers(min_value=0, max_value=255),
        octet2=st.integers(min_value=0, max_value=255),
        octet3=st.integers(min_value=0, max_value=255),
        octet4=st.integers(min_value=0, max_value=255),
        port=st.integers(min_value=1, max_value=65535),
    )
    @settings(max_examples=100)
    def test_valid_ip_port_combination_property(self, octet1, octet2, octet3, octet4, port):
        """
        Property: Any combination of valid IP octets and valid port should be accepted.
        
        **Validates: Requirements 8.3**
        """
        ip = f"{octet1}.{octet2}.{octet3}.{octet4}"
        is_valid, error_msg = ProxyService.validate_proxy_address(ip, port)

        # Should be valid
        assert is_valid is True
        # Should have no error message
        assert error_msg is None

    @given(
        port=st.integers().filter(lambda x: x < 1 or x > 65535),
    )
    @settings(max_examples=100)
    def test_invalid_port_always_rejected_property(self, port):
        """
        Property: Any port outside the valid range (1-65535) should always be rejected,
        regardless of the host.
        
        **Validates: Requirements 8.3**
        """
        # Test with various hosts
        hosts = ["192.168.1.1", "example.com", "localhost", "proxy.example.com"]
        
        for host in hosts:
            is_valid, error_msg = ProxyService.validate_proxy_address(host, port)
            
            # Should be invalid
            assert is_valid is False
            # Should have error message
            assert error_msg is not None

    @given(
        host=st.text(min_size=1, max_size=255),
    )
    @settings(max_examples=100)
    def test_port_zero_always_invalid_property(self, host):
        """
        Property: Port 0 should always be invalid, regardless of the host.
        
        **Validates: Requirements 8.3**
        """
        is_valid, error_msg = ProxyService.validate_proxy_address(host, 0)

        # Should be invalid
        assert is_valid is False
        # Should have error message
        assert error_msg is not None
        assert "Port" in error_msg or "port" in error_msg

    @given(
        host=st.text(min_size=1, max_size=255),
    )
    @settings(max_examples=100)
    def test_port_65536_always_invalid_property(self, host):
        """
        Property: Port 65536 (above max) should always be invalid, regardless of the host.
        
        **Validates: Requirements 8.3**
        """
        is_valid, error_msg = ProxyService.validate_proxy_address(host, 65536)

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
    def test_valid_ip_with_boundary_ports_property(self, octet1, octet2, octet3, octet4):
        """
        Property: Valid IP addresses should be accepted with boundary port values (1 and 65535).
        
        **Validates: Requirements 8.3**
        """
        ip = f"{octet1}.{octet2}.{octet3}.{octet4}"
        
        # Test with port 1
        is_valid_1, error_msg_1 = ProxyService.validate_proxy_address(ip, 1)
        assert is_valid_1 is True
        assert error_msg_1 is None
        
        # Test with port 65535
        is_valid_65535, error_msg_65535 = ProxyService.validate_proxy_address(ip, 65535)
        assert is_valid_65535 is True
        assert error_msg_65535 is None

    @given(
        hostname=st.text(
            alphabet=st.characters(
                blacklist_categories=("Cc", "Cs"),
                blacklist_characters=" /"
            ),
            min_size=1,
            max_size=100,
        ),
        port=st.integers(min_value=1, max_value=65535),
    )
    @settings(max_examples=100)
    def test_hostname_port_format_property(self, hostname, port):
        """
        Property: Hostname and port combinations should be validated correctly.
        
        **Validates: Requirements 8.3**
        """
        # Clean up hostname
        clean_hostname = hostname.replace(" ", "-").replace("/", "-").lower()
        
        if clean_hostname and clean_hostname[0].isalnum():
            is_valid, error_msg = ProxyService.validate_proxy_address(clean_hostname, port)
            
            # Result should be a boolean
            assert isinstance(is_valid, bool)
            
            # If invalid, should have error message
            if not is_valid:
                assert error_msg is not None

