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

# # Mainnet Server [A011]

bot     = Bot()
CCm     = bot.get_curves()
CA      = CPCAnalyzer(CCm)

pairs0  = CA.CC.pairs(standardize=False)
pairs   = CA.pairs()
pairsc  = CA.pairsc()
tokens  = CA.tokens()

assert CA.pairs()  == CCm.pairs(standardize=True)
assert CA.pairsc() == {c.pairo.primary for c in CCm if c.P("exchange")=="carbon_v1"}
assert CA.tokens() == CCm.tokens()

# ## Overall market

print(f"Total pairs:    {len(pairs0):4}")
print(f"Primary pairs:  {len(pairs):4}")
print(f"...carbon:      {len(pairsc):4}")
print(f"Tokens:         {len(CCm.tokens()):4}")
print(f"Curves:         {len(CCm):4}")

# ## By pair

# ### All pairs

cbp0 = {pair: [c for c in CCm.bypairs(pair)] for pair in CCm.pairs()} # curves by (primary) pair
nbp0 = {pair: len(cc) for pair,cc in cbp0.items()}
assert len(cbp0) == len(CCm.pairs())
assert set(cbp0) == CCm.pairs()

# ### Only those with >1 curves

cbp = {pair: cc for pair, cc in cbp0.items() if len(cc)>1}
nbp = {pair: len(cc) for pair,cc in cbp.items()}
print(f"Pairs with >1 curves:  {len(cbp)}")
print(f"Curves in those:       {sum(nbp.values())}")
print(f"Average curves/pair:   {sum(nbp.values())/len(cbp):.1f}")

# ### x=0 or y=0

xis0 = {c.cid: (c.x, c.y) for c in CCm if c.x==0}
yis0 = {c.cid: (c.x, c.y) for c in CCm if c.y==0}
assert len(xis0) == 0 # set loglevel debug to see removal of curves
assert len(yis0) == 0

# ### Prices

# #### All

prices_da = {pair: 
             [(
                Pair.n(pair), pair, c.primaryp(), c.cid, c.cid[-8:], c.P("exchange"), c.tvl(tkn=pair.split("/")[0]),
                "x" if c.itm(cc) else "", c.buysell(verbose=False), c.buysell(verbose=True, withprice=True)
              ) for c in cc 
             ] 
             for pair, cc in cbp.items()
            }
#prices_da

# #### Only for pairs that have at least on Carbon pair

prices_d = {pair: l for pair,l in prices_da.items() if pair in pairsc}
prices_l = list(it.chain(*prices_d.values()))

# +
#prices_d
# -

curves_by_pair = list(cl.Counter([r[1] for r in prices_l]).items())
curves_by_pair = sorted(curves_by_pair, key=lambda x: x[1], reverse=True)
curves_by_pair

CODE = """
# #### {pairn}

pair = "{pair}"
pricedf.loc[Pair.n(pair)]

pi = CA.pair_data(pair)
O = CPCArbOptimizer(pi.CC)
r = O.margp_optimizer(pair.split("/")[0])
r.trade_instructions(ti_format=O.TIF_DFAGGR)

r = O.margp_optimizer(pair.split("/")[1])
r.trade_instructions(ti_format=O.TIF_DFAGGR)
"""

# +
# for pair, _ in curves_by_pair:
#     print(CODE.format(pairn=Pair.n(pair), pair=pair))
# -

# #### Dataframe

pricedf0 = pd.DataFrame(prices_l, columns="pair,pairf,price,cid,cid0,exchange,vl,itm,bs,bsv".split(","))
pricedf = pricedf0.drop(['cid', 'pairf'], axis=1).sort_values(by=["pair", "exchange", "cid0"])
pricedf = pricedf.set_index(["pair", "exchange", "cid0"])
pricedf

# ### Individual frames

# #### WETH/USDC

pair = "WETH-6Cc2/USDC-eB48"
pricedf.loc[Pair.n(pair)]

pi = CA.pair_data(pair)
O = CPCArbOptimizer(pi.CC)
r = O.margp_optimizer(pair.split("/")[0], params=dict(verbose=False, debug=False))
r.trade_instructions(ti_format=O.TIF_DFAGGR)

r = O.margp_optimizer(pair.split("/")[1])
r.trade_instructions(ti_format=O.TIF_DFAGGR)


# #### BNT/WETH

pair = "BNT-FF1C/WETH-6Cc2"
pricedf.loc[Pair.n(pair)]

pi = CA.pair_data(pair)
O = CPCArbOptimizer(pi.CC)
r = O.margp_optimizer(pair.split("/")[0])
r.trade_instructions(ti_format=O.TIF_DFAGGR)

r = O.margp_optimizer(pair.split("/")[1])
r.trade_instructions(ti_format=O.TIF_DFAGGR)


# #### BNT/vBNT

pair = "BNT-FF1C/vBNT-7f94"
pricedf.loc[Pair.n(pair)]

pi = CA.pair_data(pair)
O = CPCArbOptimizer(pi.CC)
r = O.margp_optimizer(pair.split("/")[0])
r.trade_instructions(ti_format=O.TIF_DFAGGR)

r = O.margp_optimizer(pair.split("/")[1])
r.trade_instructions(ti_format=O.TIF_DFAGGR)


# #### USDT/USDC

pair = "USDT-1ec7/USDC-eB48"
pricedf.loc[Pair.n(pair)]

pi = CA.pair_data(pair)
O = CPCArbOptimizer(pi.CC)
r = O.margp_optimizer(pair.split("/")[0])
r.trade_instructions(ti_format=O.TIF_DFAGGR)

r = O.margp_optimizer(pair.split("/")[1])
r.trade_instructions(ti_format=O.TIF_DFAGGR)


# #### WBTC/WETH

pair = "WBTC-C599/WETH-6Cc2"
pricedf.loc[Pair.n(pair)]

pi = CA.pair_data(pair)
O = CPCArbOptimizer(pi.CC)
r = O.margp_optimizer(pair.split("/")[0])
r.trade_instructions(ti_format=O.TIF_DFAGGR)

r = O.margp_optimizer(pair.split("/")[1])
r.trade_instructions(ti_format=O.TIF_DFAGGR)


# #### LINK/USDT

pair = "LINK-86CA/USDT-1ec7"
pricedf.loc[Pair.n(pair)]

pi = CA.pair_data(pair)
O = CPCArbOptimizer(pi.CC)
r = O.margp_optimizer(pair.split("/")[0])
r.trade_instructions(ti_format=O.TIF_DFAGGR)

r = O.margp_optimizer(pair.split("/")[1])
r.trade_instructions(ti_format=O.TIF_DFAGGR)


# #### WBTC/USDT

pair = "WBTC-C599/USDT-1ec7"
pricedf.loc[Pair.n(pair)]

pi = CA.pair_data(pair)
O = CPCArbOptimizer(pi.CC)
r = O.margp_optimizer(pair.split("/")[0])
r.trade_instructions(ti_format=O.TIF_DFAGGR)

r = O.margp_optimizer(pair.split("/")[1])
r.trade_instructions(ti_format=O.TIF_DFAGGR)


# #### BNT/USDC

pair = "BNT-FF1C/USDC-eB48"
pricedf.loc[Pair.n(pair)]

pi = CA.pair_data(pair)
O = CPCArbOptimizer(pi.CC)
r = O.margp_optimizer(pair.split("/")[0])
r.trade_instructions(ti_format=O.TIF_DFAGGR)

r = O.margp_optimizer(pair.split("/")[1])
r.trade_instructions(ti_format=O.TIF_DFAGGR)


# #### WETH/DAI

pair = "WETH-6Cc2/DAI-1d0F"
pricedf.loc[Pair.n(pair)]

pi = CA.pair_data(pair)
O = CPCArbOptimizer(pi.CC)
r = O.margp_optimizer(pair.split("/")[0])
r.trade_instructions(ti_format=O.TIF_DFAGGR)

r = O.margp_optimizer(pair.split("/")[1])
r.trade_instructions(ti_format=O.TIF_DFAGGR)


# #### DAI/USDT

pair = "DAI-1d0F/USDT-1ec7"
pricedf.loc[Pair.n(pair)]

pi = CA.pair_data(pair)
O = CPCArbOptimizer(pi.CC)
r = O.margp_optimizer(pair.split("/")[0])
r.trade_instructions(ti_format=O.TIF_DFAGGR)

r = O.margp_optimizer(pair.split("/")[1])
r.trade_instructions(ti_format=O.TIF_DFAGGR)


# #### DAI/USDC

pair = "DAI-1d0F/USDC-eB48"
pricedf.loc[Pair.n(pair)]

pi = CA.pair_data(pair)
O = CPCArbOptimizer(pi.CC)
r = O.margp_optimizer(pair.split("/")[0])
r.trade_instructions(ti_format=O.TIF_DFAGGR)

r = O.margp_optimizer(pair.split("/")[1])
r.trade_instructions(ti_format=O.TIF_DFAGGR)


# #### WETH/USDT

pair = "WETH-6Cc2/USDT-1ec7"
pricedf.loc[Pair.n(pair)]

pi = CA.pair_data(pair)
O = CPCArbOptimizer(pi.CC)
r = O.margp_optimizer(pair.split("/")[0])
r.trade_instructions(ti_format=O.TIF_DFAGGR)

r = O.margp_optimizer(pair.split("/")[1])
r.trade_instructions(ti_format=O.TIF_DFAGGR)


# #### LINK/USDC

pair = "LINK-86CA/USDC-eB48"
pricedf.loc[Pair.n(pair)]

pi = CA.pair_data(pair)
O = CPCArbOptimizer(pi.CC)
r = O.margp_optimizer(pair.split("/")[0])
r.trade_instructions(ti_format=O.TIF_DFAGGR)

r = O.margp_optimizer(pair.split("/")[1])
r.trade_instructions(ti_format=O.TIF_DFAGGR)


# #### PEPE/WETH

pair = "PEPE-1933/WETH-6Cc2"
pricedf.loc[Pair.n(pair)]

# +
# pi = CA.pair_data(pair)
# O = CPCArbOptimizer(pi.CC)
# r = O.margp_optimizer(pair.split("/")[0])
# r.trade_instructions(ti_format=O.TIF_DFAGGR)

# +
# r = O.margp_optimizer(pair.split("/")[1])
# r.trade_instructions(ti_format=O.TIF_DFAGGR)
# -


# #### stETH/WETH

pair = "stETH-fE84/WETH-6Cc2"
pricedf.loc[Pair.n(pair)]

# +
# pi = CA.pair_data(pair)
# O = CPCArbOptimizer(pi.CC)
# r = O.margp_optimizer(pair.split("/")[0])
# r.trade_instructions(ti_format=O.TIF_DFAGGR)

# +
# r = O.margp_optimizer(pair.split("/")[1])
# r.trade_instructions(ti_format=O.TIF_DFAGGR)
# -


# #### rETH/WETH

pair = "rETH-6393/WETH-6Cc2"
pricedf.loc[Pair.n(pair)]

pi = CA.pair_data(pair)
O = CPCArbOptimizer(pi.CC)
r = O.margp_optimizer(pair.split("/")[0])
r.trade_instructions(ti_format=O.TIF_DFAGGR)

r = O.margp_optimizer(pair.split("/")[1])
r.trade_instructions(ti_format=O.TIF_DFAGGR)


# #### ARB/MATIC

pair = "ARB-4ad1/MATIC-eBB0"
pricedf.loc[Pair.n(pair)]

# +
# pi = CA.pair_data(pair)
# O = CPCArbOptimizer(pi.CC)
# r = O.margp_optimizer(pair.split("/")[0])
# r.trade_instructions(ti_format=O.TIF_DFAGGR)

# +
# r = O.margp_optimizer(pair.split("/")[1])
# r.trade_instructions(ti_format=O.TIF_DFAGGR)
# -


# #### 0x0/WETH

pair = "0x0-1AD5/WETH-6Cc2"
pricedf.loc[Pair.n(pair)]

# +
# pi = CA.pair_data(pair)
# O = CPCArbOptimizer(pi.CC)
# r = O.margp_optimizer(pair.split("/")[0])
# r.trade_instructions(ti_format=O.TIF_DFAGGR)

# +
# r = O.margp_optimizer(pair.split("/")[1])
# r.trade_instructions(ti_format=O.TIF_DFAGGR)
# -


# #### TSUKA/USDC

pair = "TSUKA-69eD/USDC-eB48"
pricedf.loc[Pair.n(pair)]

pi = CA.pair_data(pair)
O = CPCArbOptimizer(pi.CC)
r = O.margp_optimizer(pair.split("/")[0])
r.trade_instructions(ti_format=O.TIF_DFAGGR)

r = O.margp_optimizer(pair.split("/")[1])
r.trade_instructions(ti_format=O.TIF_DFAGGR)


# #### WBTC/USDC

pair = "WBTC-C599/USDC-eB48"
pricedf.loc[Pair.n(pair)]

pi = CA.pair_data(pair)
O = CPCArbOptimizer(pi.CC)
r = O.margp_optimizer(pair.split("/")[0])
r.trade_instructions(ti_format=O.TIF_DFAGGR)

r = O.margp_optimizer(pair.split("/")[1])
r.trade_instructions(ti_format=O.TIF_DFAGGR)


# #### LYXe/USDC

pair = "LYXe-be6D/USDC-eB48"
pricedf.loc[Pair.n(pair)]

pi = CA.pair_data(pair)
O = CPCArbOptimizer(pi.CC)
r = O.margp_optimizer(pair.split("/")[0])
r.trade_instructions(ti_format=O.TIF_DFAGGR)

r = O.margp_optimizer(pair.split("/")[1])
r.trade_instructions(ti_format=O.TIF_DFAGGR)


