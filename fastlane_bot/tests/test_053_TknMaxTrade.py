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
from dataclasses import asdict

from arb_optimizer import ConstantProductCurve as CPC

from fastlane_bot import Bot
from fastlane_bot.events.exchanges import UniswapV2, UniswapV3, CarbonV1, BancorV3
from fastlane_bot.helpers import maximize_last_trade_per_tkn

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




# ------------------------------------------------------------
# Test      053
# File      test_053_TknMaxTrade.py
# Segment   Test_use_0_for_sourceAmount
# ------------------------------------------------------------
def test_maximize_last_trade_per_tkn():
    route_struct = [
        {"sourceAmount": 10, "sourceToken": "bob_tkn", "minReturn": 10, "targetToken": "fred_tkn"},
        {"sourceAmount": 10, "sourceToken": "bob_tkn", "minReturn": 10, "targetToken": "fred_tkn"},
        {"sourceAmount": 10, "sourceToken": "fred_tkn", "minReturn": 10, "targetToken": "grog_tkn"},
        {"sourceAmount": 10, "sourceToken": "fred_tkn", "minReturn": 10, "targetToken": "grog_tkn"},
        {"sourceAmount": 10, "sourceToken": "grog_tkn", "minReturn": 10, "targetToken": "bob_tkn"},
        {"sourceAmount": 10, "sourceToken": "grog_tkn", "minReturn": 10, "targetToken": "bob_tkn"},
    ]

    source_token = route_struct[0]["sourceToken"]
    maximize_last_trade_per_tkn(route_struct)

    for trade in route_struct:
        if trade["sourceToken"] == source_token:
            assert trade["sourceAmount"] > 0
    assert route_struct[0]["sourceAmount"] == 10
    assert route_struct[1]["sourceAmount"] == 10
    assert route_struct[2]["sourceAmount"] == 10
    assert route_struct[3]["sourceAmount"] == 0
    assert route_struct[4]["sourceAmount"] == 10
    assert route_struct[5]["sourceAmount"] == 0
