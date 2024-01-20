"""
object representing the Bancor (constant product) AMM invariant 

(c) Copyright Bprotocol foundation 2024. 
Licensed under MIT
"""
__VERSION__ = '0.9'
__DATE__ = "18/Jan/2024"

# import decimal as d
# D = d.Decimal
# import math as m

from .invariant import Invariant, dataclass
from .functions import Function

@dataclass(frozen=True)
class BancorSwapFunction(Function):
    """represents the Bancor AMM swap function y(x,k)=k/x"""
    __VERSION__ = __VERSION__
    __DATE__ = __DATE__
    
    k: float
    
    def f(self, x):
        return self.k / x

@dataclass
class BancorInvariant(Invariant):
    """represents the Bancor invariant function"""
    __VERSION__ = __VERSION__
    __DATE__ = __DATE__
    
    def __post_init__(self):
        self._y_Func_class = BancorSwapFunction
    
    def k_func(self, x, y):
        """Bancor invariant function k(x,y)=x*y"""
        return x*y





