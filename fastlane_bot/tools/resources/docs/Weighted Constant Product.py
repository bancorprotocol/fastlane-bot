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

import numpy as np
import sympy as sp
import matplotlib.pyplot as plt

# # Weighted Constant Product Formulas


# ### Definitions

# - $x,y$ are the token balances in their native units
# - $\alpha$ is the weight of the $x$ token ($1/2$ is standard constant product)
# - $\eta = {\alpha}/{1-\alpha}$ is the weight ratio, equivalent to $\alpha$ but providing a different parameterization
# - $k$ the pool invariant

# #### Formula D1. (Definition of eta)
# $$
# \eta = \frac{\alpha}{1-\alpha}
# $$

# #### Formula D2. (Reverse eta) **OK**
# $$
# \alpha = \frac{\eta}{\eta+1}
# $$


# #### Formula D3.
# $$
# \frac{\eta}{\eta-1} = \frac \alpha {2\alpha -1}
# $$

# #### Formula D4.
# $$
# \frac{1}{\eta-1} = \frac {1-\alpha} {2\alpha -1}
# $$

# #### Formula D5. 
# $$
# \eta + 1 = \frac{1}{1-\alpha}
# $$

# #### Formula D6.

# $$
# \eta(1-\alpha)=\alpha
# $$

# ### Operational formulas

# #### Formula 1. (Invariant)
# $$
# x^\alpha y^{1-\alpha} = k^\alpha
# $$

# #### Formula 2. (x in terms of y)
# $$
# x(y) 
# = \frac{k}{ y^{\frac{1-\alpha}{\alpha}} }
# = \frac{k}{ y^{\frac{1}{\eta}} }
# $$

# #### Formula 3. (y in terms of x)
# $$
# y(x) = 
# \left(\frac{k}{x}\right)^{\frac{\alpha}{1-\alpha}} =
# \left(\frac{k}{x}\right)^\eta
# $$


# #### Formula 4. (marginal price)
# $$
# p = \frac{dy}{dx}
# = \eta \frac{y}{x} = \eta k^\eta x^{\eta-1} 
# = \eta k^{-1} y^{1+\frac 1 \eta}
# $$

# #### Formula 5. (price response function $x(p)$)
# $$
# x(p) 
# = 
# \left(\frac \eta p\right)^{1-\alpha} k^\alpha
# $$

# #### Formula 6. (price response function $y(p)$)
# $$
# y(p) = \left( \frac{kp}{\eta}  \right)^\alpha
# $$


# ## Reconciliation

# $$
# \prod_{l} 
# x_l{} ^ {r_l}
# = \kappa
# $$

# $$
# x_i {}^ {r_i}
# =
# \kappa \prod_{l \neq i} x_l ^ {- r_l}
# $$

# $$
# - \frac{ \partial x_{_{i}} } { \partial x_{_{j}} } 
# = \frac {P_i} {P_j}
# =
# \frac{x_i}{x_j}
# \left(\frac{ r_i } { r_j } \right) ^ { - 1 }
# = \frac{x_i\,r_j}{x_j\,r_i}
# $$

# In this equation
# $$
# x_i = 
# \frac
# {\kappa P_i r_i}
# {\prod_{l} \left( P_l\, r_l \right) ^ {r_l}}
# $$

# For $x$ we get Formula 5 starting with and simplifying the below formula using we choose the token balances $x=x_1, y=x_2$, the weights $\alpha_1=\alpha, \alpha_2=1-\alpha$, and the prices $p=p_1/p_2$ and the pool constant $\kappa = k^\alpha$:
# $$
# x_1 = \frac{\kappa p_1 \alpha_1} 
# {(p_1 \alpha_1)^{\alpha_1}\cdot (p_2 \alpha_2)^{\alpha_2}}
# $$
#
# Formula 6 we get when we start with the same equation except with $x_2=\cdots$ and $\kappa p_2 \alpha_2$ in the numerator

# ## Testing



x, y, k, p, al, eta = sp.symbols(r"x y k p \alpha \eta", real=True, positive=True)

eta_eq = sp.Eq(eta, al/(1-al))
eta_eq

reta_eq = sp.Eq(al, eta/(1+eta))
reta_eq


pxl_eq = sp.Eq(x, (1/k)**(eta/(eta-1)) * (p/eta)**(1/(eta-1)))
pxl_eq

pxa_eq = pxl_eq.subs(eta_eq.lhs, eta_eq.rhs).simplify()
pxa_eq

pya_eq = sp.Eq(y, k**al * (p/eta)**al).subs(eta_eq.lhs, eta_eq.rhs)
pya_eq

inv_eq.subs(pxa_eq.lhs, pxa_eq.rhs).subs(pya_eq.lhs, pya_eq.rhs).simplify()


al_eq = sp.Eq(al, sp.solve(eta_eq, al)[0])
al_eq

eta_eq2 = sp.Eq(eta/(eta-1), (eta/(eta-1)).subs(eta, eta_eq.rhs).simplify())
eta_eq2

eta_eq3 = sp.Eq(1/(eta-1), (1/(eta-1)).subs(eta, eta_eq.rhs).simplify())
eta_eq3

px_eq0 = sp.Eq(x, (1/k)**(al/(2*al-1)) * (p/eta)**(al-1))
px_eq = sp.Eq(x_eq0.lhs, x_eq0.rhs.subs(eta, eta_eq.rhs))
px_eq0

py_eq0 = sp.Eq(y, (1/k)**(al/(2*al-1)) * (p/eta)**((1-al)/(2*al-1)))
py_eq = sp.Eq(x_eq0.lhs, x_eq0.rhs.subs(eta, eta_eq.rhs))
py_eq0

inv_eq = sp.Eq(x**al * y**(1-al), k**al)
inv_eq

y_eq0 = sp.Eq(y, (k/x)**eta)
y_eq = sp.Eq(y_eq0.lhs, y_eq0.rhs.subs(eta, eta_eq.rhs))
y_eq0

y_f1 = sp.solve(inv_eq, y)[0]
y_f1

y_f2 = (k/x)**(al/(1-al))
y_f2

(y_f1-y_f2).simplify()

(y_f1-y_eq.rhs).simplify()

(sp.solve(inv_eq, y)[0]/y_eq.rhs).simplify()

inv_eq.subs(x, px_eq.rhs).subs(y, py_eq.rhs).simplify()


