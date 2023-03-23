import pytest

from fastlane_bot.constants import ec
from fastlane_bot.exceptions import InvalidPoolInitialization
from fastlane_bot.pools import BancorV2LiquidityPool
from fastlane_bot.tests.utils import get_pool_test_info
from fastlane_bot.token import ERC20Token

# test_pools.py

"""
Code Analysis:
- Represents a Bancor V2 liquidity pool
- Has optional fields such as address, anchor, liquidity, fee, contract, exchange, exchange_id
- Has an autoincrementing id
- Has tokens stored in a list
- Has properties for tkn0 and tkn1 which can be set and retrieved
- Has an update_liquidity() method which updates the liquidity of the pool
- Has a __post_init__() method which sets the id and calls the setup() method
"""

"""
Test Plan:
- test_init_with_valid_params(): tests that the pool is initialized correctly with valid parameters. Test uses [__post_init__(), setup(), validate_pool()]
- test_init_with_invalid_params(): tests that the pool is not initialized correctly with invalid parameters. Test uses [__post_init__(), setup(), validate_pool()]
- test_update_liquidity(): tests that the liquidity is updated correctly. Test uses [update_liquidity(), tkn0.amt, tkn1.amt, contract.reserveBalances()]
- test_reverse_tokens(): tests that the order of the tokens in the pool is reversed correctly. Test uses [reverse_tokens(), tokens]
- test_check_token_order(): tests that the order of the tokens in the pool is checked correctly. Test uses [check_token_order()]
- test_how_init_contract_affects_setup(): tests how calling init_contract affects setup. Tests that the constants for the pool are set correctly. Test uses [init_contract(), setup(), tkn0, tkn1]
"""


# Valid Params
exchange = "bancor_v2"
address, fee, pair, tkn0, tkn1 = get_pool_test_info(exchange)


class TestBancorV2LiquidityPool:
    def test_init_happy_path(self):
        """
        Tests that the BancorV2LiquidityPool class is initialized correctly with valid parameters.
        """
        try:
            # Act
            BancorV2LiquidityPool(
                exchange=exchange, pair=pair, fee=fee, tokens=[tkn0, tkn1]
            )
        except Exception as e:
            pytest.fail(f"Unexpected exception: {e}")

    def test_init_invalid_pair(self):
        """
        Tests the edge case where the pair is not found in the pool info for the exchange.
        """
        # Create a pool object with an invalid pair
        with pytest.raises(InvalidPoolInitialization):
            BancorV2LiquidityPool(
                exchange=exchange, pair="SOMETHING_ELSE", fee=fee, tokens=[tkn0, tkn1]
            )

    def test_reverse_tokens(self):
        """
        Tests that the order of the tokens in the pool is reversed correctly.
        """
        # Arrange
        pool = BancorV2LiquidityPool(
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
