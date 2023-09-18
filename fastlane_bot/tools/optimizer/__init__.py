"""
encapsulating optimization methods, including convex and marginal price optimization

(c) Copyright Bprotocol foundation 2023. 
Licensed under MIT

================================================================================================
                 Convex and Marginal Price Optimization for Arbitrage and Routing
================================================================================================

This module implements a number of methods that allow for routing* and arbitrage amongst a set
of AMMs. Most methods allow, subject to convergence, for the optimization and routing within
an arbitrary multi-token context. The _subject to convergence_ part is important, as the in 
particular the convex optimization methods with the solvers available to us to do not seem to
be able to handle leveraged liquidity well.

This module is still subject to active research, and comments and suggestions are welcome. 
The corresponding author is Stefan Loesch <stefan@bancor.network>


*routing is not implemented yet, but it is a trivial extension of the arbitrage methods that
only needs to be connected and properly parameterized
"""

from .cpcarboptimizer import *
from .pairoptimizer import PairOptimizer
from .margpoptimizer import MargPOptimizer
from .convexoptimizer import ConvexOptimizer