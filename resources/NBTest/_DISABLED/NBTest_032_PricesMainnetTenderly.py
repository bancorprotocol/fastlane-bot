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

from fastlane_bot import Bot, Config, ConfigDB, ConfigNetwork, ConfigProvider
from fastlane_bot.tools.cpc import ConstantProductCurve as CPC, CPCContainer, T, Pair
from fastlane_bot.tools.analyzer import CPCAnalyzer
from fastlane_bot.tools.optimizer import CPCArbOptimizer
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

# # Prices on Mainnet and Tenderly [A012]

# ## Price estimates

start_time = time.time()
botm    = Bot()
print(f"elapsed time: {time.time()-start_time:.2f}s")

start_time = time.time()
CCm     = botm.get_curves()
print(f"elapsed time: {time.time()-start_time:.2f}s")

# +
# bott    = Bot() # --> change to Tenderly bot
# CCt     = bott.get_curves()
# -

start_time = time.time()
tokensm = CCm.tokens()
prices_usdc = CCm.price_estimates(tknbs=tokensm, tknqs=f"{T.USDC}", 
                                  stopatfirst=True, verbose=False, raiseonerror=False)
print(f"elapsed time: {time.time()-start_time:.2f}s")

pricesdf = pd.DataFrame(prices_usdc, index=tokensm, columns=["USDC"]).sort_values("USDC", ascending=False)
pricesdf

print("TOKEN                       PRICE(USD)")
print("======================================")
for ix, d in pricesdf.iterrows():
    try:
        p = float(d)
        price = f"{p:12,.4f}"
        if p < 1:
            continue
    except:
        continue
    print(f"{ix:25} {price}")





print("TOKEN                       PRICE(USc)")
print("======================================")
for ix, d in pricesdf.iterrows():
    try:
        p = float(d)
        price = f"{p*100:12,.6f}"
        if p >= 1.1:
            continue
    except:
        continue
    print(f"{ix:25} {price}")

print("TOKEN                      UNAVAILABLE")
print("======================================")
for ix, d in pricesdf.iterrows():
    try:
        p = float(d)
        continue
    except:
        pass
    print(f"{ix:25}")

CCP = CCm.bypairs(CCm.filter_pairs(onein="CPI-ec53"))
CCP.plot()


