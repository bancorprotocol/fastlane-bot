# coding=utf-8
"""
This module contains the tests for the exchanges classes
"""
import json

from fastlane_bot import Bot
from fastlane_bot.tools.cpc import ConstantProductCurve as CPC
from fastlane_bot.events.exchanges import (
    UniswapV2,
    UniswapV3,
    SushiswapV2,
    CarbonV1,
    BancorV3,
)
from fastlane_bot.data.abi import (
    UNISWAP_V2_POOL_ABI,
    UNISWAP_V3_POOL_ABI,
    SUSHISWAP_POOLS_ABI,
    BANCOR_V3_POOL_COLLECTION_ABI,
    CARBON_CONTROLLER_ABI,
)
from unittest.mock import Mock
import pytest

print("{0.__name__} v{0.__VERSION__} ({0.__DATE__})".format(CPC))
print("{0.__name__} v{0.__VERSION__} ({0.__DATE__})".format(Bot))
print("{0.__name__} v{0.__VERSION__} ({0.__DATE__})".format(UniswapV2))
print("{0.__name__} v{0.__VERSION__} ({0.__DATE__})".format(UniswapV3))
print("{0.__name__} v{0.__VERSION__} ({0.__DATE__})".format(SushiswapV2))
print("{0.__name__} v{0.__VERSION__} ({0.__DATE__})".format(CarbonV1))
print("{0.__name__} v{0.__VERSION__} ({0.__DATE__})".format(BancorV3))
from fastlane_bot.testing import *

plt.style.use("seaborn-dark")
plt.rcParams["figure.figsize"] = [12, 6]
from fastlane_bot import __VERSION__

require("3.0", __VERSION__)


@pytest.fixture
def setup_data():
    with open("fastlane_bot/data/event_test_data.json", "r") as f:
        setup_data = json.load(f)
    return setup_data


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
    assert (
        uniswap_v2_exchange.get_abi() == UNISWAP_V2_POOL_ABI
    )  # replace with your constant
    assert uniswap_v2_exchange.get_fee("", mocked_contract) == ("0.003", 0.003)
    assert (
        uniswap_v2_exchange.get_tkn0("", mocked_contract, {})
        == mocked_contract.functions.token0().call()
    )
    assert (
        uniswap_v2_exchange.get_tkn1("", mocked_contract, {})
        == mocked_contract.functions.token1().call()
    )


def test_uniswap_v3_exchange(setup_data, mocked_contract):
    uniswap_v3_exchange = UniswapV3()
    assert (
        uniswap_v3_exchange.get_abi() == UNISWAP_V3_POOL_ABI
    )  # replace with your constant
    assert uniswap_v3_exchange.get_fee("", mocked_contract) == (
        mocked_contract.functions.fee().call(),
        float(mocked_contract.functions.fee().call()) / 1e6,
    )
    assert (
        uniswap_v3_exchange.get_tkn0("", mocked_contract, {})
        == mocked_contract.functions.token0().call()
    )
    assert (
        uniswap_v3_exchange.get_tkn1("", mocked_contract, {})
        == mocked_contract.functions.token1().call()
    )


def test_sushiswap_v2_exchange(setup_data, mocked_contract):
    sushiswap_v2_exchange = SushiswapV2()
    assert (
        sushiswap_v2_exchange.get_abi() == SUSHISWAP_POOLS_ABI
    )  # replace with your constant
    assert sushiswap_v2_exchange.get_fee("", mocked_contract) == ("0.003", 0.003)
    assert (
        sushiswap_v2_exchange.get_tkn0("", mocked_contract, {})
        == mocked_contract.functions.token0().call()
    )
    assert (
        sushiswap_v2_exchange.get_tkn1("", mocked_contract, {})
        == mocked_contract.functions.token1().call()
    )


def test_bancor_v3_exchange(setup_data, mocked_contract):
    bancor_v3_exchange = BancorV3()
    assert (
        bancor_v3_exchange.get_abi() == BANCOR_V3_POOL_COLLECTION_ABI
    )  # replace with your constant
    assert bancor_v3_exchange.get_fee("", mocked_contract) == ("0.000", 0.000)
    assert (
        bancor_v3_exchange.get_tkn0("", mocked_contract, setup_data["bancor_v3_event"])
        == bancor_v3_exchange.BNT_ADDRESS
    )
    assert (
        bancor_v3_exchange.get_tkn1("", mocked_contract, setup_data["bancor_v3_event"])
        == setup_data["bancor_v3_event"]["args"]["pool"]
        if setup_data["bancor_v3_event"]["args"]["pool"]
        != bancor_v3_exchange.BNT_ADDRESS
        else setup_data["bancor_v3_event"]["args"]["tkn_address"]
    )


def test_carbon_v1_exchange_update(setup_data, mocked_contract):
    carbon_v1_exchange = CarbonV1()
    assert (
        carbon_v1_exchange.get_abi() == CARBON_CONTROLLER_ABI
    )  # replace with your constant
    assert carbon_v1_exchange.get_fee("", mocked_contract) == ("0.002", 0.002)
    assert (
        carbon_v1_exchange.get_tkn0(
            "", mocked_contract, setup_data["carbon_v1_event_update"]
        )
        == setup_data["carbon_v1_event_update"]["args"]["token0"]
    )
    assert (
        carbon_v1_exchange.get_tkn1(
            "", mocked_contract, setup_data["carbon_v1_event_update"]
        )
        == setup_data["carbon_v1_event_update"]["args"]["token1"]
    )


def test_carbon_v1_exchange_create(setup_data, mocked_contract):
    carbon_v1_exchange = CarbonV1()
    assert (
        carbon_v1_exchange.get_abi() == CARBON_CONTROLLER_ABI
    )  # replace with your constant
    assert carbon_v1_exchange.get_fee("", mocked_contract) == ("0.002", 0.002)
    assert (
        carbon_v1_exchange.get_tkn0(
            "", mocked_contract, setup_data["carbon_v1_event_create"]
        )
        == setup_data["carbon_v1_event_create"]["args"]["token0"]
    )
    assert (
        carbon_v1_exchange.get_tkn1(
            "", mocked_contract, setup_data["carbon_v1_event_create"]
        )
        == setup_data["carbon_v1_event_create"]["args"]["token1"]
    )


def test_carbon_v1_exchange_delete(setup_data, mocked_contract):
    carbon_v1_exchange = CarbonV1()
    assert carbon_v1_exchange.get_abi() == CARBON_CONTROLLER_ABI
    cid = setup_data["carbon_v1_event_delete"]["args"]["id"]
    assert cid not in [strat["cid"] for strat in carbon_v1_exchange.pools]


#%%
