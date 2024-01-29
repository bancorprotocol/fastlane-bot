"""
object representing a function y = f(x; params)

(c) Copyright Bprotocol foundation 2024. 
Licensed under MIT
"""
__VERSION__ = '0.9'
__DATE__ = "18/Jan/2024"

from dataclasses import dataclass, asdict
from abc import ABC, abstractmethod
import math as m
import numpy as np
import matplotlib.pyplot as plt
from inspect import signature

from .vector import DictVector
from .kernel import Kernel

@dataclass(frozen=True)
class Function(ABC):
    """
    represent a function y = f(x; params)
    
    EXAMPLE USAGE
    
        import functions as f
        
        @f.dataclass
        class MyFunction(f.Function):
            k: float = 1
        
            def f(self, x):
                return (m.sqrt(1+x)-1)*self.k
        
        mf = MyFunction(k=2)
        mf(1)       # 0.4142
        mf.p(1)     # 0.3536
        mf.pp(1)    # -0.0883
    """
    __VERSION__ = __VERSION__
    __DATE__ = __DATE__
    
    DERIV_H = 1e-6          # step size for absolute derivative calculation
    DERIV_ETA = 1e-4        # ditto relative
    DERIV_IS_ABS = False    # whether p, pp uses absolute or relative step size
    
    @abstractmethod
    def f(self, x):
        """
        return y = f(x; k)
        """
        pass
    
    def df_dx_abs(self, x, *, h=None, precision=None):
        """
        calculates the derivative of f(x) at x with abs step size h*precision
        """
        if h is None:
            h = self.DERIV_H
        if precision:
            h *= precision
        return (self.f(x+h)-self.f(x-h)) / (2*h)
    
    def d2f_dx2_abs(self, x, *, h=None, precision=None):
        """
        calculates the second derivative of f(x) at x with abs step size h*precision
        """
        if h is None:
            h = self.DERIV_H
        if precision:
            h *= precision
        return (self.f(x+h)+self.f(x-h)-2*self.f(x)) / (h*h)
    
    def df_dx_rel(self, x, *, eta=None, precision=None):
        """
        calculates the derivative of f(x) at x with relative step size eta (h=x*eta*precision)
        """
        if eta is None:
            eta = self.DERIV_ETA
        return self.df_dx_abs(x, h=x*eta if x else None, precision=precision)
    
    def d2f_dx2_rel(self, x, *, eta=None, precision=None):
        """
        calculates the second derivative of f(x) at x with relative step size eta (h=x*eta*precision)
        """
        if eta is None:
            eta = self.DERIV_ETA
        return self.d2f_dx2_abs(x, h=x*eta if x else None, precision=precision)
    
    def p(self, x, *, precision=None):
        """alias for -f prime = -df_dx_xxx"""
        if self.DERIV_IS_ABS:
            return -self.df_dx_abs(x, precision=precision)
        else:
            return -self.df_dx_rel(x, precision=precision)
    
    def df_dx(self, x, *, precision=None):
        """alias for df_dx_xxx, equals to -p"""
        return -self.p(x, precision=precision)
    
    def pp(self, x, *, precision=None):
        """alias for -f prime prime = -d2f_dx2_xxx"""
        if self.DERIV_IS_ABS:
            return -self.d2f_dx2_abs(x, precision=precision)
        else:
            return -self.d2f_dx2_rel(x, precision=precision)
    
    def p_func(self, *, precision=None):
        """returns the derivative as a function object"""
        return DerivativeFunction(self, precision=precision)
    
    def pp_func(self, *, precision=None):
        """returns the second derivative as a function object"""
        return Derivative2Function(self, precision=precision)
    
    def params(self):
        """
        returns the parameters of the function as a dictionary
        """
        return asdict(self)
    
    def update(self, **kwargs):
        """
        returns a copy of the function, with the given parameters updated
        
        :kwargs:    parameters to update
        """
        params = {**self.params(), **kwargs}
        return self.__class__(**params)
    
    def __call__(self, x):
        """
        alias for self.f(x)
        """
        return self.f(x)

@dataclass(frozen=True)
class QuadraticFunction(Function):
    """represents a quadratic function y = ax^2 + bx + c"""
    a: float = 0
    b: float = 0
    c: float = 0
    
    def f(self, x):
        return self.a*x**2 + self.b*x + self.c

@dataclass(frozen=True)
class TrigFunction(Function):
    """represents a trigonometric function y = amp*sin( (omega*x+phase)*pi )"""
    amp: float = 1
    omega: float = 1
    phase: float = 0
    PI = m.pi
    
    def f(self, x):
        fx = self.amp * m.sin( (self.omega*x+self.phase)*self.PI )
        #print(f"x={x}, f(x) = {fx}, sin({(self.omega*x+self.phase)*self.PI})")
        return fx

@dataclass(frozen=True)
class HyperbolaFunction(Function):
    """represents a hyperbolic function y-y0 = k/(x-x0)"""
    k: float = 1
    x0: float = 0
    y0: float = 0
    
    def f(self, x):
        return self.y0 + self.k/(x-self.x0)

@dataclass(frozen=True)
class DerivativeFunction(Function):
    """represents a derivative function y = f'(x)"""
    func: Function
    precision: float = None
    
    def __post_init__(self):
        assert isinstance(self.func, Function), "f must be a Function"
        if not self.precision is None:
            self.precision = float(self.precision)
    
    def f(self, x):
        """the derivative f'(x) of self.func(x)"""
        return self.func.p(x, precision=self.precision)  
    
@dataclass(frozen=True)
class Derivative2Function(Function):
    """represents a second derivative function y = f''(x)"""
    func: Function
    precision: float = None
    
    def __post_init__(self):
        assert isinstance(self.func, Function), "f must be a Function"
        if not self.precision is None:
            self.precision = float(self.precision)
    
    def f(self, x):
        """the second derivative f''(x) of self.func(x)"""
        return self.func.pp(x, precision=self.precision)  
    
    
@dataclass
class FunctionVector(DictVector):
    """a vector of functions"""
    __VERSION__ = __VERSION__
    __DATE__ = __DATE__
    
    kernel: Kernel = None
    
    def __post_init__(self):
        super().__post_init__()
        assert all([isinstance(v, Function) for v in self.vec.keys()]), "all keys must be of type Function"
        if self.kernel is None:
            self.kernel = Kernel()  
            
    def wrap(self, func):
        """creates a FunctionVector from a function using the same kernel as self"""
        assert isinstance(func, Function), "func must be of type Function"
        return self.__class__({func: 1}, kernel=self.kernel)
            
    def __eq__(self, other):
        funcs_eq = super().__eq__(other)
        kernel_eq = self.kernel == other.kernel
        print(f"[FunctionVector::eq] called; funcs_eq={funcs_eq}, kernel_eq={kernel_eq}")
        return funcs_eq and kernel_eq  
    
    def f(self, x):
        """
        returns \sum_i vec[i] * f_i(x) where f_i is actually the dict key
        """
        return sum([f(x) * v for f, v in self.vec.items()])
    
    def f_r(self, x):
        """alias for self.restricted(self.f, x)"""
        return self.restricted(self.f, x)
    
    def f_k(self, x):
        """alias for self.apply_kernel(self.f, x)"""
        return self.apply_kernel(self.f, x)
    
    def __call__(self, x):
        """
        alias for f(x)
        """
        return self.f(x)
    
    def p(self, x):
        """
        returns \sum_i vec[i] * f'_i(x) where f'_i is the p method of the dict key
        """
        return sum([F.p(x) * v for F, v in self.vec.items()])
    
    def df_dx(self, x):
        """
        like p, but the actual derivative, not its negative
        """
        return -self.p(x)
    
    def pp(self, x):
        """
        returns \sum_i vec[i] * f''_i(x) where f''_i is the pp method of the dict key
        """
        return sum([F.pp(x) * v for F, v in self.vec.items()])
    
    def restricted(self, func, x=None):
        """
        returns func(x) restricted to the domain of self.kernel (as value or lambda if x is None)
        
        USAGE
        
        this function can either be called directly
        
            fv = FunctionVector(...)
            fv.restricted(func, x) # ==> value
            
        or be used to create a new function
        
            fv = FunctionVector(...)
            func_restricted = fv.restricted(func) # ==> lambda 
        """
        f = lambda x: func(x) if self.kernel.in_domain(x) else 0
        if x is None:
            return f
        return f(x)
    
    def apply_kernel(self, func, x=None):
        """
        returns func multiplied by the kernel value (as value or lambda if x is None)
        
        USAGE
        
        this function can either be called directly
        
            fv = FunctionVector(...)
            fv.apply_kernel(func, x) # ==> value
            
        or be used to create a new function
        
            fv = FunctionVector(...)
            func_kernel = fv.apply_kernel(func) # ==> lambda 
        """
        f = lambda x: func(x) * self.kernel(x)
        if x is None:
            return f
        return f(x)
    

    GS_TOLERANCE = 1e-6     # absolute tolerance on the y axis
    GS_ITERATIONS = 1000    # max iterations
    GS_ETA = 1e-10          # relative step size for calculating derivative
    GS_H = 1e-6             # used for x=0
    def integrate_func(self, func=None, *, steps=None, method=None):
        """integrates func (default: self.f) using the kernel"""
        if func is None:
            func = self.f
        return self.kernel.integrate(func, steps=steps, method=method)
        
    def integrate(self, *, steps=None, method=None):
        """integrates self.f using the kernel [convenience access for integrate_func(func=None)]"""
        return self.integrate_func(func=self.f, steps=steps, method=method) 
    
    def distance2(self, func=None, *, steps=None, method=None):
        """calculates the distance^2 between self and func (L2 norm)"""
        #if func is None: func = lambda x: 0
        #kernel = self.kernel if not ignore_kernel else lambda x: 1
        #f = lambda x: (self.f(x)-func(x))**2 * kernel(x)
        if not func is None:
            f = lambda x: (self.f(x)-func(x))**2 * self.kernel(x)
        else:
            f = lambda x: self.f(x)**2 * self.kernel(x)
        return self.integrate_func(func=f, steps=steps, method=method)
    
    def distance(self, func=None, *, steps=None, method=None):
        """calculates the distance between self and func (L2 norm)"""
        return m.sqrt(self.distance2(func=func, steps=steps, method=method))

    def norm2(self, *, steps=None, method=None):
        """calculates the norm^2 of self (L2 norm)"""
        return self.distance2(func=None, steps=steps, method=method)
    
    def norm(self, *, steps=None, method=None):
        """calculates the norm of self (L2 norm)"""
        return m.sqrt(self.norm2(steps=steps, method=method))
    
    def goalseek(self, target=0, *, x0=1):
        """
        very simple gradient descent implementation for a goal seek
        
        :target:    target value (default: 0)
        :x0:        starting estimate
        """
        x = x0
        iterations = self.GS_ITERATIONS
        tolerance = self.GS_TOLERANCE
        h = x0*self.GS_ETA if x0 else self.GS_H
        func = self.f
        for i in range(iterations):
            y = func(x)
            m = (func(x+h)-func(x-h)) / (2*h)
            x = x + (target-y)/m
            if abs(func(x)-target) < tolerance:
                break
        if abs(func(x)-target) > tolerance:
            raise ValueError(f"gradient descent failed to converge on {target}")
        return x
    
    MM_LEARNING_RATE = 0.2
    MM_ITERATIONS = 1000
    MM_TOLERANCE = 1e-3
    def minimize1(self, *, x0=1, learning_rate=None, iterations=None, tolerance=None):
        """
        minimizes the function using gradient descent
        
        :x0:        starting estimate (float)
        """
        if learning_rate is None:
            learning_rate = self.MM_LEARNING_RATE
        if tolerance is None:
            tolerance = self.MM_TOLERANCE
        x = x0
        for i in range(iterations or self.MM_ITERATIONS):
            x -= learning_rate * self.df_dx(x)
            #print(f"[minimize1] {i}: x={x}, gradient={self.p(x)}")
            if abs(self.p(x)) < tolerance:
                break
        if abs(self.p(x)) < tolerance:
            return x
        raise ValueError(f"gradient descent failed to converge")
    
    @staticmethod
    def e_i(i, n):
        """returns the i'th unit vector of size n"""
        result = np.zeros(n)
        result[i] = 1
        return result
    
    @staticmethod
    def e_k(k, dct):
        """returns the unit vector of key k in dct"""
        return {kk: 1 if kk==k else 0 for kk in dct.keys()}
    
    @staticmethod
    def bump(dct, k, h):
        """bumps dct[k] by +h; everthing else unmodified (returns a new dict)"""
        return {kk: v+h if kk==k else v for kk,v in dct.items()}
    
    MM_DERIV_H = 1e-6
    @classmethod
    def minimize(cls, func, *, 
                x0=None, 
                learning_rate=None, 
                iterations=None, 
                tolerance=None, 
                deriv_h=None, 
                return_path=False
        ):
        """
        minimizes the function `func` using gradient descent (multiple dimensions)
        
        :func:              function to be minimized
        :x0:                starting point (np.array-like or dct*)
        :learning_rate:     optimization parameter (float; default cls.MM_LEARNING_RATE)
        :iterations:        max iterations (int; default cls.MM_ITERATIONS)
        :tolerance:         convergence tolerance (float; default cls.MM_TOLERANCE)
        :deriv_h:           step size for derivative calculation (float; default cls.MM_DERIV_H)
        :return_path:       if True, returns the entire optimization path (list of np.array)
                            as well as the last dfdx (np.array); in this case, the result is 
                            the last element of the path
        
        *if x0 is np=array-like or None, then func will be called with positional arguments
        and the result will be returned as an np.array. if x0 is a dict, then func will be
        called with keyword arguments and the result will be returned as a dict
        """
        n = len(signature(func).parameters)
        x0 = x0 or np.ones(n)
        if not isinstance(x0, dict):
            assert len(x0) == n, f"x0 must be of size {n}, it is {len(x0)}"
        else:
            try:
                func(**x0)
            except Exception as e:
                #raise ValueError(f"failed to call func with x0={x0}") from e
                raise
        
        learning_rate = learning_rate or cls.MM_LEARNING_RATE
        tolerance = tolerance or cls.MM_TOLERANCE
        deriv_h = deriv_h or cls.MM_DERIV_H
        iterations = iterations or cls.MM_ITERATIONS
        tol_squared = tolerance**2
        
        # that's where the magic happens
        _minimize = cls._minimize_dct if isinstance(x0, dict) else cls._minimize_lst
        path, dfdx, norm2_dfdx = _minimize(func, x0, learning_rate, iterations, tol_squared, deriv_h)
        
        if return_path:
            return path, dfdx
        if norm2_dfdx < tol_squared:
            return path[-1]
        raise ValueError(f"gradient descent failed to converge")
    
    @classmethod
    def _minimize_lst(cls, func, x0, learning_rate, iterations, tol_squared, deriv_h):
        """
        executes the minimize algorithm when the x-values are in a list
        
        :returns:  tuple(path, dfdx, norm2_dfdx); result is path[-1]
        """
        x = np.array(x0, dtype=float)
        n = len(x)
        path = [tuple(x)]
        #print(f"[_minimize_lst] x0={x}")
        for iteration in range(iterations):
            f0 = func(*x)
            dfdx = np.array([
                (func( *(x+deriv_h*cls.e_i(i, n)) ) - f0) / deriv_h 
                for i in range(len(x))
            ])
            x -= learning_rate * dfdx
            path.append(tuple(x))
            #print(f"[_minimize_lst] {iteration}: adding x={x}, gradient={dfdx}")  
            norm2_dfdx = np.dot(dfdx, dfdx)
            if norm2_dfdx < tol_squared:
                break
        return path, dfdx, norm2_dfdx
    
    @classmethod
    def _minimize_dct(cls, func, x0, learning_rate, iterations, tol_squared, deriv_h):
        """
        executes the minimize algorithm when the x-values are in a dict
        
        :returns:  tuple(path, dfdx, norm2_dfdx); result is path[-1]
        """
        x = {**x0}
        path = [{**x}   ]
        #print(f"[_minimize_dct] x0={x}")
        for iteration in range(iterations):
            f0 = func(**x)
            dfdx = {
                k: (func( **(cls.bump(x, k, deriv_h)) ) - f0) / deriv_h 
                for k in x.keys()
            }
            x = {k: x[k] - learning_rate * dfdx[k] for k in x.keys()}
            path.append({**x})
            #print(f"[_minimize_dct] {iteration}: adding x={x}, gradient={dfdx}") 
            norm2_dfdx = sum(vv**2 for vv in dfdx.values())  
            if norm2_dfdx < tol_squared:
                break
        return path, dfdx, norm2_dfdx
    
    def curve_fit(self, func, params0, **kwargs):
        """
        fits a function to self using gradient descent
        
        :func:          function to fit (typically a Function object)*
        :params0:       starting parameters (dict)*
        :kwargs:        passed to self.minimize
        :returns:       the parameters of the fitted function (dict)
        
        *The func object must have and update method that accepts a dict of parameters
        with the keys of `params0` and returns a new object with the updated parameters.
        """
        
        def optimizer_func(**params):
            func1 = func.update(**params)
            return self.distance2(func=func1)
        
        return self.minimize(optimizer_func, x0=params0, **kwargs)
        
    def plot(self, func=None, *, x_min=None, x_max=None, steps=None, title=None, xlabel=None, ylabel=None, grid=True, show=True, **kwargs):
        """
        plots the function
        
        :func:      function to plot (default: self.f_r)
        :x_min:     lower bound (default: self.kernel.x_min)
        :x_max:     upper bound (default: self.kernel.x_max)
        :steps:     number of steps (default: np.linspace defaults)
        :show:      whether to call plt.show() (default: True)
        :grid:      whether to show a grid (default: True)
        :returns:   the result of plt.plot
        """
        func = func or self.f_r
        x_min = x_min or self.kernel.x_min
        x_max = x_max or self.kernel.x_max
        x = np.linspace(x_min, x_max, steps) if steps else np.linspace(x_min, x_max)
        y = [func(x) for x in x]
        plot = plt.plot(x, y, **kwargs)
        if title: plt.title(title)
        if xlabel: plt.xlabel(xlabel)
        if ylabel: plt.ylabel(ylabel)
        if grid: plt.grid(True)
        if show: plt.show()
        return plot
    
    # def __add__(self, other):
    #     assert self.kernel == other.kernel, "kernels must be equal"
    #     result = super().__add__(other)
    #     result.kernel = self.kernel
    #     return result
    
    # def __sub__(self, other):
    #     assert self.kernel == other.kernel, "kernels must be equal"
    #     result = super().__sub__(other)
    #     result.kernel = self.kernel
    #     return result
    
    def _kwargs(self, other=None):
        if not other is None:
            assert self.kernel == other.kernel, f"kernels must be equal {self.kernel} != {other.kernel}"
        return dict(kernel=self.kernel)
    
minimize = FunctionVector.minimize
    
    
    
    