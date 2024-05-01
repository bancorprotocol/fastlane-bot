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
    from fastlane_bot.tools.cpc import ConstantProductCurve as CPC, CPCContainer, T, CPCInverter, Pair
    from fastlane_bot.tools.optimizer import F, MargPOptimizer
    import fastlane_bot.tools.invariants.functions as f
    from fastlane_bot.testing import *

except:
    from tools.cpc import ConstantProductCurve as CPC, CPCContainer, T, CPCInverter, Pair
    from tools.optimizer import MargPOptimizer
    import tools.invariants.functions as f
    from tools.testing import *

print("{0.__name__} v{0.__VERSION__} ({0.__DATE__})".format(CPC))
print("{0.__name__} v{0.__VERSION__} ({0.__DATE__})".format(MargPOptimizer))

#plt.style.use('seaborn-dark')
plt.rcParams['figure.figsize'] = [12,6]
# from fastlane_bot import __VERSION__
# require("3.0", __VERSION__)
# -

# # CPC-Only incl new curves [NBTest069]
#
# Note: the core CPC tests are in NBTest 002

CURVES = {
    "s1": CPC.from_solidly(x=10, y=10),
    "s2": CPC.from_solidly(x=10, y=10, price_spread=1e-6),
    "s1a": CPC.from_solidly(x=100, y=100),
    "s2a": CPC.from_solidly(x=100, y=100, price_spread=1e-6),
    "s3": CPC.from_solidly(x=1000, y=2000),   
    "s4": CPC.from_solidly(x=1, y=2000), 
}

# ## Solidly tests

help(CPC.from_solidly)

# +
#CPC.from_solidly(k=1, x=1)

# +
#CPC.from_solidly(k=1, x=1, y=1)
assert raises(CPC.from_solidly, k=1, x=1, y=1).startswith("exactly 2 out of k,x,y")
assert raises(CPC.from_solidly, k=1).startswith("exactly 2 out of k,x,y")
assert raises(CPC.from_solidly, x=1).startswith("exactly 2 out of k,x,y")
assert raises(CPC.from_solidly, y=1).startswith("exactly 2 out of k,x,y")
assert raises(CPC.from_solidly).startswith("exactly 2 out of k,x,y")

assert raises(CPC.from_solidly, k=1, x=1) == 'providing k, x not implemented yet'
assert raises(CPC.from_solidly, k=1, y=1) == 'providing k, y not implemented yet'
# -

assert len(CPC.from_solidly(x=1, y=2000)) == 0
assert raises(CPC.from_solidly,x=1, y=2000, as_list=False).startswith('x=1 is outside the range')

# ### Curve s1 (x=10, y=10) and s2 (ditto, but spread = 1e-6)

crv_l = CURVES["s1"] # CPC.from_solidly(x=10, y=10)
crv = crv_l[0]
cp = crv.params
fn = f.Solidly(k=cp.s_k)
assert crv.constr == "solidly"
assert cp.s_x == 10
assert cp.s_y == 10
assert cp.s_k == 20000
assert cp.s_k == cp.s_x**3 * cp.s_y + cp.s_y**3 * cp.s_x
assert cp.s_kbar == 10
assert iseq(cp.s_kbar, (cp.s_k/2)**0.25)
assert iseq(cp.s_kbar, 10)
assert iseq(cp.s_xmin, 50/9)
assert iseq(cp.s_xmax, 130/9)
assert cp.s_price_spread == CPC.SOLIDLY_PRICE_SPREAD
assert cp.s_price_spread == 0.06
assert iseq(cp.s_cpck/((cp.s_cpcx0)**2)-1, cp.s_price_spread)  # cpck / cpcx^2 = p; p0 = 1
assert iseq(1-cp.s_cpck/((cp.s_cpcx0+cp.s_xmax-cp.s_xmin)**2), 1-1/(1+cp.s_price_spread))
assert iseq(crv.x_act, 40/9)
assert iseq(crv.y_act, 40/9)
assert iseq(crv.y_act, crv.x_act)

crv_l = CURVES["s2"] # CPC.from_solidly(x=10, y=10)
crv = crv_l[0]
cp = crv.params
fn = f.Solidly(k=cp.s_k)
assert crv.constr == "solidly"
assert cp.s_x == 10
assert cp.s_y == 10
assert cp.s_k == 20000
assert cp.s_k == cp.s_x**3 * cp.s_y + cp.s_y**3 * cp.s_x
assert cp.s_kbar == 10
assert iseq(cp.s_kbar, (cp.s_k/2)**0.25)
assert iseq(cp.s_kbar, 10)
assert iseq(cp.s_xmin, 50/9)
assert iseq(cp.s_xmax, 130/9)
#assert cp.s_price_spread == CPC.SOLIDLY_PRICE_SPREAD
assert cp.s_price_spread == 1e-6
assert iseq(cp.s_cpck/((cp.s_cpcx0)**2)-1, cp.s_price_spread)  # cpck / cpcx^2 = p; p0 = 1
assert iseq(1-cp.s_cpck/((cp.s_cpcx0+cp.s_xmax-cp.s_xmin)**2), 1-1/(1+cp.s_price_spread))
assert iseq(crv.x_act, 40/9)
assert iseq(crv.y_act, 40/9)
assert iseq(crv.y_act, crv.x_act)

# ### Curve s1a (x=100, y=100) and s2a (ditto, but spread = 1e-6)

crv_l = CURVES["s1a"] # CPC.from_solidly(x=100, y=100)
crv = crv_l[0]
cp = crv.params
fn = f.Solidly(k=cp.s_k)
assert crv.constr == "solidly"
assert cp.s_x == 100
assert cp.s_y == 100
assert cp.s_k == 200000000
assert cp.s_k == cp.s_x**3 * cp.s_y + cp.s_y**3 * cp.s_x
assert cp.s_kbar == 100
assert iseq(cp.s_kbar, (cp.s_k/2)**0.25)
assert iseq(cp.s_kbar, 100)
assert iseq(cp.s_xmin, 500/9)
assert iseq(cp.s_xmax, 1300/9)
assert cp.s_price_spread == CPC.SOLIDLY_PRICE_SPREAD
assert cp.s_price_spread == 0.06
assert iseq(cp.s_cpck/((cp.s_cpcx0)**2)-1, cp.s_price_spread)  # cpck / cpcx^2 = p; p0 = 1
assert iseq(1-cp.s_cpck/((cp.s_cpcx0+cp.s_xmax-cp.s_xmin)**2), 1-1/(1+cp.s_price_spread))
assert iseq(crv.x_act, 400/9)
assert iseq(crv.y_act, 400/9)
assert iseq(crv.y_act, crv.x_act)


crv_l = CURVES["s2a"] # CPC.from_solidly(x=100, y=100, price_spread=1e-6)
crv = crv_l[0]
cp = crv.params
fn = f.Solidly(k=cp.s_k)
assert crv.constr == "solidly"
assert cp.s_x == 100
assert cp.s_y == 100
assert cp.s_k == 200000000
assert cp.s_k == cp.s_x**3 * cp.s_y + cp.s_y**3 * cp.s_x
assert cp.s_kbar == 100
assert iseq(cp.s_kbar, (cp.s_k/2)**0.25)
assert iseq(cp.s_kbar, 100)
assert iseq(cp.s_xmin, 500/9)
assert iseq(cp.s_xmax, 1300/9)
#assert cp.s_price_spread == CPC.SOLIDLY_PRICE_SPREAD
assert cp.s_price_spread == 1e-6
assert iseq(cp.s_cpck/((cp.s_cpcx0)**2)-1, cp.s_price_spread)  # cpck / cpcx^2 = p; p0 = 1
assert iseq(1-cp.s_cpck/((cp.s_cpcx0+cp.s_xmax-cp.s_xmin)**2), 1-1/(1+cp.s_price_spread))
assert iseq(crv.x_act, 400/9)
assert iseq(crv.y_act, 400/9)
assert iseq(crv.y_act, crv.x_act)

# ### Curve s3 (off centre)

crv

crv_l = CURVES["s3"] # CPC.from_solidly(x=100, y=100)
crv = crv_l[0]
cp = crv.params
fn = f.Solidly(k=cp.s_k)
assert crv.constr == "solidly"
assert cp.s_x == 1000
assert cp.s_y == 2000
assert cp.s_k == 10000000000000
assert cp.s_k == cp.s_x**3 * cp.s_y + cp.s_y**3 * cp.s_x
#assert cp.s_kbar == 100
assert iseq(cp.s_kbar, (cp.s_k/2)**0.25)
assert iseq(cp.s_kbar, 1495.3487812212206)
assert iseq(cp.s_xmin, 830.7493229006781)
assert iseq(cp.s_xmax, 2159.948239541763)
assert cp.s_price_spread == CPC.SOLIDLY_PRICE_SPREAD
assert cp.s_price_spread == 0.06
assert iseq(cp.s_cpck/((cp.s_cpcx0)**2)-1, cp.s_price_spread)  # cpck / cpcx^2 = p; p0 = 1
assert iseq(1-cp.s_cpck/((cp.s_cpcx0+cp.s_xmax-cp.s_xmin)**2), 1-1/(1+cp.s_price_spread))
assert iseq(crv.x_act, 169.25067709932193)
assert iseq(crv.y_act, 1159.948239541763)

# ### Curve 4 (out of range)

crv_l = CURVES["s4"] # CPC.from_solidly(x=100, y=100)
assert len(crv_l) == 0

# ## Solidly plots [NOTEST]

# ### Curves 1 and 2

# +
crv  = CURVES["s1"][0] # CPC.from_solidly(x=10, y=10)
# cp   = crv.params
crv2 = CURVES["s2"][0] # CPC.from_solidly(x=10, y=10, price_spread=XXX)
fn = f.Solidly(k=cp.s_k)
x0 = cp.s_x
LIM = cp.s_kbar

xv = np.linspace(-LIM+0.001, 1.1*LIM, 100)
plt.figure(figsize=(6,6))
crv.plot(xvals=xv, color="red", label="cpc curve")
yv = [fn(xx+x0) - fn(x0) for xx in xv]
plt.plot(xv, yv, color="#aaa", linestyle="--", label="full curve")
plt.legend()
plt.xlim(-LIM, LIM)
plt.ylim(-LIM, LIM)
plt.savefig("/Users/skl/Desktop/img1.jpg")
plt.show()

for crv_ in [crv, crv2]:
    crv_.plot(xvals=xv, label=f"cpc curve (spread={crv_.params.s_price_spread})")
yv = [fn(xx+x0) - fn(x0) for xx in xv]
plt.plot(xv, yv, color="#aaa", linestyle="--", label="full curve")
plt.legend()
plt.xlim(-.6*LIM, .6*LIM)
plt.ylim(-.6*LIM, .6*LIM)
plt.savefig("/Users/skl/Desktop/img2.jpg")
plt.show()

for crv_ in [crv, crv2]:
    crv_.plot(xvals=xv, label=f"cpc curve (spread={crv_.params.s_price_spread})")
yv = [fn(xx+x0) - fn(x0) for xx in xv]
plt.plot(xv, yv, color="#aaa", linestyle="--", label="full curve")
plt.legend()
plt.xlim(-.45*LIM, -.2*LIM)
plt.ylim(.25*LIM, .5*LIM)
plt.savefig("/Users/skl/Desktop/img3.jpg")
plt.show()
# -

# ### Curves 1a and 2a

# +
crv  = CURVES["s1a"][0] # CPC.from_solidly(x=10, y=10)
# cp   = crv.params
crv2 = CURVES["s2a"][0] # CPC.from_solidly(x=10, y=10, price_spread=XXX)
fn = f.Solidly(k=cp.s_k)
x0 = cp.s_x
LIM = cp.s_kbar

xv = np.linspace(-LIM+0.001, 1.1*LIM, 100)
plt.figure(figsize=(6,6))
crv.plot(xvals=xv, color="red", label="cpc curve")
yv = [fn(xx+x0) - fn(x0) for xx in xv]
plt.plot(xv, yv, color="#aaa", linestyle="--", label="full curve")
plt.legend()
plt.xlim(-LIM, LIM)
plt.ylim(-LIM, LIM)
plt.savefig("/Users/skl/Desktop/img1.jpg")
plt.show()

for crv_ in [crv, crv2]:
    crv_.plot(xvals=xv, label=f"cpc curve (spread={crv_.params.s_price_spread})")
yv = [fn(xx+x0) - fn(x0) for xx in xv]
plt.plot(xv, yv, color="#aaa", linestyle="--", label="full curve")
plt.legend()
plt.xlim(-.6*LIM, .6*LIM)
plt.ylim(-.6*LIM, .6*LIM)
plt.savefig("/Users/skl/Desktop/img2.jpg")
plt.show()

for crv_ in [crv, crv2]:
    crv_.plot(xvals=xv, label=f"cpc curve (spread={crv_.params.s_price_spread})")
yv = [fn(xx+x0) - fn(x0) for xx in xv]
plt.plot(xv, yv, color="#aaa", linestyle="--", label="full curve")
plt.legend()
plt.xlim(-.45*LIM, -.2*LIM)
plt.ylim(.25*LIM, .5*LIM)
plt.savefig("/Users/skl/Desktop/img3.jpg")
plt.show()

# -
# ### Curve 3

# +
crv  = CURVES["s3"][0] # CPC.from_solidly(x=1000, y=2000)
# cp   = crv.params
# crv2 = CURVES["s2a"][0] # CPC.from_solidly(x=10, y=10, price_spread=XXX)
fn = f.Solidly(k=cp.s_k)
x0 = cp.s_x

xv = np.linspace(-1000+0.001, 2000, 100)
plt.figure(figsize=(6,6))
crv.plot(xvals=xv, color="red", label="cpc curve")
yv = [fn(xx+x0) - fn(x0) for xx in xv]
plt.plot(xv, yv, color="#aaa", linestyle="--", label="full curve")
plt.legend()
plt.xlim(-1000, 2000)
plt.ylim(-2000, 1000)
plt.savefig("/Users/skl/Desktop/img1.jpg")
plt.show()

for crv_ in [crv]:
    crv_.plot(xvals=xv, label=f"cpc curve (spread={crv_.params.s_price_spread})")
yv = [fn(xx+x0) - fn(x0) for xx in xv]
plt.plot(xv, yv, color="#aaa", linestyle="--", label="full curve")
plt.legend()
plt.xlim(-500, 1500)
plt.ylim(-1500,500)
plt.savefig("/Users/skl/Desktop/img2.jpg")
plt.show()

for crv_ in [crv]:
    crv_.plot(xvals=xv, label=f"cpc curve (spread={crv_.params.s_price_spread})")
yv = [fn(xx+x0) - fn(x0) for xx in xv]
plt.plot(xv, yv, color="#aaa", linestyle="--", label="full curve")
plt.legend()
plt.xlim(-200, 0)
plt.ylim(0,200)
plt.savefig("/Users/skl/Desktop/img3.jpg")
plt.show()

# -

# ## Optimizer [NOTEST]

# We start with three curves: two "USD/ETH" at 2000 and 2100 respectively but that unfortunately use different USD references (USDC and USDT) and one Solidly stable swap with USDC/USDT

CC = CPCContainer()
CC += [CPC.from_pk(pair="WETH/USDC", cid="buyeth",  p=2000, k=2000)]
CC += [CPC.from_pk(pair="WETH/USDT", cid="selleth", p=2100, k=2100)]
CC += [CPC.from_solidly(pair="USDC/USDT", x=10000, y=10000, cid="solidly")]
O = MargPOptimizer(CC)
CC.plot()

# We run the optimizer

r = O.optimize("USDC", params=dict(verbose=True))
rd = r.asdict
r

# And we look at the curves again

CC1 = r.curves_new
CC1.plot()

# ## Optimizer

CC = CPCContainer()
CC += [CPC.from_pk(pair="WETH/USDC", cid="buyeth",  p=2000, k=2000)]
CC += [CPC.from_pk(pair="WETH/USDT", cid="selleth", p=2100, k=2100)]
CC += [CPC.from_solidly(pair="USDC/USDT", x=10000, y=10000, cid="solidly")]
O = MargPOptimizer(CC)
#CC.plot()

r = O.optimize("USDC", params=dict(verbose=False))
rd = r.asdict()
r

assert iseq(r.p_optimal["WETH"], 2050.22767783421, eps=1e-3)
assert iseq(r.p_optimal["USDT"], 1, eps=1e-3)
assert r.p_optimal["USDC"] == 1
r.p_optimal

df = r.trade_instructions(ti_format=r.TIF_DF).fillna(0)
assert iseq(0, sum(df["USDT"]))
assert iseq(0, sum(df["WETH"]))
assert sum(df["USDC"]) < 0
assert sum(df["USDC"]) == r.result
assert iseq(r.result, -0.6271972654014917)
df

CC1 = r.curves_new
c0,c1,c2 = [*CC1]
c0.cid, c0.pair, c0.p

c1.cid, c1.pair, c1.p

c0.p/c1.p*c2.p

1-c2.p

(c0.p/c1.p-1) / (1-c2.p)

assert iseq(c0.p/c1.p-1, 1-c2.p, eps=1e-3)  # price ratio of ETH curves equals USDC/USDT price
assert iseq(c0.p/c1.p*c2.p, 1)              # circular exchange is unity


