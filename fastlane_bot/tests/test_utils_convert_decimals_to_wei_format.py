from _decimal import Decimal

import pytest

from fastlane_bot.utils import convert_decimals_to_wei_format

# test_utils.py

"""
Code Analysis:
-- Function takes two parameters: tkn_amt (the number of tokens to convert) and decimals (the number of decimals used by the token)
- Function converts the number of tokens to WEI format according to the decimals used by the token
- If the decimals is 0, it is set to 1
- The function returns an integer representing the number of tokens in WEI format
"""

"""
Test Plan:
- test_convert_decimals_to_wei_format_happy_path(): tests that the function correctly converts the number of tokens to WEI format according to the decimals used by the token
- test_convert_decimals_to_wei_format_zero_decimals(): tests that the function correctly sets the decimals to 1 if the decimals is 0
- test_convert_decimals_to_wei_format_return_type(): tests that the function returns an integer representing the number of tokens in WEI format
- test_edge_case_decimals(): tests the edge case where passing a negative decimals leads to an error
- test_edge_case_tkn_amt(): tests the edge case where passing a negative tkn_amt leads to an error
- test_edge_case_decimals_and_tkn_amt(): tests the edge case where passing negative decimals and tkn_amt leads to an error

Additional instructions:
 - Where applicable: Use mocks, set the return_value and verify calls with correct data.
"""


class TestConvertDecimalsToWeiFormat:
    def test_convert_decimals_to_wei_format_happy_path(self):
        tkn_amt = Decimal("1")
        decimals = Decimal("18")
        expected_result = 1000000000000000000
        result = convert_decimals_to_wei_format(tkn_amt, decimals)
        assert result == expected_result

    def test_convert_decimals_to_wei_format_zero_decimals(self):
        tkn_amt = Decimal("1")
        decimals = Decimal("0")
        expected_result = 10
        result = convert_decimals_to_wei_format(tkn_amt, decimals)
        assert result == expected_result

    def test_convert_decimals_to_wei_format_return_type(self):
        tkn_amt = Decimal("1")
        decimals = Decimal("18")
        result = convert_decimals_to_wei_format(tkn_amt, decimals)
        assert isinstance(result, int)
