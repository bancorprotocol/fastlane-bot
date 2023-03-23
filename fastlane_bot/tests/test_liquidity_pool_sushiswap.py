import pytest

from fastlane_bot.constants import ec
from fastlane_bot.exceptions import InvalidPoolInitialization
from fastlane_bot.networks import EthereumNetwork
from fastlane_bot.pools import SushiswapLiquidityPool
from fastlane_bot.tests.utils import get_pool_test_info

# test_pools.py

"""
Code Analysis:
-- Represents a Sushiswap liquidity pool
- Has optional fields (automatically populated if not provided) such as address, liquidity, fee, contract, exchange, and exchange_id
- Has an autoincrementing id
- Has tokens stored in a list
- Has properties for tkn0 and tkn1
- Has a check_token_order() method
- Has an update_liquidity() method
- Has a __post_init__() method which sets the id and calls the setup() method
"""

"""
Test Plan:
- test_init_with_optional_fields(): tests that the class is initialized correctly with optional fields. Test uses [__post_init__(), setup(), validate_pool()]
- test_init_without_optional_fields(): tests that the class is initialized correctly without optional fields. Test uses [__post_init__(), setup(), validate_pool()]
- test_update_liquidity(): tests that the liquidity is updated correctly. Test uses [update_liquidity(), getReserves()]
- test_reverse_tokens(): tests that the order of the tokens is reversed correctly. Test uses [reverse_tokens()]
- test_edge_case_convert_to_correct_decimal_zero_decimals(): tests the edge case where calling the method convert_to_correct_decimal() with a param of 0 decimals leads to the value being unchanged. Test uses [convert_to_correct_decimal(), Decimal()]
- test_how_update_liquidity_affects_liquidity(): tests how calling update_liquidity() affects the liquidity field. Tests that the liquidity is updated correctly. Test uses [update_liquidity(), getReserves(), liquidity]

Additional instructions:
 - Where applicable: Use mocks, set the return_value and verify calls with correct data.
"""

# Valid Params
exchange = "sushiswap_v2"
address, fee, pair, tkn0, tkn1 = get_pool_test_info(exchange)


class TestSushiswapLiquidityPool:
    def test_init_happy_path(self):
        """
        Tests that the SushiswapV2LiquidityPool class is initialized correctly with valid parameters.
        """
        try:
            # Act
            SushiswapLiquidityPool(
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
            SushiswapLiquidityPool(
                exchange=exchange, pair="SOMETHING_ELSE", fee=fee, tokens=[tkn0, tkn1]
            )

    def test_reverse_tokens(self):
        """
        Tests that the order of the tokens in the pool is reversed correctly.
        """
        # Arrange
        pool = SushiswapLiquidityPool(
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
        pool = SushiswapLiquidityPool(
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
