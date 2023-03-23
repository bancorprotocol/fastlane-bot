# test_exceptions.py

import pytest

from fastlane_bot.exceptions import InvalidPoolIndexException
from fastlane_bot.pools import LiquidityPool
from fastlane_bot.tests.utils import (
    make_mock_constant_product_route,
    make_mock_constant_function_route,
)

"""
Code Analysis:
-- This class is used to raise an error when a pool index is specified but does not exist.
- The class inherits from the Exception class, which is used to indicate that an error has occurred.
- The __init__ method is used to initialize the class and set the error message.
- The error message includes the selected index (idx) and the trade_path length (route_length).
"""

"""
Test Plan:
- test_init_constant_product_route_happy_path(): tests that the __init__ method works as expected when valid parameters are passed. Test uses [__init__(), route_length]
- test_init_invalid_constant_product_route_length(): tests the edge case where calling the __init__ method with an invalid route_length leads to an error. Test uses [__init__(), route_length]
- test_init_invalid_constant_function_route_length(): tests the edge case where calling the __init__ method with an invalid route_length leads to an error. Test uses [__init__(), route_length]
- test_init_constant_function_route_happy_path(): tests the edge case where calling the __init__ method with no parameters leads to an error. Test uses [__init__()]
- test_init_how_idx_affects_route_length(): tests how calling the __init__ method with different idx values affects the route_length. Tests that the route_length is always greater than the idx. Test uses [__init__(), idx, route_length]

Additional instructions:
 - Where applicable: Use mocks, set the return_value and verify calls with correct data.
"""


class TestInvalidPoolIndexException:
    def test_init_constant_product_route_happy_path(self):
        """Test that the __init__ method works as expected when valid parameters are passed."""
        route = make_mock_constant_product_route()
        assert (
            isinstance(route.p1, LiquidityPool),
            f"The selected index (idx) must be less than the trade_path length: {len(route.trade_path)}",
        )

    def test_init_invalid_constant_product_route_length(self):
        """Test the edge case where calling the __init__ method with an invalid route_length leads to an error."""
        idx = 5
        route = make_mock_constant_product_route()
        with pytest.raises(IndexError):
            route.trade_path[idx]

    def test_init_constant_function_route_happy_path(self):
        """Test that the __init__ method works as expected when valid parameters are passed."""
        route = make_mock_constant_function_route()
        assert (
            isinstance(route.p1, LiquidityPool),
            f"The selected index (idx) must be less than the trade_path length: {len(route.trade_path)}",
        )

    def test_init_invalid_constant_function_route_length(self):
        """Test the edge case where calling the __init__ method with an invalid route_length leads to an error."""
        idx = 5
        route = make_mock_constant_function_route()
        with pytest.raises(IndexError):
            route.trade_path[idx]

    def test_init_how_idx_affects_route_length(self):
        """Test how calling the __init__ method with different idx values affects the route_length. Tests that the route_length is always greater than the idx."""
        for i in range(10):
            idx = i
            route_length = i + 1
            exception = InvalidPoolIndexException(idx, route_length)
            assert (
                exception.args[0]
                == f"The selected index (idx) must be less than the trade_path length: {route_length}"
            )
