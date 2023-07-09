# coding=utf-8
"""
This module contains the tests for the exchanges classes
"""
import json

import pytest

from fastlane_bot import Bot
from fastlane_bot.events.pools import (
    SushiswapV2Pool,
    UniswapV2Pool,
    UniswapV3Pool,
    BancorV3Pool,
    CarbonV1Pool,
)
from fastlane_bot.tools.cpc import ConstantProductCurve as CPC

print("{0.__name__} v{0.__VERSION__} ({0.__DATE__})".format(CPC))
print("{0.__name__} v{0.__VERSION__} ({0.__DATE__})".format(Bot))
print("{0.__name__} v{0.__VERSION__} ({0.__DATE__})".format(UniswapV2Pool))
print("{0.__name__} v{0.__VERSION__} ({0.__DATE__})".format(UniswapV3Pool))
print("{0.__name__} v{0.__VERSION__} ({0.__DATE__})".format(SushiswapV2Pool))
print("{0.__name__} v{0.__VERSION__} ({0.__DATE__})".format(CarbonV1Pool))
print("{0.__name__} v{0.__VERSION__} ({0.__DATE__})".format(BancorV3Pool))
from fastlane_bot.testing import *

plt.style.use("seaborn-dark")
plt.rcParams["figure.figsize"] = [12, 6]
from fastlane_bot import __VERSION__

require("3.0", __VERSION__)


# Use pytest's fixtures to setup data for tests
@pytest.fixture
def setup_data():
    with open("fastlane_bot/data/event_test_data.json", "r") as f:
        setup_data = json.load(f)
    return setup_data


def test_uniswap_v2_pool(setup_data):
    uniswap_v2_pool = UniswapV2Pool()
    uniswap_v2_pool.update_from_event(
        setup_data["uniswap_v2_event"],
        {
            "cid": "0x",
            "fee": "0.000",
            "fee_float": 0.0,
            "exchange_name": "sushiswap_v2",
            "reserve0": setup_data["uniswap_v2_event"]["args"]["reserve0"],
            "reserve1": setup_data["uniswap_v2_event"]["args"]["reserve1"],
            "tkn0_symbol": "tkn0",
            "tkn1_symbol": "tkn1",
        },
    )
    assert (
        uniswap_v2_pool.state["tkn0_balance"]
        == setup_data["uniswap_v2_event"]["args"]["reserve0"]
    )
    assert (
        uniswap_v2_pool.state["tkn1_balance"]
        == setup_data["uniswap_v2_event"]["args"]["reserve1"]
    )


def test_sushiswap_v2_pool(setup_data):
    sushiswap_v2_pool = SushiswapV2Pool()
    sushiswap_v2_pool.update_from_event(
        setup_data["sushiswap_v2_event"],
        {
            "cid": "0x",
            "fee": "0.000",
            "fee_float": 0.0,
            "exchange_name": "uniswap_v2",
            "reserve0": setup_data["uniswap_v2_event"]["args"]["reserve0"],
            "reserve1": setup_data["uniswap_v2_event"]["args"]["reserve1"],
            "tkn0_symbol": "tkn0",
            "tkn1_symbol": "tkn1",
        },
    )
    assert (
        sushiswap_v2_pool.state["tkn0_balance"]
        == setup_data["sushiswap_v2_event"]["args"]["reserve0"]
    )
    assert (
        sushiswap_v2_pool.state["tkn1_balance"]
        == setup_data["sushiswap_v2_event"]["args"]["reserve1"]
    )


def test_uniswap_v3_pool(setup_data):
    uniswap_v3_pool = UniswapV3Pool()
    uniswap_v3_pool.update_from_event(
        setup_data["uniswap_v3_event"],
        {
            "cid": "0x",
            "fee": "0.000",
            "fee_float": 0.0,
            "exchange_name": "uniswap_v3",
            "liquidity": setup_data["uniswap_v3_event"]["args"]["liquidity"],
            "sqrtPriceX96": setup_data["uniswap_v3_event"]["args"]["sqrtPriceX96"],
            "tick": setup_data["uniswap_v3_event"]["args"]["tick"],
            "tkn0_symbol": "tkn0",
            "tkn1_symbol": "tkn1",
        },
    )
    assert (
        uniswap_v3_pool.state["liquidity"]
        == setup_data["uniswap_v3_event"]["args"]["liquidity"]
    )
    assert (
        uniswap_v3_pool.state["sqrt_price_q96"]
        == setup_data["uniswap_v3_event"]["args"]["sqrtPriceX96"]
    )
    assert (
        uniswap_v3_pool.state["tick"] == setup_data["uniswap_v3_event"]["args"]["tick"]
    )


def test_bancor_v3_pool(setup_data):
    bancor_v3_pool = BancorV3Pool()
    bancor_v3_pool.update_from_event(
        setup_data["bancor_v3_event"],
        {
            "cid": "0x",
            "fee": "0.000",
            "fee_float": 0.0,
            "exchange_name": "bancor_v3",
            "tkn0_balance": setup_data["bancor_v3_event"]["args"]["newLiquidity"],
            "tkn1_balance": 0,
            "tkn0_symbol": "tkn0",
            "tkn1_symbol": "tkn1",
        },
    )
    assert (
        bancor_v3_pool.state["tkn0_balance"]
        == setup_data["bancor_v3_event"]["args"]["newLiquidity"]
    )


def test_carbon_v1_pool_update(setup_data):
    carbon_v1_pool = CarbonV1Pool()

    # assert that the strategy already exists and has 0 balances
    carbon_v1_pool.update_from_event(
        setup_data["carbon_v1_event_create_for_update"], {}
    )
    assert (
        setup_data["carbon_v1_event_update"]["args"]["id"]
        == carbon_v1_pool.state["cid"]
    )
    assert carbon_v1_pool.state["y_0"] == 0
    assert carbon_v1_pool.state["z_0"] == 0
    assert carbon_v1_pool.state["A_0"] == 0
    assert carbon_v1_pool.state["B_0"] == 0
    assert carbon_v1_pool.state["y_1"] == 0
    assert carbon_v1_pool.state["z_1"] == 0
    assert carbon_v1_pool.state["A_1"] == 0
    assert carbon_v1_pool.state["B_1"] == 0

    # update the strategy with new balances
    carbon_v1_pool.update_from_event(setup_data["carbon_v1_event_update"], {})
    assert (
        carbon_v1_pool.state["y_0"]
        == setup_data["carbon_v1_event_update"]["args"]["order0"][0]
    )
    assert (
        carbon_v1_pool.state["z_0"]
        == setup_data["carbon_v1_event_update"]["args"]["order0"][1]
    )
    assert (
        carbon_v1_pool.state["A_0"]
        == setup_data["carbon_v1_event_update"]["args"]["order0"][2]
    )
    assert (
        carbon_v1_pool.state["B_0"]
        == setup_data["carbon_v1_event_update"]["args"]["order0"][3]
    )
    assert (
        carbon_v1_pool.state["y_1"]
        == setup_data["carbon_v1_event_update"]["args"]["order1"][0]
    )
    assert (
        carbon_v1_pool.state["z_1"]
        == setup_data["carbon_v1_event_update"]["args"]["order1"][1]
    )
    assert (
        carbon_v1_pool.state["A_1"]
        == setup_data["carbon_v1_event_update"]["args"]["order1"][2]
    )
    assert (
        carbon_v1_pool.state["B_1"]
        == setup_data["carbon_v1_event_update"]["args"]["order1"][3]
    )


def test_carbon_v1_pool_delete(setup_data):
    carbon_v1_pool = CarbonV1Pool()

    # assert that the strategy already exists and has non-zero balances
    carbon_v1_pool.update_from_event(
        setup_data["carbon_v1_event_create_for_delete"], {}
    )
    assert (
        setup_data["carbon_v1_event_delete"]["args"]["id"]
        == carbon_v1_pool.state["cid"]
    )
    assert (
        carbon_v1_pool.state["y_0"]
        == setup_data["carbon_v1_event_delete"]["args"]["order0"][0]
    )
    assert (
        carbon_v1_pool.state["z_0"]
        == setup_data["carbon_v1_event_delete"]["args"]["order0"][1]
    )
    assert (
        carbon_v1_pool.state["A_0"]
        == setup_data["carbon_v1_event_delete"]["args"]["order0"][2]
    )
    assert (
        carbon_v1_pool.state["B_0"]
        == setup_data["carbon_v1_event_delete"]["args"]["order0"][3]
    )
    assert (
        carbon_v1_pool.state["y_1"]
        == setup_data["carbon_v1_event_delete"]["args"]["order1"][0]
    )
    assert (
        carbon_v1_pool.state["z_1"]
        == setup_data["carbon_v1_event_delete"]["args"]["order1"][1]
    )
    assert (
        carbon_v1_pool.state["A_1"]
        == setup_data["carbon_v1_event_delete"]["args"]["order1"][2]
    )
    assert (
        carbon_v1_pool.state["B_1"]
        == setup_data["carbon_v1_event_delete"]["args"]["order1"][3]
    )

    # delete the strategy
    carbon_v1_pool.update_from_event(setup_data["carbon_v1_event_delete"], {})
    assert carbon_v1_pool.state["y_0"] == 0
    assert carbon_v1_pool.state["z_0"] == 0
    assert carbon_v1_pool.state["A_0"] == 0
    assert carbon_v1_pool.state["B_0"] == 0
    assert carbon_v1_pool.state["y_1"] == 0
    assert carbon_v1_pool.state["z_1"] == 0
    assert carbon_v1_pool.state["A_1"] == 0
    assert carbon_v1_pool.state["B_1"] == 0


#%%
