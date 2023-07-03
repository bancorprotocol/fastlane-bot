from fastlane_bot import Bot
from fastlane_bot.tools.cpc import ConstantProductCurve as CPC

print("{0.__name__} v{0.__VERSION__} ({0.__DATE__})".format(CPC))
print("{0.__name__} v{0.__VERSION__} ({0.__DATE__})".format(Bot))
from fastlane_bot.testing import *

plt.style.use('seaborn-dark')
plt.rcParams['figure.figsize'] = [12,6]
from fastlane_bot import __VERSION__
require("3.0", __VERSION__)

from unittest.mock import Mock

import pytest

from ..exchanges import UniswapV2, SushiswapV2, UniswapV3, BancorV3, CarbonV1
from ...data.abi import UNISWAP_V2_POOL_ABI, UNISWAP_V3_POOL_ABI, SUSHISWAP_POOLS_ABI, BANCOR_V3_POOL_COLLECTION_ABI, \
    CARBON_CONTROLLER_ABI


@pytest.fixture
def setup_data():
    return {
        "uniswap_v2_event": {'args': {'reserve0': 10941658708636, 'reserve1': 10971030461349}, 'event': 'Sync', 'logIndex': 255, 'transactionIndex': 115, 'transactionHash': '0xecca41359219ee5a0e73652d1bea48bdc73216f294e865416da3f27232fee6e8', 'address': '0x3041CbD36888bECc7bbCBc0045E3B1f144466f5f', 'blockHash': '0x859b0803d75c861baa46e4e02be794187fd9a28a048f19ca148ff7f22e80c8ff', 'blockNumber': 17613636},
        "sushiswap_v2_event": {'args': {'reserve0': 6543521908014628725401090, 'reserve1': 2535973648121313922634}, 'event': 'Sync', 'logIndex': 93, 'transactionIndex': 38, 'transactionHash': '0xc7c0560a8829fb43e05003ef07de8ce682167bb8a16a5e73d832a6a15513dace', 'address': '0x4A86C01d67965f8cB3d0AAA2c655705E64097C31', 'blockHash': '0xefc338e7672291a889029a206f93a50feba92ba7be9e1210f382d79cf2fc9972', 'blockNumber': 17613685},
        "uniswap_v3_event": {'args': {'sender': '0x0000000000a84D1a9B0063A910315C7fFA9Cd248', 'recipient': '0x0000000000a84D1a9B0063A910315C7fFA9Cd248', 'amount0': 1001531661949054480779, 'amount1': -1560777208046492502, 'sqrtPriceX96': 3141136922601321808510033604, 'liquidity': 27271279776041947233926, 'tick': -64559}, 'event': 'Swap', 'logIndex': 48, 'transactionIndex': 4, 'transactionHash': '0x2063e741127ec1a61b03f5c1e01a5ba83c695606e56b8b705b69f0218c6433f4', 'address': '0xcBcC3cBaD991eC59204be2963b4a87951E4d292B', 'blockHash': '0xc4c2ffbf7e0a2b94721eee92a8acaed343d2f332bcd83bf0b66d63b826d78cf6', 'blockNumber': 17613637},
        "bancor_v3_event": {'args': {'pool': '0x4691937a7508860F876c9c0a2a617E7d9E945D4B', 'tkn_address': '0x4691937a7508860F876c9c0a2a617E7d9E945D4B', 'prevLiquidity': 2969054758119920810356648, 'newLiquidity': 2981332708522538339515032}, 'event': 'TradingLiquidityUpdated', 'logIndex': 35, 'transactionIndex': 4, 'transactionHash': '0x2063e741127ec1a61b03f5c1e01a5ba83c695606e56b8b705b69f0218c6433f4', 'address': '0xB67d563287D12B1F41579cB687b04988Ad564C6C', 'blockHash': '0xc4c2ffbf7e0a2b94721eee92a8acaed343d2f332bcd83bf0b66d63b826d78cf6', 'blockNumber': 17613637},
        "carbon_v1_event_update": {"args": {"id": 340282366920938463463374607431768211699, "token0": "0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE", "token1": "0x6B175474E89094C44Da98b954EedeAC495271d0F", "order0": [22815419571180453234, 30000000000000000000, 80181217415, 6293971818901], "order1": [64052264601120813405051, 64052264601120813405051, 164724635005760, 1875443170982464], "reason": 1}, "event": "StrategyUpdated", "logIndex": 378, "transactionIndex": 157, "transactionHash": "0x78aeca0f0f6263a93b5f6208241e302a1994ad614968fa161ca072727b9a5f4b", "address": "0xC537e898CD774e2dCBa3B14Ea6f34C93d5eA45e1", "blockHash": "0x5d9484d50eaf69a1c5715e0a52b58a3d362bce09ff5517bc43ff6fe2cfa2965f", "blockNumber": 17613884},
        "carbon_v1_event_delete": {'args': {'owner': '0x1f660f4C9e0c833520eEfE7e207249B3Fa7DB92F', 'token0': '0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE', 'token1': '0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48', 'id': 1701411834604692317316873037158841057369, 'order0': (250000000000000000, 250000000000000000, 0, 4414201427359729), 'order1': (446009466, 446009466, 0, 10901478971)}, 'event': 'StrategyDeleted', 'logIndex': 454, 'transactionIndex': 158, 'transactionHash': '0x6e2ee77bb751644a1f0f693f4e7b2547be495d5473b378b36b58a8c72ba92421', 'address': '0xC537e898CD774e2dCBa3B14Ea6f34C93d5eA45e1', 'blockHash': '0x898cd767e25952ae0a2de3714efb6406846702815bb8f77cdbea5824a0e1d6ff', 'blockNumber': 17614185},
        "carbon_v1_event_create": {"args": {"owner": "0x11B1785D9Ac81480c03210e89F1508c8c115888E", "token0": "0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE", "token1": "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48", "id": 1701411834604692317316873037158841057529, "order0": [0, 0, 3041871764463936, 4414201427359729], "order1": [383896420, 383896420, 235894417, 11805182669]}, "event": "StrategyCreated", "logIndex": 227, "transactionIndex": 89, "transactionHash": "0x8f6ee587bd72cfa8a1a3faf165825c528df8a587827f182f099deed71c998b75", "address": "0xC537e898CD774e2dCBa3B14Ea6f34C93d5eA45e1", "blockHash": "0x7fcc4a119651992df2fd94d7d8c33f895c2076480badf5ccc6b08e78e053f8fe", "blockNumber": 17599450},
        "carbon_v1_event_create_for_update": {"args": {"owner": "0x11B1785D9Ac81480c03210e89F1508c8c115888E", "id": 340282366920938463463374607431768211699, "token0": "0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE", "token1": "0x6B175474E89094C44Da98b954EedeAC495271d0F", "order0": [0, 0, 0, 0], "order1": [0, 0, 0, 0]}, "event": "StrategyCreated", "logIndex": 378, "transactionIndex": 157, "transactionHash": "0x78aeca0f0f6263a93b5f6208241e302a1994ad614968fa161ca072727b9a5f4b", "address": "0xC537e898CD774e2dCBa3B14Ea6f34C93d5eA45e1", "blockHash": "0x5d9484d50eaf69a1c5715e0a52b58a3d362bce09ff5517bc43ff6fe2cfa2965f", "blockNumber": 17613884},
        "carbon_v1_event_create_for_delete": {'args': {'owner': '0x1f660f4C9e0c833520eEfE7e207249B3Fa7DB92F', 'token0': '0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE', 'token1': '0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48', 'id': 1701411834604692317316873037158841057369, 'order0': (250000000000000000, 250000000000000000, 0, 4414201427359729), 'order1': (446009466, 446009466, 0, 10901478971)}, 'event': 'StrategyCreated', 'logIndex': 454, 'transactionIndex': 158, 'transactionHash': '0x6e2ee77bb751644a1f0f693f4e7b2547be495d5473b378b36b58a8c72ba92421', 'address': '0xC537e898CD774e2dCBa3B14Ea6f34C93d5eA45e1', 'blockHash': '0x898cd767e25952ae0a2de3714efb6406846702815bb8f77cdbea5824a0e1d6ff', 'blockNumber': 17614185},

    }

# The contract fixture creates a mocked contract with predefined return values
@pytest.fixture
def mocked_contract():
    mocked_contract = Mock()
    mocked_contract.functions.token0.return_value.call.return_value = "token0"
    mocked_contract.functions.token1.return_value.call.return_value = "token1"
    mocked_contract.functions.fee.return_value.call.return_value = 3000
    return mocked_contract

def test_uniswap_v2_exchange(setup_data, mocked_contract):
    uniswap_v2_exchange = UniswapV2()
    assert uniswap_v2_exchange.get_abi() == UNISWAP_V2_POOL_ABI  # replace with your constant
    assert uniswap_v2_exchange.get_fee("", mocked_contract) == ("0.003", 0.003)
    assert uniswap_v2_exchange.get_tkn0("", mocked_contract, {}) == mocked_contract.functions.token0().call()
    assert uniswap_v2_exchange.get_tkn1("", mocked_contract, {}) == mocked_contract.functions.token1().call()

def test_uniswap_v3_exchange(setup_data, mocked_contract):
    uniswap_v3_exchange = UniswapV3()
    assert uniswap_v3_exchange.get_abi() == UNISWAP_V3_POOL_ABI  # replace with your constant
    assert uniswap_v3_exchange.get_fee("", mocked_contract) == (mocked_contract.functions.fee().call(), float(mocked_contract.functions.fee().call()) / 1e6)
    assert uniswap_v3_exchange.get_tkn0("", mocked_contract, {}) == mocked_contract.functions.token0().call()
    assert uniswap_v3_exchange.get_tkn1("", mocked_contract, {}) == mocked_contract.functions.token1().call()

def test_sushiswap_v2_exchange(setup_data, mocked_contract):
    sushiswap_v2_exchange = SushiswapV2()
    assert sushiswap_v2_exchange.get_abi() == SUSHISWAP_POOLS_ABI  # replace with your constant
    assert sushiswap_v2_exchange.get_fee("", mocked_contract) == ("0.003", 0.003)
    assert sushiswap_v2_exchange.get_tkn0("", mocked_contract, {}) == mocked_contract.functions.token0().call()
    assert sushiswap_v2_exchange.get_tkn1("", mocked_contract, {}) == mocked_contract.functions.token1().call()

def test_bancor_v3_exchange(setup_data, mocked_contract):
    bancor_v3_exchange = BancorV3()
    assert bancor_v3_exchange.get_abi() == BANCOR_V3_POOL_COLLECTION_ABI  # replace with your constant
    assert bancor_v3_exchange.get_fee("", mocked_contract) == ("0.000", 0.000)
    assert bancor_v3_exchange.get_tkn0("", mocked_contract, setup_data["bancor_v3_event"]) == bancor_v3_exchange.BNT_ADDRESS
    assert bancor_v3_exchange.get_tkn1("", mocked_contract, setup_data["bancor_v3_event"]) == setup_data["bancor_v3_event"]["args"]["pool"] if setup_data["bancor_v3_event"]["args"]["pool"] != bancor_v3_exchange.BNT_ADDRESS else setup_data["bancor_v3_event"]["args"]["tkn_address"]

def test_carbon_v1_exchange_update(setup_data, mocked_contract):
    carbon_v1_exchange = CarbonV1()
    assert carbon_v1_exchange.get_abi() == CARBON_CONTROLLER_ABI  # replace with your constant
    assert carbon_v1_exchange.get_fee("", mocked_contract) == ("0.002", 0.002)
    assert carbon_v1_exchange.get_tkn0("", mocked_contract, setup_data["carbon_v1_event_update"]) == setup_data["carbon_v1_event_update"]["args"]["token0"]
    assert carbon_v1_exchange.get_tkn1("", mocked_contract, setup_data["carbon_v1_event_update"]) == setup_data["carbon_v1_event_update"]["args"]["token1"]

def test_carbon_v1_exchange_create(setup_data, mocked_contract):
    carbon_v1_exchange = CarbonV1()
    assert carbon_v1_exchange.get_abi() == CARBON_CONTROLLER_ABI  # replace with your constant
    assert carbon_v1_exchange.get_fee("", mocked_contract) == ("0.002", 0.002)
    assert carbon_v1_exchange.get_tkn0("", mocked_contract, setup_data["carbon_v1_event_create"]) == setup_data["carbon_v1_event_create"]["args"]["token0"]
    assert carbon_v1_exchange.get_tkn1("", mocked_contract, setup_data["carbon_v1_event_create"]) == setup_data["carbon_v1_event_create"]["args"]["token1"]

def test_carbon_v1_exchange_delete(setup_data, mocked_contract):
    carbon_v1_exchange = CarbonV1()
    assert carbon_v1_exchange.get_abi() == CARBON_CONTROLLER_ABI
    cid = setup_data["carbon_v1_event_delete"]["args"]["id"]
    assert cid not in [strat['cid'] for strat in carbon_v1_exchange.pools]

#%%
