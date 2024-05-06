# Invariants Module

## Introduction

The core purpose of this module is to analyze with AMM invariant functions, ie functions of the type $f(x,y) = k$ where $x,y$ are token amounts and $k$ is a constant representing the scale of the AMM. Ignoring fees, the core rule of an AMM is that it is indifferent for any trade that leaves the invariant function unchanged.

The first, and still most popular invariant functions are the constant product invariant functions, which are defined as $f(x,y) = k = xy$. Their key advantage is that they are simple to implement and cheap in gas. Also, if we allow for leverage, ie virtual token balances $x_0, y_0$ so that $f(x,y) = (x_0+x)(y_0+y) = k$, then those functions can be used to approximate other invariant functions, piecewise if need be.

This module has been developed for the use of a FastLane Arbitrage bot where efficient calculation is paramount. When we were trying to implement the Solidly stable swap invariant function $f(x,y) = x^3y + xy^3$ we found that it was not analytically tractable, and that a numeric solution would have been too much of an unnecessary performance hit -- unnecessary in particular because the complexity here lies not in the stable swap part that we are most interested in, but in the wings that we are about less. So we decided to develop a module that would allow us to approximate the invariant function with a piecewise constant product invariant function, and then use the latter to calculate the former.


## Module components

This module consists of the following components that we will discuss in more detail below:

- **vector.py** - a generic vector class that interprets dictionaries as sparse vectors; this class is used below to represent vectors of functions where the function itself is the key of the dictionary and the value is the "length" of the vector in that direction

- **kernel.py** - this module contains a class that represents an (integration) _kernel_ which is a _domain_ $x_{min}\ldots x_{max}$ and a _density_ on that domain that gives a specific weight to every point that is used in the the calculation of scalar products and norms of functions; this module also implements the numerical integration of functions over a kernel

- **functions.py** - this module contains three components: (1) a class that allows to represent generic functions of one variable $x$, (2) a vector class of such functions, and (3) various example functions, including _functional_ ones that allow to modify existing functions, eg calculating their derivative

- **invariants.py** - this module contains a class the represents invariant functions, both in the _invariant format_ $f(x,y) = k$ and in the swap equation format $y = y(x,k)$

- **bancor.py** and **solidly.py** - implementations of Bancor and Solidly invariants and functions

### vector.py 

The `vector` module mostly defines the `DictVector` class. This class interprets a dictionary as a sparse vector, where the keys are the indices and the values are the values of the vector. The class implements the basic vector operations, such as addition, subtraction etc.

### kernel.py

The `kernel` module defines the `Kernel` class. A kernel is a domain $x_{min}\ldots x_{max}$ and a density function $k(x)$ on that domain. The following densities are pre-defined

- **flat** - a constant density
- **triangle** - zero at $x_{min}$ and $x_{max}$, and linearly increasing to a maximum at the midpoint
- **sawtooth** - zero at one side and linearly increasing to a maximum at the other side
- **gaussian** - Gaussian distributions of various sizes within the domain

Note that all pre-defined densities are normalized to unity on the domain $x_{min}\ldots x_{max}$ and they are of course positive. Custom densities _should_ also implement this, but this is not enforced.

### functions.py

#### Function class

The `Function` class represents a function of one variable $x$, and an arbitrary number of parameters. The core definition is the function `f(x)` method that in the base class is an abstract method. The base class then implements various numerical calculations based on `f` that subclasses can either retain, or override with analytical methods if available. Key functions available are:

- `__call__` - alias for `f`
- `df_dx_abs` and `df2_dx2_abs` - the first and second derivatives of the function, calculated with a constant perturbation $h$
- `df_dx_rel` and `df2_dx2_rel` - the first and second derivatives of the function, calculated with a relative ("percentage of $x$") perturbation $\eta$
- `p` - the _price function_, which is $-df/dx$; note the minus sign because exchanges are directed flows, one out and one in, and we want prices to be positive
- `pp` - the price convexity function, which is $-d^2f/dx^2$; again note the minus sign

Actual functions are implemented as frozen dataclasses (frozen so that they can be used as dict keys in the FunctionVector class below). An example of a quadratic function $ax^2 + bx + c$ is given below:

    @dataclass(frozen=True)
    class QuadraticFunction(Function):
        """represents a quadratic function y = ax^2 + bx + c"""
        a: float = 0
        b: float = 0
        c: float = 0
        
        def f(self, x):
            return self.a*x**2 + self.b*x + self.c

Note that this function does not implement any of the derivatives, so the numeric base class methods will be used.

**TODO: EXAMPLE WITH DERIVATIVES**

#### FunctionVector class

The `FunctionVector` class is a `DictVector` where the keys must be `Function` objects. It also contains a `Kernel` object, and in fact vector operations like addition and subtraction are only allowed between object with the same kernel. The class also implements a number of important operations, including integration, norms, root finding, minimization, and plotting.

#### Example functions

Currently the following example functions are implemented:

- `QuadraticFunction` - a quadratic function $ax^2 + bx + c$
- `TrigFunction` - a trigonometric function $\mathrm{ampl}\cdot\sin(\frac{\omega x + \mathrm{phase}}{\pi})$
- `HyperbolaFunction` - a hyperbolic function $y-y_0 = \frac{k}{x-x_0}$

It also implements the following functional functions:

- `DerivativeFunction` - the derivative of any Function object
- `Derivative2Function` - ditto second derivative

### invariant.py

## Usage examples

Usage examples for almost all use cases for which those modules were designed can be found in the various Jupyter notebooks in the _resources/analysis/202401 Solidly_ directory