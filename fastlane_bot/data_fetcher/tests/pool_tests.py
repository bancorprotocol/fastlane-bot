# pool_tests.py

import pytest
from unittest.mock import MagicMock, patch

from events.pools import UniswapV2Pool, SushiswapPool, UniswapV3Pool, PoolFactory
import pandas as pd

"""
Test Plan:
The goal is to test the functionality of the Pool class and its subclasses:
UniswapV2Pool, SushiswapPool, UniswapV3Pool, and the PoolFactory.
We will use the unittest.mock library for mocking Contracts.
We will test the following functionalities:
- Update existing pool
- Get common data
- Add event arguments
- Update from contract
- Registering pool types in the factory
- Fetching pool types from the factory
"""

# Mocking some necessary objects for testing
mock_contract = MagicMock()
mock_contract.caller.getReserves.return_value = (100, 200)
mock_contract.caller.slot0.return_value = (12345, 56789)
mock_contract.caller.liquidity.return_value = 300
mock_contract.caller.fee.return_value = "0.05"
mock_contract.caller.tickSpacing.return_value = 10

event = {
    "blockNumber": 500,
    "address": "0xAddress",
    "args": {
        "reserve0": 1000,
        "reserve1": 2000,
        "liquidity": 500,
        "sqrtPriceX96": 12345,
        "tick": 56789,
    },
}

pool_info_df = pd.DataFrame(
    {"cid": [1], "pair_name": ["pair"], "descr": ["description"]}
)


def test_sushiswap_pool():
    pool = SushiswapPool()
    pool.update_from_event(event, pool_info_df)

    assert pool.state["last_updated_block"][0] == 500
    assert pool.state["pair_name"][0] == "pair"
    assert pool.state["address"][0] == "0xAddress"

    data = pool.update_from_event(event["args"], {})
    assert data["tkn0_balance"] == 1000
    assert data["tkn1_balance"] == 2000

    contract_data = pool.update_from_contract(mock_contract)
    assert contract_data["fee"] == "0.003"
    assert contract_data["tkn0_balance"] == 100
    assert contract_data["tkn1_balance"] == 200
    assert contract_data["exchange_name"] == "uniswap_v2"


def test_uniswap_v2_pool():
    pool = UniswapV2Pool()
    pool.update_from_event(event, pool_info_df)

    assert pool.state["last_updated_block"][0] == 500
    assert pool.state["pair_name"][0] == "pair"
    assert pool.state["address"][0] == "0xAddress"

    data = pool.update_from_event(event["args"], {})
    assert data["tkn0_balance"] == 1000
    assert data["tkn1_balance"] == 2000

    contract_data = pool.update_from_contract(mock_contract)
    assert contract_data["fee"] == "0.003"
    assert contract_data["tkn0_balance"] == 100
    assert contract_data["tkn1_balance"] == 200
    assert contract_data["exchange_name"] == "uniswap_v2"


def test_uniswap_v3_pool():
    pool = UniswapV3Pool()
    pool.update_from_event(event, pool_info_df)

    assert pool.state["last_updated_block"][0] == 500
    assert pool.state["pair_name"][0] == "pair"
    assert pool.state["    address"][0] == "0xAddress"

    data = pool.update_from_event(event["args"], {})
    assert data["liquidity"] == 500
    assert data["sqrt_price_q96"] == 12345
    assert data["tick"] == 56789

    contract_data = pool.update_from_contract(mock_contract)
    assert contract_data["tick"] == 56789
    assert contract_data["sqrt_price_q96"] == 12345
    assert contract_data["liquidity"] == 300
    assert contract_data["fee"] == "0.05"
    assert contract_data["fee_float"] == 0.00005
    assert contract_data["tick_spacing"] == 10


def test_pool_factory():
    factory = PoolFactory()
    factory.register_format("uniswap_v2", UniswapV2Pool)
    factory.register_format("uniswap_v3", UniswapV3Pool)
    factory.register_format("sushiswap_v2", SushiswapPool)

    pool = factory.get_pool("uniswap_v2")
    assert isinstance(pool, UniswapV2Pool)

    pool = factory.get_pool("uniswap_v3")
    assert isinstance(pool, UniswapV3Pool)

    pool = factory.get_pool("sushiswap_v2")
    assert isinstance(pool, SushiswapPool)

    # The test should raise a ValueError for the unknown pool.
    with pytest.raises(ValueError):
        factory.get_pool("unknown_pool")


if __name__ == "__main__":
    pytest.main([__file__])
