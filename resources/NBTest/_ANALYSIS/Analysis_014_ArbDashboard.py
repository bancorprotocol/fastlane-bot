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

from fastlane_bot.bot import CarbonBot as Bot#, Config, ConfigDB, ConfigNetwork, ConfigProvider
from fastlane_bot.tools.cpc import ConstantProductCurve as CPC, CPCContainer, T, Pair
from fastlane_bot.tools.analyzer import CPCAnalyzer
from fastlane_bot.tools.optimizer import SimpleOptimizer, MargPOptimizer, ConvexOptimizer
from fastlane_bot.tools.arbgraphs import ArbGraph
print("{0.__name__} v{0.__VERSION__} ({0.__DATE__})".format(CPC))
print("{0.__name__} v{0.__VERSION__} ({0.__DATE__})".format(CPCAnalyzer))
print("{0.__name__} v{0.__VERSION__} ({0.__DATE__})".format(SimpleOptimizer))
print("{0.__name__} v{0.__VERSION__} ({0.__DATE__})".format(MargPOptimizer))
print("{0.__name__} v{0.__VERSION__} ({0.__DATE__})".format(ConvexOptimizer))
print("{0.__name__} v{0.__VERSION__} ({0.__DATE__})".format(ArbGraph))
print("{0.__name__} v{0.__VERSION__} ({0.__DATE__})".format(Bot))
from fastlane_bot.testing import *
import itertools as it
import collections as cl
plt.style.use('seaborn-dark')
plt.rcParams['figure.figsize'] = [12,6]
from fastlane_bot import __VERSION__
require("3.0", __VERSION__)

# # Mainnet Arbitrage Dashboard [A014]

bot     = Bot()
CCm     = bot.get_curves()
fn = f"../data/A014-{int(time.time())}.csv.gz"
print (f"Saving as {fn}")
CCm.asdf().to_csv(fn, compression = "gzip")


# !ls ../data

#CCm     = CPCContainer.from_df(pd.read_csv("../data/A014-1683963372.csv.gz"))
CCu3    = CCm.byparams(exchange="uniswap_v3")
CCu2    = CCm.byparams(exchange="uniswap_v2")
CCs2    = CCm.byparams(exchange="sushiswap_v2")
CCc1    = CCm.byparams(exchange="carbon_v1")
tc_u3   = CCu3.token_count(asdict=True)
tc_u2   = CCu2.token_count(asdict=True)
tc_s2   = CCs2.token_count(asdict=True)
tc_c1   = CCc1.token_count(asdict=True)
CAm     = CPCAnalyzer(CCm)


# ## Market structure analysis

CA = CAm
pairs0  = CA.CC.pairs(standardize=False)
pairs   = CA.pairs()
pairsc  = CA.pairsc()
tokens  = CA.tokens()

print(f"Total pairs:    {len(pairs0):4}")
print(f"Primary pairs:  {len(pairs):4}")
print(f"...carbon:      {len(pairsc):4}")
print(f"Tokens:         {len(CA.tokens()):4}")
print(f"Curves:         {len(CCm):4}")

CA.count_by_pairs()

CA.count_by_pairs(minn=2)

# ## Carbon

ArbGraph.from_cc(CCc1).plot()._

len(CCc1), len(CCc1.tokens())

CCc1.token_count()


len(CCc1.pairs()), CCc1.pairs()

# ## All pairs

pairsc=list(CAm.pairsc())
pairsc.sort()
pairsc += ["==/==", f"{T.WETH}/{T.USDC}", f"{T.WBTC}/{T.USDC}", f"{T.USDT}/{T.USDC}", "BNT-FF1C/vBNT-7f94"]
for pair in pairsc:
    pi = CA.pair_data(pair)
    O = MargPOptimizer(pi.CC)
    tkn0, tkn1 = pair.split("/")
    
    try:
        r0 = O.margp_optimizer(tkn0, params=dict(verbose=False, debug=False))
        r0.trade_instructions(ti_format=O.TIF_DFAGGR8)
        r00 = r0.result or 0

        r1 = O.margp_optimizer(tkn1, params=dict(verbose=False, debug=False))
        r11 = r1.result or 0
        r1.trade_instructions(ti_format=O.TIF_DFAGGR8)

        print(f"{Pair.n(pair):12}- {-r00:12.4f} {tkn0:10} {-r11:12.4f} {tkn1:10}")
    except Exception as e:
        print(f"{Pair.n(pair):12}-")

# ## Analysis by pair

pricedf = CAm.pool_arbitrage_statistics()
pricedf

# ### WETH/USDC

pair = "WETH-6Cc2/USDC-eB48"
print(f"Pair = {pair}")

df = pricedf.loc[Pair.n(pair)]
df

pi = CA.pair_data(pair)
O = MargPOptimizer(pi.CC)

# #### Target token = base token

targettkn = pair.split("/")[0]
print(f"Target token = {targettkn}")
r = O.margp_optimizer(targettkn, params=dict(verbose=False, debug=False))
r.trade_instructions(ti_format=O.TIF_DFAGGR8)

dfti1 = r.trade_instructions(ti_format=O.TIF_DFPG8)
print(f"Total gain: {sum(dfti1['gain_ttkn']):.4f} {targettkn}")
dfti1

# #### Target token = quote token

targettkn = pair.split("/")[1]
print(f"Target token = {targettkn}")
r = O.margp_optimizer(targettkn, params=dict(verbose=False, debug=False))
r.trade_instructions(ti_format=O.TIF_DFAGGR8)

dfti2 = r.trade_instructions(ti_format=O.TIF_DFPG8)
#print(f"Total gain: {sum(dfti2['gain_ttkn']):.4f}", targettkn)
dfti2

# ### WBTC/USDC

pair = f"{T.WBTC}/{T.USDC}"
print(f"Pair = {pair}")

df = pricedf.loc[Pair.n(pair)]
df

pi = CA.pair_data(pair)
O = MargPOptimizer(pi.CC)

# +
#CA.price_ranges().loc["WBTC/USDC"]
# -

# #### Target token = base token

targettkn = pair.split("/")[0]
print(f"Target token = {targettkn}")
r = O.margp_optimizer(targettkn, params=dict(verbose=False, debug=False))
r.trade_instructions(ti_format=O.TIF_DFAGGR8)

dfti1 = r.trade_instructions(ti_format=O.TIF_DFPG8)
print(f"Total gain: {sum(dfti1['gain_ttkn']):.4f} {targettkn}")
dfti1

# #### Target token = quote token

targettkn = pair.split("/")[1]
print(f"Target token = {targettkn}")
r = O.margp_optimizer(targettkn, params=dict(verbose=False, debug=False))
r.trade_instructions(ti_format=O.TIF_DFAGGR8)

dfti2 = r.trade_instructions(ti_format=O.TIF_DFPG8)
print(f"Total gain: {sum(dfti2['gain_ttkn']):.4f}", targettkn)
dfti2

# ### USDC/USDT

pair = f"{T.USDT}/{T.USDC}"
print(f"Pair = {pair}")

df = pricedf.loc[Pair.n(pair)]
df

pi = CA.pair_data(pair)
O = MargPOptimizer(pi.CC)

# #### Target token = base token

targettkn = pair.split("/")[0]
print(f"Target token = {targettkn}")
r = O.margp_optimizer(targettkn, params=dict(verbose=False, debug=False))
r.trade_instructions(ti_format=O.TIF_DFAGGR8)

dfti1 = r.trade_instructions(ti_format=O.TIF_DFPG8)
print(f"Total gain: {sum(dfti1['gain_ttkn']):.4f} {targettkn}")
dfti1

# #### Target token = quote token

targettkn = pair.split("/")[1]
print(f"Target token = {targettkn}")
r = O.margp_optimizer(targettkn, params=dict(verbose=False, debug=False))
r.trade_instructions(ti_format=O.TIF_DFAGGR8)

dfti2 = r.trade_instructions(ti_format=O.TIF_DFPG8)
print(f"Total gain: {sum(dfti2['gain_ttkn']):.4f}", targettkn)
dfti2

# ### BNT/vBNT

pair = f"{T.BNT}/vBNT-7f94"
print(f"Pair = {pair}")

df = pricedf.loc[Pair.n(pair)]
df

pi = CA.pair_data(pair)
O = MargPOptimizer(pi.CC)

# #### Target token = base token

targettkn = pair.split("/")[0]
print(f"Target token = {targettkn}")
r = O.margp_optimizer(targettkn, params=dict(verbose=False, debug=False))
r.trade_instructions(ti_format=O.TIF_DFAGGR8)

dfti1 = r.trade_instructions(ti_format=O.TIF_DFPG8)
print(f"Total gain: {sum(dfti1['gain_ttkn']):.4f} {targettkn}")
dfti1

# #### Target token = quote token

targettkn = pair.split("/")[1]
print(f"Target token = {targettkn}")
r = O.margp_optimizer(targettkn, params=dict(verbose=False, debug=False))
r.trade_instructions(ti_format=O.TIF_DFAGGR8)

dfti2 = r.trade_instructions(ti_format=O.TIF_DFPG8)
print(f"Total gain: {sum(dfti2['gain_ttkn']):.4f}", targettkn)
dfti2






