from _decimal import Decimal

import pytest

from fastlane_bot.utils import convert_to_correct_decimal

# test_utils.py

"""
Code Analysis:
-- This function takes in two parameters: an address (string) and an amount (Decimal)
- It uses the symbol associated with the address to look up the correct decimal precision
- It then calls the convert_decimals() function to convert the amount to the correct decimal precision
- The convert_decimals() function takes in two parameters: the amount (Decimal) and the number of decimals (int)
- It returns the amount (Decimal) converted to the correct decimal precision
"""

"""
Test Plan:
- test_convert_to_correct_decimal_happy_path(): tests that the function correctly converts a Decimal to the correct decimal precision when given a valid address and amount
- test_convert_to_correct_decimal_invalid_address(): tests the edge case where passing an invalid address leads to an error
- test_convert_to_correct_decimal_invalid_amount(): tests the edge case where passing an invalid amount leads to an error
- test_convert_to_correct_decimal_invalid_symbol(): tests the edge case where passing an invalid symbol leads to an error
- test_convert_to_correct_decimal_invalid_decimals(): tests the edge case where passing an invalid number of decimals leads to an error
- test_convert_to_correct_decimal_zero_amount(): tests the edge case where passing a zero amount leads to a zero result

Additional instructions:
 - Where applicable: Use mocks, set the return_value and verify calls with correct data.
"""


class TestConvertToCorrectDecimal:
    def test_convert_to_correct_decimal_invalid_address(self, mocker):
        # Arrange
        address = "invalid"
        amt = Decimal("10.0")

        # Act
        with pytest.raises(KeyError):
            convert_to_correct_decimal(address, amt)

    def test_convert_to_correct_decimal_invalid_symbol(self, mocker):
        # Arrange
        address = "0x123456789"
        amt = Decimal("10.0")
        symbol = "invalid"
        mocker.patch(
            "fastlane_bot.constants.ec.SYMBOL_FROM_ADDRESS", return_value=symbol
        )

        # Act
        with pytest.raises(KeyError):
            convert_to_correct_decimal(address, amt)
