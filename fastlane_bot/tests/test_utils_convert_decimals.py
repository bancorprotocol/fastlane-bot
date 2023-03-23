from _decimal import Decimal

from fastlane_bot.utils import convert_decimals

# test_utils.py

"""
Code Analysis:
-- This function takes two parameters: amt (a Decimal value) and n (an integer).
- It returns a Decimal value.
- The function is used to convert a Decimal value to a Decimal value of a specific precision.
- The precision is determined by the value of n.
- If the amt parameter is None, the function returns a Decimal value of 0.
- The function uses the Decimal class from the _decimal module to perform the conversion.
"""

"""
Test Plan:
- test_convert_decimals_positive_int(): tests that a positive integer is correctly converted to a Decimal value
- test_convert_decimals_negative_int(): tests that a negative integer is correctly converted to a Decimal value
- test_convert_decimals_zero(): tests that a zero is correctly converted to a Decimal value
- test_convert_decimals_positive_float(): tests that a positive float is correctly converted to a Decimal value
- test_edge_case_precision(): tests the edge case where passing a precision value of 0 leads to no conversion
- test_convert_decimals_negative_float(): tests that a negative float is correctly converted to a Decimal value

Additional instructions:
 - Where applicable: Use mocks, set the return_value and verify calls with correct data.
"""


class TestConvertDecimals:
    def test_convert_decimals_zero(self):
        amt = Decimal(0)
        n = 3
        expected_result = Decimal(0)
        result = convert_decimals(amt, n)
        assert result == expected_result

    def test_edge_case_precision(self):
        amt = Decimal(10.5)
        n = 0
        expected_result = Decimal(10.5)
        result = convert_decimals(amt, n)
        assert result == expected_result
