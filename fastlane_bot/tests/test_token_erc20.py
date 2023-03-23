# test_token.py

from fastlane_bot.constants import ec
from fastlane_bot.token import ERC20Token

"""
Code Analysis:
-- Represents an ERC20 token on the Ethereum network
- Also used for native ETH
- Symbol such as ETH, DAI, etc.
- Amount of token
- Decimals used to denominate the token
- Address of the token contract
- __post_init__() method to set the decimals and address from the symbol if they are not provided
"""

"""
Test Plan:
- test_symbol_set_correctly(): tests that the symbol is set correctly. Test uses [symbol]
- test_amt_set_correctly(): tests that the amt is set correctly. Test uses [amt]
- test_decimals_set_correctly(): tests that the decimals are set correctly. Test uses [decimals]
- test_address_set_correctly(): tests that the address is set correctly. Test uses [address]
- test_to_weth_returns_correct_address(): tests that the to_weth() method returns the correct WETH address. Test uses [to_weth()]
- test_to_eth_returns_correct_address(): tests that the to_eth() method returns the correct ETH address. Test uses [to_eth()]

Additional instructions:
 - Where applicable: Use mocks, set the return_value and verify calls with correct data.
"""


class TestERC20Token:
    def test_symbol_set_correctly(self):
        token = ERC20Token(symbol="ETH")
        assert token.symbol == "ETH"

    def test_amt_set_correctly(self):
        token = ERC20Token(amt=100)
        assert token.amt == 100

    def test_decimals_set_correctly(self):
        token = ERC20Token(decimals=18)
        assert token.decimals == 18

    def test_address_set_correctly(self):
        token = ERC20Token(address="0x123456789")
        assert token.address == "0x123456789"

    def test_to_weth_returns_correct_address(self):
        token = ERC20Token()
        assert token.to_weth() == ec.WETH_ADDRESS

    def test_to_eth_returns_correct_address(self):
        token = ERC20Token()
        assert token.to_eth() == ec.ETH_ADDRESS
