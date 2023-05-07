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

for pair in CA.pairsc():
    try:
        d = CA.pair_analysis(pair)
        #print(CA.pair_analysis_pp(d))
    except Exception as e:
        pass
#         print(f"Pair:               {pair}")
#         print(f"Error:              {e}")
#         print()

# ## Individual pairs

# +
# CODE = """
# # #### {pairn}

# pair = "{pair}"
# pricedf.loc[Pair.n(pair)]

# pi = CA.pair_data(pair)
# O = CPCArbOptimizer(pi.CC)
# r = O.margp_optimizer(pair.split("/")[0])
# r.trade_instructions(ti_format=O.TIF_DFAGGR)

# r = O.margp_optimizer(pair.split("/")[1])
# r.trade_instructions(ti_format=O.TIF_DFAGGR)
# """

# for pair, _ in curves_by_pair:
#     print(CODE.format(pairn=Pair.n(pair), pair=pair))
# -

# #### WETH/USDC

pair = "WETH-6Cc2/USDC-eB48"
d    = CA.pair_analysis(pair)

print(CA.pair_analysis_pp(d))

pairs1 = CCm.filter_pairs(bothin=f"{d.tknb}, {d.tknq}, {CPCContainer.TRIANGTOKENS}")
pairs1

CCm1 = CCm.bypairs(pairs1).byparams(exchange="carbon_v1", _inv=True)
print("exchanges", {c.P("exchange") for c in CCm1})
O = CPCArbOptimizer(CCm1)
r = O.margp_optimizer(d.tknb, params=dict(verbose=False, debug=False))
ti1 = r.trade_instructions(ti_format=O.TIF_DFAGGR)
ti1

r = O.margp_optimizer(d.tknq)
ti2 = r.trade_instructions(ti_format=O.TIF_DFAGGR)
ti2.fillna("")

CCc.tokens()

CCm1.tokens()

CCmc = CCm1.copy()
CCmc += CCc
print("exchanges", {c.P("exchange") for c in CCmc})
O = CPCArbOptimizer(CCmc)
r = O.margp_optimizer(d.tknb, params=dict(verbose=False, debug=False))
ti1 = r.trade_instructions(ti_format=O.TIF_DFAGGR)
ti1

r = O.margp_optimizer(d.tknq)
ti2 = r.trade_instructions(ti_format=O.TIF_DFAGGR)
ti2.fillna("")



# +
O = CPCArbOptimizer(CCc)

r = O.margp_optimizer(d.tknb, params=dict(verbose=False, debug=False))
ti1 = r.trade_instructions(ti_format=O.TIF_DFAGGR)

r = O.margp_optimizer(d.tknq)
ti2 = r.trade_instructions(ti_format=O.TIF_DFAGGR)
# -

ti1

ti2

CPCContainer([c]).plot()

c=CCm.bycid("1701411834604692317316873037158841057296-0")
c.p_min, c.p_max

d.curvedfx

d.ccurvedf

d.titn

d.ti1

d.ti2



