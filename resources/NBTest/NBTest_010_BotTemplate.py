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

import fastlane_bot

help(fastlane_bot.config)

Cnw = ConfigNetwork.new(network=ConfigNetwork.NETWORK_MAINNET)
C = Config(
    db = ConfigDB.new(db=ConfigDB.DATABASE_POSTGRES),
    network = Cnw,
    provider = ConfigProvider.new(network=Cnw, provider=ConfigProvider.PROVIDER_ALCHEMY),
)
C


