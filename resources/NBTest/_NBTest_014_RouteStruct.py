# -*- coding: utf-8 -*-
# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:light
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.13.1
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

from fastlane_bot import Bot,Config
#from fastlane_bot.tools.cpc import ConstantProductCurve as CPC, CPCContainer
from fastlane_bot.helpers import TradeInstruction, TxReceiptHandler, TxRouteHandler, TxSubmitHandler, TxHelpers, TxHelper
print("{0.__name__} v{0.__VERSION__} ({0.__DATE__})".format(Config))
print("{0.__name__} v{0.__VERSION__} ({0.__DATE__})".format(TradeInstruction))
print("{0.__name__} v{0.__VERSION__} ({0.__DATE__})".format(TxReceiptHandler))
print("{0.__name__} v{0.__VERSION__} ({0.__DATE__})".format(TxRouteHandler))
print("{0.__name__} v{0.__VERSION__} ({0.__DATE__})".format(TxSubmitHandler))
print("{0.__name__} v{0.__VERSION__} ({0.__DATE__})".format(TxHelpers))
print("{0.__name__} v{0.__VERSION__} ({0.__DATE__})".format(TxHelper))
from fastlane_bot.testing import *
plt.style.use('seaborn-dark')
plt.rcParams['figure.figsize'] = [12,6]
from fastlane_bot import __VERSION__
require("2.0", __VERSION__)

# # Helpers [NBTest013b]

C = Config()
bot = Bot(C)
db = bot.db
deadline = bot._get_deadline()
deadline

# ## TradeInstruction to Route

# ### TradeInstruction

# +
ti1 = TradeInstruction(
    cid='4083388403051261561560495289181218537544',
    tknin='USDC-eB48',
    amtin=5000,
    tknout='WBTB-2c599',
    amtout=0,
    ConfigObj=C,
    db = db,
    tknin_dec_override =  6,
    tknout_dec_override = 8,
    tknin_addr_override = '0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48',
    tknout_addr_override = '0x2260fac5e5542a773aa44fbcfedf7c193bc2c599',
    exchange_override = 'bancor_v3'
)

ti2 = TradeInstruction(
    cid='4083388403051261561560495289181218537544',
    tknout='USDC-eB48',
    amtout=5000,
    tknin='WBTB-2c599',
    amtin=0,
    ConfigObj=C,
    db = db,
    tknout_dec_override =  6,
    tknin_dec_override = 8,
    tknout_addr_override = '0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48',
    tknin_addr_override = '0x2260fac5e5542a773aa44fbcfedf7c193bc2c599',
    exchange_override = 'carbon_v1'
)
# -


assert str(ti1).startswith("TradeInstruction(ConfigObj=Config(network=_ConfigNetworkMainnet()")
assert str(ti2).startswith("TradeInstruction(ConfigObj=Config(network=_ConfigNetworkMainnet()")

# ### RouteStruct

route = TxRouteHandler([ti1, ti2])
assert str(route).startswith("TxRouteHandler(trade_instructions=[")
route.get_route_structs(deadline=deadline+100)










