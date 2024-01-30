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


assert not ethereum_cfg.network.HAS_LAYER_ONE_GAS_FEE
assert not polygon_cfg.network.HAS_LAYER_ONE_GAS_FEE
assert not polygon_zkevm_cfg.network.HAS_LAYER_ONE_GAS_FEE
assert not arbitrum_cfg.network.HAS_LAYER_ONE_GAS_FEE
assert optimism_cfg.network.HAS_LAYER_ONE_GAS_FEE
assert base_cfg.network.HAS_LAYER_ONE_GAS_FEE
# -

# ## Test_Solve_Trade_Output

# +
################### Base #####################
cfg = Config.new(config=Config.CONFIG_MAINNET, blockchain="coinbase_base")

tx_helpers = TxHelpers(cfg)

def test_count_zero_bytes():
    # Arrange
    data = HexBytes(b'\x00\x00\x00\x00\x00')

    # Act
    zero_bytes, non_zero_bytes = count_bytes(data)

    # Assert
    assert zero_bytes == 5
    assert non_zero_bytes == 0



test_count_zero_bytes()    
