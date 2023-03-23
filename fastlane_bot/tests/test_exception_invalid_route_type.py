# test_exceptions.py

import pytest

from fastlane_bot.exceptions import InvalidRouteTypeException

"""
Code Analysis:
-- This class is used to raise an error when the trade path specified is not of a supported type.
- It is a subclass of the Exception class.
- It has an __init__ method which takes an exchange_base parameter and sets an error message.
- The error message states that the trade path must meet the requirements of a supported route type, the first pool must be a CPMM on the specified exchange_base, the last pool must be a CPMM on the specified exchange_base, and the first and last trade_path must have the same token.
"""

"""
Test Plan:
- test_valid_route_type(): tests that a valid route type is accepted. Test uses [__init__()]
- test_error_message(): tests that the error message is correctly set. Test uses [__init__()]
- test_how_init_affects_error_message(): tests how calling __init__() affects the error message. Tests that the error message is correctly set. Test uses [__init__()]

Additional instructions:
 - Where applicable: Use mocks, set the return_value and verify calls with correct data.
"""


class TestInvalidRouteTypeException:
    def test_valid_route_type(self):
        """Tests that a valid route type is accepted."""
        exchange_base = "BASE"
        exception = InvalidRouteTypeException(exchange_base)
        assert exception is not None

    def test_error_message(self):
        """Tests that the error message is correctly set."""
        exchange_base = "BASE"
        exception = InvalidRouteTypeException(exchange_base)
        assert exception.args[0] == (
            f"The trade path must meet the requirements of a supported route type. "
            f"First pool must be a CPMM on {exchange_base}. Last pool must be a CPMM on {exchange_base}. "
            f"First and last trade_path must have the same token."
        )

    def test_how_init_affects_error_message(self):
        """Tests how calling __init__() affects the error message. Tests that the error message is correctly set."""
        exchange_base = "BASE"
        exception = InvalidRouteTypeException(exchange_base)
        assert exception.args[0] == (
            f"The trade path must meet the requirements of a supported route type. "
            f"First pool must be a CPMM on {exchange_base}. Last pool must be a CPMM on {exchange_base}. "
            f"First and last trade_path must have the same token."
        )
