# test_pools.py

import pytest

from fastlane_bot.constants import ec
from fastlane_bot.exceptions import InvalidPoolInitialization
from fastlane_bot.networks import EthereumNetwork
from fastlane_bot.pools import LiquidityPool
from fastlane_bot.token import ERC20Token

"""
Code Analysis:
-- Represents a base class for all AMM LiquidityPools
- Has required fields such as block_number, tkn0, tkn1, exchange, fee, and pair
- Has a method to check the token order for Bancor V2 pools
- Has a method to update the liquidity of the pool
- Has a post-init method to set up the pool based on the exchange type (Uniswap V2, Uniswap V3, Sushiswap, Bancor V2, Bancor V3)
- Has a method to convert the token amounts to the correct decimal format
"""

"""
Test Plan:
- test_init_happy_path(): tests that the class is initialized correctly with valid parameters. Test uses [__post_init__(), check_token_order(), update_liquidity()]
- test_init_invalid_exchange(): tests the edge case where an invalid exchange is passed in. Test uses [__post_init__()]
- test_init_invalid_tokens(): tests the edge case where invalid tokens are passed in. Test uses [__post_init__()]
- test_init_invalid_fee(): tests the edge case where an invalid fee is passed in. Test uses [__post_init__()]
- test_init_invalid_pair(): tests the edge case where an invalid pair is passed in. Test uses [__post_init__()]
- test_check_token_order_happy_path(): tests that the token order is checked correctly when the exchange is Bancor V2. Test uses [check_token_order()]

Additional instructions:
 - Where applicable: Use mocks, set the return_value and verify calls with correct data.
"""

# Valid Params
db = ec.DB
db = db[(db["exchange"] == "bancor_v2")]
address = db["address"].iloc[0]
fee = db["fee"].iloc[0]
pair = db["pair"].iloc[0]
exchange = "bancor_v2"
tkn0 = ERC20Token(symbol=db["symbol0"].iloc[0])
tkn1 = ERC20Token(symbol=db["symbol1"].iloc[0])


class TestLiquidityPool:
    def test_init_happy_path(self):
        """
        Tests that the LiquidityPool class is initialized correctly with valid parameters.
        """
        try:
            # Act
            LiquidityPool(exchange=exchange, pair=pair, fee=fee, tkn0=tkn0, tkn1=tkn1)
        except Exception as e:
            pytest.fail(f"Unexpected exception: {e}")

    def test_init_invalid_pair(self):
        """
        Tests the edge case where the pair is not found in the pool info for the exchange.
        """
        # Create a pool object with an invalid pair
        with pytest.raises(InvalidPoolInitialization):
            LiquidityPool(
                exchange=exchange, pair="SOMETHING_ELSE", fee=fee, tkn0=tkn0, tkn1=tkn1
            )

    def test_init_invalid_inputs(self):
        """
        Tests the edge case where the inputs are not valid and the pool cannot be initialized.
        """

        # Create a pool object with an invalid input
        with pytest.raises(InvalidPoolInitialization):
            LiquidityPool(
                exchange=exchange,
                pair=None,
                fee=fee,
                address=None,
                tkn0=None,
                tkn1=tkn1,
            )

    def test_reverse_tokens(self):
        """
        Tests that the order of the tokens in the pool is reversed correctly.
        """
        # Arrange
        pool = LiquidityPool(
            exchange=exchange, pair=pair, fee=fee, tkn0=tkn0, tkn1=tkn1
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

        connection = EthereumNetwork(
            network_id=ec.TEST_NETWORK,
            network_name="tenderly",
            provider_url=ec.TENDERLY_FORK_RPC,
            fastlane_contract_address=ec.FASTLANE_CONTRACT_ADDRESS,
        )

        connection.connect_network()

        # Create a pool object
        pool = LiquidityPool(
            exchange=exchange,
            pair=pair,
            tkn0=tkn0,
            tkn1=tkn1,
            init_liquidity=False,
            connection=connection.web3,
        )

        assert pool.liquidity is None
        # pool.setup()

        # Update the liquidity of the pool
        pool.update_liquidity()

        # Assert that the liquidity is updated correctly
        assert pool.liquidity > 0
