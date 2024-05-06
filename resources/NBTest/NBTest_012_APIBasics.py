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
    from tools import CurveBase, ConstantProductCurve as CPC, CurveContainer
    from tools import MargPOptimizer
    from tools.testing import *

except:
    from fastlane_bot.tools.curves import CurveBase, ConstantProductCurve as CPC, CurveContainer
    from fastlane_bot.tools.optimizer import MargPOptimizer
    from fastlane_bot.testing import *

ConstantProductCurve = CPC

#from io import StringIO
import types
import math as m

print("{0.__name__} v{0.__VERSION__} ({0.__DATE__})".format(CurveBase))
print("{0.__name__} v{0.__VERSION__} ({0.__DATE__})".format(CPC))
print("{0.__name__} v{0.__VERSION__} ({0.__DATE__})".format(CurveContainer))
print("{0.__name__} v{0.__VERSION__} ({0.__DATE__})".format(MargPOptimizer))

#plt.style.use('seaborn-dark')
#plt.rcParams['figure.figsize'] = [12,6]
# from fastlane_bot import __VERSION__
# require("3.0", __VERSION__)
# -

# # API Basics [NBTest012, ex 102]
#
# This notebook describes API features of the Optimizer library. Everything contained in this notebook's tests here should be considered stable, and breaking changes will only ever happen a major version number increases

# ## CurveBase ConstantProductCurve CPC CurveContainer
#
# The `CurveBase` object is the base class of all curve objects fed into the optimizer. Currently only the `ConstantProductCurve` object -- typically imported as `CPC` -- is providing an actual implementation for that class, and it can only describe (or approximate) constant product curves.

# ### CurveBase

# assert that certain functions exist on `CurveBase`

assert isinstance(CurveBase.dxvecfrompvec_f, types.FunctionType)
assert isinstance(CurveBase.xvecfrompvec_f, types.FunctionType)
assert isinstance(CurveBase.invariant, types.FunctionType)

# assert that CurveBase cannot be instantiated with one of the functions missing

assert raises(CurveBase)


class Curve(CurveBase):
    def dxvecfrompvec_f(self, pvec, *, ignorebounds=False):
        ...
    def xvecfrompvec_f(self, pvec, *, ignorebounds=False):
        ...
    # def invariant(self, include_target=False):  
    #     ...
assert raises(Curve)


class Curve(CurveBase):
    def dxvecfrompvec_f(self, pvec, *, ignorebounds=False):
        ...
    # def xvecfrompvec_f(self, pvec, *, ignorebounds=False):
    #     ...
    def invariant(self, include_target=False):  
        ...
assert raises(Curve)


class Curve(CurveBase):
    # def dxvecfrompvec_f(self, pvec, *, ignorebounds=False):
    #     ...
    def xvecfrompvec_f(self, pvec, *, ignorebounds=False):
        ...
    def invariant(self, include_target=False):  
        ...
assert raises(Curve)

# ### ConstantProductCurve

p = dict(foo=1, bar=2, baz=3)
kwargs = dict(pair="TKNB/TKNQ", cid="c_cid", descr="des", fee=0.005, params=p)

# #### unlevered generic constructors

# the `from_pk` constructor takes a price `p` and a constant `k`

c = CPC.from_pk(10, 10*1*25**2, **kwargs)
assert raises(CPC.from_pk, 10, 10*1*10**2, 10)
assert iseq(c.p, 10)
assert iseq(c.x, 25)
assert iseq(c.x, c.x_act)
assert iseq(c.y, 250)
assert iseq(c.y, c.y_act)
assert iseq(c.k, 6250)
assert c.pair == "TKNB/TKNQ"
assert c.cid == "c_cid"
assert c.descr == "des"
assert c.fee == 0.005
assert c.params == p

raises(CPC.from_pk, 10, 10*1*10**2, 10)

c1 = CPC.from_kx(c.k, c.x, **kwargs)
assert CPC.from_kx(k=c.k, x=c.x, **kwargs) == c1
assert raises(CPC.from_kx, 10, 10*1*10**2, 10)
assert iseq(c1.p, c.p)
assert iseq(c1.x, c.x)
assert iseq(c1.x_act, c.x_act)
assert iseq(c1.y, c.y)
assert iseq(c1.y_act, c.y_act)
assert iseq(c1.k, c.k)
assert c1.pair == c1.pair
assert c1.cid == c1.cid
assert c1.descr == c1.descr
assert c.fee == c1.fee
assert c1.params == c1.params

c1 = CPC.from_ky(c.k, c.y, **kwargs)
assert CPC.from_ky(k=c.k, y=c.y, **kwargs) == c1
assert raises(CPC.from_ky, 10, 10*1*10**2, 10)
assert iseq(c1.p, c.p)
assert iseq(c1.x, c.x)
assert iseq(c1.x_act, c.x_act)
assert iseq(c1.y, c.y)
assert iseq(c1.y_act, c.y_act)
assert iseq(c1.k, c.k)
assert c1.pair == c1.pair
assert c1.cid == c1.cid
assert c1.descr == c1.descr
assert c.fee == c1.fee
assert c1.params == c1.params

c1 = CPC.from_xy(c.x, c.y, **kwargs)
assert CPC.from_xy(x=c.x, y=c.y, **kwargs) == c1
assert raises(CPC.from_xy, 10, 10*1*10**2, 10)
assert iseq(c1.p, c.p)
assert iseq(c1.x, c.x)
assert iseq(c1.x_act, c.x_act)
assert iseq(c1.y, c.y)
assert iseq(c1.y_act, c.y_act)
assert iseq(c1.k, c.k)
assert c1.pair == c1.pair
assert c1.cid == c1.cid
assert c1.descr == c1.descr
assert c.fee == c1.fee
assert c1.params == c1.params

# #### levered generic constructors

c = CPC.from_pkpp(10, 10*1*25**2, 8, 12, **kwargs)
assert raises(CPC.from_pkpp, 10, 10*1*10**2, 8, 12, 10)
assert iseq(c.p, 10)
assert iseq(c.p_min, 8)
assert iseq(c.p_max, 12)
assert iseq(c.x, 25)
assert iseq(c.x_act, 2.1782267706180782)
assert iseq(c.y, 250)
assert iseq(c.y_act, 26.393202250021034)
assert iseq(c.k, 6250)
assert c.pair == "TKNB/TKNQ"
assert c.cid == "c_cid"
assert c.descr == "des"
assert c.fee == c1.fee
assert c.params == p

c1 = CPC.from_kx(c.k, c.x, x_act=c.x_act, y_act = c.y_act, **kwargs)
assert iseq(c1.p, c.p)
assert iseq(c1.x, c.x)
assert iseq(c1.x_act, c.x_act)
assert iseq(c1.y, c.y)
assert iseq(c1.y_act, c.y_act)
assert iseq(c1.k, c.k)

c1 = CPC.from_ky(c.k, c.y, x_act=c.x_act, y_act = c.y_act, **kwargs)
assert iseq(c1.p, c.p)
assert iseq(c1.x, c.x)
assert iseq(c1.x_act, c.x_act)
assert iseq(c1.y, c.y)
assert iseq(c1.y_act, c.y_act)
assert iseq(c1.k, c.k)

c1 = CPC.from_xy(c.x, c.y, x_act=c.x_act, y_act = c.y_act, **kwargs)
assert iseq(c1.p, c.p)
assert iseq(c1.x, c.x)
assert iseq(c1.x_act, c.x_act)
assert iseq(c1.y, c.y)
assert iseq(c1.y_act, c.y_act)
assert iseq(c1.k, c.k)

# #### Carbon constructor
#
# note: the Carbon constructor takes _only_ keyword arguments

assert raises(CPC.from_carbon, 1)

pa, pb = 12, 8    # USDC per LINK
yint = y = 25     # LINK

# with prices, `tkny` is the quote token (USDC)
#
# _note: isdydx does not matter because dy per dx is same as tknq per tknb_

c  = CPC.from_carbon(pair="LINK/USDC", tkny="USDC", yint=yint, y=y, pa=pa, pb=pb, isdydx=False)
c2 = CPC.from_carbon(pair="LINK/USDC", tkny="USDC", yint=yint, y=y, pa=pa, pb=pb, isdydx=True)
assert c.pair == "LINK/USDC"
assert c2 == c
assert iseq(c.p_max, pa)
assert iseq(c.p_min, pb)
assert iseq(c.p, c.p_max)
assert iseq(c.x_act, 0)
assert iseq(c.y_act, yint)
assert iseq(c.x, 11.353103630798294)
assert iseq(c.y, 136.23724356957953)
assert iseq(c.y/c.x, pa)

dx, dy, p_ = c.dxdyfromp_f(p=c.p_min)
dxvec = c.dxvecfrompvec_f(pvec=dict(LINK=p_, USDC=1))
assert iseq(dx, yint/m.sqrt(pa*pb))
assert iseq(dy, -yint)
assert iseq(p_, c.p_min)
assert iseq(dxvec["USDC"], dy)
assert iseq(dxvec["LINK"], dx)

# same, but with A,B (A = sqrt(pa)-sqrt(pb), B = sqrt(pb), pa > pb in dy/dx)

A = m.sqrt(pa)-m.sqrt(pb)
B = m.sqrt(pb)
c1 = CPC.from_carbon(pair="LINK/USDC", tkny="LINK", yint=yint, y=y, A=A, B=B)
assert iseq(c1.p_max, c.p_max)
assert iseq(c1.p_min, c.p_min)
assert iseq(c1.p, c.p)

# with prices, `tkny` is the base token (LINK)

pa_ = 1/pb
pb_ = 1/pa
yint_ = y_ = yint / pa_
pa_, pb_, yint_

c  = CPC.from_carbon(pair="LINK/USDC", tkny="LINK", yint=yint_, y=y_, pa=pa_, pb=pb_, isdydx=True)
c2 = CPC.from_carbon(pair="LINK/USDC", tkny="LINK", yint=yint_, y=y_, pa=pb,  pb=pa,  isdydx=False)
assert c.pair  == "USDC/LINK"
assert c2.pair == c.pair 
assert iseq(c.p_max, pa_)
assert iseq(c2.p_max, c.p_max)
assert iseq(c.p_min, pb_)
assert iseq(c2.p_min, c.p_min)
assert iseq(c.p, c.p_max)
assert iseq(c2.p, c2.p_max)
assert iseq(c.x_act, 0)
assert iseq(c2.x_act, c.x_act)
assert iseq(c.y_act, yint_)
assert iseq(c2.y_act, c.y_act)
assert iseq(c.x, 8719.18358845308)
assert iseq(c2.x, c.x)
assert iseq(c.y, 1089.897948556635)
assert iseq(c2.y, c.y)
assert iseq(c.y/c.x, pa_)
assert iseq(c2.y/c2.x, pa_)

# #### Uniswap v2 constructor

kwargs = dict(pair="LINK/USDC", descr="des", cid="cid", fee=0.005, params=p)

c = CPC.from_univ2(liq_tknb=10, liq_tknq=20, **kwargs)
assert iseq(c.x, 10)
assert iseq(c.y, 20)
assert iseq(c.k, c.x*c.y)
assert c.pair == kwargs["pair"]
assert c.descr == kwargs["descr"]
assert c.cid == kwargs["cid"]
assert c.fee == kwargs["fee"]
assert c.params == kwargs["params"]

c1 = CPC.from_univ2(liq_tknb=c.x, k=c.k, **kwargs)
assert iseq(c1.x, c.x)
assert iseq(c1.y, c.y)
assert iseq(c1.k, c.k)

c2 = CPC.from_univ2(liq_tknq=c.y, k=c.k, **kwargs)
assert iseq(c2.x, c.x)
assert iseq(c2.y, c.y)
assert iseq(c2.k, c.k)

# #### Uniswap v3 constructor

# +
# TODO
# -

# ### CurveContainer
#
# A `CurveContainer` (legacy name: `CPCContainer`) is a container object for curve objects (`CurveBase` derivatives)

# +
# TODO
# -

# ## MargPOptimizer

CC = CurveContainer([
    CPC.from_pk(pair="LINK/USDC", p=10, k = 10*250_000**2, cid="c10"),
    CPC.from_pk(pair="LINK/USDC", p=12, k = 10*250_000**2, cid="c12"),
])
pstart = dict(LINK=10.3, USDC=1)

# ### Running the optimizer

O = MargPOptimizer(CC)
r = O.optimize("USDC")
assert not r.is_error
assert r.errormsg is None
assert iseq(r.result, -10868.538042440545)
assert iseq(r.p_optimal_t[0], 10.931723975214778)
assert r.method == 'margp'
assert r.targettkn == "USDC"
assert r.time > 0
r

# #### pstart

# pstart must be a kwarg if provided

assert raises(O.optimize, "USDC", pstart)
assert not raises(O.optimize, "USDC")
assert not raises(O.optimize, "USDC", pstart=pstart)
raises(O.optimize, "USDC", pstart)

r1 = O.optimize("USDC", pstart=pstart)
assert iseq(r.result, r1.result, eps=1e-3)
assert iseq(r.p_optimal_t[0], r1.p_optimal_t[0], eps=1e-3)
r1

assert raises(O.optimize, "USDC", pstart=pstart, params=dict(pstart=pstart))
raises(O.optimize, "USDC", pstart=pstart, params=dict(pstart=pstart))

# ### Trade instructions

O = MargPOptimizer(CC)
r = O.optimize("USDC")
assert len(r.trade_instructions()) == 2
assert r.trade_instructions() == r.trade_instructions(O.TIF_OBJECTS) 

ti = r.trade_instructions(O.TIF_OBJECTS)
assert len(ti) == 2
assert isinstance(ti[0], O.TradeInstruction)
assert set(tin.cid for tin in ti) == {"c10", "c12"}
assert set(tin.tknin for tin in ti) == {"USDC", "LINK"}
assert set(tin.tknout for tin in ti) == {"USDC", "LINK"}
ti

ti0 = [tin for tin in ti if tin.cid=="c10"][0]
assert ti0.cid == "c10"
assert ti0.tknin == "USDC"
assert iseq(ti0.amtin, 113872.12474169489)
assert ti0.tknout == "LINK"
assert iseq(ti0.amtout, -10891.133853090403)
assert ti0.error is None
ti0

ti = r.trade_instructions(O.TIF_DFRAW)
assert len(ti) == 2
assert set(ti.index) == {'c10', 'c12'}
assert set(ti.pair) == {'LINK/USDC'}
assert set(ti.pairp) == {'LINK/USDC'}
assert set(ti.tknin) == {'LINK', 'USDC'}
assert set(ti.tknout) == {'LINK', 'USDC'}
ti

ti0 = ti.loc["c10"]
assert ti0["pair"] == "LINK/USDC"
assert ti0["pairp"] == "LINK/USDC"
assert ti0["tknin"] == "USDC"
assert iseq(ti0["USDC"], 113872.124742)
assert ti0["tknout"] == "LINK"
assert iseq(ti0["LINK"], -10891.133853)
ti0

r.trade_instructions(O.TIF_DF8)

r.trade_instructions(O.TIF_DFAGGR)

r.trade_instructions(O.TIF_DFPG)

1
