# exchanges_tests.py

import pytest
from unittest.mock import MagicMock, patch

from events.exchanges import UniswapV2, Sushiswap, UniswapV3, ExchangeFactory
from events.pools import UniswapV2Pool, UniswapV3Pool

"""
Test Plan:
The goal is to test the functionality of the Exchange class and its subclasses:
UniswapV2, Sushiswap, UniswapV3, and the ExchangeFactory.
We will use the unittest.mock library for mocking Contracts and Pool classes.
We will test the following functionalities:
- Addition of a pool
- Fetching of a pool
- Fetching of all pools
- Getting ABI
- Getting events
- Getting fees
- Registering exchanges in the factory
- Fetching exchanges from the factory
"""

# Mocking some necessary objects for testing
mock_contract = MagicMock()
mock_contract.events.Sync = "Sync"
mock_contract.events.Swap = "Swap"
mock_contract.functions.fee.return_value.call.return_value = "0.05"

mock_pool = MagicMock(UniswapV2Pool)
mock_pool.state.address = "0xAddress"
mock_pool.state.fee = "0.05"
mock_pool.state.fee_float = 0.05


def test_uniswap_v2():
    # test add_pool and get_pool
    uni_v2 = UniswapV2()
    uni_v2.add_pool_to_exchange(mock_pool)
    assert uni_v2.get_pool("0xAddress") == mock_pool

    # test get_pools
    assert uni_v2.get_pools() == [mock_pool]

    # test get_abi
    assert uni_v2.get_abi() == "UNISWAP_V2_POOL_ABI"

    # test get_events
    assert uni_v2.get_events(mock_contract) == ["Sync"]

    # test get_fee
    assert uni_v2.get_fee("0xAddress", mock_contract) == ("0.003", 0.003)


def test_sushiswap():
    sushi = Sushiswap()
    sushi.add_pool_to_exchange(mock_pool)
    assert sushi.get_pool("0xAddress") == mock_pool
    assert sushi.get_pools() == [mock_pool]
    assert sushi.get_abi() == "SUSHISWAP_POOLS_ABI"
    assert sushi.get_events(mock_contract) == ["Sync"]
    assert sushi.get_fee("0xAddress", mock_contract) == ("0.003", 0.003)


def test_uniswap_v3():
    uni_v3 = UniswapV3()
    uni_v3.add_pool_to_exchange(mock_pool)
    assert uni_v3.get_pool("0xAddress") == mock_pool
    assert uni_v3.get_pools() == [mock_pool]
    assert uni_v3.get_abi() == "UNISWAP_V3_POOL_ABI"
    assert uni_v3.get_events(mock_contract) == ["Swap"]
    assert uni_v3.get_fee("0xAddress", mock_contract) == ("0.05", 0.05)


def test_exchange_factory():
    factory = ExchangeFactory()

    factory.register_exchange("uniswap_v2", UniswapV2)
    factory.register_exchange("uniswap_v3", UniswapV3)
    factory.register_exchange("sushiswap_v2", Sushiswap)

    assert isinstance(factory.get_exchange("uniswap_v2"), UniswapV2)
    assert isinstance(factory.get_exchange("uniswap_v3"), UniswapV3)
    assert isinstance(factory.get_exchange("sushiswap_v2"), Sushiswap)

    # The test should raise a ValueError for the unknown exchange.
    with pytest.raises(ValueError):
        factory.get_exchange("unknown_exchange")


if __name__ == "__main__":
    pytest.main([__file__])
