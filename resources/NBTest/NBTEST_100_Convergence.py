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
try:
    from tools import ConstantProductCurve as CPC, CurveContainer
    from tools.curves import T, CPCInverter, Pair
    from tools import MargPOptimizer, PairOptimizer
    from tools.optimizer import CPCArbOptimizer, F
    from tools.analyzer import CPCAnalyzer
    from tools.testing import *    
    
    

except:
    from fastlane_bot.tools import ConstantProductCurve as CPC, CurveContainer
    from fastlane_bot.tools.curve import T, CPCInverter, Pair
    from fastlane_bot.tools import MargPOptimizer, PairOptimizer
    from fastlane_bot.tools.optimizer import CPCArbOptimizer, F
    from fastlane_bot.tools.analyzer import CPCAnalyzer
    from fastlane_bot.tools.testing import *   


import numpy as np
import matplotlib.pyplot as plt

print("{0.__name__} v{0.__VERSION__} ({0.__DATE__})".format(Pair))
print("{0.__name__} v{0.__VERSION__} ({0.__DATE__})".format(CPC))
print("{0.__name__} v{0.__VERSION__} ({0.__DATE__})".format(CPCArbOptimizer))
print("{0.__name__} v{0.__VERSION__} ({0.__DATE__})".format(MargPOptimizer))
print("{0.__name__} v{0.__VERSION__} ({0.__DATE__})".format(PairOptimizer))

plt.style.use('seaborn-v0_8-dark')
plt.rcParams['figure.figsize'] = [12,6]
# -

# # Optimizer Testing Convergence Changes [NBTest 100]

# ## THOR related Tests
#
# this test originates in the `Optimizer_2312_THOR` notebook

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

# ### CPC min range width functionality

cdata = dict(y=100, yint=100, pa=100, pb=100, pair="WETH-6Cc2/USDC-eB48", tkny="USDC-eB48")
c  = CPC.from_carbon(**cdata)
c2 = CPC.from_carbon(**cdata, minrw=1e-2)
c4 = CPC.from_carbon(**cdata, minrw=1e-4)
c6 = CPC.from_carbon(**cdata, minrw=1e-6)
c

assert c2.params.minrw==0.01
assert c4.params.minrw==0.0001
assert c6.params.minrw==0.000001
assert c.params.minrw==0.000001

assert iseq(c2.p**2/100**2, 1.01)
assert iseq(c4.p**2/100**2, 1.0001)
assert iseq(c6.p**2/100**2, 1.000001)
assert iseq(c.p, c6.p)

assert iseq(c2.p-100, 0.49875621120, eps=1e-3)
assert iseq(c4.p-100, 0.00499987500, eps=1e-3)
assert iseq(c6.p-100, 0.00004999875, eps=1e-3)
assert iseq((c2.p-100)/(c4.p-100), 99.75373596136635, eps=1e-4)
assert iseq((c4.p-100)/(c6.p-100), 99.99752507444194, eps=1e-4)

# ### margpoptimizer absolute convergence

cdata = dict(y=100, yint=100, pa=100, pb=100, pair="WETH-6Cc2/USDC-eB48", tkny="USDC-eB48")
c  = CPC.from_carbon(**cdata)
O = MargPOptimizer(CurveContainer([c,c]))
r = O.optimize("USDC-eB48", params=dict(verbose=True, debug=True), result=O.MO_DEBUG)
assert r["crit"]["crit"] == O.MO_MODE_REL
assert r["crit"]["epsr"] == O.MO_EPSR
assert r["crit"]["epsa"] == O.MO_EPSA
assert r["crit"]["epsaunit"] == O.MO_EPSAUNIT
assert r["crit"]["pstart"] is None

raises(O.optimize, "USDC-eB48", params=dict(crit="meh"))

raises(O.optimize, "USDC-eB48", mode="meh", params=dict(), result=O.MO_DEBUG)
#raises(O.optimize, "USDC-eB48", mode=O.MO_MODE_ABS, params=dict(), result=O.MO_DEBUG)
#raises(O.optimize, "USDC-eB48", mode=O.MO_MODE_ABS, params=dict(), pstart=dict(FOO=1)))
#raises(O.optimize, "USDC-eB48", mode=O.MO_MODE_ABS, params=dict(), pstart={"WETH-6Cc2":2000, "USDC-eB48":1}))

r = O.optimize("USDC-eB48", mode=O.MO_MODE_ABS, params=dict(
    eps = 1e-10,
    epsa = 100,
    epsaunit = "dollah",
    pstart = {"dollah":1, "WETH-6Cc2": 2000, "USDC-eB48":1},
), result=O.MO_DEBUG)
assert r["crit"]["crit"] == O.MO_MODE_ABS
assert r["crit"]["epsa"] == 100
assert r["crit"]["epsaunit"] == "dollah"
assert r["crit"]["pstart"] == {"dollah":1, "WETH-6Cc2": 2000, "USDC-eB48":1}

1
