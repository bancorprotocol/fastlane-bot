# test_utils.py

import pytest

from fastlane_bot.utils import swap_bancor_eth_to_weth

"""
Code Analysis:
-- This function takes an address as an argument and returns a string.
- If the address is the Ethereum address, it returns the Wrapped Ether (WETH) address for compatibility.
- If the address is not the Ethereum address, it returns the same address.
"""

"""
Test Plan:
- test_eth_address_conversion(): tests that passing the ETH address returns the WETH address
- test_non_eth_address_conversion(): tests that passing a non-ETH address returns the same address
- test_empty_string_conversion(): tests that passing an empty string returns an empty string
- test_none_conversion(): tests that passing None returns None
- test_edge_case_long_string(): tests the edge case where passing a long string leads to an error
- test_edge_case_invalid_address(): tests the edge case where passing an invalid address leads to an error

Additional instructions:
 - Where applicable: Use mocks, set the return_value and verify calls with correct data.
"""


class TestSwapBancorEthToWeth:
    def test_eth_address_conversion(self):
        result = swap_bancor_eth_to_weth("0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE")
        assert result == "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2"

    def test_non_eth_address_conversion(self):
        result = swap_bancor_eth_to_weth("0xDf5e0e81Dff6FAF3A7e52BA697820c5e32D806A8")
        assert result == "0xDf5e0e81Dff6FAF3A7e52BA697820c5e32D806A8"

    def test_empty_string_conversion(self):
        result = swap_bancor_eth_to_weth("")
        assert result == ""

    def test_none_conversion(self):
        result = swap_bancor_eth_to_weth(None)
        assert result is None
