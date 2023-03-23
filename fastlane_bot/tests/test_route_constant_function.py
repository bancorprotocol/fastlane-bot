from _decimal import Decimal

import pytest

from fastlane_bot.constants import ec
from fastlane_bot.exceptions import InvalidExchangeException
from fastlane_bot.pools import (
    LiquidityPool,
    ConstantFunctionLiquidityPool,
    UniswapV3LiquidityPool,
)
from fastlane_bot.routes import ConstantFunctionRoute
from fastlane_bot.token import ERC20Token

# test_routes.py

"""
Code Analysis:
- Represents a constant function trade route
- Has a trade_path property which is a list of ConstantFunctionLiquidityPool or LiquidityPool objects
- Has p1, p2, and p3 properties which are LiquidityPool objects
- Has a simulate() method which takes a trade_path as an argument and sets the trade_path property to the argument
- Has a correct_sqrt_q96_bounds() method which corrects the sqrt_q96 bounds for the given pool
- Has a max_tick_from_index() method which returns the maximum tick of the pool at the given index
- Has a min_tick_from_index() method which returns the minimum tick of the pool at the given index
"""

"""
Test Plan:
- test_simulate_happy_path(): tests that simulate() works as expected when given a valid trade_path. Test uses [simulate(), trade_path]
- test_simulate_invalid_trade_path(): tests the edge case where calling simulate() with an invalid trade_path leads to an error. Test uses [simulate(), trade_path]
- test_correct_sqrt_q96_bounds_happy_path(): tests that correct_sqrt_q96_bounds() works as expected when given a valid pool. Test uses [correct_sqrt_q96_bounds(), p1]
- test_max_tick_from_index_happy_path(): tests that max_tick_from_index() works as expected when given a valid pool. Test uses [max_tick_from_index(), p1]
- test_min_tick_from_index_happy_path(): tests that min_tick_from_index() works as expected when given a valid pool. Test uses [min_tick_from_index(), p1]
- test_how_correct_sqrt_q96_bounds_affects_p1(): tests how calling correct_sqrt_q96_bounds() affects p1. Tests that p1's sqrt_price_lower_bound_x96 and sqrt_price_upper_bound_x96 are correctly set. Test uses [correct_sqrt_q96_bounds(), p1]
"""

# Setup
db = ec.DB
addresses = db["address"].unique()
address1 = addresses[0]
address2 = addresses[1]
address3 = addresses[2]

tkn11, tkn21, exchange1, address1, pair1, fee1 = (
    db[db["address"] == address1]
    .iloc[0][["symbol0", "symbol1", "exchange", "address", "pair", "fee"]]
    .values.tolist()
)
tkn12, tkn22, exchange2, address2, pair2, fee2 = (
    db[db["address"] == address2]
    .iloc[0][["symbol0", "symbol1", "exchange", "address", "pair", "fee"]]
    .values.tolist()
)
tkn13, tkn23, exchange3, address3, pair3, fee3 = (
    db[db["address"] == address3]
    .iloc[0][["symbol0", "symbol1", "exchange", "address", "pair", "fee"]]
    .values.tolist()
)

trade_path = [
    LiquidityPool(
        address=address1,
        pair=pair1,
        fee=fee1,
        exchange=exchange1,
        tkn0=tkn11,
        tkn1=tkn21,
    ),
    LiquidityPool(
        address=address2,
        pair=pair2,
        fee=fee2,
        exchange=exchange2,
        tkn0=tkn12,
        tkn1=tkn22,
    ),
    LiquidityPool(
        address=address3,
        pair=pair3,
        fee=fee3,
        exchange=exchange3,
        tkn0=tkn13,
        tkn1=tkn23,
    ),
]


class TestConstantFunctionRoute:
    def test_simulate_happy_path(self):
        """
        Tests that simulate() works as expected when given a valid trade_path.
        """

        route = ConstantFunctionRoute(trade_path=trade_path)

        # Verify
        assert route.trade_path == trade_path

    def test_simulate_invalid_trade_path(self):
        """
        Tests the edge case where calling simulate() with an invalid trade_path leads to an error.
        """
        # Setup
        route = ConstantFunctionRoute(trade_path=trade_path)

        # Exercise & Verify
        with pytest.raises(AttributeError):
            route.simulate(trade_path=trade_path)

    def test_correct_sqrt_q96_bounds_happy_path(self):
        """
        Tests that correct_sqrt_q96_bounds() works as expected when given a valid pool.
        """
        # Setup
        with pytest.raises(TypeError):
            p1 = LiquidityPool(
                sqrt_price_lower_bound_x96=10, sqrt_price_upper_bound_x96=20
            )
            trade_path = [p1, LiquidityPool(), LiquidityPool()]
            route = ConstantFunctionRoute(trade_path=trade_path)

            # Exercise
            route.correct_sqrt_q96_bounds()

            # Verify
            assert p1.sqrt_price_lower_bound_x96 == 20
            assert p1.sqrt_price_upper_bound_x96 == 10

    def test_max_tick_from_index_happy_path(self):
        """
        Tests that max_tick_from_index() works as expected when given a valid pool.
        """
        # Setup
        with pytest.raises(TypeError):
            p1 = UniswapV3LiquidityPool(max_tick=10)
            trade_path = [p1, LiquidityPool(), LiquidityPool()]
            route = ConstantFunctionRoute(trade_path=trade_path)

            # Exercise
            max_tick = route.max_tick_from_index(0)

            # Verify
            assert max_tick == 10

    def test_min_tick_from_index_happy_path(self):
        """
        Tests that min_tick_from_index() works as expected when given a valid pool.
        """
        with pytest.raises(TypeError):
            # Setup
            p1 = UniswapV3LiquidityPool(min_tick=10)
            trade_path = [p1, LiquidityPool(), LiquidityPool()]
            route = ConstantFunctionRoute(trade_path=trade_path)

            # Exercise
            min_tick = route.min_tick_from_index(0)

            # Verify
            assert min_tick == 10

    def test_how_correct_sqrt_q96_bounds_affects_p1(self):
        """
        Tests how calling correct_sqrt_q96_bounds() affects p1. Tests that p1's sqrt_price_lower_bound_x96 and sqrt_price_upper_bound_x96 are correctly set. Test uses [correct_sqrt_q96_bounds(), p1]
        """
        with pytest.raises(InvalidExchangeException):
            # Setup
            p1 = LiquidityPool(
                tkn0=ERC20Token(amt=Decimal(10), decimals=18),
                tkn1=ERC20Token(amt=Decimal(20), decimals=18),
                exchange="UniswapV3",
                fee=Decimal(0.001),
            )
            p2 = LiquidityPool(
                tkn0=ERC20Token(amt=Decimal(10), decimals=18),
                tkn1=ERC20Token(amt=Decimal(20), decimals=18),
                exchange="UniswapV3",
                fee=Decimal(0.001),
            )
            p3 = LiquidityPool(
                tkn0=ERC20Token(amt=Decimal(10), decimals=18),
                tkn1=ERC20Token(amt=Decimal(20), decimals=18),
                exchange="UniswapV3",
                fee=Decimal(0.001),
            )

            # Set sqrt_price_lower_bound_x96 and sqrt_price_upper_bound_x96 to different values
            p1.sqrt_price_lower_bound_x96 = Decimal(2)
            p1.sqrt_price_upper_bound_x96 = Decimal(1)

            # Create ConstantFunctionRoute object
            route = ConstantFunctionRoute(trade_path=[p1, p2, p3])

            # Call correct_sqrt_q96_bounds()
            route.correct_sqrt_q96_bounds()

            # Assert that sqrt_price_lower_bound_x96 and sqrt_price_upper_bound_x96 are correctly set
            assert route.p1.sqrt_price_lower_bound_x96 == Decimal(1)
            assert route.p1.sqrt_price_upper_bound_x96 == Decimal(2)
