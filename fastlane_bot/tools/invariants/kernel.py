"""
Implements the `Kernel` class, an integration kernel together with numeric integration code

---
(c) Copyright Bprotocol foundation 2024. 
Licensed under MIT
"""
__VERSION__ = '0.9.1'
__DATE__ = "26/Jan/2024"

from dataclasses import dataclass, asdict
from scipy.stats import norm
import numpy as np
import math as m

@dataclass
class Kernel():
    """
    Represents a one-dimensional integration kernel and provides numeric integration code
    
    :x_min:         minimum x value for integration
    :x_max:         ditto maximum
    :kernel:        kernel function (should be positive, and defined `x_min` <= `x` <= `x_max`);
                    generically, the kernel function is a callable taking a single argument;
                    alternatively there are a number of built-in kernels that can be selected 
                    by passing the respective constant (see table)
    :method:        integration method (currently only `METHOD_TRAPEZOID`)
    :steps:         number of steps for integration
    
    ======================  ====================================================
    `kernel`                meaning
    ======================  ====================================================
    FLAT                    constant
    TRIANGLE                triangle
    SAWTOOTHL, SAWTOOTHR    sawtooth left/right
    GAUSS, GAUSSW, GAUSSN   gaussian (fitted, wide, narrow)
    ======================  ====================================================
    
    USAGE
    
    .. code-block:: python
    
        k = Kernel(x_min=-1, x_max=1, kernel=Kernel.FLAT)
        f = lambda x: x**2
        
        k(0.5)                  # 0.5
        k.integrate(f)          # ~0.6666
        
        Kernel.integrate_trapezoid(f, -1, 1, 100)  # ~0.6666
    """    
    __VERSION__ = __VERSION__
    __DATE__ = __DATE__
    
    METHOD_TRAPEZOID = 'trapezoid'
    
    FLAT = "builtin-flat"
    TRIANGLE = "builtin-triangle"
    SAWTOOTHL = "builtin-sawtoothl"
    SAWTOOTHR = "builtin-sawtoothr"
    GAUSS = "builtin-gauss"
    GAUSSW = "builtin-gausswide"
    GAUSSN = "builtin-gaussnarrow"
    
    DEFAULT_XMIN = 0
    DEFAULT_XMAX = 1
    DEFAULT_KERNEL = FLAT
    DEFAULT_METHOD = METHOD_TRAPEZOID
    DEFAULT_STEPS = 100
    
    x_min: float = DEFAULT_XMIN
    x_max: float = DEFAULT_XMAX
    kernel: callable = None
    kernel_name: str = DEFAULT_KERNEL
    method: str = DEFAULT_METHOD
    steps: int = DEFAULT_STEPS
    
    def __post_init__(self):
        assert self.x_max > self.x_min, "x_max must be greater than x_min"
        if isinstance(self.kernel, str):
            self.kernel_name = self.kernel
            self.kernel = None
            
        if self.kernel is None:
            w = self.x_max - self.x_min
            ctr = (self.x_max+self.x_min)/2
            #print("[Kernel] w = ", w)
            
            if self.kernel_name == self.FLAT:
                self.kernel = lambda x: 1/w
            
            elif self.kernel_name == self.TRIANGLE:
                self.kernel = lambda x: max(1-2*abs((x-ctr)/w),0)
                
            elif self.kernel_name == self.SAWTOOTHL:
                self.kernel = lambda x: 2/w*max(1-abs((x-self.x_min)/w),0)
                
            elif self.kernel_name == self.SAWTOOTHR:
                self.kernel = lambda x: 2/w*(1-max(1-abs((x-self.x_min)/w),0))
                
            elif self.kernel_name == self.GAUSS:
                self.kernel = lambda x: norm.pdf(x, loc=ctr, scale=w/6)/0.9973001241637569

            elif self.kernel_name == self.GAUSSW:
                self.kernel = lambda x: norm.pdf(x, loc=ctr, scale=w/3)/0.8663853060476605
                
            elif self.kernel_name == self.GAUSSN:
                self.kernel = lambda x: norm.pdf(x, loc=ctr, scale=w/12)
                
            else:
                raise ValueError(f"unknown kernel type {self.kernel_name}")
        
    def k(self, x):
        """Alias for `self.kernel(x)`, but set to zero beyond `x_min`, `x_max`"""
        if self.in_domain(x):
            #print(f"[Kernel::k] {self} {x}")
            return self.kernel(x)
        else:
            return 0
        
    def __call__(self, x):
        """Alias for `self.k`"""
        return self.k(x)
    
    def in_domain(self, x):
        """Returns True iff x is in the integration domain `x_min`...`x_max`"""
        return self.x_min <= x <= self.x_max
    
    @property
    def limits(self):
        """Convenience accessor for `(x_min, x_max)`"""
        return (self.x_min, self.x_max)
    domain = limits
    
    def integrate(self, func, *, steps=None, method=None):
        """
        Integrates `func` against the kernel (calls `integrate_trapezoid`)
        
        :func:      function to integrate (single variable)
        :steps:     number of steps for integration (default: self.steps)
        :method:    integration method (default: self.method) (1)
        :returns:   :math:`\int_{x_{min}}^{x_{max}} \mathrm{func}(x)\,\mathrm{kernel}(x)\,dx` 
        
        
        NOTE 1: currently the only method supported is `METHOD_TRAPEZOID`
        
        EXAMPLE
        
        .. code-block:: python
        
                k = Kernel(x_min=-1, x_max=1, kernel=Kernel.FLAT)
                f = lambda x: x**2
                k.integrate(f)          # ~0.6666
        """
        if steps is None:
            steps = self.steps
        if method is None:
            method = self.method
        ifunc = lambda x: func(x) * self.kernel(x)    
        
        # integrate = self.METHODS.get(method)
        # if integrate is None:
        #     raise ValueError(f"unknown integration method {method}")
        
        # return integrate(ifunc, self.x_min, self.x_max, steps)
            # the above code failed the tests on github for reasons I don't understand
            # I therefore went to the pedestrian version below
        
        if method == self.METHOD_TRAPEZOID:
            return self.integrate_trapezoid(ifunc, self.x_min, self.x_max, steps)
        else:
            raise ValueError(f"unknown integration method {method}")
    
    @staticmethod
    def integrate_trapezoid(func, x_min, x_max, steps):
        """
        Integrates a function using the trapezoid method between `x_min` and `x_max`
        
        :func:      function to integrate (single variable callable)
        :x_min:     minimum x value for integration
        :x_max:     ditto maximum
        :steps:     number of steps for integration
        :returns:   :math:`\int_{x_{min}}^{x_{max}} \mathrm{func}(x)\,dx`
        
        EXAMPLE
        
        .. code-block:: python
            
                f = lambda x: x**2
                Kernel.integrate_trapezoid(f, -1, 1, 100)  # ~0.6666
        """
        assert x_max > x_min, "x_max must be greater than x_min"
        assert steps > 0, "steps must be positive"
        
        def func1(x):
            try:
                return func(x)
            except Exception as e:
                return 0
        
        try:
            dx = (x_max-x_min)/steps
            f = [func1(x_min+i*dx) for i in range(steps+1)]
        except Exception as e:
            raise ValueError(f"calculation error (xmin={x_min}, xmax={x_max}, steps={steps}) [{e}]") from e
        return (sum(f) - 0.5*(f[0]+f[-1])) * dx
    
    # METHODS = {
    #     METHOD_TRAPEZOID: integrate_trapezoid
    # }
    