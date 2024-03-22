"""
functions library -- example functions

(c) Copyright Bprotocol foundation 2024. 
Licensed under MIT
"""
#__VERSION__    ==> core.__VERSION__
#__DATE__       ==> core.__DATE__

from .core import Function as _Function, dataclass as _dataclass
import math as _m

@_dataclass(frozen=True)
class QuadraticFunction(_Function):
    """quadratic function ``y = ax^2 + bx + c``"""
    a: float = 0
    b: float = 0
    c: float = 0
    
    def f(self, x):
        return self.a*x**2 + self.b*x + self.c
Quadratic=QuadraticFunction

@_dataclass(frozen=True)
class PowerlawFunction(_Function):
    """quadratic function ``y = N*(x-x0)^alpha``"""
    N: float = 1
    alpha: float = -1
    x0: float = 0
    
    def f(self, x):
        return self.N * (x-self.x0)**(self.alpha)
Powerlaw=PowerlawFunction

@_dataclass(frozen=True)
class TrigFunction(_Function):
    """trigonometric function ``y = amp*sin( (omega*x+phase)*pi )``"""
    amp: float = 1
    omega: float = 1
    phase: float = 0
    PI = _m.pi
    
    def f(self, x):
        fx = self.amp * _m.sin( (self.omega*x+self.phase)*self.PI )
        return fx
Trig = TrigFunction

@_dataclass(frozen=True)
class ExpFunction(_Function):
    """exponential function ``y = N*exp(k*(x-x0))``"""
    N: float = 1
    k: float = 1
    x0: float = 0
    E = _m.e
    
    def f(self, x):
        return self.N * _m.exp( self.k*(x-self.x0) )
Exp = ExpFunction

@_dataclass(frozen=True)
class LogFunction(_Function):
    """exponential function ``y = N*log_base(x-x0)``"""
    base: float = 10
    N: float = 1
    x0: float = 0
    E = _m.e
    
    def f(self, x):
        return self.N * _m.log( x-self.x0, self.base )
Log = LogFunction

@_dataclass(frozen=True)
class HyperbolaFunction(_Function):
    """hyperbola function ``y-y0 = k/(x-x0)``"""
    k: float = 1
    x0: float = 0
    y0: float = 0
    
    def f(self, x):
        return self.y0 + self.k/(x-self.x0)
Hyperbola = HyperbolaFunction
