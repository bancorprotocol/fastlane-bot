r"""
A collection of tools for analyzing AMM invariant functions

This library is independent of fastlane_bot; if you extract it, make sure
you copy the following test notebooks as well.
- NBTest_065_InvariantsDictVector
- NBTest_066_InvariantsFunctions
- NBTest_067_Invariants
- NBTest_068_InvariantsAMM

Corresponding Author: Stefan Loesch <stefan@bancor.network>
Canonic Location: https://github.com/bancorprotocol/fastlane-bot

This package contains a collection of tools for analyzing
AMM invariant functions. The focus of this package lies on
AMMs with hyperbolic invariants, ie invariants of the form

.. math::
    x\cdot y = k

where k is a constant and x,y are -- potentially virtual --
token balances of an AMM. This was the invariant function
used in the first ever AMM, Bancor, and it was taken over by
Uniswap and many others. In levered form it is the invariant
used in Uniswap v3 as well as in Bancor's Carbon. 

The core objects in this package are the `Invariant` and the
`Function` as well as `FunctionVector` objects. 

-   the `Invariant` object describes an invariant in the
    non-isolated form :math:`k=k(x,y)` that is by definition
    available for all invariant based AMMs

-   the `Function` describes the *swap function* 
    :math:`y=f(x,k)` that is obtained from the invariant
    equation by isolating y, which may or may not be
    analytically available for a given invariant.

-   the `FunctionVector` object finally describes a vector
    of `Function` objects, together with an integration
    kernel (see below) thereby effectively defining a vector
    space of functions together with a number of norms.

In addition to those higher level objects, the package also
contains a number of more fundamental objects that are used
as building blocks for those higher level objects. These
include

-   the `Kernel` object represents an *integration kernel*, ie
    a weight function together with a domain of integration;
    this object serves to define :math:`L_p` norms on the
    functions defined above, and therefore ultimately to measure
    distances

-   the `DictVector` object implements sparse vector
    functionality using dicts where the dict keys are
    considered the vector space dimensions, and the values
    the associated coefficients. Note that any allowable
    dict key is a valid dimension.


--- 
(c) Copyright Bprotocol foundation 2024. Licensed under MIT
"""
__VERSION__ = '0.9+'
__DATE__ = "20/Jan/2024+"
