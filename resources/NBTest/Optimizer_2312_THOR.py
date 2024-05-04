# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:light
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.15.2
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

# +
from tools.curves import ConstantProductCurve as CPC, CurveContainer, T, CPCInverter, Pair
from tools.optimizer import CPCArbOptimizer, F, MargPOptimizer, PairOptimizer
from tools.analyzer import CPCAnalyzer

import numpy as np
import matplotlib.pyplot as plt

#print("{0.__name__} v{0.__VERSION__} ({0.__DATE__})".format(Pair))
print("{0.__name__} v{0.__VERSION__} ({0.__DATE__})".format(CPC))
#print("{0.__name__} v{0.__VERSION__} ({0.__DATE__})".format(CPCArbOptimizer))
print("{0.__name__} v{0.__VERSION__} ({0.__DATE__})".format(MargPOptimizer))
#print("{0.__name__} v{0.__VERSION__} ({0.__DATE__})".format(PairOptimizer))

plt.style.use('seaborn-v0_8-dark')
plt.rcParams['figure.figsize'] = [12,6]
# -

# # Optimizer Testing (Thor, Dec 2023)
# _202312a-THOR-8044 Triangle_
#
# **IMPORTANT NOTE** 
#
# For the above imports to work, you must create a symlink to the `tools` module here, running
#
#     ln -s ../../fastlane_bot/tools tools
#     
# Don't forget to add a local `.gitignore` file in this case!

# ## Reading input data
#
# Set `curves_as_dicts` to the output of `CPCContainer.as_dicts`. The use `CPCContainer.from_dicts` to recreate a container.

curves_as_dicts = [{'k': 4.3078885616238194e+24,
  'x': 1250505254484.4102,
  'x_act': 0,
  'y_act': 344491.8061533139,
  'alpha': 0.5,
  'pair': 'USDC-eB48/THOR-8044',
  'cid': '74181555988764585035015664420125470098056-1',
  'fee': 2000.0,
  'descr': 'carbon_v1 THOR-8044/USDC-eB48 2000',
  'constr': 'carb',
  'params': {'exchange': 'carbon_v1',
   'tknx_dec': 18,
   'tkny_dec': 6,
   'tknx_addr': '0xa5f2211B9b8170F694421f2046281775E8468044',
   'tkny_addr': '0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48',
   'blocklud': 18758319,
   'y': 344491.8061533139,
   'yint': 344491.8061533139,
   'A': 0,
   'B': 1.659765242784964,
   'pa': 2.754820936639097,
   'pb': 2.754820936639097}},
 {'k': 1106096356.8039548,
  'x': 2619874.8519412754,
  'x_act': 2619874.8519412754,
  'y_act': 422.1943487049999,
  'alpha': 0.5,
  'pair': 'THOR-8044/WETH-6Cc2',
  'cid': '0xbf1875da0431343b56ec6295f706e257dbe85696e5270a5bdad005d37cc2fd9c',
  'fee': 0.003,
  'descr': 'sushiswap_v2 THOR-8044/WETH-6Cc2 0.003',
  'constr': 'uv2',
  'params': {'exchange': 'sushiswap_v2',
   'tknx_dec': 18,
   'tkny_dec': 18,
   'tknx_addr': '0xa5f2211B9b8170F694421f2046281775E8468044',
   'tkny_addr': '0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2',
   'blocklud': 18758340}},
 {'k': 1233376864385.0625,
  'x': 54102579.539405,
  'x_act': 54102579.539405,
  'y_act': 22797.00662861641,
  'alpha': 0.5,
  'pair': 'USDC-eB48/WETH-6Cc2',
  'cid': '0x68bd2250b4b44996e193e9e001f74a5e5a31b31fbd0bb7df34c66eb8da7e6be2',
  'fee': 3000.0,
  'descr': 'uniswap_v2 USDC-eB48/WETH-6Cc2 0.003',
  'constr': 'uv2',
  'params': {'exchange': 'uniswap_v2',
   'tknx_dec': 6,
   'tkny_dec': 18,
   'tknx_addr': '0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48',
   'tkny_addr': '0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2',
   'blocklud': 18758413}}]

CC = CurveContainer.from_dicts(curves_as_dicts)
len(CC), len(curves_as_dicts)

# ## Analyzis and visualization
#
# Note: THOR-8044 ~ 30c

# ### Visualization

CC.plot()

# ### Analysis

sgn = [1,-1,-1]
price = dict()
quote = dict()
for c,s in zip(CC, sgn):
    price[c.pair] = c.p
    quotep = f"{c.tkny} per {c.tknx}" if s > 0 else f"{c.tknx} per {c.tkny}"
    print(f"{c.pair} {s} {(c.p)**s} {quotep}")

price

# ### Carbon curve
#
# Below is the Carbon curve. It **sells THOR** and **buys USDC** at a rate of **0.36 USDC per THOR** (ignoring fees).

p0 = 1/(price["USDC-eB48/THOR-8044"])
p0

print(CC[0].description())

# Ignoring slippage and fees, it is possible to buy and sell THOR AT 0.38 USDC per THOR via the two provided curves.

p1 = 1/(price["USDC-eB48/WETH-6Cc2"] / price["THOR-8044/WETH-6Cc2"])
p1

# That's an arbitrage opportunity (Buy THOR against USDC on Carbon, sell into the arb) of about 5% meaning that at least in small size (ie before slippage) it should work

p1/p0-1

# ### Triangle curves
#
# The triangle curves are the following
#
# - **THOR/WETH** has 422 ETH and 2.6m THOR at a price of 6205 THOR per ETH
# - **WETH/USDC** has 23k ETH and 50m USDC at a price of 2373 USDC per ETH
#
# The implied **THOR** price is 0.382 USDC (memo: on Carbon it is 0.362, and the THOR loading is 344k, ie ~15% of the THOR-8044 available on the arb curve)

p1, p0, p1/p0-1, 344/2600

print(CC[1].description())

1/0.0001611505787737007

print(CC[2].description())

1/0.00042136635300378734

# ## Optimizer

# +
#help(MargPOptimizer.optimize)
# -

# ### Raw run
#
# This is the actual run, using USDC as the arbitrage token. This run does not converge; rather the THOR-8044/USDC-eB48 price oscillates between 0.38ish and 0.29ish. Note that this is way out of the (imputed) price range for the Carbon range which is very tightly centered around `p0~0.36`
#
# (uncomment the below code to see the debug run)

# Note: this section of the code no longer runs as the price estimates cannnot be found; this could be related to the fact that we moved from `ticker-shortaddr` to `address`. It does not really matter though, the code in the following sections is enough.

O = MargPOptimizer(CC)
r = O.optimize("USDC-eB48", result=O.MO_DEBUG, params=dict(debug_pe=True))
r

O = MargPOptimizer(CC)
try:
    r = O.optimize("USDC-eB48", params=dict(verbose=False, debug=False))
except Exception as e:
    print(e)
    r = None
#O.optimize("USDC", params=dict(verbose=True, debug=True))
r

# +
#r = O.optimize("USDC", params=dict(verbose=True, debug=True))
#r
# -

# ### Better prices estimates
#
# We set the initial price for THOR/USD squat into the Carbon range to see whether this works better. 
#
# TLDR -- it does not.

price_est = {
    "USDC-eB48": 1,
    "WETH-6Cc2": 2373.2,
    "THOR-8044": p0,
}
price_est

O = MargPOptimizer(CC)
r = O.optimize("USDC-eB48", params=dict(pstart=price_est, verbose=False, debug=False))
#O.optimize("USDC", params=dict(pstart=price_est, verbose=True, debug=True))
r

# #### Tighter Jacobian
#
# Currently the jacobian h is set to 1e-5 and `minrw` in the data provided is set to 1e-7 meaning that the Jacobian calculation goes outside the concentrated liquidity area and is therefore much too steep.
#
# We'll try 1e-8 as `jach` here. Turns out this works and it even converges. 

CC[0].p_max/CC[0].p_min-1

O = MargPOptimizer(CC)
r = O.optimize("USDC-eB48", params=dict(pstart=price_est, verbose=False, debug=False, jach=1e-8))
#O.optimize("USDC", params=dict(pstart=price_est, verbose=True, debug=True))
r

# +
# CCr.plot()

# +
# O = MargPOptimizer(CCr)
# r = O.optimize("USDC-eB48", params=dict(verbose=False, debug=False))
# O.optimize("USDC-eB48", params=dict(verbose=True, debug=True))
# r

# +
# p2 = r.p_optimal["THOR-8044"]
# p2

# +
# p2/p0-1

# +
# r.dtokens
# -

# #### Absolute convergence criteria

# +
#O.optimize("USDC-eB48", result=O.MO_PSTART)
# -

pstart = {'WETH-6Cc2': 2373.231732603511, 'THOR-8044': 0.36299996370000637, 'USDC-eB48': 1, "USD": 1}
params = dict(norm=O.MO_NORMLINF, epsa=10, epsaunit="USD", pstart=pstart)
r = O.optimize("USDC-eB48", mode=O.MO_MODE_ABS, params=dict(verbose=False, debug=False, **params))
#r = O.optimize("USDC-eB48", params=dict(verbose=True, debug=True, **params))
r

# ### Removing the Carbon curve
#
# Here we check how it converges if we remove the Carbon curve and replace it with a constant product curve of the same (virtual) capacity. Unsurprisingly it does and all dtokens are zero.

c0 = CC[0]
c0b = CPC.from_xy(x=c0.x, y=c0.y, pair=c0.pair)
c0b

CCb = CurveContainer.from_dicts(curves_as_dicts[1:])
CCb += c0b
CCb.plot()

O = MargPOptimizer(CCb)
r = O.optimize("USDC-eB48", params=dict(verbose=False, debug=False))
#O.optimize("USDC", params=dict(verbose=True, debug=True))
r

r.dtokens


# #### Absolute convergence criteria

# +
#O.optimize("USDC-eB48", result=O.MO_PSTART)
# -

pstart = {'WETH-6Cc2': 2373.231732603511, 'THOR-8044': 0.36299996370000637, 'USDC-eB48': 1, "USD": 1}
params = dict(norm=O.MO_NORMLINF, epsa=10, epsaunit="USD")
r = O.optimize("USDC-eB48", mode=O.MO_MODE_ABS, pstart=pstart, params=dict(verbose=False, debug=False))
#O.optimize("USDC-eB48", params=dict(verbose=True, debug=True, **params))
r

1
