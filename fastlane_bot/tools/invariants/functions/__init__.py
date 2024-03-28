"""
Represents a function ``y = f(x; params)`` and vectors thereof

This module contains two classes, ``Function`` and ``FunctionVector``. 

-   The ``Function`` class represents a function of the form ``y = f(x; params)``,
    where ``x`` is the input value and ``params`` are arbitrary additional
    parameters fed into the (data)class upon instantiation.

-   The ``FunctionVector`` class represents a vector (linear combination) of
    ``Function`` objects, and implements a function interface (via pointwise
    evaluation), a vector interface (from the ``DictVector`` inheritance). A
    ``FunctionVector`` also contains an integration kernel, which allows it to
    expose a number of norms and distance measures.
    
TODO: other imported objects eg ``DerivativeFunction``, ``Derivative2Function``

---
(c) Copyright Bprotocol foundation 2024. 
Licensed under MIT
"""
from .core import __VERSION__, __DATE__

# objects defined in core
from .core import Function, FunctionVector
from .core import PriceFunction, Price2Function
from .core import minimize, goalseek
from .core import fmt

# objects defined in funcs and funcsAMM
from .funcs import *
from .funcsAMM import *

# convenience imports
from .core import Kernel, DictVector, dataclass