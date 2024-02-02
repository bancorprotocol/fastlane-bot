# -*- coding: utf-8 -*-
# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:light
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.14.7
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

from fastlane_bot import Config, ConfigDB, ConfigNetwork, ConfigProvider, Bot
from fastlane_bot.tools.cpc import ConstantProductCurve as CPC, CPCContainer, T
print("{0.__name__} v{0.__VERSION__} ({0.__DATE__})".format(CPC))
print("{0.__name__} v{0.__VERSION__} ({0.__DATE__})".format(CarbonBot))
from fastlane_bot.testing import *
plt.style.use('seaborn-dark')
plt.rcParams['figure.figsize'] = [12,6]
from fastlane_bot import __VERSION__
require("3.0", __VERSION__)

# # Overview Notebook [NB999]

# ## Introduction
#
# ### Agenda
#
# 1. Purpose of the library and short term goals
#     1. Purpose
#     1. Goals (pairs and triangles)
# 1. Core API (bot and config)
#     1. bot.update
#     1. bot.run
#     1. config
# 1. Structure (config, database, tools, helpers; bot)
#     1. config -- configuration plus Web3 connections
#     1. database -- data base connections (based on config)
#     1. tools -- core optimization code and related data structures
#     1. helpers -- mostly transaction related
#     1. bot -- main API entry point and logic flow
# 1. Arbbot framework vs alternatives
# 1. Testing framework
# 1. Key issue: database
#     1. Update modes
#     1. Mainnet vs Tenderly issues
#     1. Database issues

# ### Core API

# #### bot.update

help(Bot.update)

# #### bot.run

help(Bot.run)

help(Bot._run)

#     XS_ARBOPPS = "arbopps"
#     XS_TI = "ti"
#     XS_ORDSCAL = "ordscal"
#     XS_AGGTI = "aggti"
#     XS_ORDINFO = "ordinfo"
#     XS_ENCTI = "encti"
#     XS_ROUTE = "route"

# #### Config

help(Config.new)

# ## Goal

# ### Tenderly

C_db = db_.ConfigDB.new(db=S.DATABASE_SQLITE, SQLITE_DB="tenderly")
C_nw = network_.ConfigNetwork.new(network=S.NETWORK_TENDERLY)
C = Config(db=C_db, logger=C_log, network=C_nw)
bot = Bot(ConfigObj=C)
bot.update()
CCm = bot.get_curves()

# ### Mainnet

C_db = db_.ConfigDB.new(db=S.DATABASE_SQLITE, SQLITE_DB="mainnet")
C = Config(db=C_db)
bot = Bot(ConfigObj=C)
bot.update()
CCm = bot.get_curves()

# ## Execution

# ### Configuration
#
# - `flt`: flashloanable tokens
# - `loglevel`: `LL_DEBUG` , `LL_INFO` `LL_WARN` `LL_ERR`

flt = [T.USDC]
C = Config.new(config=Config.CONFIG_TENDERLY, loglevel=Config.LL_INFO)

bot = CarbonBot(ConfigObj=C)

# ### Database update [Tenderly specific]

# provided here for convenience; must be commented out for tests
bot.update(drop_tables=True, top_n=10, only_carbon=False)

# ### Execution

bot.run(flashloan_tokens=flt, mode=bot.RUN_SINGLE)

# ## Execution analysis

CCm = bot.get_curves()

# ### Arbitrage opportunities

ops = bot._find_arbitrage(flashloan_tokens=flt, CCm=CCm)["r"]
ops

# ### Route struct

try:
    route_struct = bot._run(flashloan_tokens=flt, CCm=CCm)
except bot.NoArbAvailable as e:
    print(f"[NoArbAvailable] {e}")
    route_struct = None
route_struct

# ### Orderering info

try:
    ordinfo = bot._run(flashloan_tokens=flt, CCm=CCm)
    flashloan_amount = ordinfo[1]
    flashloan_token_address = ordinfo[2]
    print(f"Flashloan: {flashloan_amount} [{flashloan_token_address}]")
except bot.NoArbAvailable as e:
    print(f"[NoArbAvailable] {e}")
    ordinfo = None
ordinfo

# ## Market analysis

# ### Overall market

exch0 = {c.P("exchange") for c in CCm}
print("Number of curves:", len(CCm))
print("Number of tokens:", len(CCm.tokens()))
#print("Exchanges:", exch0)
print("---")
for xc in exch0:
    print(f"{xc+':':16} {len(CCm.byparams(exchange=xc)):4}")

# ### Pair

pair = f"{T.ECO}/{T.USDC}"

CCp = CCm.bypairs(pair)
exch = {c.P("exchange") for c in CCp}
print("pair:           ", pair)
print("curves:         ", len(CCp))
print("exchanges:      ", exch)
for xc in exch:
    c = CCp.byparams(exchange=xc)[0]
    print(f"{xc+':':16} {c.p:.4f} {1/c.p:.4f}")

# ## Technical

# ### Validation and assertions

assert C.DATABASE == C.DATABASE_POSTGRES
assert C.POSTGRES_DB == "tenderly"
assert C.NETWORK == C.NETWORK_TENDERLY
assert C.PROVIDER == C.PROVIDER_TENDERLY
assert str(type(bot.db)) == "<class 'fastlane_bot.db.manager.DatabaseManager'>"
assert C.w3.provider.endpoint_uri.startswith("https://rpc.tenderly.co/fork/")
assert bot.db.carbon_controller.address == '0xC537e898CD774e2dCBa3B14Ea6f34C93d5eA45e1'

# ### Tenderly shell commands
#
# Run those commands in a shell if there are Tenderly connection issues

C_nw = ConfigNetwork.new(network=ConfigNetwork.NETWORK_TENDERLY)
c1, c2 = C_nw.shellcommand().splitlines()
print(c1)
print(c2)
# !{c1}
# !{c2}




