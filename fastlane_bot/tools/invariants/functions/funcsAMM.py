"""
functions library -- AMM-related example functions

(c) Copyright Bprotocol foundation 2024. 
Licensed under MIT
"""
#__VERSION__    ==> core.__VERSION__
#__DATE__       ==> core.__DATE__

from .core import Function as _Function, dataclass as _dataclass
import math as _m

@_dataclass(frozen=True)
class CPMMFunction(_Function):
    """constant product market maker function y = k/x"""
    k: float = 1
    
    def f(self, x):
        return self.k/x
    
    def p(self, x):
        return self.k/x**2
    
    def pp(self, x):
        return -2*self.k/x**3
CPMM = CPMMFunction
UniV2 = CPMMFunction
BancorV21 = CPMMFunction
BancorV3 = CPMMFunction
