import json

import nest_asyncio
import pytest
from unittest.mock import AsyncMock, MagicMock
from fastlane_bot.events.async_event_update_utils import TokenFeeResponse, get_token_and_fee
from web3.contract import AsyncContract

from fastlane_bot.events.exchanges import CarbonV1, UniswapV2, BancorV2

nest_asyncio.apply()

# Define a fixture for the contract object
@pytest.fixture
def contract():
    return AsyncMock(spec=AsyncContract)

# Define a fixture for the event object
@pytest.fixture
def uniswap_v2_event():
    return {
        "args": {
            "reserve0": 10941658708636,
            "reserve1": 10971030461349
        },
        "event": "Sync",
        "logIndex": 255,
        "transactionIndex": 115,
        "transactionHash": "0xecca41359219ee5a0e73652d1bea48bdc73216f294e865416da3f27232fee6e8",
        "address": "0x3041CbD36888bECc7bbCBc0045E3B1f144466f5f",
        "blockHash": "0x859b0803d75c861baa46e4e02be794187fd9a28a048f19ca148ff7f22e80c8ff",
        "blockNumber": 17613636
    }


@pytest.fixture
def carbon_v1_event():
    return {
        "args": {
            "owner": "0xDdD6516Ed7e9B2dEfb2e1aE50379943cC9eE2b73",
            "token0": "0x1F573D6Fb3F13d689FF844B4cE37794d79a7FF1C",
            "token1": "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48",
            "id": 2381976568446569244243622252022377480690,
            "order0": [
                1221000000000000000000,
                1221000000000000000000,
                0,
                6111054486652827
            ],
            "order1": [
                464234783,
                464234783,
                0,
                173512828
            ]
        },
        "event": "StrategyCreated",
        "logIndex": 131,
        "transactionIndex": 88,
        "transactionHash": "0x2e147a21fa45c76c9fa0231a52629b71dcc7293747c4fb1c96f7e0ce5f058c9a",
        "address": "0xC537e898CD774e2dCBa3B14Ea6f34C93d5eA45e1",
        "blockHash": "0x452c70bd1d52430fbc2327425f1ad3e59a3e1ff5f0a84d4a6aaf757c4d3a942f",
        "blockNumber": 18176438
    }

@pytest.fixture
def bancor_v2_event():
    return {
        "args": {
            "_token1": "0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE",
            "_token2": "0x1F573D6Fb3F13d689FF844B4cE37794d79a7FF1C",
            "_rateN": 5698079648237338312679700,
            "_rateD": 1404376232459809237924},
        "event": "TokenRateUpdate",
        "logIndex": 106,
        "transactionIndex": 22,
        "transactionHash": "0x5b03ac11612de4b57824bcec404cdbbe96265425c073b3ac3abfa9b9edf8dd1e",
        "address": "0xADd45B18153382D69AB5A13c44d1782B8f3aDEEc",
        "blockHash": "0x45f34d791644169219b806ebdf60341fb5e62e4ed49e9da225e34d82e17f1f8b",
        "blockNumber": 18005932
    }

@pytest.mark.asyncio
async def test_get_token_and_fee_carbon_v1(contract, carbon_v1_event):
    # Mock the Exchange and its methods
    exchange = AsyncMock(spec=CarbonV1)
    exchange.exchange_name = "carbon_v1"
    exchange.base_exchange_name = "carbon_v1"
    exchange.get_tkn0 = AsyncMock(return_value=carbon_v1_event["args"]["token0"])
    exchange.get_tkn1 = AsyncMock(return_value=carbon_v1_event["args"]["token1"])
    exchange.get_fee = AsyncMock(return_value=0.003)

    # Call the function under test
    response = await get_token_and_fee(exchange, carbon_v1_event["address"], contract, carbon_v1_event)

    # Verify the response
    assert isinstance(response, TokenFeeResponse)
    assert response.exchange_name == "carbon_v1"
    assert response.tkn0_address == carbon_v1_event["args"]["token0"]
    assert response.tkn1_address == carbon_v1_event["args"]["token1"]
    assert response.fee == 0.003
    assert response.cid is not None
    assert response.strategy_id == str(carbon_v1_event["args"]["id"])


@pytest.mark.asyncio
async def test_get_token_and_fee_uniswap_v2(contract, uniswap_v2_event):
    # Mock the Exchange and its methods
    exchange = AsyncMock(spec=UniswapV2)
    exchange.exchange_name = "uniswap_v2"
    exchange.base_exchange_name = "uniswap_v2"
    exchange.get_tkn0 = AsyncMock(return_value="0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48")
    exchange.get_tkn1 = AsyncMock(return_value="0xdAC17F958D2ee523a2206206994597C13D831ec7")
    exchange.get_fee = AsyncMock(return_value=0.003)

    # Call the function under test
    response = await get_token_and_fee(exchange, uniswap_v2_event["address"], contract, uniswap_v2_event)

    # Verify the response
    assert isinstance(response, TokenFeeResponse)
    assert response.exchange_name == "uniswap_v2"
    assert response.tkn0_address == "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48"
    assert response.tkn1_address == "0xdAC17F958D2ee523a2206206994597C13D831ec7"
    assert response.fee == 0.003
    assert response.cid is not None
    assert response.strategy_id == 0
    assert response.anchor is None


@pytest.mark.asyncio
async def test_get_token_and_fee_bancor_v2(contract, bancor_v2_event):
    # Mock the Exchange and its methods
    exchange = AsyncMock(spec=BancorV2)
    exchange.exchange_name = "bancor_v2"
    exchange.base_exchange_name = "bancor_v2"
    exchange.get_tkn0 = AsyncMock(return_value="0x1F573D6Fb3F13d689FF844B4cE37794d79a7FF1C")
    exchange.get_tkn1 = AsyncMock(return_value="0x7f39C581F595B53c5cb19bD0b3f8dA6c935E2Ca0")
    exchange.get_fee = AsyncMock(return_value=0.003)
    exchange.get_anchor = AsyncMock(return_value='0xB2607CB158bc222DD687e4D794c607B5ce983Ce2')
    exchange.get_connector_tokens = AsyncMock(return_value='0x7f39C581F595B53c5cb19bD0b3f8dA6c935E2Ca0')

    # Call the function under test
    response = await get_token_and_fee(exchange, bancor_v2_event["address"], contract, bancor_v2_event)

    # Verify the response
    assert isinstance(response, TokenFeeResponse)
    assert response.exchange_name == "bancor_v2"
    assert response.tkn0_address == "0x1F573D6Fb3F13d689FF844B4cE37794d79a7FF1C"
    assert response.tkn1_address == "0x7f39C581F595B53c5cb19bD0b3f8dA6c935E2Ca0"
    assert response.fee == 0.003
    assert response.cid is not None
    assert response.strategy_id == 0
    assert response.anchor is '0xB2607CB158bc222DD687e4D794c607B5ce983Ce2'


