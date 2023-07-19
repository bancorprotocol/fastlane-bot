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
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

# +
from fastlane_bot import Config, ConfigDB, ConfigNetwork, ConfigProvider, Bot
from web3 import Web3
from fastlane_bot.data.abi import CARBON_CONTROLLER_ABI

print("{0.__name__} v{0.__VERSION__} ({0.__DATE__})".format(Config))
print("{0.__name__} v{0.__VERSION__} ({0.__DATE__})".format(Bot))
from fastlane_bot.testing import *

from fastlane_bot import __VERSION__
require("2.0", __VERSION__)
# +
# raise
# -

# # BOT TEMPLATE [NBTest010]

# ## Mainnet Alchemy [NOTEST]

C = Config.new(config=Config.CONFIG_MAINNET)
assert C.DATABASE == C.DATABASE_POSTGRES
assert C.POSTGRES_DB == "mainnet"
assert C.NETWORK == C.NETWORK_MAINNET
assert C.PROVIDER == C.PROVIDER_ALCHEMY
print("Web3 API:", C.w3.api)

# ## Tenderly [NOTEST]

pass


# ## Mainnet Alchemy Configuration

C = Config.new(config=Config.CONFIG_MAINNET)
assert C.DATABASE == C.DATABASE_POSTGRES
assert C.POSTGRES_DB == "mainnet"
assert C.NETWORK == C.NETWORK_MAINNET
assert C.PROVIDER == C.PROVIDER_ALCHEMY
assert C.w3.__class__.__name__ == "Web3"
assert C.w3.isConnected()
assert C.w3.provider.endpoint_uri.startswith("https://eth-mainnet.alchemyapi.io/v2")

bot = Bot(ConfigObj=C)

# +
# bot.update_pools()

# +
# bot.drop_tables()
# -


# ## Unittest Configuration

C = Config.new(config=Config.CONFIG_UNITTEST)
assert C.DATABASE == C.DATABASE_UNITTEST
assert C.NETWORK == C.NETWORK_MAINNET
#assert C.PROVIDER == C.PROVIDER_UNITTEST
assert C.PROVIDER == C.PROVIDER_ALCHEMY


bot = Bot(ConfigObj=C)

# ## Mainnet Alchemy change DB

C_nw = ConfigNetwork.new(network=ConfigNetwork.NETWORK_MAINNET)
C_db = ConfigDB.new(db=ConfigDB.DATABASE_POSTGRES, POSTGRES_DB="postgres")
C_pr = ConfigProvider.new(network=C_nw)
C = Config(db = C_db, network = C_nw, provider = C_pr)
assert C_db.POSTGRES_URL.endswith("/postgres")
assert C.DATABASE == C.DATABASE_POSTGRES
assert C.POSTGRES_DB == "postgres"
assert C.NETWORK == C.NETWORK_MAINNET
assert C.PROVIDER == C.PROVIDER_ALCHEMY
assert C.w3.__class__.__name__ == "Web3"
C

bot = Bot(ConfigObj=C)

# ## Bot update on the mainnet [NOTEST]

C = Config.new(config=Config.CONFIG_MAINNET)
assert C.DATABASE == C.DATABASE_POSTGRES
assert C.POSTGRES_DB == "mainnet"
assert C.NETWORK == C.NETWORK_MAINNET
assert C.PROVIDER == C.PROVIDER_ALCHEMY
assert C.w3.__class__.__name__ == "Web3"
assert C.w3.isConnected()
assert C.w3.provider.endpoint_uri.startswith("https://eth-mainnet.alchemyapi.io/v2")
bot = Bot(ConfigObj=C)


bot.update(drop_tables=False)
