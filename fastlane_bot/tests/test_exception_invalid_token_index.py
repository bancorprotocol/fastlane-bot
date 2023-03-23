# test_exceptions.py

import pytest

from fastlane_bot.exceptions import InvalidTokenIndexException
from fastlane_bot.tests.utils import make_mock_constant_function_route

"""
Code Analysis:
-- This class is used to raise an error when the index of the selected token is not 0 or 1.
- The class inherits from the Exception class, which is a built-in class in Python.
- The __init__ method is used to initialize the class and takes an optional argument idx.
- The __init__ method also sets the error message to be displayed when the exception is raised.
"""

"""
Test Plan:
- test_init_with_valid_idx(): tests that the __init__ method works correctly when a valid index is passed as an argument. Test uses [__init__(), field1]
- test_init_without_idx(): tests that the __init__ method works correctly when no index is passed as an argument. Test uses [__init__(), field1]
- test_init_with_string_idx(): tests the edge case where calling the __init__ method with a string index leads to an error. Test uses [__init__(), field1]
- test_init_with_float_idx(): tests the edge case where calling the __init__ method with a float index leads to an error. Test uses [__init__(), field1]
- test_init_with_negative_idx(): tests the edge case where calling the __init__ method with a negative index leads to an error. Test uses [__init__(), field1]

Additional instructions:
 - Where applicable: Use mocks, set the return_value and verify calls with correct data.
"""


class TestInvalidTokenIndexException:
    def test_init_with_valid_idx(self):
        """Test that the __init__ method works correctly when a valid index is passed as an argument."""
        exception = InvalidTokenIndexException(idx=0)
        assert exception.args[0] == "The selected token index: 0 must be 0 or 1"

    def test_init_without_idx(self):
        """Test that the __init__ method works correctly when no index is passed as an argument."""
        exception = InvalidTokenIndexException()
        assert exception.args[0] == "The selected token index: None must be 0 or 1"

    def test_init_with_string_idx(self):
        """Test the edge case where calling the __init__ method with a string index leads to an error."""
        route = make_mock_constant_function_route()
        with pytest.raises(AssertionError):
            route.validate_token_idx(idx="foo")

    def test_init_with_float_idx(self):
        """Test the edge case where calling the __init__ method with a float index leads to an error."""
        route = make_mock_constant_function_route()
        with pytest.raises(AssertionError):
            route.validate_token_idx(idx=1.5)

    def test_init_with_negative_idx(self):
        """Test the edge case where calling the __init__ method with a negative index leads to an error."""
        route = make_mock_constant_function_route()
        with pytest.raises(AssertionError):
            route.validate_token_idx(idx=-1)
