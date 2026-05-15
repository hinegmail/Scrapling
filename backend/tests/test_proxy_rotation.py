"""Property-based tests for proxy rotation logic

**Validates: Requirements 8.4**

This module contains property-based tests for proxy rotation logic.
The tests verify that the rotation system cycles through all available proxies
in a round-robin fashion, repeating the cycle after reaching the end.
"""

import pytest
from hypothesis import given, strategies as st, settings

from app.services.proxy import ProxyService


class TestProxyRotation:
    """Property-based tests for proxy rotation logic
    
    **Validates: Requirements 8.4**
    
    These tests verify that the proxy rotation system correctly cycles through
    all available proxies in a round-robin fashion. For a list of N proxies,
    executing N+1 requests should cycle through all proxies exactly once,
    then repeat the cycle.
    """

    @given(
        proxy_list=st.lists(
            st.text(min_size=1, max_size=100),
            min_size=1,
            max_size=10,
            unique=True,
        ),
        request_index=st.integers(min_value=0, max_value=1000),
    )
    @settings(max_examples=100)
    def test_proxy_rotation_returns_valid_proxy(self, proxy_list, request_index):
        """
        Property: For any non-empty proxy list and request index, rotation should
        return a valid proxy from the list.
        
        **Validates: Requirements 8.4**
        """
        proxy = ProxyService.rotate_proxy(proxy_list, request_index)
        
        # Should return a proxy from the list
        assert proxy in proxy_list

    @given(
        proxy_list=st.lists(
            st.text(min_size=1, max_size=100),
            min_size=1,
            max_size=10,
            unique=True,
        ),
    )
    @settings(max_examples=100)
    def test_proxy_rotation_cycles_through_all_proxies(self, proxy_list):
        """
        Property: For a list of N proxies, executing N requests should use each
        proxy exactly once in order.
        
        **Validates: Requirements 8.4**
        """
        n = len(proxy_list)
        used_proxies = []
        
        # Execute N requests
        for i in range(n):
            proxy = ProxyService.rotate_proxy(proxy_list, i)
            used_proxies.append(proxy)
        
        # Should have used each proxy exactly once
        assert len(used_proxies) == n
        assert set(used_proxies) == set(proxy_list)
        
        # Should be in order
        for i, proxy in enumerate(used_proxies):
            assert proxy == proxy_list[i]

    @given(
        proxy_list=st.lists(
            st.text(min_size=1, max_size=100),
            min_size=1,
            max_size=10,
            unique=True,
        ),
    )
    @settings(max_examples=100)
    def test_proxy_rotation_repeats_cycle(self, proxy_list):
        """
        Property: For a list of N proxies, after N requests, the cycle should
        repeat from the beginning.
        
        **Validates: Requirements 8.4**
        """
        n = len(proxy_list)
        
        # Get proxies for first cycle
        first_cycle = [ProxyService.rotate_proxy(proxy_list, i) for i in range(n)]
        
        # Get proxies for second cycle
        second_cycle = [ProxyService.rotate_proxy(proxy_list, n + i) for i in range(n)]
        
        # Cycles should be identical
        assert first_cycle == second_cycle

    @given(
        proxy_list=st.lists(
            st.text(min_size=1, max_size=100),
            min_size=1,
            max_size=10,
            unique=True,
        ),
    )
    @settings(max_examples=100)
    def test_proxy_rotation_n_plus_one_requests(self, proxy_list):
        """
        Property: For a list of N proxies, executing N+1 requests should cycle
        through all proxies exactly once, then use the first proxy again.
        
        **Validates: Requirements 8.4**
        """
        n = len(proxy_list)
        
        # Execute N+1 requests
        proxies_used = [ProxyService.rotate_proxy(proxy_list, i) for i in range(n + 1)]
        
        # First N proxies should be all proxies in order
        assert proxies_used[:n] == proxy_list
        
        # The (N+1)th proxy should be the first proxy again
        assert proxies_used[n] == proxy_list[0]

    @given(
        proxy_list=st.lists(
            st.text(min_size=1, max_size=100),
            min_size=1,
            max_size=10,
            unique=True,
        ),
        request_index=st.integers(min_value=0, max_value=1000),
    )
    @settings(max_examples=100)
    def test_proxy_rotation_modulo_property(self, proxy_list, request_index):
        """
        Property: For any request index, the returned proxy should be at position
        (request_index % len(proxy_list)) in the list.
        
        **Validates: Requirements 8.4**
        """
        proxy = ProxyService.rotate_proxy(proxy_list, request_index)
        expected_index = request_index % len(proxy_list)
        expected_proxy = proxy_list[expected_index]
        
        # Should match expected proxy
        assert proxy == expected_proxy

    @given(
        proxy_list=st.lists(
            st.text(min_size=1, max_size=100),
            min_size=1,
            max_size=10,
            unique=True,
        ),
    )
    @settings(max_examples=100)
    def test_proxy_rotation_consistency(self, proxy_list):
        """
        Property: For the same request index, rotation should always return the
        same proxy (consistency property).
        
        **Validates: Requirements 8.4**
        """
        request_index = 42
        
        proxy1 = ProxyService.rotate_proxy(proxy_list, request_index)
        proxy2 = ProxyService.rotate_proxy(proxy_list, request_index)
        proxy3 = ProxyService.rotate_proxy(proxy_list, request_index)
        
        # All should be identical
        assert proxy1 == proxy2 == proxy3

    @given(
        proxy_list=st.lists(
            st.text(min_size=1, max_size=100),
            min_size=1,
            max_size=10,
            unique=True,
        ),
    )
    @settings(max_examples=100)
    def test_proxy_rotation_sequential_order(self, proxy_list):
        """
        Property: For sequential request indices, rotation should return proxies
        in the order they appear in the list, cycling back to the start.
        
        **Validates: Requirements 8.4**
        """
        n = len(proxy_list)
        
        # Get proxies for 2 full cycles
        proxies_used = [ProxyService.rotate_proxy(proxy_list, i) for i in range(2 * n)]
        
        # First cycle should match the list
        assert proxies_used[:n] == proxy_list
        
        # Second cycle should also match the list
        assert proxies_used[n:2*n] == proxy_list

    @given(
        proxy_list=st.lists(
            st.text(min_size=1, max_size=100),
            min_size=1,
            max_size=10,
            unique=True,
        ),
    )
    @settings(max_examples=100)
    def test_proxy_rotation_single_proxy(self, proxy_list):
        """
        Property: For a list with a single proxy, all requests should return
        that same proxy.
        
        **Validates: Requirements 8.4**
        """
        if len(proxy_list) != 1:
            pytest.skip("Test requires single proxy list")
        
        single_proxy = proxy_list[0]
        
        # Test multiple requests
        for i in range(10):
            proxy = ProxyService.rotate_proxy(proxy_list, i)
            assert proxy == single_proxy

    @given(
        proxy_list=st.lists(
            st.text(min_size=1, max_size=100),
            min_size=2,
            max_size=10,
            unique=True,
        ),
    )
    @settings(max_examples=100)
    def test_proxy_rotation_two_proxies(self, proxy_list):
        """
        Property: For a list with two proxies, requests should alternate between them.
        
        **Validates: Requirements 8.4**
        """
        if len(proxy_list) != 2:
            pytest.skip("Test requires two proxy list")
        
        proxy1, proxy2 = proxy_list[0], proxy_list[1]
        
        # Test alternation
        for i in range(10):
            proxy = ProxyService.rotate_proxy(proxy_list, i)
            if i % 2 == 0:
                assert proxy == proxy1
            else:
                assert proxy == proxy2

    @given(
        proxy_list=st.lists(
            st.text(min_size=1, max_size=100),
            min_size=1,
            max_size=10,
            unique=True,
        ),
    )
    @settings(max_examples=100)
    def test_proxy_rotation_large_request_index(self, proxy_list):
        """
        Property: For very large request indices, rotation should still work
        correctly using modulo arithmetic.
        
        **Validates: Requirements 8.4**
        """
        n = len(proxy_list)
        large_index = 1000000
        
        proxy = ProxyService.rotate_proxy(proxy_list, large_index)
        expected_index = large_index % n
        expected_proxy = proxy_list[expected_index]
        
        # Should match expected proxy
        assert proxy == expected_proxy

    @given(
        proxy_list=st.lists(
            st.text(min_size=1, max_size=100),
            min_size=1,
            max_size=10,
            unique=True,
        ),
    )
    @settings(max_examples=100)
    def test_proxy_rotation_zero_index(self, proxy_list):
        """
        Property: Request index 0 should always return the first proxy.
        
        **Validates: Requirements 8.4**
        """
        proxy = ProxyService.rotate_proxy(proxy_list, 0)
        
        # Should be the first proxy
        assert proxy == proxy_list[0]

    @given(
        proxy_list=st.lists(
            st.text(min_size=1, max_size=100),
            min_size=1,
            max_size=10,
            unique=True,
        ),
    )
    @settings(max_examples=100)
    def test_proxy_rotation_boundary_indices(self, proxy_list):
        """
        Property: Request indices at cycle boundaries should return correct proxies.
        
        **Validates: Requirements 8.4**
        """
        n = len(proxy_list)
        
        # Test boundary indices
        for cycle in range(3):
            # First proxy of cycle
            proxy_at_start = ProxyService.rotate_proxy(proxy_list, cycle * n)
            assert proxy_at_start == proxy_list[0]
            
            # Last proxy of cycle
            proxy_at_end = ProxyService.rotate_proxy(proxy_list, cycle * n + n - 1)
            assert proxy_at_end == proxy_list[n - 1]

    def test_proxy_rotation_empty_list(self):
        """
        Property: For an empty proxy list, rotation should return None.
        
        **Validates: Requirements 8.4**
        """
        proxy = ProxyService.rotate_proxy([], 0)
        
        # Should return None for empty list
        assert proxy is None

    @given(
        proxy_list=st.lists(
            st.text(min_size=1, max_size=100),
            min_size=1,
            max_size=10,
            unique=True,
        ),
    )
    @settings(max_examples=100)
    def test_proxy_rotation_no_skipping(self, proxy_list):
        """
        Property: For sequential requests, no proxy should be skipped in the cycle.
        
        **Validates: Requirements 8.4**
        """
        n = len(proxy_list)
        
        # Get proxies for one full cycle
        proxies_used = [ProxyService.rotate_proxy(proxy_list, i) for i in range(n)]
        
        # Count occurrences of each proxy
        for proxy in proxy_list:
            assert proxies_used.count(proxy) == 1

    @given(
        proxy_list=st.lists(
            st.text(min_size=1, max_size=100),
            min_size=1,
            max_size=10,
            unique=True,
        ),
    )
    @settings(max_examples=100)
    def test_proxy_rotation_multiple_cycles(self, proxy_list):
        """
        Property: For multiple complete cycles, each proxy should be used
        exactly once per cycle.
        
        **Validates: Requirements 8.4**
        """
        n = len(proxy_list)
        num_cycles = 5
        
        # Get proxies for multiple cycles
        proxies_used = [ProxyService.rotate_proxy(proxy_list, i) for i in range(n * num_cycles)]
        
        # Each proxy should appear exactly num_cycles times
        for proxy in proxy_list:
            assert proxies_used.count(proxy) == num_cycles

    @given(
        proxy_list=st.lists(
            st.text(min_size=1, max_size=100),
            min_size=1,
            max_size=10,
            unique=True,
        ),
    )
    @settings(max_examples=100)
    def test_proxy_rotation_deterministic(self, proxy_list):
        """
        Property: Proxy rotation should be deterministic - the same sequence
        of request indices should always produce the same sequence of proxies.
        
        **Validates: Requirements 8.4**
        """
        n = len(proxy_list)
        indices = list(range(n * 3))
        
        # Get proxies twice
        proxies1 = [ProxyService.rotate_proxy(proxy_list, i) for i in indices]
        proxies2 = [ProxyService.rotate_proxy(proxy_list, i) for i in indices]
        
        # Should be identical
        assert proxies1 == proxies2

    @given(
        proxy_list=st.lists(
            st.text(min_size=1, max_size=100),
            min_size=1,
            max_size=10,
            unique=True,
        ),
    )
    @settings(max_examples=100)
    def test_proxy_rotation_fair_distribution(self, proxy_list):
        """
        Property: Over a full cycle, each proxy should be used exactly once,
        ensuring fair distribution.
        
        **Validates: Requirements 8.4**
        """
        n = len(proxy_list)
        
        # Get proxies for one full cycle
        proxies_used = [ProxyService.rotate_proxy(proxy_list, i) for i in range(n)]
        
        # Each proxy should appear exactly once
        for proxy in proxy_list:
            assert proxies_used.count(proxy) == 1
        
        # Total should equal list size
        assert len(proxies_used) == n
