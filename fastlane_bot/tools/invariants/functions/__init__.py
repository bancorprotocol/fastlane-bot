"""
object representing a function y = f(x; params) and a vector thereof

(c) Copyright Bprotocol foundation 2024. 
Licensed under MIT
"""
from .core import __VERSION__, __DATE__

# objects defined in core
from .core import Function, FunctionVector
from .core import DerivativeFunction, Derivative2Function
from .core import minimize, goalseek
from .core import fmt

# objects defined in funcs and funcsAMM
from .funcs import *
from .funcsAMM import *

# convenience imports
from .core import Kernel, DictVector, dataclass