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

# +
from fastlane_bot import Config, ConfigDB, ConfigNetwork, ConfigProvider, Bot
print("{0.__name__} v{0.__VERSION__} ({0.__DATE__})".format(Config))
print("{0.__name__} v{0.__VERSION__} ({0.__DATE__})".format(Bot))
from fastlane_bot.testing import *

from fastlane_bot import __VERSION__
require("2.0", __VERSION__)
# -

# # BOT TEMPLATE [NBTest010]

# ## Mainnet/Alchemy Configuration

# +
# C_nw = ConfigNetwork.new(network=ConfigNetwork.NETWORK_MAINNET)
# C_db = ConfigDB.new(db=ConfigDB.DATABASE_POSTGRES)
# C_pr = ConfigProvider.new(network=C_nw, provider=ConfigProvider.PROVIDER_ALCHEMY)
# C = Config(db = C_db, network = C_nw, provider = C_pr)
# C
# -

C = Config.new(config=Config.CONFIG_MAINNET)

assert C.DATABASE == C.DATABASE_POSTGRES
assert C.NETWORK == C.NETWORK_MAINNET
assert C.PROVIDER == C.PROVIDER_ALCHEMY

bot = Bot(ConfigObj=C)

# ## Tenderly Configuration

C = Config.new(config=Config.CONFIG_TENDERLY)

# +
# C_nw = ConfigNetwork.new(network=ConfigNetwork.NETWORK_TENDERLY)
# C_db = ConfigDB.new(db=ConfigDB.DATABASE_POSTGRES)
# C_pr = ConfigProvider.new(network=C_nw)
# C = Config(db = C_db, network = C_nw, provider = C_pr)
# C
# -

assert C.DATABASE == C.DATABASE_POSTGRES
assert C.NETWORK == C.NETWORK_TENDERLY
assert C.PROVIDER == C.PROVIDER_TENDERLY

bot = Bot(ConfigObj=C)

# ## Unittest Configuration

C = Config.new(config=Config.CONFIG_UNITTEST)
assert C.DATABASE == C.DATABASE_UNITTEST
assert C.NETWORK == C.NETWORK_MAINNET
assert C.PROVIDER == C.PROVIDER_UNITTEST


