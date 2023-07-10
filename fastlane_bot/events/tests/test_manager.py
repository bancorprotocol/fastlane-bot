# coding=utf-8
"""
This module contains the tests for the manager class methods which are multicall related
"""

from unittest.mock import Mock, patch, call

import brownie
import pytest
from unittest.mock import MagicMock
from brownie import multicall as brownie_multicall

from fastlane_bot import Bot, Config
from fastlane_bot.events.exchanges import (
    UniswapV2,
    UniswapV3,
    SushiswapV2,
    CarbonV1,
    BancorV3,
)
from fastlane_bot.events.managers.base import Manager
from fastlane_bot.tools.cpc import ConstantProductCurve as CPC

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
def pool_data():
    nan = np.NaN
    pool_data = [
        {
            "cid": "0xb3b0dbb95f1f70e1f053360d9bccef3fbe7c5e2b615e833a9faae18c299a0fc9",
            "last_updated": nan,
            "last_updated_block": 17634372,
            "descr": "bancor_v3 BNT-FF1C/MATIC-eBB0 0.000",
            "pair_name": "BNT-FF1C/MATIC-eBB0",
            "exchange_name": "bancor_v3",
            "fee": "0.000",
            "fee_float": 0.0,
            "address": "0x9f8F72aA9304c8B593d555F12eF6589cC3A579A2",
            "anchor": nan,
            "tkn0_address": "0x1F573D6Fb3F13d689FF844B4cE37794d79a7FF1C",
            "tkn1_address": "0x7D1AfA7B718fb893dB30A3aBc0Cfc608AaCfeBB0",
            "tkn0_key": "BNT-FF1C",
            "tkn1_key": "MATIC-eBB0",
            "tkn0_decimals": 18,
            "tkn1_decimals": 18,
            "exchange_id": 2,
            "tkn0_symbol": "BNT",
            "tkn1_symbol": "MATIC",
            "timestamp": nan,
            "tkn0_balance": 371729474548077247680443,
            "tkn1_balance": 216554584335493056216168,
            "liquidity": nan,
            "sqrt_price_q96": nan,
            "tick": nan,
            "tick_spacing": 0,
        },
        {
            "cid": "0x38d373a29b8a7e621ee373ee76138184a67092259bd24ab1434ec90b98235efd",
            "last_updated": nan,
            "last_updated_block": 17634372,
            "descr": "bancor_v3 BNT-FF1C/ENS-9D72 0.000",
            "pair_name": "BNT-FF1C/ENS-9D72",
            "exchange_name": "bancor_v3",
            "fee": "0.000",
            "fee_float": 0.0,
            "address": "0xBC19712FEB3a26080eBf6f2F7849b417FdD792CA",
            "anchor": nan,
            "tkn0_address": "0x1F573D6Fb3F13d689FF844B4cE37794d79a7FF1C",
            "tkn1_address": "0xC18360217D8F7Ab5e7c516566761Ea12Ce7F9D72",
            "tkn0_key": "BNT-FF1C",
            "tkn1_key": "ENS-9D72",
            "tkn0_decimals": 18,
            "tkn1_decimals": 18,
            "exchange_id": 2,
            "tkn0_symbol": "BNT",
            "tkn1_symbol": "ENS",
            "timestamp": nan,
            "tkn0_balance": 104058085529730176588006,
            "tkn1_balance": 4547023863756451207684,
            "liquidity": nan,
            "sqrt_price_q96": nan,
            "tick": nan,
            "tick_spacing": 0,
        },
        {
            "cid": "0x56f1f774ece226fac7c9940c98ead630bfc18a39fa2f2bdcdc56e6234d4477b1",
            "last_updated": nan,
            "last_updated_block": 17634372,
            "descr": "bancor_v3 BNT-FF1C/ALPHA-0975 0.000",
            "pair_name": "BNT-FF1C/ALPHA-0975",
            "exchange_name": "bancor_v3",
            "fee": "0.000",
            "fee_float": 0.0,
            "address": "0x8798249c2E607446EfB7Ad49eC89dD1865Ff4272",
            "anchor": nan,
            "tkn0_address": "0x1F573D6Fb3F13d689FF844B4cE37794d79a7FF1C",
            "tkn1_address": "0xa1faa113cbE53436Df28FF0aEe54275c13B40975",
            "tkn0_key": "BNT-FF1C",
            "tkn1_key": "ALPHA-0975",
            "tkn0_decimals": 18,
            "tkn1_decimals": 18,
            "exchange_id": 2,
            "tkn0_symbol": "BNT",
            "tkn1_symbol": "ALPHA",
            "timestamp": nan,
            "tkn0_balance": 0,
            "tkn1_balance": 0,
            "liquidity": nan,
            "sqrt_price_q96": nan,
            "tick": nan,
            "tick_spacing": 0,
        },
        {
            "cid": "0x1b65e937b57a618d40da4236ae854d33a843042a9abc84ba72d808ad67435a42",
            "last_updated": nan,
            "last_updated_block": 17634372,
            "descr": "bancor_v3 BNT-FF1C/HEGIC-8430 0.000",
            "pair_name": "BNT-FF1C/HEGIC-8430",
            "exchange_name": "bancor_v3",
            "fee": "0.000",
            "fee_float": 0.0,
            "address": "0x5218E472cFCFE0b64A064F055B43b4cdC9EfD3A6",
            "anchor": nan,
            "tkn0_address": "0x1F573D6Fb3F13d689FF844B4cE37794d79a7FF1C",
            "tkn1_address": "0x584bC13c7D411c00c01A62e8019472dE68768430",
            "tkn0_key": "BNT-FF1C",
            "tkn1_key": "HEGIC-8430",
            "tkn0_decimals": 18,
            "tkn1_decimals": 18,
            "exchange_id": 2,
            "tkn0_symbol": "BNT",
            "tkn1_symbol": "HEGIC",
            "timestamp": nan,
            "tkn0_balance": 0,
            "tkn1_balance": 0,
            "liquidity": nan,
            "sqrt_price_q96": nan,
            "tick": nan,
            "tick_spacing": 0,
        },
        {
            "cid": "0x561b7f22cadc1359057c07c5a1f11ae4d087a753aa87629ed92b38175e60c3ae",
            "last_updated": nan,
            "last_updated_block": 17634372,
            "descr": "bancor_v3 BNT-FF1C/ZCN-3B78 0.000",
            "pair_name": "BNT-FF1C/ZCN-3B78",
            "exchange_name": "bancor_v3",
            "fee": "0.000",
            "fee_float": 0.0,
            "address": "0x1559FA1b8F28238FD5D76D9f434ad86FD20D1559",
            "anchor": nan,
            "tkn0_address": "0x1F573D6Fb3F13d689FF844B4cE37794d79a7FF1C",
            "tkn1_address": "0xb9EF770B6A5e12E45983C5D80545258aA38F3B78",
            "tkn0_key": "BNT-FF1C",
            "tkn1_key": "ZCN-3B78",
            "tkn0_decimals": 18,
            "tkn1_decimals": 10,
            "exchange_id": 2,
            "tkn0_symbol": "BNT",
            "tkn1_symbol": "ZCN",
            "timestamp": nan,
            "tkn0_balance": 109709381661658805787397,
            "tkn1_balance": 3264962522647673,
            "liquidity": nan,
            "sqrt_price_q96": nan,
            "tick": nan,
            "tick_spacing": 0,
        },
    ]
    return pool_data


@pytest.fixture
def carbon_events():
    carbon_events = [
        {
            "last_updated_block": 17634377,
            "address": "0xC537e898CD774e2dCBa3B14Ea6f34C93d5eA45e1",
            "exchange_name": "carbon_v1",
            "tkn0_address": "0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE",
            "tkn1_address": "0x6B175474E89094C44Da98b954EedeAC495271d0F",
            "tkn0_symbol": "ETH",
            "tkn1_symbol": "DAI",
            "tkn0_decimals": 18,
            "tkn1_decimals": 18,
            "cid": 340282366920938463463374607431768211457,
            "tkn0_key": "ETH-EEeE",
            "tkn1_key": "DAI-1d0F",
            "pair_name": "ETH-EEeE/DAI-1d0F",
            "fee_float": 0.002,
            "fee": "0.002",
            "descr": "carbon_v1 ETH-EEeE/DAI-1d0F 0.002",
            "y_0": 1000000000000000,
            "y_1": 0,
            "z_0": 1000000000000000,
            "z_1": 0,
            "A_0": 0,
            "A_1": 0,
            "B_0": 6382340776412,
            "B_1": 1875443170982464,
        },
        {
            "last_updated_block": 17634377,
            "address": "0xC537e898CD774e2dCBa3B14Ea6f34C93d5eA45e1",
            "exchange_name": "carbon_v1",
            "tkn0_address": "0x6B175474E89094C44Da98b954EedeAC495271d0F",
            "tkn1_address": "0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE",
            "tkn0_symbol": "DAI",
            "tkn1_symbol": "ETH",
            "tkn0_decimals": 18,
            "tkn1_decimals": 18,
            "cid": 340282366920938463463374607431768211593,
            "tkn0_key": "DAI-1d0F",
            "tkn1_key": "ETH-EEeE",
            "pair_name": "DAI-1d0F/ETH-EEeE",
            "fee_float": 0.002,
            "fee": "0.002",
            "descr": "carbon_v1 DAI-1d0F/ETH-EEeE 0.002",
            "y_0": 0,
            "y_1": 0,
            "z_0": 0,
            "z_1": 0,
            "A_0": 88739322630080,
            "A_1": 30784910546,
            "B_0": 1876725096051745,
            "B_1": 6418617024516,
        },
        {
            "last_updated_block": 17634377,
            "address": "0xC537e898CD774e2dCBa3B14Ea6f34C93d5eA45e1",
            "exchange_name": "carbon_v1",
            "tkn0_address": "0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE",
            "tkn1_address": "0x6B175474E89094C44Da98b954EedeAC495271d0F",
            "tkn0_symbol": "ETH",
            "tkn1_symbol": "DAI",
            "tkn0_decimals": 18,
            "tkn1_decimals": 18,
            "cid": 340282366920938463463374607431768211614,
            "tkn0_key": "ETH-EEeE",
            "tkn1_key": "DAI-1d0F",
            "pair_name": "ETH-EEeE/DAI-1d0F",
            "fee_float": 0.002,
            "fee": "0.002",
            "descr": "carbon_v1 ETH-EEeE/DAI-1d0F 0.002",
            "y_0": 157076304796171508,
            "y_1": 191076681422897394849,
            "z_0": 257505273765924104,
            "z_1": 462002783910000000000,
            "A_0": 197764438468,
            "A_1": 235894416821184,
            "B_0": 6293971818901,
            "B_1": 1873305839476414,
        },
        {
            "last_updated_block": 17634377,
            "address": "0xC537e898CD774e2dCBa3B14Ea6f34C93d5eA45e1",
            "exchange_name": "carbon_v1",
            "tkn0_address": "0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE",
            "tkn1_address": "0x6B175474E89094C44Da98b954EedeAC495271d0F",
            "tkn0_symbol": "ETH",
            "tkn1_symbol": "DAI",
            "tkn0_decimals": 18,
            "tkn1_decimals": 18,
            "cid": 340282366920938463463374607431768211607,
            "tkn0_key": "ETH-EEeE",
            "tkn1_key": "DAI-1d0F",
            "pair_name": "ETH-EEeE/DAI-1d0F",
            "fee_float": 0.002,
            "fee": "0.002",
            "descr": "carbon_v1 ETH-EEeE/DAI-1d0F 0.002",
            "y_0": 0,
            "y_1": 0,
            "z_0": 0,
            "z_1": 0,
            "A_0": 69065909368,
            "A_1": 106270057837888,
            "B_0": 6457478834827,
            "B_1": 1874403645842739,
        },
        {
            "last_updated_block": 17634377,
            "address": "0xC537e898CD774e2dCBa3B14Ea6f34C93d5eA45e1",
            "exchange_name": "carbon_v1",
            "tkn0_address": "0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE",
            "tkn1_address": "0x6B175474E89094C44Da98b954EedeAC495271d0F",
            "tkn0_symbol": "ETH",
            "tkn1_symbol": "DAI",
            "tkn0_decimals": 18,
            "tkn1_decimals": 18,
            "cid": 340282366920938463463374607431768211673,
            "tkn0_key": "ETH-EEeE",
            "tkn1_key": "DAI-1d0F",
            "pair_name": "ETH-EEeE/DAI-1d0F",
            "fee_float": 0.002,
            "fee": "0.002",
            "descr": "carbon_v1 ETH-EEeE/DAI-1d0F 0.002",
            "y_0": 1,
            "y_1": 940344,
            "z_0": 9403439,
            "z_1": 940344,
            "A_0": 0,
            "A_1": 0,
            "B_0": 785475461108442,
            "B_1": 2814749767,
        },
    ]
    return carbon_events


@pytest.fixture
def manager(pool_data):
    cfg = Config.new(config=Config.CONFIG_MAINNET)
    w3 = cfg.w3
    manager = Manager(
        cfg=cfg,
        pool_data=pool_data,
        alchemy_max_block_fetch=20,
        web3=w3,
        SUPPORTED_EXCHANGES=["bancor_v3", "carbon_v1"],
    )
    return manager


def get_rows_to_update(pool_data):
    # return the index of the pool_data
    rows_to_update = [idx for idx, row in enumerate(pool_data)]
    return rows_to_update


# This is a simple counter variable that we'll increment every time we call the function.
multicall_counter = 0


def my_multicall(*args, **kwargs):
    # This is a wrapper function that increments the counter each time it's called,
    # then calls the original function.
    global multicall_counter
    multicall_counter += 1
    return brownie_multicall(*args, **kwargs)


@patch.object(brownie, "multicall", autospec=True)
@patch("fastlane_bot.events.manager.Base.update")
def test_update_pools_directly_from_contracts_bancor_v3(
    self, update_mock, manager, pool_data
):

    # Replace the original function with our wrapper function.
    brownie.multicall = my_multicall

    # Now when you call your function, the counter will be incremented each time
    # the brownie.multicall function is called.
    manager.update_pools_directly_from_contracts(
        n_jobs=2, rows_to_update=[0, 1, 2, 3], not_bancor_v3=False, current_block=1
    )

    # And you can check the value of the counter.
    assert multicall_counter == 1

    # Check the 'update' function calls
    expected_calls = [
        call(pool_info=pool_data[i], limiter=False, block_number=1)
        for i in [0, 1, 2, 3]
    ]
    manager.update.assert_has_calls(expected_calls, any_order=True)


@patch.object(brownie, "multicall", autospec=True)  # We mock the multicall function
def test_get_strats_by_pair(self, manager):

    manager.cfg.MULTICALL_CONTRACT_ADDRESS = (
        "0x5BA1e12693Dc8F9c48aAD8770482f4739bEeD696"
    )
    all_pairs = [(1, 2), (3, 4)]
    carbon_controller_mock = Mock()
    carbon_controller_mock.strategiesByPair.side_effect = [[(5, 6)], [(7, 8)]]
    result = manager.get_strats_by_pair(all_pairs, carbon_controller_mock)
    carbon_controller_mock.strategiesByPair.assert_has_calls(
        [call(*pair) for pair in all_pairs]
    )
    brownie.multicall.assert_called_once_with(
        address="0x5BA1e12693Dc8F9c48aAD8770482f4739bEeD696"
    )
