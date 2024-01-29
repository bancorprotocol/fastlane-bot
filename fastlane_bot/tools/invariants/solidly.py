"""
object representing the Solidly AMM invariant 

(c) Copyright Bprotocol foundation 2024. 
Licensed under MIT
"""
__VERSION__ = '0.9'
__DATE__ = "18/Jan/2024"

import decimal as d
D = d.Decimal
import math as m

from .invariant import Invariant, dataclass
from .functions import Function


@dataclass(frozen=True)
class SolidlySwapFunction(Function):
    r"""
    represents the Solidly AMM swap function y(x,k)=k/x
    
    :method: METHOD_FLOAT, METHOD_DEC (default), METHOD_TAYLOR
    
    
    ==============================================
                MATHEMATICAL BACKGROUND
    ==============================================
    
    The Solidly **invariant equation** is 
    $$
        x^3y+xy^3 = k
    $$

    which is a stable swap curve, but more convex than for example Curve. 

    To obtain the **swap equation** we solve the above invariance equation 
    as $y=y(x; k)$. This gives the following result
    $$
    y(x;k) = \frac{x^2}{\left(-\frac{27k}{2x} + \sqrt{\frac{729k^2}{x^2} + 108x^6}\right)^{\frac{1}{3}}} - \frac{\left(-\frac{27k}{2x} + \sqrt{\frac{729k^2}{x^2} + 108x^6}\right)^{\frac{1}{3}}}{3}
    $$

    We can introduce intermediary **variables L and M** ($L(x;k), M(x;k)$) 
    to write this a bit more simply

    $$
    L(x,k) = L_1(x) \equiv -\frac{27k}{2x} + \sqrt{\frac{729k^2}{x^2} + 108x^6}
    $$
    $$
    M(x,k) = L^{1/3}(x,k) = \sqrt[3]{L(x,k)}
    $$
    $$
    y = \frac{x^2}{\sqrt[3]{L}} - \frac{\sqrt[3]{L}}{3} = \frac{x^2}{M} - \frac{M}{3} 
    $$

    If we rewrite the equation for L as below we see that it is not 
    particularly well conditioned for small $x$
    $$
    L(x,k) = L_2(x) \equiv \frac{27k}{2x} \left(\sqrt{1 + \frac{108x^8}{729k^2}} - 1 \right)
    $$

    For simplicity we introduce the **variable xi** $\xi=\xi(x,k)$ as
    $$
    \xi(x, k)  = \frac{108x^8}{729k^2}
    $$

    then we can rewrite the above equation as 
    $$
    L_2(x;k) \equiv \frac{27k}{2x} \left(\sqrt{1 + \xi(x,k)} - 1 \right)
    $$

    Note the Taylor expansion for $\sqrt{1 + \xi} - 1$ is 
    $$
    \sqrt{1+\xi}-1 = \frac{\xi}{2} - \frac{\xi^2}{8} + \frac{\xi^3}{16} - \frac{5\xi^4}{128} + O(\xi^5)
    $$

    and tests suggest that it is very good for at least $|\xi| < 10^{-5}$
    """
    __VERSION__ = __VERSION__
    __DATE__ = __DATE__
    
    k: float
    
    METHOD_FLOAT = "float"
    METHOD_DEC100 = "decimal100"
    METHOD_DEC1000 = "decimal1000"
    METHOD_TAYLOR = "taylor"
    def __post_init__(self, method=None):
        if method is None:
            method = self.METHOD_DEC1000
        #self._method = method
        super().__setattr__("_method", method)
        if method == self.METHOD_FLOAT:
            #self.L = self._L1_float
            super().__setattr__("L", self._L1_float)
        elif method == self.METHOD_DEC100:
            #self.L = self._L1_dec100
            super().__setattr__("L", self._L1_dec100)
        elif method == self.METHOD_DEC1000:
            #self.L = self._L1_dec1000
            super().__setattr__("L", self._L1_dec1000)
        elif method == self.METHOD_TAYLOR:
            #self.L = self._L2_taylor
            super().__setattr__("L", self._L2_taylor)
        else:
            raise ValueError(f"method={method} must be one of self.METHOD_FLOAT, self.METHOD_DEC, self.METHOD_TAYLOR")

    @property
    def method(self):
        """the method used to calculate y(x,k)"""
        return self._method
    
    @staticmethod    
    def _L1_float(x, k):
        """using float (precision issues)"""
        return -27*k/(2*x) + m.sqrt(729*k**2/x**2 + 108*x**6)/2
    
    @staticmethod
    def _L1_dec(x, k, *, precision):
        """using decimal to avoid precision issues (slow)"""
        prec0 = d.getcontext().prec
        d.getcontext().prec = precision
        x,k = D(x), D(k)
        xi = (108 * x**8) / (729 * k**2)
        lam = (D(1) + xi).sqrt() - D(1)
        L = lam * (27 * k) / (2 * x)
        d.getcontext().prec = prec0
        return float(L)
    
    @staticmethod
    def _L1_dec100(x, k):
        """using decimal 100 to avoid precision issues (slow; calls _L1_dec)"""
        return SolidlySwapFunction._L1_dec(x, k, precision=100)
    
    @staticmethod
    def _L1_dec1000(x, k):
        """using decimal 1000 to avoid precision issues (very slow; calls _L1_dec)"""
        return SolidlySwapFunction._L1_dec(x, k, precision=1000)
    
    @staticmethod
    def _L2_taylor(x, k):
        """
        using Taylor expansion for small x for avoid precision issues (transition artefacts)
        """
        xi = (108 * x**8) / (729 * k**2)
        #print(f"xi = {xi}")
        if xi > 1e-5:
            # full formula for $sqrt(1 + \xi) - 1$
            lam = (m.sqrt(1 + xi) - 1)
        else:
            # Taylor expansion of $sqrt(1 + \xi) - 1$
            lam = xi*(1/2 - xi*(1/8 - xi*(1/16 - 0.0390625*xi)))
            # the relative error of this Taylor approximation is for xi < 0.025 is 1e-5 or better
            # for xi ~ 1e-15 the full term is unstable (because 1 + 1e-16 ~ 1 in double precision)
            # therefore the switchover should happen somewhere between 1e-12 and 1e-2
        L = lam * (27*k) / (2*x)
        return L


    def f(self, x):
        L,M,y = [None]*3
        try:
            L = self.L(x, self.k)
            M = L**(1/3)
            y = x*x/M - M/3
        except Exception as e:
            print("Exception: ", e)
            print(f"x={x}, k={k}, L={L}, M={M}, y={y}")
        return y

@dataclass
class SolidlyInvariant(Invariant):
    """represents the Solidly invariant function"""
    __VERSION__ = __VERSION__
    __DATE__ = __DATE__
    
    def __post_init__(self):
        self._y_Func_class = SolidlySwapFunction
    
    def k_func(self, x, y):
        """Solidly invariant function k(x,y)=x^3*y + x*y^3"""
        return x**3 * y + x * y**3
    
