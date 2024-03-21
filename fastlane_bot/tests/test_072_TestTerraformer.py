
'''
This module tests the Terraformer
'''

from unittest.mock import MagicMock, AsyncMock
from run_blockchain_terraformer import organize_pool_details_balancer, organize_pool_details_uni_v2, organize_pool_details_solidly_v2, organize_pool_details_uni_v3


def test_organize_pool_details_uni_v2_strategy_id():
    # Mock the input parameters
    pool_data = {
        "args": {
            "pair": "0x123",
            "token0": "0x456",
            "token1": "0x789"
        },
        "blockNumber": 123456
    }
    token_manager = MagicMock()
    exchange = "test_exchange"
    default_fee = "0.3"
    web3 = MagicMock()
    web3.to_checksum_address.return_value = "0x123"

    # Process the function
    result = organize_pool_details_uni_v2(
        pool_data, token_manager, exchange, default_fee, web3
    )

    # Check if the result contains 'strategy_id' with value 0
    assert "strategy_id" in result
    assert result["strategy_id"] == 0

def test_organize_pool_details_uni_v3_strategy_id():
    # Mock the input parameters
    pool_data = {
        "args": {
            "pool": "0x123",
            "token0": "0x456",
            "token1": "0x789",
            "tickSpacing": 10,
            "fee": "3000"
        },
        "blockNumber": 123456
    }
    token_manager = MagicMock()
    exchange = "test_exchange"
    web3 = MagicMock()
    web3.to_checksum_address.return_value = "0x123"

    # Call the function with the mock objects
    pool_info = organize_pool_details_uni_v3(
        pool_data, token_manager, exchange, web3
    )

    # Assert the 'strategy_id' in the output is 0
    assert "strategy_id" in pool_info
    assert pool_info["strategy_id"] == 0

def test_organize_pool_details_solidly_v2_strategy_id():
    # Mock the input parameters
    pool_data = {
        "args": {
            "pair": "0x123",
            "token0": "0x456",
            "token1": "0x789",
            "stable": True
        },
        "blockNumber": 123456
    }
    token_manager = MagicMock()
    exchange = "test_exchange"
    exchange_object = MagicMock()
    exchange_object.get_abi.return_value = "test_abi"
    exchange_object.get_fee = AsyncMock(return_value=("0.3", 0.3))
    web3 = MagicMock()
    web3.to_checksum_address.return_value = "0x123"
    async_web3 = MagicMock()
    async_web3.eth.contract.return_value = AsyncMock()

    # Run the coroutine with asyncio.run (Python 3.7+)
    pool_info = organize_pool_details_solidly_v2(
            pool_data, token_manager, exchange, exchange_object, web3, async_web3
        )


    # Check if the result contains 'strategy_id' with value 0
    assert "strategy_id" in pool_info
    assert pool_info["strategy_id"] == 0

def test_organize_pool_details_balancer_strategy_id():
    # Mock the input parameters
    pool_data = {
        "swapEnabled": True,
        "id": "pool123",
        "poolType": "type1",
        "address": "0x123",
        "tokens": [
            {"address": "0x456", "symbol": "TKN1", "decimals": 18, "weight": 0.5},
            {"address": "0x789", "symbol": "TKN2", "decimals": 18, "weight": 0.5}
        ],
        "swapFee": "0.003"
    }
    token_prices = {
        "0x456": {"usd": "1"},
        "0x789": {"usd": "2"}
    }
    web3 = MagicMock()
    web3.to_checksum_address.side_effect = lambda x: x  # Mock checksum address to return the same value

    # Call the function
    pool_info = organize_pool_details_balancer(pool_data, token_prices, web3)

    # Check the 'strategy_id' in the output
    assert "strategy_id" in pool_info
    assert pool_info["strategy_id"] == 0