# -*- coding: utf-8 -*-
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
    from fastlane_bot.tools.cpc import ConstantProductCurve as CPC, CPCContainer
    from fastlane_bot.tools.optimizer import CPCArbOptimizer, MargPOptimizer, PairOptimizer
    from fastlane_bot.testing import *

except:
    from tools.cpc import ConstantProductCurve as CPC, CPCContainer
    from tools.optimizer import CPCArbOptimizer, MargPOptimizer, PairOptimizer
    from testing import *
ConstantProductCurve = CPC

from io import StringIO

print("{0.__name__} v{0.__VERSION__} ({0.__DATE__})".format(CPC))
print("{0.__name__} v{0.__VERSION__} ({0.__DATE__})".format(CPCContainer))
print("{0.__name__} v{0.__VERSION__} ({0.__DATE__})".format(CPCArbOptimizer))
print("{0.__name__} v{0.__VERSION__} ({0.__DATE__})".format(MargPOptimizer))
print("{0.__name__} v{0.__VERSION__} ({0.__DATE__})".format(PairOptimizer))

#plt.style.use('seaborn-dark')
#plt.rcParams['figure.figsize'] = [12,6]
# from fastlane_bot import __VERSION__
# require("3.0", __VERSION__)
# -

# # CPC and Optimizer New Features [NBTest101]

Curves = [
    ConstantProductCurve(k=27518385.40998667, x=1272.2926367501436, x_act=0, y_act=2000.9999995236503, alpha=0.5, pair='LINK/USDP', cid='0x425d5d4ad7243f88d9f4cde8da52863b45af1f64e05bede1299909bcaa6c52d1-0', fee=2000, descr='carbon_v1 0x514910771AF9Ca656af840dff83E8264EcF986CA\\/0x8E870D67F660D95d5be530380D0eC0bd388289E1 2000', constr='carb', params={'exchange': 'carbon_v1', 'y': 2000.9999995236503, 'yint': 2000.9999995236503, 'A': 0.38144823884371704, 'B': 3.7416573867739373, 'pa': 16.99999999999995, 'pb': 13.99999999999997}),
    ConstantProductCurve(k=6.160500599566333e+18, x=11099999985.149971, x_act=0, y_act=55.50000002646446, alpha=0.5, pair='USDP/LINK', cid='0x425d5d4ad7243f88d9f4cde8da52863b45af1f64e05bede1299909bcaa6c52d1-1', fee=2000, descr='carbon_v1 0x514910771AF9Ca656af840dff83E8264EcF986CA\\/0x8E870D67F660D95d5be530380D0eC0bd388289E1 2000', constr='carb', params={'exchange': 'carbon_v1', 'y': 55.50000002646446, 'yint': 55.50000002646446, 'A': 0, 'B': 0.22360678656963742, 'pa': 0.04999999999999889, 'pb': 0.04999999999999889}),
    ConstantProductCurve(k=14449532.299465338, x=57487.82879658422, x_act=0, y_act=5.0, alpha=0.5, pair='LINK/ETH', cid='0x3fcccfe0063b71fc973fab8dea39b6be9da80125910c10e57b924b3e4687295a-0', fee=2000, descr='carbon_v1 0x514910771AF9Ca656af840dff83E8264EcF986CA/0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE 2000', constr='carb', params={'exchange': 'carbon_v1', 'y': 5.0, 'yint': 8.582730309868262, 'A': 0.002257868117407469, 'B': 0.06480740698407672, 'pa': 0.004497751124437756, 'pb': 0.004199999999999756}),
    ConstantProductCurve(k=14456757.06563651, x=251.4750925240284, x_act=0, y_act=807.9145301701096, alpha=0.5, pair='ETH/LINK', cid='0x3fcccfe0063b71fc973fab8dea39b6be9da80125910c10e57b924b3e4687295a-1', fee=2000, descr='carbon_v1 0x514910771AF9Ca656af840dff83E8264EcF986CA/0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE 2000', constr='carb', params={'exchange': 'carbon_v1', 'y': 807.9145301701096, 'yint': 1974.7090228584536, 'A': 0.519359008452966, 'B': 14.907119849998594, 'pa': 237.97624997025295, 'pb': 222.22222222222211}),
    ConstantProductCurve(k=56087178.30932376, x=131.6236694086859, x_act=0, y_act=15920.776548455418, alpha=0.5, pair='ETH/USDP', cid='0x6cc4b198ec4cf17fdced081b5611279be73e200711238068b5340e606ba86646-0', fee=2000, descr='carbon_v1 0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE\\/0x8E870D67F660D95d5be530380D0eC0bd388289E1 2000', constr='carb', params={'exchange': 'carbon_v1', 'y': 15920.776548455418, 'yint': 32755.67010983316, 'A': 4.373757425036729, 'B': 54.77225575051648, 'pa': 3498.2508745627138, 'pb': 2999.9999999999854}),
    ConstantProductCurve(k=56059148.73497429, x=426117.72306081816, x_act=0, y_act=5.0, alpha=0.5, pair='USDP/ETH', cid='0x6cc4b198ec4cf17fdced081b5611279be73e200711238068b5340e606ba86646-1', fee=2000, descr='carbon_v1 0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE\\/0x8E870D67F660D95d5be530380D0eC0bd388289E1 2000', constr='carb', params={'exchange': 'carbon_v1', 'y': 5.0, 'yint': 10.106093048875099, 'A': 0.0013497708452092638, 'B': 0.016903085094568837, 'pa': 0.0003331667499582927, 'pb': 0.0002857142857142352}),
]

CC1 = CPCContainer(Curves[0:1])
CC2 = CPCContainer(Curves[0:2])
CC6 = CPCContainer(Curves)

O1 = MargPOptimizer(CC1)
O2 = MargPOptimizer(CC2)
O6 = MargPOptimizer(CC6)

# ## CPCArbOptimizer Dump Curves [NOTEST]

O = O6

# ### Dump as json
#
# dumps the dict representation as json

O2.dump_curves(O.DC_JSON)

# ### Dump as dicts
#
# similar to json dumping, except that the result is a Python representation of dicts that can be directly run as Python code

O2.dump_curves(O.DC_DICTS)

# ### Dump as data frame
#
# dumps as Pandas data frame

# +
#O1.dump_curves(O.DC_DF)
# -

# ### Dump as constructor
#
# dumps as CPC constructors (one per line; every line ends with comma, including last)

O2.dump_curves(O.DC_CONSTR)

# ### Dump into StringIO to capture output
#
# A StringIO object (or any other open file object for that matter) can be passed via the `dest` parameter. The value can then be extracted using `getvalue()`, or as generally for file using `seek(0)` and `read()`

out = StringIO()
O6.dump_curves(O.DC_CONSTR, dest=out)
outl = out.getvalue().splitlines()
len(outl), outl[0]

# ## CPCArbOptimizer

O = O6

out1 = StringIO()
O.dump_curves(O.DC_JSON, dest=out1)
r = out1.getvalue()
assert r.startswith('[{"k": 27518385.40998667, "x": 1272.2926367501436,')
#r

out1 = StringIO()
O.dump_curves(O.DC_DICTS, dest=out1)
r = out1.getvalue()
assert r.startswith("[{'k': 27518385.40998667, 'x': 1272.2926367501436,")
#r

out1 = StringIO()
O.dump_curves(O.DC_CONSTR, dest=out1)
rl = out1.getvalue().splitlines()
assert len(rl) == len(O.curves)
assert rl[0].startswith("ConstantProductCurve(k=27518385")

rl[0]

# ## MargPOptimizer

pass

# ## CPC

pass


