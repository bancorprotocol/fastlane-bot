# test_token.py

from fastlane_bot.constants import ec
from fastlane_bot.token import EthBaseToken

"""
Code Analysis:
-- The class is used to represent tokens on the Ethereum network.
- It has a symbol, amount, decimals, and address.
- It has methods to convert to and from wei, convert ETH to WETH, and convert WETH to ETH.
- It also has methods to check if the token is ETH, WETH, or BNT.
- It has a __repr__ method to return a string representation of the token.
"""

"""
Test Plan:
- test_convert_to_wei(): tests that the convert_to_wei() method correctly converts a token amount to wei. Test uses [convert_to_wei(), decimals]
- test_convert_from_wei(): tests that the convert_from_wei() method correctly converts a wei amount to token. Test uses [convert_from_wei(), decimals]
- test_is_eth(): tests that the is_eth() method correctly returns True if the token is ETH. Test uses [is_eth(), symbol]
- test_is_weth(): tests that the is_weth() method correctly returns True if the token is WETH. Test uses [is_weth(), symbol]
- test_convert_eth_to_weth(): tests the edge case where calling the convert_eth_to_weth() method with an ETH address leads to the WETH address. Test uses [convert_eth_to_weth(), address]
- test_how_convert_to_wei_affects_convert_from_wei(): tests how calling convert_to_wei() affects convert_from_wei(). Tests that calling convert_to_wei() followed by convert_from_wei() returns the original amount. Test uses [convert_to_wei(), convert_from_wei(), decimals]

Additional instructions:
 - Where applicable: Use mocks, set the return_value and verify calls with correct data.
"""


class TestEthBaseToken:
    def test_is_eth(self):
        token = EthBaseToken(symbol="ETH")
        assert token.is_eth() == True

    def test_is_weth(self):
        token = EthBaseToken(symbol="WETH")
        assert token.is_weth() == True

    def test_convert_eth_to_weth(self):
        token = EthBaseToken(address=ec.ETH_ADDRESS)
        assert token.convert_eth_to_weth() == ec.WETH_ADDRESS

    def test_how_convert_to_wei_affects_convert_from_wei(self):
        token = EthBaseToken(symbol="ETH", decimals=18)
        amount = 10
        wei = token.convert_to_wei(amount)
        assert token.convert_from_wei(wei) == amount
