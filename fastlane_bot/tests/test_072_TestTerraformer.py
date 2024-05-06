
'''
This module tests the Terraformer
'''

from unittest.mock import MagicMock, AsyncMock
import run_blockchain_terraformer as terraformer

ADDRESS_1 = "0x".ljust(42, "1")
ADDRESS_2 = "0x".ljust(42, "2")
ADDRESS_3 = "0x".ljust(42, "3")

def test_organize_pool_details_uni_v2_strategy_id():
    # Mock the input parameters
    pool_data = {
        "args": {
            "pair": ADDRESS_1,
            "token0": ADDRESS_2,
            "token1": ADDRESS_3
        },
        "blockNumber": 123456
    }
    token_manager = MagicMock()
    exchange = terraformer.UNISWAP_V2_NAME
    default_fee = "0.3"
    web3 = MagicMock()

    # Call the tested function
    result = terraformer.organize_pool_details_uni_v2(
        pool_data, token_manager, exchange, default_fee, web3
    )

    # Assert that the output 'strategy_id' is 0
    assert "strategy_id" in result
    assert result["strategy_id"] == 0

def test_organize_pool_details_uni_v3_strategy_id():
    # Mock the input parameters
    pool_data = {
        "args": {
            "pool": ADDRESS_1,
            "token0": ADDRESS_2,
            "token1": ADDRESS_3,
            "tickSpacing": 10,
            "fee": "3000"
        },
        "blockNumber": 123456
    }
    token_manager = MagicMock()
    exchange = terraformer.UNISWAP_V3_NAME
    web3 = MagicMock()

    # Call the tested function
    pool_info = terraformer.organize_pool_details_uni_v3(
        pool_data, token_manager, exchange, web3
    )

    # Assert that the output 'strategy_id' is 0
    assert "strategy_id" in pool_info
    assert pool_info["strategy_id"] == 0

def test_organize_pool_details_solidly_v2_strategy_id():
    # Mock the input parameters
    pool_data = {
        "args": {
            "pair": ADDRESS_1,
            "token0": ADDRESS_2,
            "token1": ADDRESS_3,
            "stable": True
        },
        "blockNumber": 123456
    }
    token_manager = MagicMock()
    exchange = terraformer.SOLIDLY_V2_NAME
    exchange_object = MagicMock()
    exchange_object.get_abi.return_value = "test_abi"
    exchange_object.get_fee = AsyncMock(return_value=("0.3", 0.3))
    web3 = MagicMock()
    async_web3 = MagicMock()
    async_web3.eth.contract.return_value = AsyncMock()

    # Call the tested function
    pool_info = terraformer.organize_pool_details_solidly_v2(
        pool_data, token_manager, exchange, exchange_object, web3, async_web3
    )

    # Assert that the output 'strategy_id' is 0
    assert "strategy_id" in pool_info
    assert pool_info["strategy_id"] == 0

def test_organize_pool_details_balancer_strategy_id():
    # Mock the input parameters
    pool_data = {
        "swapEnabled": True,
        "id": "pool123",
        "poolType": "type1",
        "address": ADDRESS_1,
        "tokens": [
            {"address": ADDRESS_2, "symbol": "TKN1", "decimals": 18, "weight": 0.5},
            {"address": ADDRESS_3, "symbol": "TKN2", "decimals": 18, "weight": 0.5}
        ],
        "swapFee": "0.003"
    }

    # Call the tested function
    pool_info = terraformer.organize_pool_details_balancer(pool_data)

    # Assert that the output 'strategy_id' is 0
    assert "strategy_id" in pool_info
    assert pool_info["strategy_id"] == 0