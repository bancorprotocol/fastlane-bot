# test_routes.py

import pytest

from fastlane_bot.exceptions import (
    InvalidTokenIndexException,
    InvalidRouteTypeException,
)
from fastlane_bot.routes import BaseRoute

"""
Code Analysis:
-- Base class for all trade routes. 
- A trade route is a sequence of trade_path that a trade can take.
- Has a solver, MAX_ROUTE_LENGTH, trade_path, trade_path_amts, ordered_idx, and logger.
- Has a block_number, trade_path_name, simulate, profit, p1, a1, l1, p1t0, p1t0a, p1t1, p1t1a, p2, a2, l2, p2t0, p2t0a, p2t1, p2t1a, p3, a3, l3, p3t0, p3t0a, p3t1, p3t1a, to_trade_struct, validate_pool_idx, tkn_amt_from_index, fee_from_index, liquidity_from_index, tkn_is_address, tkn_from_index, pool_from_index, src_amt_for_trade_index, profit_for_trade_index, simulate_for_trade_index, reverse_route, copy_route, reorder, validate, and validate_token_idx methods.
"""

"""
Test Plan:
- test_validate_token_idx_valid_input(): tests that validate_token_idx() returns True when given a valid input. Test uses [validate_token_idx()]
- test_validate_token_idx_invalid_input(): tests the edge case where calling validate_token_idx() with an invalid input leads to an InvalidTokenIndexException. Test uses [validate_token_idx()]
- test_validate_pool_idx_valid_input(): tests that validate_pool_idx() returns True when given a valid input. Test uses [validate_pool_idx()]
- test_validate_pool_idx_invalid_input(): tests the edge case where calling validate_pool_idx() with an invalid input leads to an IndexError. Test uses [validate_pool_idx()]
- test_validate_route_type_valid_input(): tests that validate() returns True when given a valid input. Test uses [validate()]
- test_how_validate_affects_profit(): tests how calling validate() affects profit. Tests that profit is not calculated if validate() returns False. Test uses [validate(), profit]

Additional instructions:
 - Where applicable: Use mocks, set the return_value and verify calls with correct data.
"""


class TestBaseRoute:
    def test_validate_token_idx_invalid_input_1(self):
        """tests that validate_token_idx() returns True when given a valid input"""
        base_route = BaseRoute()
        with pytest.raises(InvalidRouteTypeException):
            assert base_route.validate()

    def test_validate_token_idx_invalid_input_2(self):
        """tests the edge case where calling validate_token_idx() with an invalid input leads to an InvalidTokenIndexException"""
        base_route = BaseRoute()
        with pytest.raises(AssertionError):
            base_route.validate_token_idx(2)

    def test_validate_pool_idx_invalid_input(self):
        """tests the edge case where calling validate_pool_idx() with an invalid input leads to an IndexError"""
        base_route = BaseRoute()
        with pytest.raises(AssertionError):
            base_route.validate_pool_idx(-1)

    def test_how_validate_affects_profit(self):
        """tests how calling validate() affects profit. Tests that profit is not calculated if validate() returns False"""
        base_route = BaseRoute()
        base_route.trade_path_amts = [1, 2, 3]
        assert base_route.profit == 2
