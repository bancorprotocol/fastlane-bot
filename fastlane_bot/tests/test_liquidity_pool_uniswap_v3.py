from _decimal import Decimal

import pytest

from fastlane_bot.constants import ec
from fastlane_bot.exceptions import InvalidPoolInitialization
from fastlane_bot.networks import EthereumNetwork
from fastlane_bot.pools import UniswapV3LiquidityPool
from fastlane_bot.tests.utils import get_pool_test_info

# test_pools.py

"""
Code Analysis:
-- Represents a Uniswap V3 pool
- Has optional fields (automatically populated if not provided) such as address, liquidity, fee, contract, exchange, exchange_id, id, sqrt_price_q96, tick, nxt_sqrt_price_q96, slot0, max_in_swap_token_0, max_in_swap_token_1, max_out_swap_token_0, max_out_swap_token_1, sqrt_price_q96_lower_bound, sqrt_price_q96_upper_bound, and tokens
- Has properties such as tkn0, tkn1, tick_spacing, lower_tick, upper_tick, t0decimal_mod, and t1decimal_mod
- Has static methods such as fee_tier_to_tick_spacing, multiply_by_decimals, and tick_to_sqrt_price_q96
- Has methods such as check_token_order, update_liquidity, calc_amount0, calc_amount1, calculate_max_swap_token0, calculate_max_swap_token1, correct_upper_lower_bounds, and __post_init__
"""

"""
Test Plan:
- test_check_token_order_happy_path(): tests that check_token_order() works as expected when given valid tokens. Test uses [check_token_order()]
- test_update_liquidity_happy_path(): tests that update_liquidity() works as expected when given valid parameters. Test uses [update_liquidity(), contract.slot0(), contract.liquidity()]
- test_calc_amount0_happy_path(): tests that calc_amount0() works as expected when given valid parameters. Test uses [calc_amount0(), correct_upper_lower_bounds()]
- test_calc_amount1_happy_path(): tests that calc_amount1() works as expected when given valid parameters. Test uses [calc_amount1(), correct_upper_lower_bounds()]
- test_correct_upper_lower_bounds_edge_case(): tests the edge case where calling correct_upper_lower_bounds() with lower_bound > upper_bound leads to lower_bound and upper_bound being swapped. Test uses [correct_upper_lower_bounds()]
- test_post_init_affects_tick_spacing(): tests how calling __post_init__() affects tick_spacing. Tests that tick_spacing is correctly calculated. Test uses [__post_init__(), fee_tier_to_tick_spacing(), lower_tick, upper_tick]

Additional instructions:
 - Where applicable: Use mocks, set the return_value and verify calls with correct data.
"""

# Valid Params
exchange = "uniswap_v3"
address, fee, pair, tkn0, tkn1 = get_pool_test_info(exchange)


class TestUniswapV3LiquidityPool:
    def test_check_token_order_happy_path(self):
        try:
            # Act
            UniswapV3LiquidityPool(
                exchange=exchange,
                pair=pair,
                fee=fee,
                address=address,
                tokens=[tkn0, tkn1],
            )
        except Exception as e:
            pytest.fail(f"Unexpected exception: {e}")

    def test_init_invalid_pair(self):
        """
        Tests the edge case where the pair is not found in the pool info for the exchange.
        """
        # Create a pool object with an invalid pair
        with pytest.raises(InvalidPoolInitialization):
            UniswapV3LiquidityPool(
                exchange=exchange, pair="SOMETHING_ELSE", fee=fee, tokens=[tkn0, tkn1]
            )

    def test_reverse_tokens(self):
        """
        Tests that the order of the tokens in the pool is reversed correctly.
        """
        # Arrange
        pool = UniswapV3LiquidityPool(
            exchange=exchange, pair=pair, fee=fee, tokens=[tkn0, tkn1]
        )

        TKN0 = pool.tkn0.symbol
        TKN1 = pool.tkn1.symbol

        # Act
        # Reverse the tokens in the pool
        pool.reverse_tokens()

        # Assert that the tokens are reversed correctly
        assert pool.tkn0.symbol == TKN1
        assert pool.tkn1.symbol == TKN0
