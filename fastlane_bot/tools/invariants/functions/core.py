"""
functions library -- core objects (Function, FunctionVector)

(c) Copyright Bprotocol foundation 2024. 
Licensed under MIT
"""
__VERSION__ = '0.9.7'
__DATE__ = "21/Mar/2024"

from dataclasses import dataclass, asdict
from abc import ABC, abstractmethod
import math as m
import numpy as np
import matplotlib.pyplot as plt
from inspect import signature

from ..vector import DictVector
from ..kernel import Kernel

def _fmt(x, format_string, as_float=True):
    """formats as float (if possible and requested)"""
    if as_float:
        try: x = float(x)
        except: pass
    try: x = format(x, format_string)
    except: pass
    if as_float:
        try: x = float(x)
        except: pass
    return x
    
def fmt(dct_or_list, format_string=None, as_float=True):
    """format dct key=>value -> key: str"""
    format_string = format_string or ".4f"
    if isinstance(dct_or_list, dict):
        return {key: _fmt(value, format_string, as_float) for key, value in dct_or_list.items()}
        #return {key: fmt2(format(fmt2(value), format_string)) for key, value in dct_or_list.items()}
    else: 
        return [_fmt(value, format_string, as_float) for value in dct_or_list]
        #return [fmt2(format(fmt2(value), format_string)) for value in dct_or_list]


##############################################################################
## CLASS FUNCTION  
@dataclass(frozen=True)
class Function(ABC):
    r"""
    Represents a function ``y = f(x; params)``
    
    The Function class is an abstract base class that represents an arbitrary
    function of the form ``y = f(x; params)``. The function is inserted into the
    object via overriding the ``f`` method, and the parameters are inserted via
    the (data)class constructor. The class also exposes a number of methods and
    properties that are useful for analyzing the function, notably the first
    and second derivate and the so-called price function :math:`p(x) = -f'(x)`.
    
    
    The below example shows how to implement the function
    
    .. math::
    
        f_k(x) = \left(\sqrt{1+x} - 1\right)*k
    
    .. code-block:: python
    
        import functions as f
        
        @f.dataclass(frozen=True)
        class MyFunction(f.Function):
            k: float = 1
        
            def f(self, x):
                return (m.sqrt(1+x)-1)*self.k
        
        mf = MyFunction(k=2)
        mf(1)       # 0.4142
        mf.p(1)     # 0.3536
        mf.df_dx(1) # -0.3536
        mf.pp(1)    # -0.0883
        
    For functions where we know the derivatives analytically, we can override
    the ``p`` and ``pp`` methods (we should not usually touch ``df_dx`` as it refers
    back to ``p`` in a trivial manner). The below implements a simple hyperbolic
    function to the type found in an AMM:

    .. code-block:: python
    
        import functions as f
        
        @f.dataclass(frozen=True)
        class HyperbolaFunction(f.Function):
        
            k: float = 1
            
            def f(self, x):
                return self.k/x
            
            def p(self, x):
                return -self.k/(x*x)
                
            def pp(self, x):
                return 2*self.k/(x*x*x)
    
    Note that we are using *frozen* dataclasses here which allows us to use those
    functions as keys in a dict, which we will make use of in the `FunctionVector`
    class derived. If you need to change an attribute in a frozen class you can
    do so using the following trick:
    
    .. code-block:: python
    
        super().__setattr__('k', 2)     # changes k to 2 despite the class being frozen
    """
    __VERSION__ = __VERSION__
    __DATE__ = __DATE__
    
    DERIV_H = 1e-6          # step size for absolute derivative calculation
    DERIV_ETA = 1e-4        # ditto relative
    DERIV_IS_ABS = False    # whether p, pp uses absolute or relative step size
    
    @abstractmethod
    def f(self, x):
        """
        returns ``y = f(x; k)`` [to be implemented by subclass]
        
        :x:             input value x (token balance)
        :returns:       output value y (other token balance)
        
        this function must be implemented by the subclass as
        it specifies the actual function other parameters --
        notably the pool constant ``k`` -- will usually be parts
        of the (dataclass) constructor
        """
        pass
    
    def df_dx_abs(self, x, *, h=None, precision=None):
        """
        calculates the derivative of ``f(x)`` at ``x`` with absolute step size ``h*precision``
        """
        if h is None:
            h = self.DERIV_H
        if precision:
            h *= precision
        try:
            #print("[df_dx_abs] trying double-sided")
            return (self.f(x+h)-self.f(x-h)) / (2*h)
        except TypeError:
            try:
                #print(f"[df_dx_abs] double-sided failed, trying top (x={x})")
                return (self.f(x+h)-self.f(x)) / h
            except TypeError:
                try:
                    #print(f"[df_dx_abs] top failed, trying bottom (x={x})")
                    return (self.f(x)-self.f(x-h)) / h
                except TypeError:
                    #print(f"[df_dx_abs] all failed (x={x})")
                    return None
    
    def d2f_dx2_abs(self, x, *, h=None, precision=None):
        """
        calculates the second derivative of f(x) at x with abs step size h*precision
        """
        if h is None:
            h = self.DERIV_H
        if precision:
            h *= precision
        try:
            return (self.f(x+h)-2*self.f(x)+self.f(x-h)) / (h*h)
        except TypeError: # None values
            return None
        
    def df_dx_rel(self, x, *, eta=None, precision=None):
        """
        calculates the derivative of ``f(x)`` at ``x`` with relative step size ``eta`` (``h=x*eta*precision``)
        """
        if eta is None:
            eta = self.DERIV_ETA
        return self.df_dx_abs(x, h=x*eta if x else None, precision=precision)
    
    def d2f_dx2_rel(self, x, *, eta=None, precision=None):
        """
        calculates the second derivative of ``f(x)`` at ``x`` with relative step size ``eta`` (``h=x*eta*precision``)
        """
        if eta is None:
            eta = self.DERIV_ETA
        return self.d2f_dx2_abs(x, h=x*eta if x else None, precision=precision)
    
    def p(self, x, *, precision=None):
        """
        price function (alias for ``-df_dx_xxx``)
        
        Note: this function CAN be overridden by the subclass if it can be
        calculated analytically in this case the precision parameter should be
        ignored
        """
        try:
            if self.DERIV_IS_ABS:
                return -self.df_dx_abs(x, precision=precision)
            else:
                return -self.df_dx_rel(x, precision=precision)
        except TypeError:
            return None
    
    def df_dx(self, x, *, precision=None):
        """
        first derivative (alias  for ``-p``)
        
        note: this function calls ``p`` and it should not be overridden
        """
        try:
            return -self.p(x, precision=precision)
        except TypeError:
            return None
    
    def pp(self, x, *, precision=None):
        """
        derivative of the price function (alias for ``-d2f_dx2_xxx``)
        
        Note: this function does not call `p` but goes via ``d2f_dx2_xxx``; if ``p``
        is overrriden then it may make sense to override this function as well
        """
        try:
            if self.DERIV_IS_ABS:
                return -self.d2f_dx2_abs(x, precision=precision)
            else:
                return -self.d2f_dx2_rel(x, precision=precision)
        except TypeError:
            return None
    
    def p_func(self, *, precision=None):
        """returns the derivative as a function object"""
        return PriceFunction(self, precision=precision)
    
    def pp_func(self, *, precision=None):
        """returns the second derivative as a function object"""
        return Price2Function(self, precision=precision)
    
    def params(self, *, classname=False):
        """
        returns the parameters of the function as a dictionary
        
        :classname:    if True, includes the class name in the dict (default: False)
        """
        result = asdict(self)
        if classname:
            result["_classname"] = self.__class__.__name__
        return result
    
    def update(self, **kwargs):
        """
        returns a copy of the function, with the given parameters updated
        
        :kwargs:    parameters to update
        """
        params = {**self.params(), **kwargs}
        try:    del params["_classname"]
        except  KeyError: pass
        return self.__class__(**params)
    
    def __call__(self, x):
        """
        alias for self.f(x)
        """
        return self.f(x)
    
    PLT_STEPS = 100
    PLT_SHOW = False
    PLT_GRID = True
    def plot(self, x_min, x_max, func=None, *, steps=None, title=None, xlabel=None, ylabel=None, grid=None, show=None, **kwargs):
        """
        plots the function ``func`` (default: ``self.f``) over the interval [``x_min``, ``x_max``]
        
        :x_min:     lower bound
        :x_max:     upper bound
        :func:      function to plot (default: ``self.f``)
        :steps:     number of steps (default: PLT_STEPS or ``np.linspace`` defaults)
        :show:      whether to call ``plt.show()`` (default: PLT_SHOW)
        :grid:      whether to show a grid (default: PLT_GRID)
        :returns:   the result of ``plt.plot``
        """
        if xlabel is None: xlabel = "x"
        if ylabel is None and func is None: ylabel = "y"
        func = func or self.f
        if show is None: show = self.PLT_SHOW
        if grid is None: grid = self.PLT_GRID
        steps = steps or self.PLT_STEPS
        x = np.linspace(x_min, x_max, steps) if steps else np.linspace(x_min, x_max)
        y = [func(x) for x in x]
        plot = plt.plot(x, y, **kwargs)
        if title: plt.title(title)
        if xlabel: plt.xlabel(xlabel)
        if ylabel: plt.ylabel(ylabel)
        if grid: plt.grid(True)
        if show: plt.show()
        return plot
    
    def wrap(self, fv_or_kernel=None):
        """
        wraps this function in a FunctionVector
        
        :fv_or_kernel:  either a FunctionVector or a Kernel
        :returns:       FunctionVector(self, kernel=kernel)
        """
        if isinstance(fv_or_kernel, FunctionVector):
            kernel = fv_or_kernel.kernel
        else:
            kernel = fv_or_kernel
        if kernel is None:
            kernel = Kernel()
        return FunctionVector({self: 1}, kernel=kernel)
    
    

##############################################################################
## CLASS FUNCTION VECTOR    
@dataclass
class FunctionVector(DictVector):
    r"""
    a vector of functions
    
    :kernel:        the integration kernel to use (default: Kernel())
    
    A function vector is a linear combination of Function objects. It exposes
    the usual **vector properties** (technically it is a `DictVector` subclass) where
    the functions themselves used as dict keys and therefore the *dimensions* of the 
    vector space. Note that there is an additional constraint the only vectors that
    have the same kernel can be aggregated.
    
    It also exposes properties related to **pointwise evaluation** of the functions, notably
    the function value of the vector at point x is given as
    
    .. math::
    
        f_v(x) = \sum_i \alpha_i * f_i(x)
    
    and this carries over to the price functions an derivatives that are exposed
    in the ``p``, ``df_dx``, ``pp`` etc methods.
    
    Finally it exposes properties related to **integration** of the functions
    based on the kernel, notably the `integrate` method that integrates the
    vector of functions as well as various norms and distance measures.
    """
    __VERSION__ = __VERSION__
    __DATE__ = __DATE__
    
    kernel: Kernel = None
    
    def __post_init__(self):
        super().__post_init__()
        assert all([isinstance(v, Function) for v in self.vec.keys()]), "all keys must be of type Function"
        if self.kernel is None:
            self.kernel = Kernel()  
            
    def wrap(self, func):
        """
        creates a FunctionVector from a function using the same kernel as self
        
        :func:      the function to wrap (a Function object)
        :returns:   a new FunctionVector object wrapping `fu`nc`, with the same kernel as ``self``
        
        .. code-block:: python
        
            fv0 = FunctionVector(kernel=mykernel)       # creates a FV with a specific kernel
            f   = MyFunction()                          # creates a Function object
            fv0.wrap(f)                                 # a FV object with the same kernel as fv0
        """
        try:
            return self.__class__({f: 1 for f in func}, kernel=self.kernel)
        except:
            assert isinstance(func, Function), "func must be of type Function"
            return self.__class__({func: 1}, kernel=self.kernel)
    
    def functions(self):
        """returns all functions in self as a list"""
        return list(self.vec.keys())
    
    def function(self, i=0):
        """returns the i'th function in self"""
        return self.functions()[i]
    
    def params(self, index=None, *, as_dict=None, classname=None):
        """
        retrieve params of the underlying function(s)
        
        :index:         the index (0,1,2...) of the item to be retrieved
        :as_dict:       if True, returns items as dict, otherwise as list
        :classname:     if True, includes the class name in the params
        
        
        index       as_dict         Action
        ---         ---             ---
        None        True            return all as dict
        None        False           return all as list
        None        None            list as_dict = True
        int         True            return params of item i (key => params)
        int         False           ditto, params only
        int         None            like as_dict = True
        """
        if index is None :
            # return all as dict
            as_dict = as_dict if not as_dict is None else False
            classname = classname if not classname is None else True
            result = {f: f.params(classname=classname) for f in self.functions()}
            if as_dict:
                return result
            return list(result.values())
        
        else:
            # index given => return params of item i
            as_dict = as_dict if not as_dict is None else False
            classname = classname if not classname is None else True
            f = self.function(index)
            if as_dict:
                return {f: f.params(classname=classname)}
            return f.params(classname=classname)

        
    def update(self, params=None, index=None, *, key=None, **kwargs):
        """
        creates a copy of the FunctionVector, with the relevant functions updated
        
        :index:     if not None, only updates the i'th function
        :params:    the parameters to be updated (single dict or list of dicts)
        :key:       if not None, only updates the function with the given key
        :returns:   the newly created, updated FunctionVector
        """
        if index is None and key is None and len(self.vec) == 1:
            index = 0
        if isinstance(params, list) or isinstance(params, tuple):
            assert index is None and key is None, "index and key must be None if params is a list"
            raise NotImplementedError("update with list of params not implemented yet")
        else:
            if params is None: params = dict()
            params = {**params, **kwargs}
            assert not index is None or not key is None, "exactly one of index or key must be given"
            assert not(not index is None and not key is None), "can't give both index and key"
            assert key is None, "key not implemented yet"
            funcs = self.functions()
            funcs[index] = funcs[index].update(**params)
            return self.wrap(funcs)
            
    def __eq__(self, other):
        funcs_eq = super().__eq__(other)
        kernel_eq = self.kernel == other.kernel
        print(f"[FunctionVector::eq] called; funcs_eq={funcs_eq}, kernel_eq={kernel_eq}")
        return funcs_eq and kernel_eq  
    
    def f(self, x):
        r"""
        returns the function value
        
        .. math::
        
            f(x) = \sum_i \alpha_i * f_i(x)
        """
        fv_t = ((f(x), v) for f, v in self.vec.items())
        return sum([f_x * v for f_x, v in fv_t if not f_x is None])
    
    def f_r(self, x):
        """alias for ``self.restricted(self.f, x)``"""
        return self.restricted(self.f, x)
    
    def f_k(self, x):
        """alias for ``self.apply_kernel(self.f, x)``"""
        return self.apply_kernel(self.f, x)
    
    def __call__(self, x):
        """
        alias for ``f(x)``
        """
        return self.f(x)
    
    def p(self, x):
        r"""
        returns :math:`\sum_i \alpha_i * p_i(x)` where :math:`p_i` is the price function of :math:`f_i`
        """
        return sum([F.p(x) * v for F, v in self.vec.items()])
    
    def df_dx(self, x):
        r"""
        derivative of ``self.f`` (alias for ``-p``)
                
        .. math::
        
            \frac{df}{dx}(x) = \sum_i \alpha_i * \frac{df_i}{dx}(x)
        """
        return -self.p(x)
    
    def pp(self, x):
        r"""
        derivative of the price function of ``self.f``
        
        .. math::
        
            pp(x) = \sum_i \alpha_i * pp_i(x)
        """
        return sum([F.pp(x) * v for F, v in self.vec.items()])
    
    def restricted(self, func, x=None):
        """
        returns ``func(x)`` restricted to the domain of ``self.kernel`` (as value or lambda if ``x`` is ``None``)
        
        USAGE
        
        this function can either be called directly
        
        .. code-block:: python
        
            fv = FunctionVector(...)
            fv.restricted(func, x) # ==> value
            
        or be used to create a new function
        
        .. code-block:: python
        
            fv = FunctionVector(...)
            func_restricted = fv.restricted(func) # ==> lambda 
        """
        f = lambda x: func(x) if self.kernel.in_domain(x) else 0
        if x is None:
            return f
        return f(x)
    
    def apply_kernel(self, func, x=None):
        """
        returns ``func`` multiplied by the kernel value (as value or lambda if ``x`` is None)
        
        USAGE
        
        this function can either be called directly
        
        .. code-block:: python
        
            fv = FunctionVector(...)
            fv.apply_kernel(func, x) # ==> value
            
        or be used to create a new function
        
        .. code-block:: python
        
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
        """integrates ``func`` (default: ``self.f``) using the kernel"""
        if func is None:
            func = self.f
        return self.kernel.integrate(func, steps=steps, method=method)
        
    def integrate(self, *, steps=None, method=None):
        """integrates ``self.f`` using the kernel [convenience access for ``integrate_func(func=None)``]"""
        return self.integrate_func(func=self.f, steps=steps, method=method) 
    
    ########################################################################
    ## distance functions
    
    ###################################
    ## ...on self.f
    def dist2_L2(self, func=None, *, steps=None, method=None):
        """
        calculates the L2 distance-squared between ``self`` and ``func`` (L2 norm squared)
        """
        if not func is None:
            f = lambda x: (self.f(x)-func(x))**2 * self.kernel(x)
        else:
            f = lambda x: self.f(x)**2 * self.kernel(x)
        return self.integrate_func(func=f, steps=steps, method=method)
    
    def dist_L2(self, func=None, *, steps=None, method=None):
        """calculates the distance between ``self`` and ``func`` (L2 norm)"""
        return m.sqrt(self.dist2_L2(func=func, steps=steps, method=method))
    
    def dist_L1(self, func=None, *, steps=None, method=None):
        """
        calculates the L1 distance between ``self`` and ``func`` (L1 norm)
        """
        if not func is None:
            f = lambda x: (abs(self.f(x)-func(x))) * self.kernel(x)
        else:
            f = lambda x: abs(self.f(x)) * self.kernel(x)
        return self.integrate_func(func=f, steps=steps, method=method)

    ###################################
    ## ...on self.p
    def distp2_L2(self, func=None, *, steps=None, method=None):
        """
        calculates the L2 distance-squared between ``self.p`` and ``func`` (L2 norm squared)
        """
        if not func is None:
            f = lambda x: (self.p(x)-func(x))**2 * self.kernel(x)
        else:
            f = lambda x: self.p(x)**2 * self.kernel(x)
        return self.integrate_func(func=f, steps=steps, method=method)
    
    def distp_L2(self, func=None, *, steps=None, method=None):
        """calculates the distance between ``self.p`` and ``func`` (L2 norm)"""
        return m.sqrt(self.distp2_L2(func=func, steps=steps, method=method))
    
    def distp_L1(self, func=None, *, steps=None, method=None):
        """
        calculates the L1 distance between ``self.p`` and ``func`` (L1 norm)
        """
        if not func is None:
            f = lambda x: (abs(self.p(x)-func(x))) * self.kernel(x)
        else:
            f = lambda x: abs(self.p(x)) * self.kernel(x)
        return self.integrate_func(func=f, steps=steps, method=method)
    
    ########################################################################
    ## norm functions
    
    ###################################
    ## ...on self.f
    def norm2_L2(self, *, steps=None, method=None):
        """calculates the L2 norm squared of ``self``"""
        return self.dist2_L2(func=None, steps=steps, method=method)
    norm2 = norm2_L2
    
    def norm_L2(self, *, steps=None, method=None):
        """calculates the L2 norm of ``self``"""
        return m.sqrt(self.norm2(steps=steps, method=method))
    norm = norm_L2
    
    def norm_L1(self, *, steps=None, method=None):
        """calculates the L1 norm of ``self``"""
        return self.dist_L1(func=None, steps=steps, method=method)
    norm1 = norm_L1
    
    ###################################
    ## ...on self.p
    def normp2_L2(self, *, steps=None, method=None):
        """calculates the L2 norm squared of ``self.p``"""
        return self.distp2_L2(func=None, steps=steps, method=method)
    normp2 = normp2_L2
    
    def normp_L2(self, *, steps=None, method=None):
        """calculates the L2 norm of ``self``"""
        return m.sqrt(self.normp2(steps=steps, method=method))
    normp = normp_L2
    
    def normp_L1(self, *, steps=None, method=None):
        """calculates the L1 norm of ``self``"""
        return self.distp_L1(func=None, steps=steps, method=method)
    normp1 = normp_L1


    ########################################################################
    ## goalseek and minimization
    
    ###################################
    ## goalseek
    def goalseek(self, target=0, *, func=None, x0=1):
        """
        very simple gradient descent implementation for a goal seek
        
        :target:            target value (default: 0)
        :func:              function for goal seek (default: self.f)
        :x0:                starting estimate
        :learning_rate:     optimization parameter (float; default ``cls.MM_LEARNING_RATE``)
        :iterations:        max iterations (int; default ``cls.MM_ITERATIONS``)
        :tolerance:         convergence tolerance (float; ``default cls.MM_TOLERANCE``)
        """
        x = x0
        iterations = self.GS_ITERATIONS
        tolerance = self.GS_TOLERANCE
        h = x0*self.GS_ETA if x0 else self.GS_H
        func = func or self.f
        for i in range(iterations):
            y = func(x)
            m = (func(x+h)-func(x-h)) / (2*h)
            x = x + (target-y)/m
            if abs(func(x)-target) < tolerance:
                break
        if abs(func(x)-target) > tolerance:
            raise ValueError(f"gradient descent failed to converge on {target}")
        return x
    
    def goalseek(self, func=None, target=0, *, x0=1, iterations=None, tolerance=None, eta=None, h=None):
        """alias for ``self.goalseek``, but with defaults for ``func=self.f``"""
        func = func or self.f
        return self.goalseek_cls(func, target=target, x0=x0, iterations=iterations, tolerance=tolerance, eta=eta, h=h)
    
    @classmethod
    def goalseek_cls(cls, func, target=0, *, x0=1, iterations=None, tolerance=None, eta=None, h=None):
        """
        very simple gradient descent implementation for a goal seek (classmethod)
        
        :target:    target value (default: 0)
        :x0:        starting estimate
        """
        x = x0
        iterations = iterations or cls.GS_ITERATIONS
        tolerance = tolerance or cls.GS_TOLERANCE
        hh = x0*(eta or cls.GS_ETA) if x0 else (h or cls.GS_H)
        for i in range(iterations):
            y = func(x)
            m = (func(x+hh)-func(x-hh)) / (2*hh)
            x = x + (target-y)/m
            if abs(func(x)-target) < tolerance:
                break
        if abs(func(x)-target) > tolerance:
            raise ValueError(f"gradient descent failed to converge on {target}")
        return x

    ###################################
    ## minimization   
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
    
    
    MM_DERIV_H = 1e-6
    MM_VERBOSITY_QUIET = 0
    MM_VERBOSITY_MIN = 1
    MM_VERBOSITY_LOW = 10
    MM_VERBOSITY_HIGH = 20
    
    @classmethod
    def minimize(cls, func, *, 
                x0=None, 
                learning_rate=None, 
                iterations=None, 
                tolerance=None, 
                deriv_h=None, 
                return_path=False,
                verbosity = MM_VERBOSITY_QUIET,
        ):
        """
        minimizes the function ``func`` using gradient descent (multiple dimensions)
        
        :func:              function to be minimized
        :x0:                starting point (``np.array``-like or dct (1))
        :learning_rate:     optimization parameter (float; default ``cls.MM_LEARNING_RATE``)
        :iterations:        max iterations (int; default ``cls.MM_ITERATIONS``)
        :tolerance:         convergence tolerance (float; default ``cls.MM_TOLERANCE``)
        :deriv_h:           step size for derivative calculation (float; default ``cls.MM_DERIV_H``)
        :return_path:       if True, returns the entire optimization path (list of ``np.array``)
                            as well as the last dfdx (``np.array``); in this case, the result is 
                            the last element of the path
        
        NOTE1: if `x0` is ``np.array``-like or ``None``, then `func` will be called with 
        positional arguments and the result will be returned as an ``np.array``. If ``x0`` 
        is a dict, then ``func`` will be called with keyword arguments and the result 
        will be returned as a dict
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
        path, dfdx, norm2_dfdx = _minimize(func, x0, learning_rate, iterations, tol_squared, deriv_h, verbosity)
        
        if verbosity >= cls.MM_VERBOSITY_HIGH:
            print(f"[minimize] algorithm returned, norm={m.sqrt(norm2_dfdx)}")
        if return_path:
            if verbosity >= cls.MM_VERBOSITY_HIGH:
                print(f"[minimize] return path (len={len(path)}), final point={path[-1]})")
            return path, dfdx
        if norm2_dfdx < tol_squared:
            if verbosity >= cls.MM_VERBOSITY_LOW:
                print(f"[minimize] converged in {len(path)} iterations, norm={m.sqrt(norm2_dfdx):.6f}\nx={path[-1]})")
            return path[-1]
        if verbosity >= cls.MM_VERBOSITY_MIN:
            print(f"[minimize] did not converge in {len(path)} iterations, norm={m.sqrt(norm2_dfdx):.4f}, x={path[-1]})")
        raise ValueError(f"gradient descent failed to converge")
    
    @classmethod
    def _minimize_lst(cls, func, x0, learning_rate, iterations, tol_squared, deriv_h, verbosity):
        """
        executes the minimize algorithm when the x-values are in a list
        
        :returns:  ``tuple(path, dfdx, norm2_dfdx)``; result is ``path[-1]``
        """
        x = np.array(x0, dtype=float)
        n = len(x)
        path = [tuple(x)]
        if verbosity >= cls.MM_VERBOSITY_HIGH:
            print(f"[_minimize_lst] x0={fmt(x, '.4f')}")
        
        for iteration in range(iterations):
            f0 = func(*x)
            dfdx = np.array([
                (func( *(x+deriv_h*cls.e_i(i, n)) ) - f0) / deriv_h 
                for i in range(len(x))
            ])
            dx = learning_rate * dfdx
            x -= dx
            path.append(tuple(x))
            #print(f"[_minimize_lst] {iteration}: adding x={x}, gradient={dfdx}")  
            norm2_dfdx = np.dot(dfdx, dfdx)
            if verbosity >= cls.MM_VERBOSITY_HIGH:
                print(f"[_minimize_lst] {iteration}: norm={m.sqrt(norm2_dfdx):.4f}\nx={fmt(x, '.4f')}\ngradient={fmt(dfdx, '.4f')}\ndx={fmt(dx, '.4f')}\n\n")
            if norm2_dfdx < tol_squared:
                break
        return path, dfdx, norm2_dfdx
    
    @classmethod
    def _minimize_dct(cls, func, x0, learning_rate, iterations, tol_squared, deriv_h, verbosity):
        """
        executes the minimize algorithm when the x-values are in a dict
        
        :returns:  ``tuple(path, dfdx, norm2_dfdx)``; result is ``path[-1]``
        """
        x = {**x0}
        path = [{**x}]
        if verbosity >= cls.MM_VERBOSITY_HIGH:
            print(f"[_minimize_dct] x0={fmt(x, '.4f')}")
        for iteration in range(iterations):
            f0 = func(**x)
            dfdx = {
                k: (func( **(cls.bump(x, k, deriv_h)) ) - f0) / deriv_h 
                for k in x.keys()
            }
            dx = {k: -learning_rate * dfdx[k] for k in x.keys()}
            x = {k: x[k] + dx[k] for k in x.keys()}
            path.append({**x})
            norm2_dfdx = sum(vv**2 for vv in dfdx.values())  
            if verbosity >= cls.MM_VERBOSITY_HIGH:
                print(f"[_minimize_dct] {iteration}: norm={m.sqrt(norm2_dfdx):.8f}\nx={fmt(x, '.4f')}\ngradient={fmt(dfdx, '.4f')}\ndx={fmt(dx, '.4f')}\n\n")
            if norm2_dfdx < tol_squared:
                break
        return path, dfdx, norm2_dfdx
    
    CF_NORM_L1 = "L1"       # L1 norm for distance
    CF_NORM_L2 = "L2"       # ditto L2
    CF_NORM_L2S = "L2S"     # ditto L2, but don't bother with sqrt
    
    def curve_fit(self, func, params0, norm=None, **kwargs):
        """
        fits a function to ``self`` using gradient descent
        
        :func:          function to fit (typically a Function object) (1)
        :params0:       starting parameters (dict) (1)
        :kwargs:        passed to self.minimize
        :returns:       the parameters of the fitted function (dict)
        
        NOTE1: The ``func`` object must have an ``update`` method that accepts a dict of 
        parameters with the keys of ``params0`` and returns a new object with the updated 
        parameters.
        """
        if norm is None:
            norm = self.CF_NORM_L2S
        if norm == self.CF_NORM_L1:
            #print("[curve_fit] using L1 norm")
            dist_func = self.dist_L1
        elif norm == self.CF_NORM_L2:
            #print("[curve_fit] using L2 norm")
            dist_func = self.dist_L2
        elif norm == self.CF_NORM_L2S:
            #print("[curve_fit] using L2S norm")
            dist_func = self.dist2_L2
        
        def optimizer_func(**params):
            #print("[optimizer_func] updating", params)
            func1 = func.update(**params)
            return dist_func(func=func1)
        
        return self.minimize(optimizer_func, x0=params0, **kwargs)
    
    ###############################
    ## helpers and utilities
    @staticmethod    
    def e_i(i, n):
        """returns the ``i``'th unit vector of size ``n``"""
        result = np.zeros(n)
        result[i] = 1
        return result
    
    @staticmethod
    def e_k(k, dct):
        """returns the unit vector of key ``k`` in ``dct``"""
        return {kk: 1 if kk==k else 0 for kk in dct.keys()}
    
    @staticmethod
    def bump(dct, k, h):
        """bumps ``dct[k]`` by ``+h``; everything else unmodified (returns a new dict)"""
        return {kk: v+h if kk==k else v for kk,v in dct.items()}    
    
    
    def plot(self, func=None, *, x_min=None, x_max=None, steps=None, title=None, xlabel=None, ylabel=None, grid=True, show=False, **kwargs):
        """
        plots the function ``func`` (default: ``self.f_r``) over the interval [``x_min``, ``x_max``]
        
        :func:      function to plot (default: ``self.f_r``)
        :x_min:     lower bound (default: ``self.kernel.x_min``)
        :x_max:     upper bound (default: ``self.kernel.x_max``)
        :steps:     number of steps (default: ``np.linspace`` defaults)
        :show:      whether to call plt.show() (default: ``False``)
        :grid:      whether to show a grid (default: ``True``)
        :returns:   the result of ``plt.plot``
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
goalseek = FunctionVector.goalseek_cls

    
##################################################################################
## FUNCTIONAL OBJECTS
@dataclass(frozen=True)
class PriceFunction(Function):
    """
    a function object representing the price function of another function
    
    :func:          the function to derive the price function from
    :precision:     the precision to use for the derivative calculation
    :returns:       a new function object with `self.f = func.p`
    """
    func: Function
    precision: float = None
    
    def __post_init__(self):
        assert isinstance(self.func, Function), "f must be a Function"
        if not self.precision is None:
            self.precision = float(self.precision)
    
    def f(self, x):
        """the price function ``p = -f'(x)`` of ``self.func(x)``"""
        return self.func.p(x, precision=self.precision)  
    
@dataclass(frozen=True)
class Price2Function(Function):
    """
    a function object representing the derivative of the price function of another function
    
    :func:          the function to derive the derivative of the price function from
    :precision:     the precision to use for the derivative calculation
    :returns:       a new function object with `self.f = func.pp`
    """
    func: Function
    precision: float = None
    
    def __post_init__(self):
        assert isinstance(self.func, Function), "f must be a Function"
        if not self.precision is None:
            self.precision = float(self.precision)
    
    def f(self, x):
        """the second derivative ``f''(x)`` of ``self.func(x)``"""
        return self.func.pp(x, precision=self.precision)  
    
    
    