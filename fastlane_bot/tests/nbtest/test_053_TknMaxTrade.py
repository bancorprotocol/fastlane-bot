# ------------------------------------------------------------
# Auto generated test file `test_053_TknMaxTrade.py`
# ------------------------------------------------------------
# source file   = NBTest_053_TknMaxTrade.py
# test id       = 053
# test comment  = TknMaxTrade
# ------------------------------------------------------------



"""
This module contains the tests for the exchanges classes
"""
from fastlane_bot import Bot, Config
from fastlane_bot.bot import CarbonBot
from fastlane_bot.tools.cpc import ConstantProductCurve
from fastlane_bot.tools.cpc import ConstantProductCurve as CPC
from fastlane_bot.events.exchanges import UniswapV2, UniswapV3,  CarbonV1, BancorV3
from fastlane_bot.events.interface import QueryInterface
from fastlane_bot.helpers.poolandtokens import PoolAndTokens
from fastlane_bot.helpers import TradeInstruction, TxReceiptHandler, TxRouteHandler, TxSubmitHandler, TxHelpers, TxHelper
from fastlane_bot.events.managers.manager import Manager
from fastlane_bot.events.interface import QueryInterface
from fastlane_bot.helpers.routehandler import RouteStruct, maximize_last_trade_per_tkn
from joblib import Parallel, delayed
from dataclasses import dataclass, asdict, field
import pytest
import math
import json
print("{0.__name__} v{0.__VERSION__} ({0.__DATE__})".format(CPC))
print("{0.__name__} v{0.__VERSION__} ({0.__DATE__})".format(Bot))
print("{0.__name__} v{0.__VERSION__} ({0.__DATE__})".format(UniswapV2))
print("{0.__name__} v{0.__VERSION__} ({0.__DATE__})".format(UniswapV3))

print("{0.__name__} v{0.__VERSION__} ({0.__DATE__})".format(CarbonV1))
print("{0.__name__} v{0.__VERSION__} ({0.__DATE__})".format(BancorV3))
from fastlane_bot.testing import *

plt.style.use('seaborn-dark')
plt.rcParams['figure.figsize'] = [12,6]
from fastlane_bot import __VERSION__
require("3.0", __VERSION__)




# ------------------------------------------------------------
# Test      053
# File      test_053_TknMaxTrade.py
# Segment   Test_use_0_for_sourceAmount
# ------------------------------------------------------------
def test_test_use_0_for_sourceamount():
# ------------------------------------------------------------
    
    # +
    
    
    ti1 = RouteStruct(
    platformId=8,
    sourceToken="0xeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee",
    targetToken="0x6b175474e89094c44da98b954eedeac495271d0f",
    sourceAmount=62211456000000000000,
    minTargetAmount=99890009252976620728523,
    deadline=1702409775,
    customAddress="0x6b175474e89094c44da98b954eedeac495271d0f",
    customInt=0,
    customData="0x"
    )
    
    ti2 = RouteStruct(platformId=4,
    sourceToken="0x6b175474e89094c44da98b954eedeac495271d0f",
    targetToken="0xeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee",
    sourceAmount=99890009252976620728523,
    minTargetAmount=62256092760867779024,
    deadline=1702409775,
    customAddress="0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2",
    customInt=3000,
    customData="0x")
    
    
    ti3 = RouteStruct(
    platformId=8,
    sourceToken="0xeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee",
    targetToken="0x6b175474e89094c44da98b954eedeac495271d0f",
    sourceAmount=62211456000000000000,
    minTargetAmount=99890009252976620728523,
    deadline=1702409775,
    customAddress="0x6b175474e89094c44da98b954eedeac495271d0f",
    customInt=0,
    customData="0x"
    )
    ti4 = RouteStruct(
    platformId=8,
    sourceToken="0xeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee",
    targetToken="0x6b175474e89094c44da98b954eedeac495271d0f",
    sourceAmount=62211456000000000000,
    minTargetAmount=99890009252976620728523,
    deadline=1702409775,
    customAddress="0x6b175474e89094c44da98b954eedeac495271d0f",
    customInt=0,
    customData="0x"
    )
    
    ti5 = RouteStruct(platformId=4,
    sourceToken="0x6b175474e89094c44da98b954eedeac495271d0f",
    targetToken="0xeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee",
    sourceAmount=99890009252976620728523,
    minTargetAmount=62256092760867779024,
    deadline=1702409775,
    customAddress="0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2",
    customInt=3000,
    customData="0x")
    
    instructions = [ti1, ti2]
    instructions2 = [asdict(ti3), asdict(ti4), asdict(ti5)]
     
    max_trade_route_struct = maximize_last_trade_per_tkn(instructions)
    max_trade_route_struct2 = maximize_last_trade_per_tkn(instructions2)
    
    assert max_trade_route_struct[0].sourceAmount == 0, f"[NBTest_053] sourceAmount expected 0, actual: {max_trade_route_struct[0].sourceAmount}"
    assert max_trade_route_struct[1].sourceAmount == 0, f"[NBTest_053] sourceAmount expected 0, actual: {max_trade_route_struct[1].sourceAmount}"
    assert max_trade_route_struct2[0]["sourceAmount"] == 62211456000000000000, f"[NBTest_053] sourceAmount expected 0, actual: {max_trade_route_struct2[0]['sourceAmount']}"
    assert max_trade_route_struct2[1]["sourceAmount"] == 0, f"[NBTest_053] sourceAmount expected 0, actual: {max_trade_route_struct2[1]['sourceAmount']}"
    assert max_trade_route_struct2[2]["sourceAmount"] == 0, f"[NBTest_053] sourceAmount expected 0, actual: {max_trade_route_struct2[2]['sourceAmount']}"
    
    # -
    
    
    
    
    