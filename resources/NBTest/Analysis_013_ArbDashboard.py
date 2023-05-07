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

import time
start_time = time.time()
from fastlane_bot import Bot, Config, ConfigDB, ConfigNetwork, ConfigProvider
from fastlane_bot.tools.cpc import ConstantProductCurve as CPC, CPCContainer, T, Pair
from fastlane_bot.tools.analyzer import CPCAnalyzer, AttrDict
from fastlane_bot.tools.optimizer import CPCArbOptimizer
from fastlane_bot.branch import BRANCH
print("{0.__name__} v{0.__VERSION__} ({0.__DATE__})".format(CPC))
print("{0.__name__} v{0.__VERSION__} ({0.__DATE__})".format(CPCAnalyzer))
print("{0.__name__} v{0.__VERSION__} ({0.__DATE__})".format(CPCArbOptimizer))
print("{0.__name__} v{0.__VERSION__} ({0.__DATE__})".format(Bot))
from fastlane_bot.testing import *
import itertools as it
import collections as cl
plt.style.use('seaborn-dark')
plt.rcParams['figure.figsize'] = [12,6]
from fastlane_bot import __VERSION__
require("3.0", __VERSION__)
print(f"elapsed time: {time.time()-start_time:.2f}s")
print("BRANCH:", BRANCH)

# # Arbitrage Dashboard [A013]

bot     = Bot()
CCm     = bot.get_curves()
CA      = CPCAnalyzer(CCm)
pairsc  = CA.pairsc()
print(f"elapsed time: {time.time()-start_time:.2f}s")

# ## All (Carbon) pairs

print(f"Tokens:  {len(CA.tokens()):4}")
print(f"Pairs:   {len(CA.pairs()) :4} [carbon: {len(CA.pairsc()) :4}]")
print(f"Curves:  {len(CA.curves()):4} [carbon: {len(CA.curvesc()):4}]") 

nocav = True
for pair in CA.pairsc():
    try:
        d = CA.pair_analysis(pair, novac=nocav)
        print(CA.pair_analysis_pp(d, nocav=nocav))
        #print(f"elapsed time: {time.time()-start_time:.2f}s")
    except Exception as e:
        pass
        print(f"[{pair}: {e} ]\n")

# ## Individual pairs

# #### WETH/USDC

pair    = "WETH-6Cc2/USDC-eB48"
d       = CA.pair_analysis(pair)
CC_crb  = CA.curvesc(ascc=True).bypairs(pair)

print(CA.pair_analysis_pp(d))

d.xpairs

d.tib_xnoc

d.tiq_xnoc

d.xarbvalq

d.xarbvalb

d.tib_xf

d.tiq_xf

d.tib

d.tiq

d.tibq

d.arbvalb, d.tknb

d.arbvalq, d.tknq


