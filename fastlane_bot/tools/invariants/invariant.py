"""
Represents an AMM invariant 

An AMM invariant is a function :math:`k(x, y)` that is constant for all x, y in
the AMM, typically expressed in a form like :math:`x\cdot y = k`. This is
distinct from the swap function :math:`y=f(x, k)` which is obtained from the
invariant by isolating y.

Usually working with the swap function is more convenient. However, in some cases
the invariant can be computed analytically whilst the swap function can not. The
``Invariant`` class -- which is the core class of this module -- allows amongst other
things to estimate the swap function numerically rather than having to solve for
it analytically which may not always be possible.

---
(c) Copyright Bprotocol foundation 2024. 
Licensed under MIT
"""
__VERSION__ = '0.9.1'
__DATE__ = "7/Feb/2024"

#from dataclasses import dataclass, asdict
from .functions import Function, dataclass
from abc import ABC, abstractmethod

@dataclass
class Invariant(ABC):
    """
    Represents an AMM invariant
    
    This class is an abstract base class that represents an arbitrary AMM invariant. In order
    to obtain a usuable invariant object, one must subclass this class and implement the
    ``k_func`` method. For example the following code snippet shows how to implement a simple
    constant product invariant:
    
    .. code-block:: python
        
        class ConstantProductInvariant(Invariant):
            def k_func(self, x, y):
                return x*y
                
        cpi = ConstantProductInvariant()
        cpi.y_func(x=20, k=100)  # returns ~5 (calculated numerically)
        
                
    The constant product invariant is analytically very easy to handle, and therefore a better
    implementation would be to also implement the ``y_Func`` method, which returns the swap function
    as a ``Function`` object. This is shown in the following code snippet:
    
    .. code-block:: python
    
        class ConstantProductSwapFunction(Function):
            def f(self, x):
                return self.k / x
                
        class ConstantProductInvariant2(Invariant):
            def k_func(self, x, y):
                return x*y
            
            YFUNC_CLASS = ConstantProductSwapFunction
            
        cpi = ConstantProductInvariant2()
        cpi.y_func(x=20, k=100)  # returns 5 (calculated analytically)


    """
    __VERSION__ = __VERSION__
    __DATE__ = __DATE__
    

    
    @abstractmethod
    def k_func(self, x, y):
        """
        returns invariant value k = k(x, y)
        """
        pass
    
    YFUNC_CLASS = None
        # override this in a derived class with a Function class returning the
        # swap function as a Function object if the latter is analytically available 
        # self.YFUNC_CLASS(k=k) should return a Function object for y(x; k)
        
    
    def y_Func(self, k):
        """
        returns y = y(x=.; k) as a Function object (may also return None)
        
        USAGE
        
        .. code-block:: python
        
            y_func = y_Func(k=k)
            y = y_func(x)
        """
        if not self.YFUNC_CLASS:
            return None
        return self.YFUNC_CLASS(k=k)
    
    def y_func(self, x, k):
        """
        returns y = y(x,k)
        
        :x:         token balance x
        :k:         pool invariant k
        :returns:   token balance y = y(x, k) (1)
        
        NOTE 1: y is calculated from ``y_Func`` if possible or numerically via
        ``y_func_from_k_func`` otherwise
        """
        y_Func_k = self.y_Func(k=k)
        if not y_Func_k is None:
            return y_Func_k.f(x)
        return self.y_func_from_k_func(x, k)
    
    def p_func(self, x, k):
        """
        returns p = -dy/dx = p(x, k)
        
        :x:         token balance x
        :k:         pool invariant k
        :returns:   price function p = -y'(x, k) (1)
        
        NOTE 1: this currently only works if y_func is analytic, in which case
        the value returned is ``self.y_Func(k=k).p(x)``
        """
        if self.y_func_is_analytic:
            return self.y_Func(k=k).p(x)
        raise NotImplementedError("p_func not implemented for non-analytic y_func")
    
    @property
    def y_func_is_analytic(self):
        """
        whether y_func is obtained as an analytic calculation (ie, not via y_func_from_k_func)
        """
        return not self.YFUNC_CLASS is None
    
    GS_GRADIENT='gradient'
    GS_BISECT='bisect'
    def y_func_from_k_func(self, x, k, *, x0=None, x_lo=None, x_hi=None, method=None):
        """
        solves y = y(x, k) from k = k(x, y)
        
        :x0:            starting estimate (for gradient, default = 1)
        :x_hi:          upper bound (for bisect, default = 1e10)
        :x_lo:          ditto lower (default = 1e-10)
        :method:        one of GS_GRADIENT (default) or GS_BISECT
        """
        if method is None:
            method = self.GS_GRADIENT
        if method == self.GS_GRADIENT:
            if x0 is None:
                x0 = 1
            return self.goalseek_gradient(lambda y: self.k_func(x, y), x0=x0, target=k)
        elif method == self.GS_BISECT:
            if x_lo is None:
                x_lo = 1e-10
            if x_hi is None:
                x_hi = 1e10
            return self.goalseek_bisect(lambda y: self.k_func(x, y), target=k, x_lo=x_lo, x_hi=x_hi)
        else:
            raise ValueError(f"method={method} must be one of self.GS_GRADIENT, self.GS_BISECT")

    class ConvergenceError(ValueError):
        """raised when a goal seek fails to converge"""
        pass
    
    GSGD_TOLERANCE = 1e-6     # absolute tolerance on the y axis
    GSGD_ITERATIONS = 1000    # max iterations
    GSGD_ETA = 1e-10          # relative step size for calculating derivative
    GSGD_H = 1e-6             # used for x=0
    def goalseek_gradient(self, func, target=0, *, x0=1):
        """
        very simple gradient descent implementation for a goal seek
        
        :func:      function for goal seek, eg ``lambda x: x**2-1``
        :target:    target value (default: 0)
        :x0:        starting estimate
        :raises:    ``ConvergenceError`` if it fails to converge
        :returns:   ``x`` such that ``func(x)`` is close to target
        """
        #learning_rate = 0.1  # Learning rate (step size)
        x = x0
        iterations = self.GSGD_ITERATIONS
        tolerance = self.GSGD_TOLERANCE
        h = x0*self.GSGD_ETA if x0 else self.GSGD_H
        #print(f"[goalseek_gradient]: x={x}, y={func(x)}")
        for i in range(iterations):
            y = func(x)
            m = (func(x+h)-func(x-h)) / (2*h)
            x = x + (target-y)/m
            #print(f"[goalseek_gradient] {i}: x={x}, y={func(x)}")
            if abs(func(x)-target) < tolerance:
                #print("[goalseek_gradient] converged (f, crit, tol)", func(x), abs(func(x)-target), tolerance)
                break
        if abs(func(x)-target) > tolerance:
            raise self.ConvergenceError(f"gradient descent failed to converge on {target}")
        return x
    
    GSBS_ITERATIONS = GSGD_ITERATIONS   # max iterations
    GSBS_TOLERANCE = GSGD_TOLERANCE     # absolute tolerance on the y axis
    GSBS_XLO = 1e-10                    # lower bound on x
    GSBS_XHI = 1e10                     # upper bound on x
    def goalseek_bisect(self, func, target=0, *, x_lo=None, x_hi=None):
        """
        bisect implementation for goal seek
        
        :func:      function for goal seek, eg ``lambda x: x**2-1``
        :target:    target value (default: 0)
        :x_lo:      lower bound on x (default: GSBS_XLO=1e-10)
        :x_hi:      upper bound on x (default: GSBS_XHI=1e10)
        :raises:    ``ConvergenceError`` if it fails to converge
        :returns:   ``x`` such that ``func(x)`` is close to target
        """
        if x_lo is None:
            x_lo = self.GSBS_XLO
        if x_hi is None:
            x_hi = self.GSBS_XHI
        if x_lo > x_hi:
            x_lo, x_hi = x_hi, x_lo
        assert x_lo != x_hi, f"x_lo={x_lo} must not be equal to x_hi={x_hi}"
        f = lambda x: func(x)-target
        assert f(x_lo) * f(x_hi) < 0, f"target={target} must be between func(x_lo)={func(x_lo)} and func(x_hi)={func(x_hi)}"
        sgn = 1 if f(x_hi) > 0 else -1
        iterations = self.GSBS_ITERATIONS
        tolerance = self.GSBS_TOLERANCE
        for i in range(iterations):
            x_mid = (x_lo+x_hi)/2
            f_mid = f(x_mid)
            #print(f"[goalseek_bisect] {i}: x_lo={x_lo}, x_hi={x_hi}, x_mid={x_mid}, f={f_mid}")
            if abs(f_mid) < tolerance:
                break
            if f_mid*sgn < 0:
                x_lo = x_mid
            else:
                x_hi = x_mid
        if abs(f_mid) > tolerance:
            raise self.ConvergenceError(f"bisect failed to converge on {target}")
        return x_mid
