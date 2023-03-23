# test_utils.py

import pytest

from fastlane_bot.constants import ec
from fastlane_bot.utils import swap_weth_to_bancor_eth

"""
Code Analysis:
-- This function takes a token address as an argument.
- It checks if the token address is for WETH (Wrapped Ether).
- If the token address is for WETH, it returns the address for ETH on Bancor.
- If the token address is not for WETH, it returns the original token address.
"""

"""
Test Plan:
- test_happy_path_weth(): tests that passing WETH as a parameter returns the address for ETH on Bancor
- test_happy_path_other_token(): tests that passing a token other than WETH as a parameter returns the original token address
- test_edge_case_empty_string(): tests the edge case where passing an empty string as a parameter leads to an error
- test_edge_case_none(): tests the edge case where passing None as a parameter leads to an error
- test_edge_case_invalid_address(): tests the edge case where passing an invalid address as a parameter leads to an error
- test_edge_case_invalid_type(): tests the edge case where passing an invalid type as a parameter leads to an error

Additional instructions:
 - Where applicable: Use mocks, set the return_value and verify calls with correct data.
"""


class TestSwapWethToBancorEth:
    def test_happy_path_weth(self):
        symbol = "WETH"
        expected = "ETH"
        actual = swap_weth_to_bancor_eth(symbol)
        assert expected == actual

    def test_happy_path_other_token(self):
        symbol = "BNT"
        expected = "BNT"
        actual = swap_weth_to_bancor_eth(symbol)
        assert expected == actual
