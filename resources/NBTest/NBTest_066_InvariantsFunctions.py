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
    import fastlane_bot.tools.invariants.functions as f
    from fastlane_bot.tools.invariants.kernel import Kernel
    from fastlane_bot.testing import *

except:
    import tools.invariants.functions as f
    from tools.invariants.kernel import Kernel
    from testing import *

import numpy as np
import math as m
import matplotlib.pyplot as plt

plt.rcParams['figure.figsize'] = [12,6]

print("{0.__name__} v{0.__VERSION__} ({0.__DATE__})".format(f.Function))
print("{0.__name__} v{0.__VERSION__} ({0.__DATE__})".format(Kernel))
# -

# # Functions (Invariants Module; NBTest066)

# ## Functions

# ### Built in functions
# #### QuadraticFunction

qf = f.QuadraticFunction(a=1, b=0, c=-10)
assert qf.params() == {'a': 1, 'b': 0, 'c': -10}
assert qf.a == 1
assert qf.b == 0
assert qf.c == -10

qf2 = qf.update(c=-5)
assert raises(qf.update, k=1)
assert qf2.params() == {'a': 1, 'b': 0, 'c': -5}

x_v = np.linspace(-5,5)
y1_v = [qf(xx) for xx in x_v]
y2_v = [qf2(xx) for xx in x_v]
plt.plot(x_v, y1_v, label="qf")
plt.plot(x_v, y2_v, label="qf2")
plt.legend()
plt.grid()

x_v = np.linspace(-5,5)
y1_v = [qf(xx) for xx in x_v]
y2_v = [qf.p(xx) for xx in x_v]
y3_v = [qf.pp(xx) for xx in x_v]
plt.plot(x_v, y1_v, label="f")
plt.plot(x_v, y2_v, label="f'")
plt.plot(x_v, y3_v, label="f''")
plt.legend()
plt.grid()

# #### TrigFunction

# +
qf = f.TrigFunction()
assert qf.params() == {'amp': 1, 'omega': 1, 'phase': 0}
assert qf.amp == 1
assert qf.omega == 1
assert qf.phase == 0
assert int(qf.PI) == 3

qf2 = qf.update(phase=1.5*qf.PI)
assert qf2.params() == {'amp': 1, 'omega': 1, 'phase': 1.5*qf.PI}
# -

x_v = np.linspace(0, 4, 100)
y1_v = [qf(xx) for xx in x_v]
y2_v = [qf2(xx) for xx in x_v]
plt.plot(x_v, y1_v, label="qf")
plt.plot(x_v, y2_v, label="qf2")
plt.legend()
plt.grid()

# #### HyperbolaFunction

# +
qf = f.HyperbolaFunction()
assert qf.params() == {'k': 1, 'x0': 0, 'y0': 0}
assert qf.k == 1
assert qf.x0 == 0
assert qf.y0 == 0

qf2 = qf.update(y0=0.5)
# assert qf2.params() == {'amp': 1, 'omega': 1, 'phase': 1.5*qf.PI}
# -

x_v = np.linspace(1, 10, 100)
y1_v = np.array([qf(xx) for xx in x_v])
y2_v = np.array([qf2(xx) for xx in x_v])
assert iseq(min(y2_v-y1_v), 0.5)
assert iseq(max(y2_v-y1_v), 0.5)
plt.plot(x_v, y1_v, label="qf")
plt.plot(x_v, y2_v, label="qf2")
plt.legend()
plt.grid()

# ### Derivatives

qf = f.QuadraticFunction(a=1, b=2, c=3)
qfp = qf.p_func()
qfpp = qf.pp_func()
assert qf.params() == {'a': 1, 'b': 2, 'c': 3}
assert qfp.func is qf
assert qfpp.func is qf

x_v = np.linspace(-5,5)
y1_v = [qf(xx) for xx in x_v]
y2_v = [qfp(xx) for xx in x_v]
y3_v = [qfpp(xx) for xx in x_v]
plt.plot(x_v, y1_v, label="f")
plt.plot(x_v, y2_v, label="f'")
plt.plot(x_v, y3_v, label="f''")
plt.legend()
plt.grid()

y2a_v = [qf.p(xx) for xx in x_v]   # calculate the derivative from the original object
y3a_v = [qf.pp(xx) for xx in x_v]  # ditto second derivative
y3b_v = [qfp.p(xx) for xx in x_v]  # calculate the second derivative as derivative from the derivative object
assert y2a_v == y2_v        # those are literally two ways of getting the same result
assert y3a_v == y3_v        # ditto
assert iseq(min(y3_v), -2)  # check that the second derivative is correct
assert iseq(max(y3_v), -2)  # ditto
assert iseq(min(y3b_v), 2)  # ditto, but the other way
assert iseq(max(y3b_v), 2)  # ditto
min(y3_v), max(y3_v), min(y3b_v), max(y3b_v)


# ### Custom function

@f.dataclass(frozen=True)
class MyFunction(f.Function):
    k: float = 1
    
    def f(self, x):
        return (m.sqrt(1+x)-1)*self.k
mf = MyFunction()
mf2 = mf.update(k=2)
mf(1),mf.p(1),mf.pp(1)

x_v = np.linspace(0,10)
y1_v = [mf(xx) for xx in x_v]
y2_v = [mf2(xx) for xx in x_v]
plt.plot(x_v, y1_v, label="mf")
plt.plot(x_v, y2_v, label="nf2")
plt.legend()
plt.grid()

# ## Kernel

# ### Integration function

integrate = Kernel.integrate_trapezoid
ONE = lambda x: 1
LIN = lambda x: 2*x
SQR = lambda x: 3*x*x

assert iseq(integrate(ONE, 0, 1, 2), 1)    # trapezoid integrates constant perfectly
assert iseq(integrate(ONE, 0, 1, 100), 1)
assert iseq(integrate(LIN, 0, 1, 2), 1)    # ditto linear
assert iseq(integrate(LIN, 0, 1, 100), 1)
assert iseq(integrate(SQR, 0, 1, 100), 1, eps=1e-3)
assert iseq(integrate(SQR, 0, 1, 1000), 1, eps=1e-6)

# ### Default kernel

k = Kernel(steps=1000)
assert k.x_min == 0
assert k.x_max == 1
assert set(k.kernel(xx) for xx in np.linspace(k.x_min, k.x_max, 50)) == {1}
assert iseq(k.integrate(ONE), 1)
assert iseq(k.integrate(LIN), 1)
assert iseq(k.integrate(SQR), 1)
x_v = np.linspace(-0.5, 1.5, 1000)
plt.plot(x_v, [k.k(xx) for xx in x_v], label="default kernel")
plt.legend()
plt.grid()
plt.show()

# ### Flat kernels

k.integrate(ONE)

k = Kernel(x_max=2, kernel=lambda x: 0.5, steps=1000)
assert k.x_min == 0
assert k.x_max == 2
assert set(k.kernel(xx) for xx in np.linspace(k.x_min, k.x_max, 50)) == {0.5}
assert iseq(k.integrate(ONE), 1)
assert iseq(k.integrate(LIN), 2)
assert iseq(k.integrate(SQR), 4)
x_v = np.linspace(-0.5, 2.5, 1000)
plt.plot(x_v, [k.k(xx) for xx in x_v], label="flat kernel 0..2")
plt.legend()
plt.grid()
plt.show()

k = Kernel(x_max=4, kernel=lambda x: 0.25, steps=1000)
assert k.x_min == 0
assert k.x_max == 4
assert set(k.kernel(xx) for xx in np.linspace(k.x_min, k.x_max, 50)) == {0.25}
assert iseq(k.integrate(ONE), 1)
assert iseq(k.integrate(LIN), 4)
assert iseq(k.integrate(SQR), 16)
x_v = np.linspace(-0.5, 4.5, 1000)
plt.plot(x_v, [k.k(xx) for xx in x_v], label="flat kernel 0..4")
plt.legend()
plt.grid()
plt.show()

k.integrate(LIN), k.integrate(SQR)

# ### Triangle and sawtooth kernels

kf = Kernel(x_min=1, x_max=3, kernel=Kernel.FLAT, steps=1000)
kl = Kernel(x_min=1, x_max=3, kernel=Kernel.SAWTOOTHL, steps=1000)
kr = Kernel(x_min=1, x_max=3, kernel=Kernel.SAWTOOTHR, steps=1000)
kt = Kernel(x_min=1, x_max=3, kernel=Kernel.TRIANGLE, steps=1000)
x_v = np.linspace(0.5, 3.5, 1000)
plt.plot(x_v, [kf.k(xx) for xx in x_v], label="flat")
plt.plot(x_v, [kl.k(xx) for xx in x_v], label="sawtooth left")
plt.plot(x_v, [kr.k(xx) for xx in x_v], label="sawtooth right")
plt.plot(x_v, [kt.k(xx) for xx in x_v], label="triangle")
plt.legend()
plt.grid()
plt.show()

# +
assert iseq(kf.integrate(ONE), 1)
assert iseq(kl.integrate(ONE), 1)
assert iseq(kr.integrate(ONE), 1)
assert iseq(kt.integrate(ONE), 1)

assert iseq(kf.integrate(LIN), 4)
assert iseq(kl.integrate(LIN), 10/3)
assert iseq(kr.integrate(LIN), 14/3)
assert iseq(kt.integrate(LIN), 4)

assert iseq(kf.integrate(SQR), 13)
assert iseq(kl.integrate(SQR), 9)
assert iseq(kr.integrate(SQR), 17)
assert iseq(kt.integrate(SQR), 12.5)
# -

# ### Gaussian kernels

kf = Kernel(x_min=1, x_max=3, kernel=Kernel.FLAT, steps=1000)
kg = Kernel(x_min=1, x_max=3, kernel=Kernel.GAUSS, steps=1000)
kw = Kernel(x_min=1, x_max=3, kernel=Kernel.GAUSSW, steps=1000)
kn = Kernel(x_min=1, x_max=3, kernel=Kernel.GAUSSN, steps=1000)
x_v = np.linspace(0.5, 3.5, 1000)
plt.plot(x_v, [kf.k(xx) for xx in x_v], label="flat")
plt.plot(x_v, [kg.k(xx) for xx in x_v], label="gauss")
plt.plot(x_v, [kw.k(xx) for xx in x_v], label="gauss wide")
plt.plot(x_v, [kn.k(xx) for xx in x_v], label="gauss narrow")
plt.legend()
plt.grid()
plt.show()

assert iseq(kf.integrate(ONE), 1)
assert iseq(kg.integrate(ONE), 1, eps=1e-3)
assert iseq(kw.integrate(ONE), 1, eps=1e-3)
assert iseq(kn.integrate(ONE), 1, eps=1e-3)

# ## Function Vector

# ### vector operations and consistency

knl = Kernel(x_min=1, x_max=3, kernel=Kernel.FLAT, steps=1000)
f1 = f.QuadraticFunction(a=3, c=1)
f2 = f.QuadraticFunction(b=2)
f3 = f.QuadraticFunction(a=3, b=2, c=1)
f1v = f.FunctionVector({f1: 1}, kernel=knl)
f2v = f.FunctionVector({f2: 1}, kernel=knl)
fv = f.FunctionVector({f1: 1, f2: 1}, kernel=knl)
assert fv == f1v + f2v
x_v = np.linspace(1, 3, 100)
y1_v = [f1(xx) for xx in x_v]
y2_v = [f2(xx) for xx in x_v]
y3_v = [f3(xx) for xx in x_v]
yv_v = [fv(xx) for xx in x_v]
y_diff = np.array(yv_v) - np.array(y3_v)
plt.plot(x_v, y1_v, label="f1")
plt.plot(x_v, y2_v, label="f2")
plt.plot(x_v, y3_v, label="f3")
plt.legend()
plt.grid()

assert max(y_diff)<1e-10
assert min(y_diff)>-1e-10
plt.plot(x_v, yv_v, linewidth=3, label="vector")
plt.plot(x_v, y3_v, linestyle="--", color="#ccc", label="f3")
plt.legend()
plt.grid()
plt.show()
plt.plot(x_v, y_diff)
plt.grid()
max(y_diff), min(y_diff)

# check that you can't add vectors with different kernel

# +
f1v = f.FunctionVector({f1: 1}, kernel=knl)
f2v = f.FunctionVector({f2: 1}, kernel=knl)
assert not raises(lambda: f1v+f2v)
assert not raises(lambda: f1v-f2v)

f1v = f.FunctionVector({f1: 1}, kernel=knl)
f2v = f.FunctionVector({f2: 1}, kernel=None)
assert raises(lambda: f1v+f2v)
assert raises(lambda: f1v-f2v)
# -

# ### convenience methods
#

fv = f.FunctionVector(
    {
        f.QuadraticFunction(a=1, b=2): 1,
        f.HyperbolaFunction(k=100, x0=2): 1,
        f.TrigFunction(phase=0.5): 1,
    }, 
    kernel=knl
)

# #### params

assert isinstance(fv.params(as_dict=True), dict)
assert len(fv.params()) == len(fv)
fv.params(as_dict=True)

assert fv.params() == fv.params(as_dict=False)
assert not fv.params(as_dict=False) == fv.params(as_dict=True)
assert len(fv.params(as_dict=False)) == len(fv)
assert list(fv.params(as_dict=True).values()) == fv.params(as_dict=False)
assert fv.params(as_dict=False)[1] == {'k': 100, 'x0': 2, 'y0': 0, '_classname': 'HyperbolaFunction'}
assert fv.params(as_dict=False, classname=False)[2] == {'amp': 1, 'omega': 1, 'phase': 0.5}
fv.params(as_dict=False)

assert fv.params(index=2) == fv.params(2)
assert isinstance(fv.params(index=2, as_dict=True), dict)
assert isinstance(fv.params(index=2, as_dict=False), dict)
assert fv.params(index=2, as_dict=False) != fv.params(index=2, as_dict=True)
assert fv.params(index=2) == {'amp': 1, 'omega': 1, 'phase': 0.5, '_classname': 'TrigFunction'}
assert fv.params(index=2, classname=False) == {'amp': 1, 'omega': 1, 'phase': 0.5}
fv.params(index=2)

# #### update

assert raises(fv.update, [1,2,3]) == 'update with list of params not implemented yet'
assert raises(fv.update, [1,2,3], index=1) == 'index and key must be None if params is a list'
assert raises(fv.update, [1,2,3], 1) == 'index and key must be None if params is a list'
assert raises(fv.update, [1,2,3], key=1) == 'index and key must be None if params is a list'
assert raises(fv.update, dict()) == 'exactly one of index or key must be given'
assert raises(fv.update, dict(), index=1, key=1) == "can't give both index and key"
assert raises(fv.update, dict(), key=1) == "key not implemented yet"
params = fv.params()
fv.params()

fv_1 = fv.update(dict(c=3), 0)
params1 = fv_1.params()
assert params[0] != params1[0] 
assert params[1:] == params1[1:]
assert params1[0] == {'a': 1, 'b': 2, 'c': 3, '_classname': 'QuadraticFunction'}
assert params1[0]["c"] == 3
assert params1[0]["a"] == params[0]["a"]
assert params1[0]["b"] == params[0]["b"]
assert params1[0]["_classname"] == params[0]["_classname"]
params1

# ### integration and norms

# #### high level

f1,f2

f1v = f.FunctionVector({f1: 1}, kernel=knl)
f2v = f1v.wrap(f2)
f1v.plot(show=False, label="f1")
f2v.plot(show=False, label="f2")
fv=f1v+f2v
fv.plot(show=False, label="f1+f2")
plt.legend()
print(f1v.kernel)
plt.show()
assert f1v.kernel == f2v.kernel
assert f1v.kernel == fv.kernel

# +
assert iseq(f1v.integrate(), 13+1)
    # assert iseq(kf.integrate(ONE), 1)
    # assert iseq(kf.integrate(SQR), 13)

assert iseq(f2v.integrate(), 4)
    # assert iseq(kf.integrate(LIN), 4)

assert iseq(fv.integrate(), 18)
# -

f2v.integrate()

# #### quantification

kernel = f.Kernel(x_min=0, x_max=1)
qf_v = f.QuadraticFunction(c=1).wrap(kernel)
qf2_v = f.QuadraticFunction(c=2).wrap(kernel)
qfl_v = f.QuadraticFunction(b=1).wrap(kernel)
qfq_v = f.QuadraticFunction(a=1).wrap(kernel)
qfl1_v = qfl_v + qf_v
qflm_v = 2*qfl_v - qf_v
qf_v.plot(show=False)
qf2_v.plot(show=False)
qfl_v.plot(show=False)
qfq_v.plot(show=False)
qfl1_v.plot(show=False)
qflm_v.plot(show=False)
#plt.ylim(-1,None)

# +
# f(x) = 1 => Int = 1, Norm2 = 1
assert qf_v.integrate() == 1
assert qf_v.norm2() == 1
assert qf_v.norm1() == 1
assert qf_v.norm() == 1

# f(x) = 2 => Int = 2, Norm2 = 4
assert qf2_v.integrate() == 2
assert qf2_v.norm2() == 4
assert qf2_v.norm1() == 2
assert qf2_v.norm() == 2

# f(x) = x => Int = 1/2, Norm2 = 1/3
assert qfl_v.integrate() == 1/2
assert iseq(qfl_v.norm2(), qfq_v.integrate())
assert iseq(qfl_v.norm2(), 1/3, eps=1e-3)
assert iseq(qfl_v.norm1(), 1/2, eps=1e-3)
assert iseq(qfl_v.norm(), m.sqrt(qfl_v.norm2()))

# f(x) = x^2 => Int = 1/3, Norm2 = 1/5
assert iseq(qfq_v.integrate(), 1/3, eps=1e-3)
assert iseq(qfq_v.norm2(), 1/5, eps=1e-3)
assert iseq(qfq_v.norm1(), 1/3, eps=1e-3)
assert iseq(qfq_v.norm(), m.sqrt(qfq_v.norm2()))

# f(x) = 1 + x ==> Int = 1.5, Norm2 = 2 1/3
assert iseq(qfl1_v.integrate(), 1.5)
assert iseq(qfl1_v.integrate(), qfl_v.integrate() + qf_v.integrate())
assert iseq(qfl1_v.norm2(), 2+1/3, eps=1e-3)
    # (1+x)^2 = x^2 + 2x + 1 => 1/3 x^3 + x^2 + x = 2 1/3 
assert iseq(qfl1_v.norm1(), 1.5, eps=1e-3)
assert iseq(qfl1_v.norm(), m.sqrt(qfl1_v.norm2()))

# f(x) = 1 - 2x => Int = 0, Norm1 = 1/2, Norm2 = 1/3
assert iseq(0, qflm_v.integrate(), eps=1e-3)
assert iseq(qflm_v.norm2(), 1/3, eps=1e-3)
    # x - 2/3 x^3 = 1/3
assert iseq(qflm_v.norm1(), 1/2, eps=1e-3)
assert iseq(qflm_v.norm(), m.sqrt(qflm_v.norm2()))
# -

# ### goal seek and minimize

f1 = f.QuadraticFunction(a=1, c=-4)
f1v = f.FunctionVector().wrap(f1)
x_v = np.linspace(-2.5, 2.5, 100)
y1_v = [f1(xx) for xx in x_v]
plt.plot(x_v, y1_v, label="f")
#plt.legend()
plt.grid()

assert iseq(f1v.goalseek(target=0, x0=1), 2)
assert iseq(f1v.goalseek(target=0, x0=-1), -2)
assert iseq(f1v.goalseek(target=-3, x0=1), 1)
assert iseq(f1v.goalseek(target=-3, x0=-1), -1)
assert iseq(0, f1v.minimize1(x0=5), eps=1e-3)
f1v.minimize1(x0=5)

f2 = f.QuadraticFunction(a=3, b=2, c=1)
f2v = f.FunctionVector({f2: 1})
x_v = np.linspace(-2.5, 2.5, 100)
y2_v = [f2(xx) for xx in x_v]
plt.plot(x_v, y2_v, label="f")
#plt.legend()
plt.grid()

assert iseq(f2v.goalseek(target=5), 0.8685170919424989, eps=1e-4)
assert iseq(f2v.minimize1(), -0.3332480000000852, eps=1e-4)
f2v.goalseek(target=5), f2v.minimize1()

# ## Restricted and apply kernel
#
# restricted functions (`f_r`, more generally `restricted(func)`) are zero outside the kernel domain; kernel-applied functions (`f_k`, more generally `apply_kernel(func)`) is multiplied with the kernel

func = f.TrigFunction()

# ### Flat kernel

# +
kernel = Kernel(0, 1, Kernel.FLAT)
fv = f.FunctionVector({func: 1}, kernel=kernel)
f_r = fv.restricted(fv.f)
f_k = fv.apply_kernel(fv.f) 

assert not fv.f(-0.5) == 0
assert not fv.f(1.5) == 0
assert f_r(-0.5) == fv.f_r(-0.5) == 0
assert f_r(1.5) == fv.f_r(1.5) == 0
assert f_r(0.5) == fv.f_r(0.5) == fv.f(0.5)
assert f_r(0.25) == fv.f_r(0.25) == fv.f(0.25)
assert f_r(0.75) == fv.f_r(0.75) == fv.f(0.75)

assert f_k(-0.5) == fv.f_k(-0.5) == 0
assert f_k(1.5) == fv.f_k(1.5) == 0
assert f_k(0.5) == fv.f_k(0.5) == fv.f(0.5)   * kernel(0.5)
assert f_k(0.25) == fv.f_k(0.25) == fv.f(0.25) * kernel(0.25)
assert f_k(0.75) == fv.f_k(0.75) == fv.f(0.75) * kernel(0.75)

fv.plot(fv.f, x_min=-1, x_max=2, title="full function [self.f]")
fv.plot(fv.f_r, x_min=-1, x_max=2, title="restricted function [self.f_r]")
fv.plot(fv.f_k, x_min=-1, x_max=2, title="flat kernel applied [self.f_k]")
# -

# ### Sawtooth-Left kernel

# +
kernel = Kernel(0, 1, Kernel.SAWTOOTHL)
fv = f.FunctionVector({func: 1}, kernel=kernel)
f_r = fv.restricted(fv.f)
f_k = fv.apply_kernel(fv.f) 

assert not fv.f(-0.5) == 0
assert not fv.f(1.5) == 0
assert f_r(-0.5) == fv.f_r(-0.5) == 0
assert f_r(1.5) == fv.f_r(1.5) == 0
assert f_r(0.5) == fv.f_r(0.5) == fv.f(0.5)
assert f_r(0.25) == fv.f_r(0.25) == fv.f(0.25)
assert f_r(0.75) == fv.f_r(0.75) == fv.f(0.75)

assert f_k(-0.5) == fv.f_k(-0.5) == 0
assert f_k(1.5) == fv.f_k(1.5) == 0
assert f_k(0.5) == fv.f_k(0.5) == fv.f(0.5)   * kernel(0.5)
assert f_k(0.25) == fv.f_k(0.25) == fv.f(0.25) * kernel(0.25)
assert f_k(0.75) == fv.f_k(0.75) == fv.f(0.75) * kernel(0.75)

fv.plot(fv.f, x_min=-1, x_max=2, title="full function [self.f]")
fv.plot(fv.f_r, x_min=-1, x_max=2, title="restricted function [self.f_r]")
fv.plot(fv.f_k, x_min=-1, x_max=2, title="sawtooth-left kernel applied [self.f_k]")
# -

# ## Curve fitting

# ### norm and curve distance
#
# We have various ways of measuring the distance between a FunctionVector (that includes a kernel) and a Function, all being based on the L2 norm with kernel applied
#
# - Use `FunctionVector.distance2` for the squared distance between the FunctionVector and the Function, or `distance` for the squareroot thereof*
#
# - Wrap the Function in a FunctionVector with the same kernel using the `wrap` method, substract the two FunctionVectors from each other, and use `norm2` or `norm`
#
# *in optimization you typically want to use the squared function because it behaves better and you don't have to calculate the square root

# +
# create the template function vector
fv_t = f.FunctionVector(kernel=Kernel(x_min=-1, x_max=1, kernel=Kernel.FLAT))
assert fv_t.f(0) == 0

# create target and match functions and wrap them in FunctionVector
f0 = f.TrigFunction(phase=1/2)
f0v = fv_t.wrap(f0)
f1v = fv_t.wrap(f.QuadraticFunction(c=0))
f2v = fv_t.wrap(f.QuadraticFunction(a=-2, c=1))

# check norms and distances
diff1 = (f0v-f1v).norm()
diff2 = (f0v-f2v).norm()
assert iseq( (f0v-f1v).norm2(), (f0v-f1v).norm()**2)
assert iseq( (f0v-f2v).norm2(), (f0v-f2v).norm()**2)
assert iseq(f1v.dist2_L2(f0), (f0v-f1v).norm2())
assert iseq(f2v.dist2_L2(f0), (f0v-f2v).norm2())
assert iseq(f1v.dist_L2(f0), (f0v-f1v).norm())
assert iseq(f2v.dist_L2(f0), (f0v-f2v).norm())
assert iseq(f1v.dist_L1(f0), (f0v-f1v).norm1())
assert iseq(f2v.dist_L1(f0), (f0v-f2v).norm1())

# plot
f0v.plot(show=False, label="f0 [target function]")
f1v.plot(show=False, label=f"f1 [match 1]: dist={diff1:.2f}")
f2v.plot(show=False, label=f"f2 [match 2]: dist={diff2:.2f}")
plt.legend()
plt.show()
# -

# ### norm and curve distance on price functions
#
# Note: what we call a _price function_ is simply the negative first derivative, assuming the functions are swap function

# +
fv_t = f.FunctionVector(kernel=Kernel(x_min=0, x_max=1, kernel=Kernel.FLAT))
fn1_fv = fv_t.wrap(f.QuadraticFunction(c=1))  # f(x) = 1
fn2_fv = fv_t.wrap(f.QuadraticFunction(c=1, b=-1)) # f(x) = 1-x
null_f = lambda x: 0
half_f = lambda x: 0.5
one_f = lambda x: 1
fn1_fv.plot(label="fn1(x)=1", linewidth=3)
fn2_fv.plot(label="fn2(x)=1-x")
fn1_fv.plot(func=fn1_fv.p, label="fn1.p(x)=0")
fn2_fv.plot(func=fn2_fv.p, linestyle="--", color="#faa", label="fn2.p(x)=1")

plt.legend()
plt.show()
# -

# #### norm

# +
# method-level equality
# ... on self.f
assert fn1_fv.norm2_L2 == fn1_fv.norm2 
assert fn1_fv.norm_L2 == fn1_fv.norm
assert fn1_fv.norm_L1 == fn1_fv.norm1 
# ... on self.p
assert fn1_fv.normp2_L2 == fn1_fv.normp2 
assert fn1_fv.normp_L2 == fn1_fv.normp
assert fn1_fv.normp_L1 == fn1_fv.normp1 

# checking values fn1
# ... on self.f
assert fn1_fv.norm2_L2() == 1
assert fn1_fv.norm_L2() == 1
assert fn1_fv.norm_L1() == 1
# ... on self.p
assert fn1_fv.normp2_L2() == 0
assert fn1_fv.normp_L2() == 0
assert fn1_fv.normp_L1() == 0

# # checking values fn2
# # ... on self.f
assert iseq(1/3, fn2_fv.norm2_L2(), eps=1e-4)
assert iseq(m.sqrt(1/3), fn2_fv.norm_L2(), eps=1e-4)
assert iseq(1/2, fn2_fv.norm_L1(), eps=1e-4)
# # ... on self.p
assert iseq(1, fn2_fv.normp2_L2(), eps=1e-4)
assert iseq(1, fn2_fv.normp_L2(), eps=1e-4)
assert iseq(1, fn2_fv.normp_L1(), eps=1e-4)
# -

# #### distance

# +
# checking values fn1 vs null_f [1-0]
# ... on self.f
assert fn1_fv.dist2_L2(func=null_f) == 1
assert fn1_fv.dist_L2(func=null_f) == 1
assert fn1_fv.dist_L1(func=null_f) == 1
# ... on self.p
assert fn1_fv.distp2_L2(func=null_f) == 0
assert fn1_fv.distp_L2(func=null_f) == 0
assert fn1_fv.distp_L1(func=null_f) == 0

# # checking values fn2 vs null_f [1-x-0]
# # ... on self.f
assert iseq(1/3, fn2_fv.dist2_L2(func=null_f), eps=1e-4)
assert iseq(m.sqrt(1/3), fn2_fv.dist_L2(func=null_f), eps=1e-4)
assert iseq(1/2, fn2_fv.dist_L1(func=null_f), eps=1e-4)
# # ... on self.p
assert iseq(1, fn2_fv.distp2_L2(func=null_f), eps=1e-4)
assert iseq(1, fn2_fv.distp_L2(func=null_f), eps=1e-4)
assert iseq(1, fn2_fv.distp_L1(func=null_f), eps=1e-4)

# +
# checking values fn1 vs one_f [1-1]
# ... on self.f
assert fn1_fv.dist2_L2(func=one_f) == 0
assert fn1_fv.dist_L2(func=one_f) == 0
assert fn1_fv.dist_L1(func=one_f) == 0
# ... on self.p
assert fn1_fv.distp2_L2(func=one_f) == 1
assert fn1_fv.distp_L2(func=one_f) == 1
assert fn1_fv.distp_L1(func=one_f) == 1

# # checking values fn2 vs one_f [1-x-1]
# # ... on self.f
assert iseq(1/3, fn2_fv.dist2_L2(func=one_f), eps=1e-4)
assert iseq(m.sqrt(1/3), fn2_fv.dist_L2(func=one_f), eps=1e-4)
assert iseq(1/2, fn2_fv.dist_L1(func=one_f), eps=1e-4)
# # ... on self.p
assert iseq(0, fn2_fv.distp2_L2(func=one_f), eps=1e-4)
assert iseq(0, fn2_fv.distp_L2(func=one_f), eps=1e-4)
assert iseq(0, fn2_fv.distp_L1(func=one_f), eps=1e-4)

# +
# checking values fn1 vs half_f [1-0.5=0.5]
# ... on self.f
assert fn1_fv.dist2_L2(func=half_f) == 0.25
assert fn1_fv.dist_L2(func=half_f) == 0.5
assert fn1_fv.dist_L1(func=half_f) == 0.5
# ... on self.p
assert fn1_fv.distp2_L2(func=half_f) == 0.25
assert fn1_fv.distp_L2(func=half_f) == 0.5
assert fn1_fv.distp_L1(func=half_f) == 0.5

# # checking values fn2 vs half_f [1-x-0.5=0.5-x]
# # ... on self.f
assert iseq(1/12, fn2_fv.dist2_L2(func=half_f), eps=1e-3)        #int_0..1 (0.5-x)^2 = 1/12
assert iseq(m.sqrt(1/12), fn2_fv.dist_L2(func=half_f), eps=1e-3)
assert iseq(1/4, fn2_fv.dist_L1(func=half_f), eps=1e-4)
# # ... on self.p
assert iseq(0.25, fn2_fv.distp2_L2(func=half_f), eps=1e-4)
assert iseq(0.5, fn2_fv.distp_L2(func=half_f), eps=1e-4)
assert iseq(0.5, fn2_fv.distp_L1(func=half_f), eps=1e-4)
# -

# ### curve fitting

# #### flat kernel

fv_template = f.FunctionVector(kernel=Kernel(x_min=-1, x_max=1, kernel=Kernel.FLAT))
target_f = f.TrigFunction(phase=1/2)
target_fv = fv_template.wrap(target_f)
f_match0 = f.QuadraticFunction()
params0 = dict(a=0, b=0, c=0)
params = target_fv.curve_fit(f_match0, params0)
f_match = f_match0.update(**params)
params, f_match

f_match_v = target_fv.wrap(f_match)
diff = (target_fv-f_match_v).norm()
target_fv.plot(show=False, label="target function")
f_match_v.plot(show=False, label=f"match  (dist={diff:.2f})")
plt.title(f"Best fit (a={params['a']:.2f}, b={params['b']:.2f}, c={params['c']:.2f}); dist={diff:.2f}")
plt.legend()
f_match_v

# #### skewed kernel (sawtooth-left)

fv_template = f.FunctionVector(kernel=Kernel(x_min=-1, x_max=1, kernel=Kernel.SAWTOOTHL))
target_f = f.TrigFunction(phase=1/2)
target_fv = fv_template.wrap(target_f)
f_match0 = f.QuadraticFunction()
params0 = dict(a=0, b=0, c=0)
params = target_fv.curve_fit(f_match0, params0)
f_match = f_match0.update(**params)
target_fv.kernel, params, f_match

f_match_v = target_fv.wrap(f_match)
diff = (target_fv-f_match_v).norm()
target_fv.plot(show=False, label="target function")
f_match_v.plot(show=False, label=f"match  (dist={diff:.2f})")
plt.title(f"Best fit (a={params['a']:.2f}, b={params['b']:.2f}, c={params['c']:.2f}); dist={diff:.2f}")
plt.legend()
f_match_v

# ## High dimensional minimization

# ### Example
#
# here we use as example the function
#
# $$
# f(x,y) = (x-2)^2 + (y-2)^2
# $$
#
# which obviously should be minimal at $(x,y) = (2,2)$

func = lambda x,y: (x-2)**2 + (y-2)**2

r, dxdy = f.minimize(func, x0=[20, -5], learning_rate=None, return_path=True)
assert iseq(r[-1][0], 2, eps=1e-3)
assert iseq(r[-1][1], 2, eps=1e-3)
r[-1], dxdy

x,y = zip(*r)
plt.scatter(x,y)
plt.title("Convergence path")
plt.grid()

r, dxdy = f.minimize(func, x0=dict(x=20, y=-5), learning_rate=None, return_path=True)
assert iseq(r[-1]["x"], 2, eps=1e-3)
assert iseq(r[-1]["y"], 2, eps=1e-3)
r[-1], dxdy

# ### Testing e_i, e_k and bump

e_i = f.FunctionVector.e_i
e_k = f.FunctionVector.e_k
bump = f.FunctionVector.bump

assert np.array_equal(e_i(1,5), np.array([0., 1., 0., 0., 0.]))
assert e_k("b", dict(a=1, b=2, c=3)) == {'a': 0, 'b': 1, 'c': 0}
assert bump(dict(a=1, b=2, c=3), "b", 0.25) == {'a': 1, 'b': 2.25, 'c': 3}

# ## Sundry tests

fmt = f.core.fmt
dct = {"a": 1.234578, "b": 2.3456789}
lst = list(dct.values())
assert fmt(dct) == {'a': 1.2346, 'b': 2.3457}
assert fmt(lst) == [1.2346, 2.3457]
assert fmt(dct, ".2f") == {'a': 1.23, 'b': 2.35}
assert fmt(lst, ".2f") == [1.23, 2.35]
assert fmt(lst, ".2f", as_float=False) == ['1.23', '2.35']
fmt(lst, ".2f")

# ## Function examples [NOTEST]

# ### QuadraticFunction

fn1 = f.Quadratic(a=1, b=2, c=3)
print(fn1.params())
fn2 = fn1.update(b=3, c=4)
diff2 = lambda x: (fn1(x)-fn2(x))**2
fn1.plot(-5,5, label="fn1")
fn2.plot(-5,5, label="fn2")
fn2.plot(-5,5, func=diff2, label="(fn1-fn2)^2")
fn2.plot(-5,5, func=fn2.p, label="-fn2'")
fn2.plot(-5,5, func=fn2.pp, label="-fn2''")
plt.legend()
x0 = f.goalseek(func=diff2)
print(f"fn1 = fn2 @ ({x0:.2f}, {fn1(x0):.2f})")
plt.show()

# ### PowerlawFunction

fn1 = f.Powerlaw()
print(fn1.params())
fn2 = fn1.update(x0=0.5)
fn3 = fn2.update(alpha=-1.5)
diff2 = lambda x: (fn3(x)-fn1(x))**2
fn1.plot(1,3, label="fn1")
fn2.plot(1,3, label="fn2")
fn3.plot(1,3, label="fn3")
fn2.plot(1,3, func=diff2, label="(fn3-fn1)^2")
fn2.plot(1,3, func=fn2.p, label="-fn2'")
fn2.plot(2,3, func=fn2.pp, label="-fn2''")
plt.legend()
x0 = f.goalseek(func=diff2)
print(f"fn1 = fn3 @ ({x0:.2f}, {fn1(x0):.2f})")
plt.show()

# ### TrigFunction

fn1 = f.Trig()
print(fn1.params())
fn2 = fn1.update(omega=1.2)
fn3 = fn2.update(phase=-0.1)
diff2 = lambda x: (fn3(x)-fn1(x))**2
fn1.plot(1,3, label="fn1")
fn2.plot(1,3, label="fn2")
fn3.plot(1,3, label="fn3")
fn2.plot(1,3, func=diff2, label="(fn3-fn1)^2")
#fn2.plot(1,3, func=fn2.p, label="-fn2'")
#fn2.plot(1,3, func=fn2.pp, label="-fn2''")
plt.legend()
x0 = f.goalseek(func=diff2, x0=1.5)
print(f"fn1 = fn3 @ ({x0:.2f}, {fn1(x0):.2f})")
plt.show()

# ### ExpFunction

fn1 = f.Exp()
print(fn1.params())
fn2 = fn1.update(k=1.2)
fn3 = fn2.update(x0=0.1)
diff2 = lambda x: (fn3(x)-fn1(x))**2
fn1.plot(0, 2, label="fn1")
fn2.plot(0, 2, label="fn2")
fn3.plot(0, 2, label="fn3")
fn2.plot(0, 2, func=diff2, label="(fn3-fn1)^2")
fn2.plot(0, 2, func=fn2.p, label="-fn2'")
fn2.plot(0, 2, func=fn2.pp, label="-fn2''")
plt.legend()
x0 = f.goalseek(func=diff2, x0=1.5)
print(f"fn1 = fn3 @ ({x0:.2f}, {fn1(x0):.2f})")
plt.show()

# ### LogFunction

fn1 = f.Log()
print(fn1.params())
fn2 = fn1.update(base=fn1.E)
fn3 = fn2.update(x0=0.1)
diff2 = lambda x: (fn3(x)-fn1(x))**2
fn1.plot(1, 5, label="fn1")
fn2.plot(1, 5, label="fn2")
fn3.plot(1, 5, label="fn3")
fn2.plot(1, 5, func=diff2, label="(fn3-fn1)^2")
fn2.plot(1, 5, func=fn2.p, label="-fn2'")
fn2.plot(1, 5, func=fn2.pp, label="-fn2''")
plt.legend()
x0 = f.goalseek(func=diff2, x0=1.5)
print(f"fn1 = fn3 @ ({x0:.2f}, {fn1(x0):.2f})")
plt.show()

# ### HyperbolaFunction

fn1 = f.Hyperbola()
print(fn1.params())
fn2 = fn1.update(k=1.2)
fn3 = fn2.update(x0=-0.5)
diff2 = lambda x: (fn3(x)-fn1(x))**2
fn1.plot(0.5, 3, label="fn1")
fn2.plot(0.5, 3, label="fn2")
fn3.plot(0.5, 3, label="fn3")
fn2.plot(0.5, 3, func=diff2, label="(fn3-fn1)^2")
fn2.plot(0.5, 3, func=fn2.p, label="-fn2'")
fn2.plot(1.5, 3, func=fn2.pp, label="-fn2''")
plt.legend()
x0 = f.goalseek(func=diff2, x0=1.5)
print(f"fn1 = fn3 @ ({x0:.2f}, {fn1(x0):.2f})")
plt.show()

# ## Function examples
#
# _shortened version of the [NOTEST] section above, removing the charts_

fn1 = f.Quadratic(a=1, b=2, c=3)
assert f.Quadratic is f.QuadraticFunction
assert fn1.params() == {'a': 1, 'b': 2, 'c': 3}
fn2 = fn1.update(b=0)
assert fn2.params() == {'a': 1, 'b': 0, 'c': 3}
assert iseq(fn1(1), 6, fn1.f(1))
assert iseq(-fn1.p(1), 4, fn1.df_dx(1))
assert iseq(-fn1.pp(1), 2)
fn1(1), -fn1.p(1), -fn1.pp(1)

fn1 = f.Powerlaw()
assert f.Powerlaw is f.PowerlawFunction
assert fn1.params() == {'N': 1, 'alpha': -1, 'x0': 0}
fn2 = fn1.update(alpha=-2)
assert fn2.params() == {'N': 1, 'alpha': -2, 'x0': 0}
assert iseq(fn1(1), 1, fn1.f(1))
assert iseq(-fn1.p(1), -1, fn1.df_dx(1))
assert iseq(-fn1.pp(1), 2)
fn1(1), -fn1.p(1), -fn1.pp(1)

fn1 = f.Trig()
assert f.Trig is f.TrigFunction
assert fn1.params() == {'amp': 1, 'omega': 1, 'phase': 0}
fn2 = fn1.update(amp=-2)
assert fn2.params() == {'amp': -2, 'omega': 1, 'phase': 0}
assert iseq(0, fn1(1), fn1.f(1))
assert iseq(-fn1.PI, -fn1.p(1), fn1.df_dx(1))
assert iseq(0, -fn1.pp(1))
fn1(1), -fn1.p(1), -fn1.pp(1)

fn1 = f.Exp(k=2)
assert f.Exp is f.ExpFunction
assert fn1.params() == {'N': 1, 'k': 2, 'x0': 0}
fn2 = fn1.update(k=-2)
assert fn2.params() == {'N': 1, 'k': -2, 'x0': 0}
assert iseq(fn1.E**2, fn1(1), fn1.f(1))
assert iseq(2*fn1.E**2, -fn1.p(1), fn1.df_dx(1))
assert iseq(4*fn1.E**2, -fn1.pp(1))
fn1(1), -fn1.p(1), -fn1.pp(1)

fn1 = f.Log()
assert f.Log is f.LogFunction
assert fn1.params() == {'base': 10, 'N': 1, 'x0': 0}
fn2 = fn1.update(base=fn1.E)
assert fn2.params() == {'base': fn1.E, 'N': 1, 'x0': 0}
assert iseq(0, fn1(1), fn1.f(1))
assert iseq(0.4342944833508522, -fn1.p(1), fn1.df_dx(1))
assert iseq(-0.4342944840747152, -fn1.pp(1))
fn1(1), -fn1.p(1), -fn1.pp(1)

fn1 = f.Hyperbola()
assert f.Hyperbola is f.HyperbolaFunction
assert fn1.params() == {'k': 1, 'x0': 0, 'y0': 0}
fn2 = fn1.update(x0=1)
assert fn2.params() == {'k': 1, 'x0': 1, 'y0': 0}
assert iseq(1, fn1(1), fn1.f(1))
assert iseq(-1, -fn1.p(1), fn1.df_dx(1))
assert iseq(2, -fn1.pp(1))
fn1(1), -fn1.p(1), -fn1.pp(1)
