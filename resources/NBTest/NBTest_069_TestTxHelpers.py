# -*- coding: utf-8 -*-
# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:light
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.14.5
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# +
# coding=utf-8
"""
This module contains the tests for the exchanges classes
"""
from unittest.mock import Mock

from fastlane_bot import Bot, Config
from fastlane_bot.bot import CarbonBot
from fastlane_bot.tools.cpc import ConstantProductCurve as CPC
from fastlane_bot.events.exchanges import UniswapV2, UniswapV3,  CarbonV1, BancorV3
from fastlane_bot.events.interface import QueryInterface
from fastlane_bot.helpers import TradeInstruction, TxRouteHandler
from fastlane_bot.events.interface import QueryInterface
from fastlane_bot.testing import *
from fastlane_bot.config.network import *
from web3 import Web3
from web3.types import TxReceipt, HexBytes
import pytest
from fastlane_bot.helpers.txhelpers import count_bytes, TxHelpers
import json
from typing import Dict
print("{0.__name__} v{0.__VERSION__} ({0.__DATE__})".format(CPC))
print("{0.__name__} v{0.__VERSION__} ({0.__DATE__})".format(Bot))
print("{0.__name__} v{0.__VERSION__} ({0.__DATE__})".format(UniswapV2))
print("{0.__name__} v{0.__VERSION__} ({0.__DATE__})".format(UniswapV3))
print("{0.__name__} v{0.__VERSION__} ({0.__DATE__})".format(CarbonV1))
print("{0.__name__} v{0.__VERSION__} ({0.__DATE__})".format(BancorV3))
from fastlane_bot.testing import *

plt.rcParams['figure.figsize'] = [12,6]
from fastlane_bot import __VERSION__
require("3.0", __VERSION__)
# -

cfg = Config.new(config=Config.CONFIG_MAINNET, blockchain="ethereum")
cfg.network.SOLIDLY_V2_FORKS = ["solidly_v2"]
setup_bot = CarbonBot(ConfigObj=cfg)
pools = None
with open('fastlane_bot/data/tests/latest_pool_data_testing.json') as f:
    pools = json.load(f)
pools = [pool for pool in pools]
pools[0]
static_pools = pools
state = pools
exchanges = list({ex['exchange_name'] for ex in state})
db = QueryInterface(state=state, ConfigObj=cfg, exchanges=exchanges)


# # Test_TxHelpers [NBTest069]

# ## Test_HAS_LAYER_ONE_GAS_FEE

# +
ethereum_cfg = Config.new(config=Config.CONFIG_MAINNET, blockchain="ethereum")
polygon_cfg = Config.new(config=Config.CONFIG_MAINNET, blockchain="polygon")
optimism_cfg = Config.new(config=Config.CONFIG_MAINNET, blockchain="optimism")
polygon_zkevm_cfg = Config.new(config=Config.CONFIG_MAINNET, blockchain="polygon_zkevm")
arbitrum_cfg = Config.new(config=Config.CONFIG_MAINNET, blockchain="arbitrum_one")
base_cfg = Config.new(config=Config.CONFIG_MAINNET, blockchain="coinbase_base")


assert not ethereum_cfg.network.GAS_ORACLE_ADDRESS
assert not polygon_cfg.network.GAS_ORACLE_ADDRESS
assert not polygon_zkevm_cfg.network.GAS_ORACLE_ADDRESS
assert not arbitrum_cfg.network.GAS_ORACLE_ADDRESS
assert optimism_cfg.network.GAS_ORACLE_ADDRESS
assert base_cfg.network.GAS_ORACLE_ADDRESS
# -

# ## Test_Solve_Trade_Output

# +
################### Base #####################
cfg = Config.new(config=Config.CONFIG_MAINNET, blockchain="coinbase_base")

tx_helpers = TxHelpers(cfg)

def test_count_zero_bytes():
    # Arrange
    data = HexBytes('0x02f904d18221052d8310a1d08310a2da830a26fc942ae2404cd44c830d278f51f053a08f54b3756e1c80b904642e540b1000000000000000000000000000000000000000000000000000000000000000400000000000000000000000000000000000000000000000000000000000000160000000000000000000000000000000000000000000000000000000000000000100000000000000000000000000000000000000000000000000000000000000200000000000000000000000000000000000000000000000000000000000000007000000000000000000000000000000000000000000000000000000000000006000000000000000000000000000000000000000000000000000000000000000a00000000000000000000000000000000000000000000000000000000000000001000000000000000000000000420000000000000000000000000000000000000600000000000000000000000000000000000000000000000000000000000000010000000000000000000000000000000000000000000000000001007a3dd3a0000000000000000000000000000000000000000000000000000000000000000002000000000000000000000000000000000000000000000000000000000000004000000000000000000000000000000000000000000000000000000000000001a0000000000000000000000000000000000000000000000000000000000000000c000000000000000000000000420000000000000000000000000000000000000600000000000000000000000065a2508c429a6078a7bc2f7df81ab575bd9d92750000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000094b37f736765e3b0000000000000000000000000000000000000000000000000000000065c2b889000000000000000000000000cf77a3ba9a5ca399b7c97c74d54e5b1beb874e43000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000001200000000000000000000000000000000000000000000000000000000000000020000000000000000000000000420dd381b31aef6683db6b902084cb0ffece40da000000000000000000000000000000000000000000000000000000000000000b00000000000000000000000065a2508c429a6078a7bc2f7df81ab575bd9d927500000000000000000000000042000000000000000000000000000000000000060000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000104210f356d830000000000000000000000000000000000000000000000000000000065c2b8890000000000000000000000002f87bf58d5a9b2efade55cdbd46153a0902be6fa000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000001200000000000000000000000000000000000000000000000000000000000000000c080a0e3376517dc6210175ccfed7f905ce959443bbbc02a3d247bdf279c554aa0068ba03e2a6edb6ce3119c317c581726564bc832732f254e004568cc09338176a33885')

    # Act
    zero_bytes, non_zero_bytes = count_bytes(data)
    # Assert
    assert zero_bytes == 966
    assert non_zero_bytes == 271



test_count_zero_bytes()    
# -


