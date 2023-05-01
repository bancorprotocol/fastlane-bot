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

# ## Tenderly Configuration
#
# _this does not work in the same notebook as the other stuff due to limitations of the provider_


pass

# +
# C = Config.new(config=Config.CONFIG_TENDERLY)
# assert C.DATABASE == C.DATABASE_POSTGRES
# assert C.POSTGRES_DB == "tenderly"
# assert C.NETWORK == C.NETWORK_TENDERLY
# assert C.PROVIDER == C.PROVIDER_TENDERLY
# assert C.w3.__class__.__name__ == "Web3"
# assert C.w3.isConnected()
# assert C.w3.provider.endpoint_uri.startswith("https://rpc.tenderly.co/fork/")

# mainnet_w3 = Web3(Web3.HTTPProvider(f"https://eth-mainnet.alchemyapi.io/v2/{os.environ.get('WEB3_ALCHEMY_PROJECT_ID')}"))
# assert mainnet_w3.eth.blockNumber != C.w3.eth.block_number
# print(f"Mainnet block = {mainnet_w3.eth.block_number}, Tenderly block = {C.w3.eth.block_number}")
# CARBON_CONTROLLER = C.w3.eth.contract(address="0xC537e898CD774e2dCBa3B14Ea6f34C93d5eA45e1", abi=CARBON_CONTROLLER_ABI)
# fee = CARBON_CONTROLLER.caller.tradingFeePPM()
# assert type(fee) == int

# +
# C_nw = ConfigNetwork.new(network=ConfigNetwork.NETWORK_TENDERLY)
# C_db = ConfigDB.new(db=ConfigDB.DATABASE_POSTGRES)
# C_pr = ConfigProvider.new(network=C_nw)
# C = Config(db = C_db, network = C_nw, provider = C_pr)
# C
# +
# bot = Bot(ConfigObj=C)
# -




