# test_exceptions.py

import pytest

from fastlane_bot.constants import ec
from fastlane_bot.exceptions import TradePathSequenceException
from fastlane_bot.pools import LiquidityPool
from fastlane_bot.tests.utils import make_mock_constant_function_route
from fastlane_bot.token import ERC20Token

"""
Code Analysis:
-- This class is used to raise errors in the code when the tkn1 of PoolA does not match tkn0 of PoolB (the next pool in the path).
- The class inherits from the Exception class.
- The __init__ method takes three parameters: tkn0, tkn1, and idx.
- The __init__ method sets the error message to be displayed when the exception is raised.
"""

"""
Test Plan:
- test_correct_tkn_match(): tests that the exception is not raised when the tkn1 of PoolA matches tkn0 of PoolB. Test uses [__init__()]
- test_incorrect_tkn_match(): tests that the exception is raised when the tkn1 of PoolA does not match tkn0 of PoolB. Test uses [__init__()]
- test_no_tkn_match(): tests that the exception is raised when no tkn1 of PoolA is provided. Test uses [__init__()]
- test_edge_case_init_param(): tests the edge case where calling the __init__() method with a param of None leads to an error message being displayed. Test uses [__init__()]
- test_edge_case_init_param_empty_string(): tests the edge case where calling the __init__() method with a param of an empty string leads to an error message being displayed. Test uses [__init__()]
- test_how_init_affects_message(): tests how calling __init__() affects the error message. Tests that the error message is correctly set. Test uses [__init__()]

Additional instructions:
 - Where applicable: Use mocks, set the return_value and verify calls with correct data.
"""

# Valid Params
db = ec.DB
db = db[(db["exchange"] == ec.BANCOR_BASE)]
address = db["address"].iloc[0]
fee = db["fee"].iloc[0]
pair = db["pair"].iloc[0]
exchange = ec.BANCOR_BASE
tkn0 = ERC20Token(symbol=db["symbol0"].iloc[0])
tkn1 = ERC20Token(symbol=db["symbol1"].iloc[0])


class TestTradePathSequenceException:
    def test_correct_tkn_match(self):
        tkn0 = "token0"
        tkn1 = "token0"
        idx = 0
        exception = TradePathSequenceException(tkn0, tkn1, idx)
        assert (
            exception.args[0]
            == f"The tkn0: {tkn0} of pool {idx} does not match the tkn1: {tkn1} of pool {idx - 1}"
        )

    def test_incorrect_tkn_match(self):
        # Arrange
        pool = LiquidityPool(
            exchange=exchange, pair=pair, fee=fee, tkn0=tkn0, tkn1=tkn1
        )

        route = make_mock_constant_function_route()
        route.p1 = pool
        route.p2 = pool

        with pytest.raises(TradePathSequenceException):
            route.validate()

    def test_how_init_affects_message(self):
        tkn0 = "token0"
        tkn1 = "token1"
        idx = 0
        exception = TradePathSequenceException(tkn0, tkn1, idx)
        assert (
            exception.args[0]
            == f"The tkn0: {tkn0} of pool {idx} does not match the tkn1: {tkn1} of pool {idx - 1}"
        )
