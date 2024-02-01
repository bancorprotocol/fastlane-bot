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
# -
# # BOT TEMPLATE Tenderly [NBTest010b]

# ## Tenderly shell commands [NOTEST]
#
# note: the ! commands must be commented out when tests are created

C_nw = ConfigNetwork.new(network=ConfigNetwork.NETWORK_TENDERLY)
c1, c2 = C_nw.shellcommand().splitlines()

print(c1)
print(c2)
# !{c1}
# !{c2}

# ## Tenderly Configuration

# ### Shell commands
#
# Those shell commands need to be run before being able to connect to tenderly

C_nw = ConfigNetwork.new(network=ConfigNetwork.NETWORK_TENDERLY)
c1, c2 = C_nw.shellcommand().splitlines()
assert c2 == 'brownie networks add "Ethereum" "tenderly" host=https://rpc.tenderly.co/fork/058b12b9-c69e-4676-a7bd-2ba09c9b23c7 chainid=1'
assert c1 == 'brownie networks delete tenderly'

print(c1)
print(c2)

# +
# !{c2}
# !{c1}
# -

# ### Connection proper

C = Config.new(config=Config.CONFIG_TENDERLY)
assert C.DATABASE == C.DATABASE_POSTGRES
assert C.POSTGRES_DB == "tenderly"
assert C.NETWORK == C.NETWORK_TENDERLY
assert C.PROVIDER == C.PROVIDER_TENDERLY
assert C.w3.__class__.__name__ == "Web3"
assert C.w3.isConnected()
#assert C.w3.provider.endpoint_uri.startswith("https://rpc.tenderly.co/fork/")

# ## Tests that can fail [NOTEST]
#
# for some reason they work in a notebook but fail as tests

C = Config.new(config=Config.CONFIG_TENDERLY)
assert C.DATABASE == C.DATABASE_POSTGRES
assert C.POSTGRES_DB == "tenderly"
assert C.NETWORK == C.NETWORK_TENDERLY
assert C.PROVIDER == C.PROVIDER_TENDERLY
assert C.w3.__class__.__name__ == "Web3"
assert C.w3.isConnected()
assert C.w3.provider.endpoint_uri.startswith("https://rpc.tenderly.co/fork/")

mainnet_w3 = Web3(Web3.HTTPProvider(f"https://eth-mainnet.alchemyapi.io/v2/{os.environ.get('WEB3_ALCHEMY_PROJECT_ID')}"))
assert mainnet_w3.eth.blockNumber != C.w3.eth.block_number
print(f"Mainnet block = {mainnet_w3.eth.block_number}, Tenderly block = {C.w3.eth.block_number}")
CARBON_CONTROLLER = C.w3.eth.contract(address="0xC537e898CD774e2dCBa3B14Ea6f34C93d5eA45e1", abi=CARBON_CONTROLLER_ABI)
fee = CARBON_CONTROLLER.caller.tradingFeePPM()
assert type(fee) == int

C_nw = ConfigNetwork.new(network=ConfigNetwork.NETWORK_TENDERLY)
C_db = ConfigDB.new(db=ConfigDB.DATABASE_POSTGRES)
C_pr = ConfigProvider.new(network=C_nw)
C = Config(db = C_db, network = C_nw, provider = C_pr)
C

bot = Bot(ConfigObj=C)

# ## Bot update [NOTEST]

help(bot.update)

# +
#bot.update(drop_tables=True, only_carbon=False)
# -

help(bot.update)


