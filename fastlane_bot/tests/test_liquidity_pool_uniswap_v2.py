# test_pools.py

import pytest

from fastlane_bot.constants import ec
from fastlane_bot.exceptions import InvalidPoolInitialization
from fastlane_bot.networks import EthereumNetwork
from fastlane_bot.pools import UniswapV2LiquidityPool
from fastlane_bot.tests.utils import get_pool_test_info

"""
Code Analysis:
-- Represents a Uniswap V2 liquidity pool.
- Has fields for block number, address, liquidity, fee, contract, exchange, exchange_id, and id.
- Has properties for tkn0, tkn1, and base_pair.
- Has methods for reverse_tokens, validate_pool, init_contract, setup, convert_to_correct_decimal, to_pandas, check_token_order, and update_liquidity.
- Has a __post_init__ method which sets the id and calls the setup method.
"""

"""
Test Plan:
- test_init_happy_path(): tests that the UniswapV2LiquidityPool class is initialized correctly with valid parameters. Test uses [__post_init__(), setup(), validate_pool(), update_liquidity()]
- test_init_invalid_pair(): tests the edge case where the pair is not found in the pool info for the exchange. Test uses [__post_init__(), setup(), validate_pool()]
- test_init_invalid_address(): tests the edge case where the address is not valid. Test uses [__post_init__(), setup(), validate_pool()]
- test_reverse_tokens(): tests that the order of the tokens in the pool is reversed correctly. Test uses [reverse_tokens(), validate_pool()]
- test_update_liquidity(): tests that the liquidity of the pool is updated correctly. Test uses [update_liquidity(), validate_pool()]
- test_how_update_liquidity_affects_liquidity(): tests how calling update_liquidity affects the liquidity field. Tests that the liquidity is updated correctly. Test uses [update_liquidity(), validate_pool(), liquidity]

Additional instructions:
 - Where applicable: Use mocks, set the return_value and verify calls with correct data.
"""

# Valid Params
exchange = "uniswap_v2"
address, fee, pair, tkn0, tkn1 = get_pool_test_info(exchange)


class TestUniswapV2LiquidityPool:
    def test_init_happy_path(self):
        """
        Tests that the SushiswapV2LiquidityPool class is initialized correctly with valid parameters.
        """
        try:
            # Act
            UniswapV2LiquidityPool(
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
            UniswapV2LiquidityPool(
                exchange=exchange, pair="SOMETHING_ELSE", fee=fee, tokens=[tkn0, tkn1]
            )

    def test_reverse_tokens(self):
        """
        Tests that the order of the tokens in the pool is reversed correctly.
        """
        # Arrange
        pool = UniswapV2LiquidityPool(
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

    def test_update_liquidity(self):
        """
        Tests that the liquidity of the pool is updated correctly.
        """

        # Create a pool object

        connection = EthereumNetwork(
            network_id=ec.TEST_NETWORK,
            network_name="tenderly",
            provider_url=ec.TENDERLY_FORK_RPC,
            fastlane_contract_address=ec.FASTLANE_CONTRACT_ADDRESS,
        )

        connection.connect_network()

        # Create a pool object
        pool = UniswapV2LiquidityPool(
            exchange=exchange,
            init_liquidity=False,
            init_setup=False,
            address=address,
            fee=fee,
            tokens=[tkn0, tkn1],
            connection=connection.web3,
        )

        # Initialize the pool contract
        pool.setup()

        assert pool.tkn0.amt == 0

        # Update the liquidity of the pool
        pool.update_liquidity()

        # Assert that the liquidity is updated correctly
        assert pool.tkn0.amt > 0
