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

from fastlane_bot import Config
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

# # Helpers [NBTest013]

C = Config()

# ## TradeInstruction

# ## TxReceiptHandler
#
# Note: `TxReceiptHandler` is currently a dummy class. No tests to do.

h = TxReceiptHandler()
assert type(h).__name__ == "TxReceiptHandler"
assert type(h).__bases__[0].__name__ == "TxReceiptHandlerBase"

# +
#help(h)
# -

# ## TxRouteHandler

h = TxRouteHandler(ConfigObj=C)
assert type(h).__name__ == "TxRouteHandler"
assert type(h).__bases__[0].__name__ == "TxRouteHandlerBase"

# +
#help(h)
# -

# ## TxSubmitHandler

h = TxSubmitHandler(ConfigObj=C)
assert type(h).__name__ == "TxSubmitHandler"
assert type(h).__bases__[0].__name__ == "TxSubmitHandlerBase"

help(h)

# ## TradeInstruction

h = TradeInstruction(ConfigObj=C)
assert type(h).__name__ == "TradeInstruction"

# +
#help(h)
# -

# ## TxHelpers

h = TxHelpers(ConfigObj=C)
assert type(h).__name__ == "TxHelpers"

help(h)

# ## TxHelper

h = TxHelper(ConfigObj=C)
assert type(h).__name__ == "TxHelper"

help(h)


