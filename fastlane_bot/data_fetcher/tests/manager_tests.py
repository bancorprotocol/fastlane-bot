import pytest
from web3 import Web3
import pandas as pd
from unittest.mock import MagicMock

from events.manager import Manager
from events.exchanges import exchange_factory
from events.pools import pool_factory

"""
# Test Plan:
# The purpose of this test module is to test the Manager class and ensure its methods function as expected. 
# We achieve this by creating isolated tests for each method in the Manager class.
# Mock objects are used to avoid real interaction with blockchain and provide expected return values.
# We are focusing on 'happy path' scenarios, ensuring that given the right input, we get the expected output. 
"""

# Constants for testing
FAKE_WEB3 = Web3(
    Web3.HTTPProvider("http://127.0.0.1:8545")
)  # Replace with actual provider if necessary.
EMPTY_DF = pd.DataFrame()
SUPPORTED_EXCHANGES = ["uniswap_v2", "uniswap_v3"]


# Mocking Exchange class to avoid any real interaction with blockchain
class MockExchange:
    def get_abi(self):
        return []

    def get_events(self, contract):
        return []

    def get_pools(self):
        return []

    def get_fee(self, addr, contract):
        return 0.03, 0.00003

    def add_pool(self, pool):
        pass


exchange_factory.get_exchange = MagicMock(return_value=MockExchange())
pool_factory.get_pool = MagicMock()


@pytest.fixture
def manager():
    return Manager(
        web3=FAKE_WEB3, pool_data=EMPTY_DF, SUPPORTED_EXCHANGES=SUPPORTED_EXCHANGES
    )


def test_post_init(manager):
    """
    Test the post initialization method.
    Ensures that the exchanges are initialized as expected.
    """
    assert len(manager.exchanges) == len(SUPPORTED_EXCHANGES)
    assert all([ex in manager.exchanges for ex in SUPPORTED_EXCHANGES])


def test_init_exchange_contracts(manager):
    """
    Test the initialization of exchange contracts.
    Ensures that event contracts and pool contracts are initialized as expected.
    """
    manager.init_exchange_contracts()
    assert len(manager.event_contracts) == len(SUPPORTED_EXCHANGES)
    assert len(manager.pool_contracts) == len(SUPPORTED_EXCHANGES)


def test_get_event_exchange_name(manager):
    """
    Test the method for getting exchange name from event.
    Ensures that the correct exchange name is returned based on the event data.
    """
    event = {"args": {"sqrtPriceX96": 100}}
    assert manager.exchange_name_from_event(event) == "uniswap_v3"

    event = {"args": {"reserve0": 100}}
    assert manager.exchange_name_from_event(event) == "uniswap_v2"


def test_get_or_create_token_contracts(manager):
    """
    Test the method for creating and retrieving token contracts.
    Ensures that the contract is correctly returned based on the address, and that new contracts are correctly created.
    """
    address = "0x1"  # A fake address
    contract = manager.get_or_create_token_contracts(
        manager.web3, manager.erc20_contracts, address
    )
    assert contract == manager.erc20_contracts[address]

    address = "0x2"  # Another fake address
    new_contract = manager.get_or_create_token_contracts(
        manager.web3, manager.erc20_contracts, address
    )
    assert new_contract != contract
    assert new_contract == manager.erc20_contracts[address]


# ... Continue writing unit tests for other methods in the Manager class ...


if __name__ == "__main__":
    pytest.main([__file__])
