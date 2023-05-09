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

from fastlane_bot import Bot#, Config, ConfigDB, ConfigNetwork, ConfigProvider
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

# # Mainnet Statistics [A011]

bot     = Bot()
CCm     = bot.get_curves()
#CCm     = CPCContainer.from_df(pd.read_csv("A011.csv.gz"))
#CCm.asdf().to_csv("A011-test.csv.gz", compression = "gzip")
CCu3    = CCm.byparams(exchange="uniswap_v3")
CCu2    = CCm.byparams(exchange="uniswap_v2")
CCs2    = CCm.byparams(exchange="sushiswap_v2")
CCc1    = CCm.byparams(exchange="carbon_v1")
tc_u3   = CCu3.token_count(asdict=True)
tc_u2   = CCu2.token_count(asdict=True)
tc_s2   = CCs2.token_count(asdict=True)
tc_c1   = CCc1.token_count(asdict=True)
CAm     = CPCAnalyzer(CCm)


# ## Market structure analysis [NOTEST]

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

# ### All crosses

CCx = CCm.bypairs(
    CCm.filter_pairs(notin=f"{T.ETH},{T.USDC},{T.USDT},{T.BNT},{T.DAI},{T.WBTC}")
)
len(CCx), CCx.token_count()[:10]

AGx=ArbGraph.from_cc(CCx)
AGx.plot(labels=False, node_size=50, node_color="#fcc")._

# ### Biggest crosses (HEX, UNI, ICHI, FRAX)

CCx2 = CCx.bypairs(
    CCx.filter_pairs(onein=f"{T.HEX}, {T.UNI}, {T.ICHI}, {T.FRAX}")
)
ArbGraph.from_cc(CCx2).plot()
len(CCx2)

# ### Carbon

ArbGraph.from_cc(CCc1).plot()._

len(CCc1), len(CCc1.tokens())

CCc1.token_count()


len(CCc1.pairs()), CCc1.pairs()

# ### Token subsets

O = MargPOptimizer(CCm.bypairs(
    CCm.filter_pairs(bothin=f"{T.ETH},{T.USDC},{T.USDT},{T.BNT},{T.DAI},{T.WBTC}")
))
r = O.margp_optimizer(f"{T.USDC}", params=dict(verbose=False, debug=False))
r.trade_instructions(ti_format=O.TIF_DFAGGR)

# +
#r.trade_instructions(ti_format=O.TIF_DFAGGR).fillna("").to_excel("ti.xlsx")

# +
#ArbGraph.from_r(r).plot()._

# +
#O.CC.plot()
# -

# ## All pairs

for pair in CAm.pairsc():
    pi = CA.pair_data(pair)
    O = MargPOptimizer(pi.CC)
    tkn0, tkn1 = pair.split("/")
    
    try:
        r0 = O.margp_optimizer(tkn0, params=dict(verbose=False, debug=False))
        r0.trade_instructions(ti_format=O.TIF_DFAGGR)
        r00 = r0.result or 0

        r1 = O.margp_optimizer(targettkn, params=dict(verbose=False, debug=False))
        r11 = r1.result or 0
        r1.trade_instructions(ti_format=O.TIF_DFAGGR)

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
r.trade_instructions(ti_format=O.TIF_DFAGGR)

dfti1 = r.trade_instructions(ti_format=O.TIF_DFPG8)
print(f"Total gain: {sum(dfti1['gain_ttkn']):.4f} {targettkn}")
dfti1

# #### Target token = quote token

targettkn = pair.split("/")[1]
print(f"Target token = {targettkn}")
r = O.margp_optimizer(targettkn, params=dict(verbose=False, debug=False))
r.trade_instructions(ti_format=O.TIF_DFAGGR)

dfti2 = r.trade_instructions(ti_format=O.TIF_DFPG8)
print(f"Total gain: {sum(dfti2['gain_ttkn']):.4f}", targettkn)
dfti2


