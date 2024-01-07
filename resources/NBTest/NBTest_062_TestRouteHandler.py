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
import unittest
from unittest.mock import Mock, call, MagicMock

from fastlane_bot import Bot, Config
from fastlane_bot.bot import CarbonBot
from fastlane_bot.tools.cpc import ConstantProductCurve
from fastlane_bot.tools.cpc import ConstantProductCurve as CPC
from fastlane_bot.events.exchanges import UniswapV2, UniswapV3,  CarbonV1, BancorV3
from fastlane_bot.events.interface import QueryInterface
from fastlane_bot.helpers.poolandtokens import PoolAndTokens
from fastlane_bot.helpers import TradeInstruction, TxReceiptHandler, TxRouteHandler, TxSubmitHandler, TxHelpers, TxHelper
from fastlane_bot.helpers.routehandler import ExchangeNotSupportedError
from fastlane_bot.events.managers.manager import Manager
from fastlane_bot.events.interface import QueryInterface
from joblib import Parallel, delayed
from dataclasses import dataclass, asdict, field
from fastlane_bot.testing import *
from fastlane_bot.config.network import *
import math
import json
from typing import Dict
print("{0.__name__} v{0.__VERSION__} ({0.__DATE__})".format(CPC))
print("{0.__name__} v{0.__VERSION__} ({0.__DATE__})".format(Bot))
print("{0.__name__} v{0.__VERSION__} ({0.__DATE__})".format(UniswapV2))
print("{0.__name__} v{0.__VERSION__} ({0.__DATE__})".format(UniswapV3))
print("{0.__name__} v{0.__VERSION__} ({0.__DATE__})".format(CarbonV1))
print("{0.__name__} v{0.__VERSION__} ({0.__DATE__})".format(BancorV3))
from fastlane_bot.testing import *

#plt.style.use('seaborn-dark')
plt.rcParams['figure.figsize'] = [12,6]
from fastlane_bot import __VERSION__
require("3.0", __VERSION__)
# -

#

# +
cfg = Config.new(config=Config.CONFIG_MAINNET, blockchain="ethereum")

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

# -

# # Test_Route_Handler_Solve_Trade_Output [NBTest062]

# ## Test Solve Trade Output

# +
cfg.network.SOLIDLY_V2_FORKS = ["solidly_v2"]

trade_instruction_0 = TradeInstruction(
    cid='4083388403051261561560495289181218537544',
    tknin='0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2',
    amtin=5000,
    tknout='0x514910771AF9Ca656af840dff83E8264EcF986CA',
    amtout=1,
    ConfigObj=cfg,
    db = db,
    tknin_dec_override =  18,
    tknout_dec_override = 18,
    tknin_addr_override = '0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2',
    tknout_addr_override = '0x514910771AF9Ca656af840dff83E8264EcF986CA',
    exchange_override = 'solidly_v2'
)
trade_instruction_1 = TradeInstruction(
    cid='4083388403051261561560495289181218537544',
    tknin='0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2',
    amtin=5000,
    tknout='0x514910771AF9Ca656af840dff83E8264EcF986CA',
    amtout=1,
    ConfigObj=cfg,
    db = db,
    tknin_dec_override =  18,
    tknout_dec_override = 18,
    tknin_addr_override = '0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2',
    tknout_addr_override = '0x514910771AF9Ca656af840dff83E8264EcF986CA',
    exchange_override = 'uniswap_v2'
)

mock_trade_instruction_0 = Mock(TradeInstruction) #TradeInstruction(mocker, ConfigObj=cfg)
mock_trade_instruction_0.ConfigObj = cfg
mock_trade_instruction_0.db = db
mock_trade_instruction_0.tknin_address = "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2"
mock_trade_instruction_0.tknout_address = "0x514910771AF9Ca656af840dff83E8264EcF986CA"
mock_trade_instruction_0._is_carbon = False
mock_trade_instruction_0.amt_out=Decimal('4.98450E-13')

# mock_trade_instruction_1 = Mock(TradeInstruction) #TradeInstruction(mocker, ConfigObj=cfg)
# mock_trade_instruction_1.ConfigObj = cfg
# mock_trade_instruction_1.db = db
# mock_trade_instruction_1.tknout_address = "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2"
# mock_trade_instruction_1.tknin_address = "0x514910771AF9Ca656af840dff83E8264EcF986CA"
# mock_trade_instruction_1._is_carbon = False

mock_curve_0 = Mock()
mock_curve_0.exchange_name = "uniswap_v2"
mock_curve_0.pair_name = "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2/0x514910771AF9Ca656af840dff83E8264EcF986CA"
mock_curve_0.tkn0_balance = Decimal("1000")
mock_curve_0.tkn1_balance = Decimal("500000")
mock_curve_0.fee = Decimal("0.003")
mock_curve_0.fee_float = Decimal("0.003")

mock_curve_1 = Mock()
mock_curve_1.exchange_name = "solidly_v2"
mock_curve_1.pair_name = "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2/0x514910771AF9Ca656af840dff83E8264EcF986CA"
mock_curve_1.tkn0_balance = Decimal("1000")
mock_curve_1.tkn1_balance = Decimal("500000")
mock_curve_1.fee = Decimal("0.003")
mock_curve_1.fee_float = Decimal("0.003")
mock_curve_1.pool_type = "volatile"

mock_curve_2 = Mock()
mock_curve_2.exchange_name = "bobs_burger_exchange"
mock_curve_2.pair_name = "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2/0x514910771AF9Ca656af840dff83E8264EcF986CA"
mock_curve_2.tkn0_balance = Decimal("1000")
mock_curve_2.tkn1_balance = Decimal("500000")
mock_curve_2.fee = Decimal("0.003")
mock_curve_2.fee_float = Decimal("0.003")


mock_curve_3 = Mock()
mock_curve_3.exchange_name = "solidly_v2"
mock_curve_3.pair_name = "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2/0x514910771AF9Ca656af840dff83E8264EcF986CA"
mock_curve_3.tkn0_balance = Decimal("1000")
mock_curve_3.tkn1_balance = Decimal("500000")
mock_curve_3.fee = Decimal("0.003")
mock_curve_3.fee_float = Decimal("0.003")
mock_curve_3.pool_type = "stable"

txroutehandler = TxRouteHandler(trade_instructions=[trade_instruction_0, trade_instruction_1])
# -



# +
# Test that a Solidly V2 Stable pool throws an error since it isn't supported yet
assert raises(txroutehandler._solve_trade_output, mock_curve_3, mock_trade_instruction_0, Decimal("0.05")).startswith("[routerhandler.py _solve_trade_output] Solidly V2 stable pools are not yet supported"), f"[NBTest 062 TestRouteHandler] Expected _solve_trade_output to raise an error for a Solidly V2 Stable pool"

# Test that Solidly V2 Volatile pool returns the same format as a Uni V2 pool
solidly_output = txroutehandler._solve_trade_output(curve=mock_curve_0, trade=trade_instruction_0, amount_in=Decimal("0.05"))[0]
uni_v2_output = txroutehandler._solve_trade_output(curve=mock_curve_0, trade=trade_instruction_1, amount_in=Decimal("0.05"))[0]
assert type(solidly_output) == Decimal, f"[NBTest 062 TestRouteHandler] Expected type of output for Solidly V2 Volatile pool to be of type Decimal, found {type(solidly_output)}"
assert solidly_output == uni_v2_output, f"[NBTest 062 TestRouteHandler] Expected output for Solidly V2 Volatile pool to the same as Uni V2 pool, found {solidly_output} vs {uni_v2_output}"
# -



# ## 



# ## 




