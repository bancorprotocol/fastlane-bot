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

from fastlane_bot import Config, ConfigDB, ConfigNetwork, ConfigProvider, Bot
from fastlane_bot.tools.cpc import ConstantProductCurve as CPC, CPCContainer
print("{0.__name__} v{0.__VERSION__} ({0.__DATE__})".format(CPC))
print("{0.__name__} v{0.__VERSION__} ({0.__DATE__})".format(Bot))
from fastlane_bot.testing import *
plt.style.use('seaborn-dark')
plt.rcParams['figure.figsize'] = [12,6]
from fastlane_bot import __VERSION__
require("2.0", __VERSION__)

# # Testing the _run functions [NBTest011]

# ## Mainnet Alchemy Configuration

# ### Set up the bot

C = Config.new(config=Config.CONFIG_MAINNET)
assert C.DATABASE == C.DATABASE_POSTGRES
assert C.POSTGRES_DB == "mainnet"
assert C.NETWORK == C.NETWORK_MAINNET
assert C.PROVIDER == C.PROVIDER_ALCHEMY
bot = Bot(ConfigObj=C)

help(bot._run)
#help(CPC.from_carbon)
#help(CPC.from_univ3)

# ### Set up the curves

cc1 = CPC.from_carbon(pair="ETH/USDC", tkny="ETH", yint=10, y=10, pa=1/2000, pb=1/2010, cid="c-1")
assert iseq(1/2000, cc1.p, cc1.p_max)
assert iseq(1/2010, cc1.p_min)
assert cc1.p_convention() == 'ETH per USDC'
assert cc1.p_min < cc1.p_max
cc1

cu1 = CPC.from_univ3(pair="ETH/USDC", Pmarg=2100.5, uniPa=2100, uniPb=2101, 
                     uniL=m.sqrt(20*2000), fee=0, cid="uni1", descr="")
assert iseq(cu1.p, 2100.5)
assert iseq(cu1.p_min, 2100)
assert iseq(cu1.p_max, 2101)
assert cu1.p_convention() == 'USDC per ETH'
assert cc1.p_min < cc1.p_max
cu1

c0 = CPC.from_pk(pair="ETH/USDC", p=2100, k=0.1*200)

assert cc1.p < cu1.p, f"must have {cc1.p} < {cu1.p} for arbitrage"

CCm = CPCContainer([cc1, cu1, c0])
CCm.plot()

# ### Run `_find_arbitrage_opportunities}`

# #### AO_TOKENS

r=bot._find_arbitrage_opportunities(flashloan_tokens=["ETH"], CCm=CCm, result=bot.AO_TOKENS)
r

assert r[0] == {'ETH', 'USDC'}
assert r[1] == [('USDC', 'ETH')]

# #### AO_CANDIDATES

bot._find_arbitrage_opportunities(flashloan_tokens=["ETH"], CCm=CCm, result=bot.AO_CANDIDATES)

# #### Full

bot._find_arbitrage_opportunities(flashloan_tokens=["ETH"], CCm=CCm)

# ### Run `_run`

# #### XS_ARBOPPS

bot._run(flashloan_tokens=["ETH"], CCm=CCm, result=bot.XS_ARBOPPS)

# #### XS_TI

bot._run(flashloan_tokens=["ETH"], CCm=CCm, result=bot.XS_TI)

# #### XS_ORDSCAL

bot._run(flashloan_tokens=["ETH"], CCm=CCm, result=bot.XS_ORDSCAL)

# #### XS_AGGTI

bot._run(flashloan_tokens=["ETH"], CCm=CCm, result=bot.XS_AGGTI)

# #### XS_ORDTI

bot._run(flashloan_tokens=["ETH"], CCm=CCm, result=bot.XS_ORDTI)

# #### XS_ENCTI

bot._run(flashloan_tokens=["ETH"], CCm=CCm, result=bot.XS_ENCTI)

# #### XS_ROUTE

bot._run(flashloan_tokens=["ETH"], CCm=CCm, result=bot.XS_ROUTE)

