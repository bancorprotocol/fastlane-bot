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
import numpy as np
import math as m
import matplotlib.pyplot as plt
import pandas as pd
from sympy import symbols, sqrt, Eq
import decimal as d

import invariants.functions as f
from invariants.solidly import SolidlyInvariant, SolidlySwapFunction

from testing import *
D = d.Decimal
plt.rcParams['figure.figsize'] = [6,6]

print("---")
print("{0.__name__} v{0.__VERSION__} ({0.__DATE__})".format(f.Function))
print("{0.__name__} v{0.__VERSION__} ({0.__DATE__})".format(SolidlyInvariant))


# -

# # Solidly Analysis

# ## Equations

# ### Invariant function
#
# The Solidly invariant function is 
#
# $$
#     x^3y+xy^3 = k
# $$
#
# which is a stable swap curve, but more convex than say curve. 

def invariant_eq(x, y, k=0, *, aserr=False):
    """returns f(x,y)-k or f(x,y)/k - 1"""
    if aserr:
        return (x**3 * y + x * y**3)/k-1
    else:
        return x**3 * y + x * y**3 - k


# ### Swap equation
#
# Solving the invariance equation as $y=y(x; k)$ gives the following result
#
# $$
# y(x;k) = \frac{x^2}{\left(-\frac{27k}{2x} + \sqrt{\frac{729k^2}{x^2} + 108x^6}\right)^{\frac{1}{3}}} - \frac{\left(-\frac{27k}{2x} + \sqrt{\frac{729k^2}{x^2} + 108x^6}\right)^{\frac{1}{3}}}{3}
# $$
#
# We can introduce intermediary variables $L(x;k), M(x;k)$ to write this a bit more simply
#
# $$
# L = -\frac{27k}{2x} + \sqrt{\frac{729k^2}{x^2} + 108x^6}
# $$
#
# $$
# M = L^{1/3} = \sqrt[3]{L}
# $$
#
# $$
# y = \frac{x^2}{\sqrt[3]{L}} - \frac{\sqrt[3]{L}}{3} = \frac{x^2}{M} - \frac{M}{3} 
# $$
#
# Using the function $y(x;k)$ we can easily derive the swap equation at point $(x; k)$ as
#
# $$
# \Delta y = y(x+\Delta x; k) - y(x; k)
# $$

# +
x, k = symbols('x k')

y = x**2 / ((-27*k/(2*x) + sqrt(729*k**2/x**2 + 108*x**6)/2)**(1/3)) - (-27*k/(2*x) + sqrt(729*k**2/x**2 + 108*x**6)/2)**(1/3)/3
y
# -

L = -27*k/(2*x) + sqrt(729*k**2/x**2 + 108*x**6)/2
y2 = x**2 / (L**(1/3)) - (L**(1/3))/3
y2


# #### Precision issues and L
#
# Note that as above, $L$ (that we call $L_1$ now) is not particularly well conditioned. 
#
# $$
# L_1 = -\frac{27k}{2x} + \sqrt{\frac{729k^2}{x^2} + 108x^6}
# $$
#
# This alternative form works better
#
# $$
# L_2(x;k) = \frac{27k}{2x} \left(\sqrt{1 + \frac{108x^8}{729k^2}} - 1 \right)
# $$
#
# Furthermore
#
# $$
# \sqrt{1+\xi}-1 = \frac{\xi}{2} - \frac{\xi^2}{8} + \frac{\xi^3}{16} - \frac{5\xi^4}{128} + O(\xi^5)
# $$

# +
def L1(x,k):
    return -27*k/(2*x) + sqrt(729*k**2/x**2 + 108*x**6)/2

def L2(x,k):
    xi = (108 * x**8) / (729 * k**2)
    #print(f"xi = {xi}")
    if xi > 1e-5:
        lam = (m.sqrt(1 + xi) - 1)
    else:
        lam = xi*(1/2 - xi*(1/8 - xi*(1/16 - 0.0390625*xi)))
        # the relative error of this Taylor approximation is for xi < 0.025 is 1e-5 or better
        # for xi ~ 1e-15 the full term is unstable (because 1 + 1e-16 ~ 1 in double precision)
        # therefore the switchover should happen somewhere between 1e-12 and 1e-2
    #lam1 = 0
    #lam2 = xi/2 - xi**2/8 
    #lam2 = xi/2 - xi**2/8 + xi**3/16 - 0.0390625*xi**4
    #lam2 = xi*(1/2 - xi*(1/8 - xi*(1/16 - 0.0390625*xi)))
    #lam = max(lam1, lam2)
        # for very small xi we can get zero or close to zero in the full formula
        # in this case the taulor approximation is better because for small xi it is always > 0
        # we simply use the max of the two -- the Taylor gets negative quickly
    L = lam * (27 * k) / (2 * x)
    return L

def L3(x,k):
    """going via decimal"""
    x = D(x)
    k = D(k)
    xi = (108 * x**8) / (729 * k**2)
    lam = (D(1) + xi).sqrt() - D(1)
    L = lam * (27 * k) / (2 * x)
    return float(L)


# -

L1(0.1, 1), L2(0.1,1)

M = L**(1/3)
y3 = x**2 / M - M/3
y3

assert y  == y2
assert y  == y3
assert y2 == y3


# +
def swap_eq(x,k):
    """using floats only"""
    L,M,y = [None]*3
    try:
        #L = -27*k/(2*x) + m.sqrt(729*k**2/x**2 + 108*x**6)/2
        L = L2(x,k)
        M = L**(1/3)
        y = x**2/M - M/3
    except Exception as e:
        print("Exception: ", e)
        print(f"x={x}, k={k}, L={L}, M={M}, y={y}")
    return y

def swap_eq_dec(x,k):
    """using decimals for the calculation of L"""
    L,M,y = [None]*3
    try:
        #L = -27*k/(2*x) + m.sqrt(729*k**2/x**2 + 108*x**6)/2
        L = L3(x,k)
        M = L**(1/3)
        y = x**2/M - M/3
    except Exception as e:
        print("Exception: ", e)
        print(f"x={x}, k={k}, L={L}, M={M}, y={y}")
    return y


# +
def swap_eq2(x, k):
    # Calculating the components of the swap equation
    term1_numerator = (2/3)**(1/3) * x**3
    term1_denominator = (9 * k * x**2 + m.sqrt(3) * m.sqrt(27 * k**2 * x**4 + 4 * x**12))**(1/3)

    term2_numerator = (9 * k * x**2 + m.sqrt(3) * m.sqrt(27 * k**2 * x**4 + 4 * x**12))**(1/3)
    term2_denominator = 2**(1/3) * 3**(2/3) * x

    # Swap equation calculation
    y = -term1_numerator / term1_denominator + term2_numerator / term2_denominator

    return y

# Example usage
x_value = 1  # Replace with the desired value of x
k_value = 1  # Replace with the desired value of k
print(swap_eq(x_value, k_value))


# -

# ### Price equation
#
# The derivative $p=dy/dx$ is as follows
#
# $$
# p=\frac{dy}{dx} = 6^{\frac{1}{3}}\left(\frac{-2 \cdot 3^{\frac{1}{3}} \cdot x \cdot \sqrt{\frac{27k^2 + 4x^8}{x^2}} \cdot \left(-9k + \sqrt{3} \cdot x \cdot \sqrt{\frac{27k^2 + 4x^8}{x^2}}\right) \cdot \left(3k \cdot x \cdot \sqrt{\frac{27k^2 + 4x^8}{x^2}} + \sqrt{3} \cdot \left(-9k^2 + 4x^8\right)\right) + 2^{\frac{1}{3}} \cdot \sqrt{\frac{27k^2 + 4x^8}{x^2}} \cdot \left(\frac{-9k + \sqrt{3} \cdot x \cdot \sqrt{\frac{27k^2 + 4x^8}{x^2}}}{x}\right)^{\frac{5}{3}} \cdot \left(-3k \cdot x \cdot \sqrt{\frac{27k^2 + 4x^8}{x^2}} + \sqrt{3} \cdot \left(9k^2 - 4x^8\right)\right) + 4 \cdot 3^{\frac{1}{3}} \cdot \left(-9k + \sqrt{3} \cdot x \cdot \sqrt{\frac{27k^2 + 4x^8}{x^2}}\right)^2 \cdot \left(27k^2 + 4x^8\right)}{6 \cdot x \cdot \left(\frac{-9k + \sqrt{3} \cdot x \cdot \sqrt{\frac{27k^2 + 4x^8}{x^2}}}{x}\right)^{\frac{7}{3}} \cdot \left(27k^2 + 4x^8\right)}\right)
# $$
#
#

# +
def price_eq(x, k):
    # Components of the derivative
    term1_numerator = 2**(1/3) * x**3 * (18 * k * x + (m.sqrt(3) * (108 * k**2 * x**3 + 48 * x**11)) / (2 * m.sqrt(27 * k**2 * x**4 + 4 * x**12)))
    term1_denominator = 3 * (9 * k * x**2 + m.sqrt(3) * m.sqrt(27 * k**2 * x**4 + 4 * x**12))**(4/3)
    
    term2_numerator = 18 * k * x + (m.sqrt(3) * (108 * k**2 * x**3 + 48 * x**11)) / (2 * m.sqrt(27 * k**2 * x**4 + 4 * x**12))
    term2_denominator = 3 * 2**(1/3) * 3**(2/3) * x * (9 * k * x**2 + m.sqrt(3) * m.sqrt(27 * k**2 * x**4 + 4 * x**12))**(2/3)
    
    term3 = -3 * 2**(1/3) * x**2 / (9 * k * x**2 + m.sqrt(3) * m.sqrt(27 * k**2 * x**4 + 4 * x**12))**(1/3)
    
    term4 = -(9 * k * x**2 + m.sqrt(3) * m.sqrt(27 * k**2 * x**4 + 4 * x**12))**(1/3) / (2**(1/3) * 3**(2/3) * x**2)
    
    # Combining all terms
    dy_dx = (term1_numerator / term1_denominator) + (term2_numerator / term2_denominator) + term3 + term4

    return dy_dx

# Example usage
x_value = 1  # Replace with the desired value of x
k_value = 1  # Replace with the desired value of k
print(price_eq(x_value, k_value))

# -

# #### Inverting the price equation
#
# The above equations 
# ([obtained thanks to Wolfram Alpha](https://chat.openai.com/share/55151f92-411c-43c1-a6ec-180856762a82), 
# the interface of which still sucks) are rather complex, and unfortunately they can't apparently be inverted analytically to get $x=x(p;k)$

# ## Charts

# ### Invariant equation
#
# _(see Freeze04 for the latest version)_

y_f = swap_eq

# +
# k_v = [1**4, 2**4, 3**4, 5**4]
# #k_v = [1**4]
# x_v = np.linspace(0, m.sqrt(10), 50)
# x_v = [xx**2 for xx in x_v]
# x_v[0] = x_v[1]/2
# y_v_dct = {kk: [y_f(xx, kk) for xx in x_v] for kk in k_v}
# plt.grid(True)
# for kk, y_v in y_v_dct.items(): 
#     plt.plot(x_v, y_v, marker=None, linestyle='-', label=f"k={kk}")
# plt.legend()
# plt.xlim(0, max(x_v))
# plt.ylim(0, max(x_v))
# plt.show()
# -

# Checking the invariant equation at a specific point (xx; kk)

# +
# kk = 625
# xx = 3
# invariant_eq(x=xx, y=swap_eq(xx, kk), k=kk, aserr=True)
# -

# Calculating a histogram of relative errors, ie what the relative error in the invariant equation is at various points $xx$ of the swap equation and at various $kk$

# +
# y_inv_dct = {kk: [invariant_eq(x=xx, y=swap_eq(xx, kk), k=kk, aserr=True) for xx in x_v] for kk in k_v}
# y_inv_lst = [v for lst in y_inv_dct.values() for v in lst]
# #y_inv_lst
# plt.hist(y_inv_lst, bins=200, color="blue")
# plt.title("Histogram of relative errors [f(x,y)/k - 1]")
# plt.show()
# -

# Maximum relative error for different values of $k$

# +
# {k: max([abs(vv) for vv in v]) for k,v in y_inv_dct.items()}
# -

# Minimum relative error for different values of $k$

# +
# {k: min([abs(vv) for vv in v]) for k,v in y_inv_dct.items()}

# +
# kk = 5**4
# x_v = np.linspace(0, m.sqrt(20), 50)
# x_v = [xx**2 for xx in x_v]
# x_v[0] = x_v[1]/2
# plt.grid(True)
# plt.plot(x_v, [y_f(xx, kk) for xx in x_v], marker=None, linestyle='-', label=f"k={kk}")
# inv_dct = {xx: invariant_eq(x=xx, y=swap_eq(xx, kk), k=kk, aserr=True) for xx in x_v}
# plt.legend()
# plt.xlim(0, max(x_v))
# plt.ylim(0, max(x_v))
# plt.show()
# plt.plot(inv_dct.keys(), inv_dct.values())
# plt.title(f"Relative error as a function of x for k={kk}")
# plt.show()
# -

# Same analysis as above, but much higher resolution

# +
# NUMPOINTS = 10000
# kk = 5**4
# x_v = np.linspace(0, m.sqrt(20), NUMPOINTS)
# x_v = [xx**2 for xx in x_v]
# x_v[0] = x_v[1]/2
# plt.grid(True)
# plt.plot(x_v, [y_f(xx, kk) for xx in x_v], marker=None, linestyle='-', label=f"k={kk}")
# inv_dct = {xx: invariant_eq(x=xx, y=swap_eq(xx, kk), k=kk, aserr=True) 
# #           for xx in x_v[int(0.2*NUMPOINTS):int(0.5*NUMPOINTS)] # <=== CHANGE RANGE HERE
#            for xx in x_v # <=== CHANGE RANGE HERE
# }
# plt.legend()
# plt.xlim(0, max(x_v))
# plt.ylim(0, max(x_v))
# plt.show()
# plt.plot(inv_dct.keys(), inv_dct.values())
# plt.title(f"Relative error as a function of x for k={kk} (highres)")
# plt.grid()
# plt.show()
# plt.plot(inv_dct.keys(), inv_dct.values())
# plt.title(f"Relative error as a function of x for k={kk} (highres)")
# plt.grid()
# plt.ylim(0,1e-13)
# plt.show()
# -

# same as above, but using decimal

# +
# NUMPOINTS = 10000
# kk = 5**4
# x_v = np.linspace(0, m.sqrt(20), NUMPOINTS)
# x_v = [xx**2 for xx in x_v]
# x_v[0] = x_v[1]/2
# plt.grid(True)
# plt.plot(x_v, [y_f(xx, kk) for xx in x_v], marker=None, linestyle='-', label=f"k={kk}")
# inv_dct = {xx: invariant_eq(x=xx, y=swap_eq_dec(xx, kk), k=kk, aserr=True) 
# #           for xx in x_v[int(0.15*NUMPOINTS):int(0.3*NUMPOINTS)] # <=== CHANGE RANGE HERE
#            for xx in x_v 
# }
# plt.legend()
# plt.xlim(0, max(x_v))
# plt.ylim(0, max(x_v))
# plt.show()
# plt.plot(inv_dct.keys(), inv_dct.values())
# plt.title(f"Relative error as a function of x for k={kk} (highres)")
# plt.grid()
# plt.show()
# plt.plot(inv_dct.keys(), inv_dct.values())
# plt.title(f"Relative error as a function of x for k={kk} (highres)")
# plt.grid()
# plt.ylim(0,1e-13)
# plt.show()
# -

# ### Numerical considerations
#
# _(see Freeze04 for the latest version)_
#
# #### Comparing L1 with L2
#
# L1 and L2 are different expressions of the L term above. L2 is the naive formula, L1 is optimized. L2 can be zero for very small values (and it is not even continous; see 0.009 and 0.01 below) whilst L1 is *always* greater than zero.

xs_v = [0.0001, 0.001, 0.009, 0.01, 0.015, 0.02, 0.05]
[(L1(xx,1), L2(xx, 1)) for xx in xs_v]

# +
# plt.plot(x_v, [L2(xx, 1) - L1(xx, 1) for xx in x_v])

# +
# plt.plot(x_v, [L1(xx, 1) for xx in x_v])
# plt.plot(x_v, [L2(xx, 1) for xx in x_v])
# plt.grid()
# plt.show()
# -

# ## Curvature and regions
#
# _(note that from here onwards we are using the library functions we've developed on the way rather than the explicit functions defined above)_
#
# ### Overview
#
# Here we look at the different _regions_ of the curve, most importantly the central, flat, region and its boundaries. Firstly we note that the invariance equation is homogenous
#
# $$
#     (\lambda x)^3(\lambda y)+(\lambda x)(\lambda y)^3 = 
#     \lambda^4 (x^3y+xy^3) = \lambda^4 k
# $$
#
# In other words, if a point $(x, y)$ is on curve $k$, then the point $(\lambda x, \lambda y)$ is on the curve $\lambda^4 k$, and in fact there is a 1:1 relationship between _all_ points on the curve $k$ and _all_ points on the curve $\lambda^4 k$ using this relationship. 
#
# **Important side note:** This scaling relation also shows that the financially important quantity is $\sqrt[4]{k}$, in the sense that this quantity scales linearly with the financial size of the curve.
#
# The points $(\lambda x, \lambda y)$ are _rays_ that come from the origin of the coordinate system. We now identify the ray where the curvature starts to bite, and this will be the boundary of our approximation
#
# Below we draw the rays as well as the **central tangents**, ie the tangents going through the point $x=y$. For a curve $k$, a the central point we have $2x^4=k$ and therefore it is at $(x,y) = (\sqrt[4]{k/2}, \sqrt[4]{k/2})$. The slope at this point is -1, so the equation is
#
# $$
# t(x;k) = \sqrt[4]{\frac k 2} - (x-\sqrt[4]{\frac k 2})
# $$
#
# We also note that $\sqrt[4]{k/2} = \sqrt[4]{k} \sqrt[4]{0.5}$

# +
x_v = np.linspace(0, m.sqrt(10), 50)
x_v = [xx**2 for xx in x_v]
x_v[0] = x_v[1]/2
k_sqrt4_v = [2, 3.5, 5, 6.5]

# draw the invariance curves
k_v = [kk**4 for kk in k_sqrt4_v]
for kk in k_v: 
    y_f = SolidlySwapFunction(k=kk)
    yy_v = [y_f(xx) for xx in x_v]
    #yy_v = [y_f(xx, kk) for xx in x_v]
    plt.plot(x_v, yy_v, marker=None, linestyle='-', label=f"k={kk}")

# draw the central tangents
C = 0.5**(0.25)
for kk in k_sqrt4_v:
    yy_v = [C*kk - (xx-C*kk) for xx in x_v]
    plt.plot(x_v, yy_v, marker=None, linestyle='--', color="#aaa")

# draw the rays
for mm in [2.6, 6]:
    yy_v = [mm*xx for xx in x_v]
    plt.plot(x_v, yy_v, marker=None, linestyle='dotted', color="#aaa", label=f"ray (m={mm})")
    yy_v = [1/mm*xx for xx in x_v]
    plt.plot(x_v, yy_v, marker=None, linestyle='dotted', color="#aaa")

plt.grid(True)
plt.legend()
plt.xlim(0, max(x_v))
plt.ylim(0, max(x_v))
plt.show()
# -

# ### best hyperbola fit
#
# We now try the best possible (levered) hyperbola fit for one of those curves. Note that the levered hyperbola has the equation 
#
# $$
# y-y_0 = \frac{k}{x-x_0}
# $$
#
# and has therefore three free paramters, $(k, x_0, y_0)$. We fit those numerically.

# #### Unfitted hyperbola for demonstration
#
# (focus of Freeze04)
#
# Here we create four charts
# 1. The target curve, and a (bad) fit for demonstration, shown over a sufficiently wide range
# 2. The difference between the target curve and the fit
# 3. Target curve and fit, withing the kernel area
# 4. Difference, within kernel area (title contains L2 norm)
#

# +
k_sqrt4 = 5
kernel = f.Kernel(x_min=1, x_max=7, kernel=f.Kernel.FLAT)

######## FIRST CHART -- WIDE CURVES
x_v = np.linspace(0, m.sqrt(10), 50)
x_v = [xx**2 for xx in x_v]
x_v[0] = x_v[1]/2

# draw the invariance curve
k_v = [kk**4 for kk in k_sqrt4_v]
k = k_sqrt4**4
y1_f = SolidlySwapFunction(k=k)
yy_v = [y1_f(xx) for xx in x_v]
plt.plot(x_v, yy_v, marker=None, linestyle='-', label=f"k={k} ({k_sqrt4})")

# draw the central tangent
C = 0.5**(0.25)
yy_v = [C*k_sqrt4 - (xx-C*k_sqrt4) for xx in x_v]
plt.plot(x_v, yy_v, marker=None, linestyle='--', color="#aaa")

# draw the rays
for mm in [2.6, 6]:
    yy_v = [mm*xx for xx in x_v]
    plt.plot(x_v, yy_v, marker=None, linestyle='dotted', color="#aaa", label=f"ray (m={mm})")
    yy_v = [1/mm*xx for xx in x_v]
    plt.plot(x_v, yy_v, marker=None, linestyle='dotted', color="#aaa")
    
# draw the hyperbola
hyperbola_p = dict(x0=-1, y0=-1, k=25)
y2_f = f.HyperbolaFunction(**hyperbola_p)
yy_v = [y2_f(xx) for xx in x_v]
plt.plot(x_v, yy_v, marker=None, linestyle='--', color="red", label=f"hyperbola {hyperbola_p}")

plt.grid()
plt.legend()
plt.xlim(0, max(x_v))
plt.ylim(0, max(x_v))
plt.show()


######## SECOND CHART -- DIFFERENCE
dy_f = f.FunctionVector({y1_f: 1, y2_f:-1}, kernel=kernel)
yy_v = [dy_f(xx) for xx in x_v]
plt.plot(x_v, yy_v, marker=None)
plt.grid()
plt.xlim(0, max(x_v))
plt.ylim(-8,2)
#plt.legend()
plt.title("difference")
plt.show()


######## THIRD CHART -- CURVES WITHIN KERNEL
x_v = np.linspace(kernel.x_min, kernel.x_max, 100)

# draw the invariance curve
k_v = [kk**4 for kk in k_sqrt4_v]
k = k_sqrt4**4
y1_f = SolidlySwapFunction(k=k)
yy_v = [y1_f(xx) for xx in x_v]
plt.plot(x_v, yy_v, marker=None, linestyle='-', label=f"k={k} ({k_sqrt4})")

# draw the hyperbola
hyperbola_p = dict(x0=-1, y0=-1, k=25)
y2_f = f.HyperbolaFunction(**hyperbola_p)
yy_v = [y2_f(xx) for xx in x_v]
plt.plot(x_v, yy_v, marker=None, linestyle='--', color="red", label=f"hyperbola {hyperbola_p}")

plt.grid()
plt.legend()
plt.xlim(*kernel.limits)
#plt.ylim(0, None)
plt.show()


######## FOURTH CHART -- DIFFERENCE
dy_f = f.FunctionVector({y1_f: 1, y2_f:-1}, kernel=kernel)
yy_v = [dy_f(xx) for xx in x_v]
plt.plot(x_v, yy_v, marker=None)
plt.grid()
plt.xlim(*kernel.limits)
#plt.legend()
norm = dy_f.norm()
plt.title(f"difference [norm={norm:.2f}]")
plt.show()

y1_f, y2_f, dy_f
# -

# ## Generic numerical questions
#
# _(see Freeze04 for the latest results)_

# ### Square root term
#
# Here we are looking at the term $\sqrt{1+\xi}-1$ to understand up to which point we need the Tayler approximation, and whether there is a point going for T4 instead of T4. As a reminder
#
# $$
# \sqrt{1+\xi}-1 = \frac{\xi}{2} - \frac{\xi^2}{8} + \frac{\xi^3}{16} - \frac{5\xi^4}{128} + O(\xi^5)
# $$

x1_v = np.linspace(0,1,100)
x1_v[0] = x1_v[1]/2
data = [(
    xx, 
    m.sqrt(1+xx)-1,
    xx * (0.5 - xx*1/8),
    #xx/2 - xx**2/8 + xx**3/16 - xx**4 * 5 / 128,
    xx * (0.5 - xx*(1/8 - xx*(1/16 - 5/128*xx))),
) for xx in x1_v
]
df = pd.DataFrame(data, columns=['xi', 'Float', 'Taylor2', 'Taylor4']).set_index("xi")
oldfs = plt.rcParams['figure.figsize']
plt.rcParams['figure.figsize'] = [12,6]
#plt.figure(figsize=(12, 6))
df.plot()
plt.grid(True)
plt.rcParams['figure.figsize'] = oldfs
plt.savefig("/Users/skl/Desktop/image.jpg")
#plt.grid()
df.head()

# +
# x2_v = np.linspace(0,0.2,100)
# x1_v[0] = x1_v[1]/2
# data = [(
#     xx, 
#     m.sqrt(1+xx)-1,
#     xx * (0.5 - xx*1/8),
#     #xx/2 - xx**2/8 + xx**3/16 - xx**4 * 5 / 128,
#     xx * (0.5 - xx*(1/8 - xx*(1/16 - 5/128*xx))),
# ) for xx in x2_v
# ]
# df = pd.DataFrame(data, columns=['x', 'Float', 'Taylor2', 'Taylor4']).set_index("x")
# df.plot()
# plt.grid()
# df2 = df.copy()
# df2["Err2"] = df2["Taylor2"]/df2["Float"] - 1
# df2["Err4"] = df2["Taylor4"]/df2["Float"] - 1
# plt.show()
# df2.plot(y=["Err2", "Err4"])
# plt.grid()
# plt.title("Relative error of Taylor 2 4 term approximations")
# plt.ylim(-0.001, 0.0001)
# df2.head()
# -

# ### Decimal vs float
# #### Precision
#
# we compare $\sqrt{1+\xi}-1$ for float, Taylor and Decimal
#
# $$
# \sqrt{1+\xi}-1 = \frac{\xi}{2} - \frac{\xi^2}{8} + \frac{\xi^3}{16} - \frac{5\xi^4}{128} + O(\xi^5)
# $$

# +
# import decimal as d
# D = d.Decimal
# d.getcontext().prec = 1000  # Set the precision to 30 decimal places (adjust as needed)
# xd_v = [1e-18*1.5**nn for nn in np.linspace(0, 103, 500)]
# xd_v[0], xd_v[-1]

# +
# fmt = lambda x: x
# fmt = float
# ONE = D(1)
# data = [(
#     xx, 
#     m.sqrt(1+xx)-1,
#     xx * (0.5 - xx*1/8),
#     #xx/2 - xx**2/8 + xx**3/16 - xx**4 * 5 / 128,
#     xx * (0.5 - xx*(1/8 - xx*(1/16 - 5/128*xx))),
#     fmt((ONE+D(xx)).sqrt()-1),
# ) for xx in xd_v
# ]
# df = pd.DataFrame(data, columns=['x', 'Float', 'Taylor2', 'Taylor4', 'Dec']).set_index("x")
# df.head()

# +
# df.plot()
# # plt.xlim(0, None)
# # plt.ylim(0, 100)
# plt.grid()

# +
# df.iloc[:80].plot()
# plt.grid()

# +
# df.iloc[:100].plot()
# plt.grid()

# +
# LOC = 480
# df.iloc[LOC:].plot()
# plt.grid()

# +
# df2 = pd.DataFrame([
#     (df["Float"]-df["Taylor4"])/df["Taylor4"],
#     (df["Taylor2"]-df["Taylor4"])/df["Taylor4"],
#     (df["Dec"]-df["Taylor4"])/df["Taylor4"],
# ]).transpose()
# df2.columns = ["Float", "Taylor2", "Dec"]
# df2
# -

# #### Timing
#
# (focus of Freeze03)

import time
import decimal as d
D = d.Decimal

# +
# def timer(func, *args, N=None, **kwargs):
#     """times the calls to func; func is called with args and kwargs; returns time in msec per 1m calls"""
#     if N is None:
#         N = 10_000_000
#     start_time = time.time()
#     for _ in range(N):
#         func(*args, **kwargs)
#     end_time = time.time()
#     return (end_time - start_time)/N*1_000_000*1000

# def timer1(func, arg, N=None):
#     """times the calls to func; func is called with arg; returns time in msec per 1m calls"""
#     if N is None:
#         N = 10_000_000
#     start_time = time.time()
#     for _ in range(N):
#         func(arg)
#     end_time = time.time()
#     return (end_time - start_time)/N*1_000_000*1000

# def timer2(func, arg1, arg2, N=None):
#     """times the calls to func; func is called with arg1, arg2; returns time in msec per 1m calls"""
#     if N is None:
#         N = 10_000_000
#     start_time = time.time()
#     for _ in range(N):
#         func(arg1, arg2)
#     end_time = time.time()
#     return (end_time - start_time)/N*1_000_000*1000
#-

# identify function (`lambda`)

timer(lambda x: x, 1), timer1(lambda x: x, 1)


# ditto, defined with `def`

def idfunc(x):
    return x
timer(idfunc, 1), timer1(idfunc, 1)

# sin, sqrt, exp etc as reference

(timer(m.sin, 1), timer(m.cos, 1), timer(m.tan, 1), 
 timer(m.sqrt, 1), timer(m.exp, 1), timer(m.log, 1))

(timer1(m.sin, 1), timer1(m.cos, 1), timer1(m.tan, 1), 
 timer1(m.sqrt, 1), timer1(m.exp, 1), timer1(m.log, 1))

# **float** calculation

timer(lambda xx: m.sqrt(1+xx)-1, 1), timer1(lambda xx: m.sqrt(1+xx)-1, 1)

# **taylor** calculations

timer(lambda xx: xx * (0.5 - xx*1/8), 1), timer1(lambda xx: xx * (0.5 - xx*1/8), 1)

(timer(lambda xx: xx * (0.5 - xx*(1/8 - xx*(1/16 - 5/128*xx))), 1),
timer1(lambda xx: xx * (0.5 - xx*(1/8 - xx*(1/16 - 5/128*xx))), 1))

(timer(lambda xx: xx/2 - xx**2/8 + xx**3/16 - xx**4 * 5 / 128, 1),
timer1(lambda xx: xx/2 - xx**2/8 + xx**3/16 - xx**4 * 5 / 128, 1))

# **decimal** calculations

# +
# d.getcontext().prec = 30
# ONE = D(1)
# (timer(lambda xx: D(1+xx).sqrt()-1,  1, N=100_000),
#  timer(lambda xx: ONE+xx.sqrt()-1, ONE, N=100_000))

# +
# d.getcontext().prec = 100
# ONE = D(1)
# (timer(lambda xx: D(1+xx).sqrt()-1,  1, N=10_000),
#  timer(lambda xx: ONE+xx.sqrt()-1, ONE, N=10_000))

# +
# d.getcontext().prec = 1_000
# ONE = D(1)
# (timer(lambda xx: D(1+xx).sqrt()-1,  1, N=1_000),
#  timer(lambda xx: ONE+xx.sqrt()-1, ONE, N=1_000))
# -

# decimal conversions

# +
# d.getcontext().prec = 30
# ONE = D("0."+"9"*d.getcontext().prec)
# PI = m.pi
# (timer(lambda xx: D(xx),  PI, N=1_000_000),
#  timer(lambda: float(ONE), N=1_000_000),
#  ONE
# )

# +
# d.getcontext().prec = 100
# ONE = D("0."+"9"*d.getcontext().prec)
# (timer(lambda xx: D(xx),  PI, N=1_000_000),
#  timer(lambda: float(ONE), N=1_000_000),
#  ONE
# )

# +
# d.getcontext().prec = 1000
# ONE = D("0."+"9"*d.getcontext().prec)
# (timer(lambda xx: D(xx),  PI, N=1_000_000),
#  timer(lambda: float(ONE), N=1_000_000),
#  ONE
# )
# -

# `L2` (using Taylor) vs `L3` (using decimal)

# +
# d.getcontext().prec = 30
# r = (   
#     timer2(L2, 1, 625, N=1_000_000),
#     timer2(L3, 1, 625, N=10_000),
# )
# r, r[1]/r[0]

# +
# d.getcontext().prec = 100
# r = (   
#     timer2(L2, 1, 625, N=1_000_000),
#     timer2(L3, 1, 625, N=10_000),
# )
# r, r[1]/r[0]

# +
# d.getcontext().prec = 1000
# r = (   
#     timer2(L2, 1, 625, N=1_000_000),
#     timer2(L3, 1, 625, N=10_000),
# )
# r, r[1]/r[0]
# -

D(2).sqrt()**2

# checking the performance of exponential on vectors (result: np.exp is faster than 10**; it may be worth pre-calculating np.log(10) for small vectors)

v1 = 10**np.linspace(1,2, 10)
v3 = 10**np.linspace(1,2, 1000)

# +
# r = (
#     timer1(lambda x: 10**x, v1, N=100_000),
#     timer1(lambda x: 10**x, v3, N=100_000)
# )
# r, r[1]/r[0]

# +
# r = (
#     timer1(lambda x: np.exp(v1*np.log(10)), v1, N=100_000),
#     timer1(lambda x: np.exp(v3*np.log(10)), v3, N=100_000)
# )
# r, r[1]/r[0]

# +
# LOG10 = np.log(10)
# r = (
#     timer1(lambda x: np.exp(v1*LOG10),      v3, N=100_000),
#     timer1(lambda x: np.exp(v3*np.log(10)), v3, N=100_000)
# )
# r, r[1]/r[0]
# -


