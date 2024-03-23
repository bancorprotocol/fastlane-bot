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
import invariants.functions as f
from invariants.kernel import Kernel
import numpy as np
import math as m
import matplotlib.pyplot as plt

from testing import *
plt.rcParams['figure.figsize'] = [12,6]

print("{0.__name__} v{0.__VERSION__} ({0.__DATE__})".format(f.Function))
print("{0.__name__} v{0.__VERSION__} ({0.__DATE__})".format(Kernel))
# -

# # Functions and integration kernels

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

# ### integration

f1v = f.FunctionVector({f1: 1}, kernel=knl)
f2v = f.FunctionVector({f2: 1}, kernel=knl)
#f1v.kernel, f2v.kernel

knl = f1v.kernel
assert f1v.kernel == f2v.kernel
assert f1v.kernel == fv.kernel
x_v = np.linspace(knl.x_min, knl.x_max)
plt.plot(x_v, [f1v(xx) for xx in x_v], label="f1")
plt.plot(x_v, [f2v(xx) for xx in x_v], label="f2")
plt.plot(x_v, [fv(xx) for xx in x_v], label="f=f1+f2")
plt.grid()
plt.show()

# +
assert iseq(f1v.integrate(), 13+1)
    # assert iseq(kf.integrate(ONE), 1)
    # assert iseq(kf.integrate(SQR), 13)

assert iseq(f2v.integrate(), 4)
    # assert iseq(kf.integrate(LIN), 4)

assert iseq(fv.integrate(), 18)
# -

f2v.integrate()

# ### goal seek and minimize

f1 = f.QuadraticFunction(a=1, c=-4)
f1v = f.FunctionVector({f1: 1})
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

# plot
f0v.plot(show=False, label="f0 [target function]")
f1v.plot(show=False, label=f"f1 [match 1]: dist={diff1:.2f}")
f2v.plot(show=False, label=f"f2 [match 2]: dist={diff2:.2f}")
plt.legend()
plt.show()
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


