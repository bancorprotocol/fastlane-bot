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

from fastlane_bot import Config, ConfigDB, ConfigNetwork, ConfigProvider
from fastlane_bot.bot import CarbonBot
from fastlane_bot.tools.cpc import ConstantProductCurve as CPC, CPCContainer, T

print("{0.__name__} v{0.__VERSION__} ({0.__DATE__})".format(CPC))
print("{0.__name__} v{0.__VERSION__} ({0.__DATE__})".format(CarbonBot))
from fastlane_bot.testing import *

plt.style.use("seaborn-dark")
plt.rcParams["figure.figsize"] = [12, 6]
from fastlane_bot import __VERSION__

require("2.0", __VERSION__)

# # Testing the _run functions on TENDERLY EXAMPLE TX [NBTest011b1]

# ## TENDERLY Configuration

# ### Set up the bot and curves

C = Config.new(config=Config.CONFIG_TENDERLY)
assert C.DATABASE == C.DATABASE_POSTGRES
assert C.POSTGRES_DB == "tenderly"
assert C.NETWORK == C.NETWORK_TENDERLY
assert C.PROVIDER == C.PROVIDER_TENDERLY
bot = CarbonBot(ConfigObj=C)
assert str(type(bot.db)) == "<class 'fastlane_bot.db.manager.DatabaseManager'>"

C_nw = ConfigNetwork.new(network=ConfigNetwork.NETWORK_TENDERLY)
c1, c2 = C_nw.shellcommand().splitlines()
# # !{c1}
# # !{c2}

# provided here for convenience; must be commented out for tests
bot.update(drop_tables=True, top_n=10, only_carbon=False)

CCm = bot.get_curves()
exch = {c.P("exchange") for c in CCm}
print("Number of curvers:", len(CCm))
print("Number of tokens:", len(CCm.tokens()))
print("Exchanges:", exch)

CCm.bypairs(f"{T.ECO}/{T.USDC}")[0].p

CCm.bypairs(f"{T.ECO}/{T.USDC}")[1].p

# ## Actual run

flt = [T.USDC]
bot._run(flashloan_tokens=flt, CCm=CCm)

# ## Analytics

ops = bot._run(flashloan_tokens=flt, CCm=CCm, result=bot.XS_ARBOPPS)
ops

ops

route_struct = bot._run(flashloan_tokens=flt, CCm=CCm, result=bot.XS_ROUTE)
route_struct

route_struct

ordinfo = bot._run(flashloan_tokens=flt, CCm=CCm, result=bot.XS_ORDINFO)
flashloan_amount = ordinfo[1]
flashloan_token_address = ordinfo[2]

flashloan_amount, flashloan_token_address

# +
### This to manually submit
# bot._validate_and_submit_transaction_tenderly(
#         ConfigObj = C,
#         route_struct = route_struct,
#         src_amount = flashloan_amount,
#         src_address = flashloan_token_address,
#             )
# -

# ### Hard coded example

# +
# deadline = bot._get_deadline()

# +
## example format encoded data

# 0x
# 0000000000000000000000000000000000000000000000000000000000000020    # this is 32
# 0000000000000000000000000000000000000000000000000000000000000001    # this is number of orders
# 0000000000000000000000000000000c00000000000000000000000000000048    # cid
# 000000000000000000000000000000000000000000000000000000012a05f200    # amount

# +
# want to input $5000 USDC in exchang for WBTC
# amount = hex(int(5000 * 1e6))  #amount to pad out zeros
# amount

# +
# convert the cid and then pad with zeros
# cid = hex(4083388403051261561560495289181218537544)
# cid

# +
# TODO create the customdata with the zero padding

# +
# route_struct = [
#   {'exchangeId': 6,
#   'targetToken': C.w3.to_checksum_address('0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599'),
#   'minTargetAmount': 1,
#   'deadline': deadline,
#   'customAddress': C.w3.to_checksum_address('0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599'),
#   'customInt': 0,
#   'customData': '0x000000000000000000000000000000000000000000000000000000000000002000000000000000000000000000000000000000000000000000000000000000010000000000000000000000000000000c00000000000000000000000000000048000000000000000000000000000000000000000000000000000000012a05f200'},
#  {'exchangeId': 2,
#   'targetToken': C.w3.to_checksum_address('0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48'),
#   'minTargetAmount': 1,
#   'deadline': deadline,
#   'customAddress': C.w3.to_checksum_address('0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48'),
#   'customInt': 0,
#   'customData': '0x'}
# ]
# flashloan_token_address =C.w3.to_checksum_address('0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48')
# flashloan_amount = 5000000000

# +
# bot._validate_and_submit_transaction_tenderly(
#         ConfigObj = C,
#         route_struct = route_struct,
#         src_amount = flashloan_amount,
#         src_address = flashloan_token_address,
#             )
