"""
Optimization methods for AMM routing and arbitrage

This module implements a number of methods that allow for
routing (1) and arbitrage amongst a set of AMMs. Most
methods allow, subject to convergence, for the optimization
and routing within an arbitrary multi-token context. The
*subject to convergence* part is important, as in particular
the convex optimization methods with the solvers available
to us to do not seem to be able to handle leveraged
liquidity well. Specifically, the following algorithms are
implemented:

-   **Marginal Price Optimization**: a highly efficient
    robust and efficient optimization method developed by us
    specifically for the Fastlane Bot; it is based on the
    insight that in any optimal state, the marginal prices
    of all curves must be consistent, and therefore to
    optimize the state of the entire market we only have to
    look at all possibly marginal prices, which is a much
    smaller set than all possible AMM states

-   **Pair Optimization**: the predecessor of the Marginal
    Price Optimization method in the context of *pairs*,
    meaning that we only look at AMMs trading one specific
    pair; in this case the optimization algorithm is a
    one-dimensional goal seek, and using a multi-dimensional
    Newtown-Raphson method is overkill in this case

-   **Convex Optimization**: this method is based on a paper
    by Angeris et al (2), showing that routing and arbitrage
    of AMMs are convex optimization problems; this is a very
    interesting approach and works very well for unlevered
    curves. However, for levered curves (Carbon, Uniswap v3)
    we ran into convergence issues which is why we moved on 
    to the marginal price method

Marginal price optimization is implemented in the class
``MargPOptimizer``, pair optimization in the class
``PairOptimizer``, and convex optimization in the class
``ConvexOptimizer``. All those classes are subclasses of
``CPCArbOptimizer``, and ultimately of ``OptimizerBase``.


NOTE 1: routing is not implemented yet, but it is a trivial
extension of the arbitrage methods that only needs to be
connected and properly parameterized

NOTE 2: https://angeris.github.io/papers/cfmm-chapter.pdf

This module is still subject to active research, and
comments and suggestions are welcome. The corresponding
author is Stefan Loesch <stefan@bancor.network>

---
(c) Copyright Bprotocol foundation 2023. 
Licensed under MIT.
"""

from .cpcarboptimizer import *
from .pairoptimizer import PairOptimizer
from .margpoptimizer import MargPOptimizer
from .convexoptimizer import ConvexOptimizer