CPC 
===
CPC stands for *ConstantProductCurve*, ie the hyperbolic
curve implied by $xy=k$ when operating an AMM. Whilst this
module is still mostly focused on classes dealing with CPCs
it has been extended to deal with some non-constant-product
AMMs as well.

The key classes defined in the modules are
`ConstantProductCurve` (typically imported as `CPC`) and
`CPCContainer`, the latter being a container object for
multiple CPCs, representing a market, or a segment thereof.

The `CPC` class derives from and abstract base class
`CurveBase`. This class defines the functions that any curve
class that is used in the `Optimizer` module must implement. 

.. automodule:: tools.cpc


CPC
---
version |cpc_vd|

.. autoclass:: ConstantProductCurve
    :members:

CPCContainer
------------
version |cpc_container_vd|

.. autoclass:: CPCContainer
    :members:

CurveBase
---------

.. automodule:: tools.cpcbase
.. autoclass:: CurveBase
    :members:
