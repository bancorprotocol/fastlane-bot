"""
object representing an AMM invariant 

(c) Copyright Bprotocol foundation 2024. 
Licensed under MIT
"""
__VERSION__ = '0.9'
__DATE__ = "18/Jan/2024"

#from dataclasses import dataclass, asdict
from .functions import Function, dataclass
from abc import ABC, abstractmethod

@dataclass
class Invariant(ABC):
    """represents an AMM invariant function"""
    __VERSION__ = __VERSION__
    __DATE__ = __DATE__
    
    @abstractmethod
    def k_func(self, x, y):
        """
        returns invariant value k = k(x, y)
        """
        pass
    
    def y_Func(self, k):
        """
        returns y = y(x=.; k) as a Function object (may also return None)
        
        USAGE
        
            y_func = y_Func(k=k)
            y = y_func(x)
        """
        y_Func_class = getattr(self, '_y_Func_class', None)
        if not y_Func_class:
            return None
        return y_Func_class(k=k)
    
    def y_func(self, x, k):
        """
        returns y = y(x,k), from y_Func if present or via y_func_from_k_func otherwise
        """
        y_Func_k = self.y_Func(k=k)
        if not y_Func_k is None:
            return y_Func_k.f(x)
        return self.y_func_from_k_func(x, k)
    
    def p_func(self, x, k):
        """returns p = dy/dx = p(x, k)"""
        if self.y_func_is_analytic:
            return self.y_Func(k=k).p(x)
        raise NotImplementedError("p_func not implemented for non-analytic y_func")
    
    @property
    def y_func_is_analytic(self):
        """
        whether y_func is obtained as an analytic calculation (ie, not via y_func_from_k_func)
        """
        return not self.y_Func is None
    
    GS_GRADIENT='gradient'
    GS_BISECT='bisect'
    def y_func_from_k_func(self, x, k, *, x0=None, x_lo=None, x_hi=None, method=None):
        """
        solves y = y(x, k) from k = k(x, y)
        
        :x0:            starting estimate (for gradient)
        :x_lo, x_hi:    lower and upper bounds (for bisect)
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

    GSGD_TOLERANCE = 1e-6     # absolute tolerance on the y axis
    GSGD_ITERATIONS = 1000    # max iterations
    GSGD_ETA = 1e-10          # relative step size for calculating derivative
    GSGD_H = 1e-6             # used for x=0
    def goalseek_gradient(self, func, target=0, *, x0=1):
        """
        very simple gradient descent implementation for a goal seek
        
        :target:    target value (default: 0)
        :x0:        starting estimate
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
            raise ValueError(f"gradient descent failed to converge on {target}")
        return x
    
    GSBS_ITERATIONS = GSGD_ITERATIONS   # max iterations
    GSBS_TOLERANCE = GSGD_TOLERANCE     # absolute tolerance on the y axis
    GSBS_XLO = 1e-10                    # lower bound on x
    GSBS_XHI = 1e10                     # upper bound on x
    def goalseek_bisect(self, func, target=0, *, x_lo=None, x_hi=None):
        """
        bisect implementation for goal seek
        
        :target:    target value (default: 0)
        :x_lo:      lower bound on x (default: GSBS_XLO=1e-10)
        :x_hi:      upper bound on x (default: GSBS_XHI=1e10)
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
            raise ValueError(f"bisect failed to converge on {target}")
        return x_mid
