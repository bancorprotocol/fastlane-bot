import eth_event
import pytest

from fastlane_bot.constants import ec
from fastlane_bot.exceptions import InvalidPoolInitialization
from fastlane_bot.pools import BaseLiquidityPool
from fastlane_bot.tests.utils import get_pool_test_info
from fastlane_bot.utils import get_abi_and_router

# test_pools.py

"""
Code Analysis:
-- Represents a pool
- Has properties such as address, liquidity, fee, contract, exchange, exchange_id, and id
- Has methods to check token order, update liquidity, reverse tokens, validate pool, init contract, setup, convert to correct decimal, and to pandas
- Has an abstract method to check token order and update liquidity
"""

"""
Test Plan:
- test_init_contract_happy_path(): tests that the init_contract() method initializes the contract correctly when given valid parameters. Test uses [init_contract(), contract, address, abi]
- test_init_contract_invalid_address(): tests the edge case where calling the init_contract() method with an invalid address leads to an error. Test uses [init_contract(), address]
- test_init_contract_invalid_abi(): tests the edge case where calling the init_contract() method with an invalid ABI leads to an error. Test uses [init_contract(), abi]
- test_setup_happy_path(): tests that the setup() method sets the constants for the pool correctly when given valid parameters. Test uses [setup(), tkn0, tkn1, exchange, pair, _ABI, _POOL_INFO_FOR_EXCHANGE]
- test_setup_invalid_pair(): tests the edge case where calling the setup() method with an invalid pair leads to an error. Test uses [setup(), pair]
- test_how_update_liquidity_affects_liquidity(): tests how calling update_liquidity() affects the liquidity field. Tests that the liquidity field is updated correctly. Test uses [update_liquidity(), liquidity]

Additional instructions:
 - Where applicable: Use mocks, set the return_value and verify calls with correct data.
"""

# Valid Params
exchange = "sushiswap_v2"
address, fee, pair, tkn0, tkn1 = get_pool_test_info(exchange)


class TestBaseLiquidityPool:
    def test_init_contract_happy_path(self):
        """
        Tests that the init_contract() method initializes the contract correctly when given valid parameters.
        """
        # Arrange
        # Create a pool object
        pool = BaseLiquidityPool(
            exchange=exchange, address=address, init_liquidity=False
        )

        assert pool.liquidity is None

        abi = ec.__getattribute__(f"SUSHISWAP_POOLS_ABI")

        # Assert
        assert pool.contract.address == address
        assert pool.contract.abi == abi

    def test_init_contract_invalid_address(self):
        """
        Tests the edge case where calling the init_contract() method with an invalid address leads to an error.
        """
        # Arrange
        contract_address = "invalid"

        # Act & Assert
        with pytest.raises(InvalidPoolInitialization):
            pool = BaseLiquidityPool(
                exchange=exchange, address=contract_address, init_liquidity=False
            )
            pool.setup()

    def test_setup_invalid_pair(self):
        """
        Tests the edge case where calling the setup() method with an invalid pair leads to an error.
        """

        # Arrange, Act & Assert
        with pytest.raises(InvalidPoolInitialization):
            BaseLiquidityPool(tokens=["INVALID", "INVALID"], exchange=exchange).setup()
