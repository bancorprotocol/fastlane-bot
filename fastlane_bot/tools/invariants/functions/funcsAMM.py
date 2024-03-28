"""
functions library -- AMM-related example functions

(c) Copyright Bprotocol foundation 2024. 
Licensed under MIT
"""
#__VERSION__    ==> core.__VERSION__
#__DATE__       ==> core.__DATE__

from .core import Function as _Function, dataclass as _dataclass
import math as _m
import decimal as _d
_D = _d.Decimal

@_dataclass(frozen=True)
class CPMMFunction(_Function):
    """
    constant product market maker: y = k/x
    
    :k:         pool constant (scales with square of pool liquidity)
    """
    k: float = 1
    
    @property
    def kbar(self):
        """kbar = sqrt(k), ie the properly scaling version of k"""
        return _m.sqrt(self.k)
    
    @classmethod
    def from_kbar(cls, kbar):
        """create a CPMMFunction from kbar"""
        return cls(k=kbar**2)
    
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

@_dataclass(frozen=True)
class VirtualTokenBalancesCPMMFunction(_Function):
    """
    levered CPMM using virtual token balances: (y+y0) = k/(x+x0)
    
    :k:         pool constant (scales with square of pool liquidity)
    :x0, y0:    virtual pool liquidity
    :clip:      if True, don't allow negative values for x and y
    """
    k: float = 1
    x0: float = 0
    y0: float = 0
    
    def __post_init__(self, clip=False):
        #super().__post_init__()
        super().__setattr__("clip", clip)
    
    @property
    def kbar(self):
        """kbar = sqrt(k), ie the properly scaling version of k"""
        return _m.sqrt(self.k)
    
    @classmethod
    def from_kbar(cls, kbar, x0=0, y0=0):
        """create a CPMMFunction from kbar"""
        return cls(k=kbar**2, x0=x0, y0=y0)
    
    @classmethod
    def from_xpxp(cls, *, xa, pa, xb, pb, y0=None, ya=None, yb=None):
        """
        create a CPMMFunction from two x values and the associated prices
        
        :xa, xb:        virtual pool liquidity at the two fixed points (xa<xb)
        :pa, pb:        associated prices at the two fixed points (pa>pb)
        :y0, ya, yb:    y0, or y(xa), y(xb) [at most one given; if none, y0=0]
        """
        # alternative constructor, determining the curve by two points on a x-axis 
        # $x_a, x_b$ and the associated prices $p_a, p_b$; note that we are missing 
        # a parameter, $y_0$, which is a non-financial parameter in this case as a 
        # shift in the y direction does not affect prices as long as the curve does 
        # not run out of tokens
        # We have the following equations:

        # $$
        # \frac k {(x_0+x_a)^2} = p_a,\quad \frac k {(x_0+x_b)^2} = p_b
        # $$
        # Solving for $x_0, k$ we find
        # $$
        # x_0 = \frac{-(p_a x_a) + \sqrt{p_a p_b (x_a - x_b)^2} + p_b x_b}{p_a - p_b} \\
        # k = p_a \left(x_a + \frac{-(p_a x_a) + \sqrt{p_a p_b (x_a - x_b)^2} + p_b x_b}{p_a - p_b}\right)^2
        # = p_a (x_a + x_0)^2
        # $$
        # or 
        #     x0 = (-(pa * xa) + m.sqrt(pa * pb * (xa - xb)**2) + pb * xb) / (pa - pb)
        #     k  = pa * ((xa + (-(pa * xa) + m.sqrt(pa * pb * (xa - xb)**2) + pb * xb) / (pa - pb)) ** 2)
        #     k = pa * (xa + x0) ** 2

        assert xa<xb, f"xa={xa} must be < xb={xb}"
        assert pa>pb, f"pa={pa} must be > pb={pb}"
        
        # core calculation
        x0 = (-(pa * xa) + _m.sqrt(pa * pb * (xa - xb)**2) + pb * xb) / (pa - pb)
        k  = pa * (xa + x0) ** 2
        
        # now deal with y0
        ny = len([y for y in [y0, ya, yb] if y is not None])
        if ny>1:
            raise ValueError(f"at most 1 of y0, ya, yb can be given, but got {ny} [y0={y0}, ya={ya}, yb={yb}]")
        elif ny==0:
            y0 = 0
        else:
            if not y0 is None:
                pass
            elif not ya is None:
                # ya = k/(xa+x0) - y0 ==> y0 = k/(xa+x0) - ya
                y0 = k / (xa+x0) - ya
                #print(f"[y0] f(a)={ k / (xa+x0)}, ya={ya}, y0={y0}, k={k}, x0={x0}, xa={xa}")
            elif not yb is None:
                # yb = k/(xb+x0) - y0 ==> y0 = k/(xb+x0) - yb
                y0 = k / (xb+x0) - yb
        
        # return the new object
        #print(f"[LCPMM] k={k}, x0={x0}, y0={y0}")
        return cls(k=k, x0=x0, y0=y0)
    
    def f(self, x):
        if x<0 and self.clip:
            #print("[f] x<0", x) 
            return None
        y = self.k/(x+self.x0) - self.y0
        if y<0 and self.clip:
            #print(f"[f] y<0; y={y}, x={x}, x0={self.x0}, y0={self.y0}, k={self.k}")  
            return None
        return y
    
    # def p(self, x):
    #     p = self.k/(x+self.x0)**2
    #     if p < self.Pb or p > self.Pa:
    #         return None
    #     else:
    #         return p
    
    # def pp(self, x):
    #     return -2*self.k/(x+self.x0)**3
LCPMM = VirtualTokenBalancesCPMMFunction
VTBCPMM = VirtualTokenBalancesCPMMFunction


@_dataclass(frozen=True)
class UniV3Function(_Function):
    """
    functionally equivalent to VTBCPMM, but with different parameterization
    
    :L:         effective pool constant (equals kbar = sqrt(k) for VTBCPMM)
    :Pa, Pb:    start and end price of the range, in dy/dx, Pa > Pb
    """
    # In Uniswap, the range is from $P_a \ldots P_b, P_a > P_b$ with liquidity 
    # constant $L = \bar k = \sqrt{k}$. We know that 

    # $$
    # p=-\frac{dy}{dx}=\frac{L^2}{x_v^2} = \left(\frac L {x_v}\right)^2
    # $$

    # Of course the virtual token balances $x_v = x_0 + x$ and 
    # $y_v(x) = y_0 + y(x)$ also satisfy the equation
    # $$
    # y_v = \frac{L^2}{x_v}, x_v = \frac{L^2}{y_v}
    # $$
    # and inserting this into the above equation yields
    # $$
    # \sqrt p= \frac L {x_v} = \frac {y_v} L
    # $$

    # We know that $x_v(P_a) < x_v(P_b)$. Therefore, at $P_a$, we have $x=0$ and 
    # therefore

    # $$
    # \sqrt{P_a} = \frac L {x_0}, x_0 = \frac L {\sqrt{P_a}}
    # $$

    # The same reasoning as above leads us to
    # $$
    # \sqrt{P_b} = \frac {y_0} L, y_0 = \sqrt{P_b} L
    # $$

    # Therefore we now can apply our regular levered AMM equation

    # $$
    # y(x)+y_0 = y(x) + \sqrt{P_b} L = \frac k {x+x_0} 
    # = \frac {L^2} {x + \frac{L}{\sqrt{P_a}}}
    # $$

    # for $x = 0$ we get

    # $$
    # y(x_0) = L \sqrt{P_a} - y_0 = L(\sqrt{P_a} - \sqrt{P_b})
    # $$
    
    L: float
    Pa: float
    Pb: float
    
    def __post_init__(self):
        if self.Pa <= self.Pb:
            raise ValueError(f"Pa={self.Pa} must be > Pb={self.Pb}")
        #super().__post_init__()
        super().__setattr__("x0", self.L / _m.sqrt(self.Pa))
        super().__setattr__("y0", self.L * _m.sqrt(self.Pb))
        #print("[UniV3Function] x0, y0:", self.x0, self.y0)
        
    @property
    def kbar(self):
        """kbar = sqrt(k), ie the properly scaling version of k"""
        return self.L

    @property
    def k(self):
        """k = L**2"""
        return self.L**2
    
    def f(self, x):
        if x<0: return None
        y = self.k/(x+self.x0) - self.y0
        if y<0: return None
        return y
    
    def p(self, x):
        p = self.k/(x+self.x0)**2
        if p < self.Pb or p > self.Pa:
            return None
        else:
            return p
    
    def pp(self, x):
        return -2*self.k/(x+self.x0)**3
UniV3 = UniV3Function

@_dataclass(frozen=True)
class CarbonFunction(_Function):
    """
    functionally equivalent to VTBCPMM, but with different parameterization, except unidirectional curve
    
    :y:         current pool liquidity in token y
    :yint:      initial / maximal pool liquidity in token y (at price Pa)
    :L:         effective pool constant (equals kbar = sqrt(k) for VTBCPMM)
    :Pa, Pb:    start and end price of the range, in dy/dx, Pa > Pb*
    :A, B:      alternatives for Pa, Pb; A = sqrt(Pa) - sqrt(Pb), B = sqrt(Pb)*
    
    
    *must provide either (Pa, Pb) or (A, B) but not both
    """
    
    Pa: float
    Pb: float
    yint: float
    y: float = None


    def __post_init__(self):
        
        if self.y is None:
            super().__setattr__("y", self.yint)
            
        if self.Pa <= self.Pb:
            raise ValueError(f"Pa={self.Pa} must be > Pb={self.Pb}")
        
        A = _m.sqrt(self.Pa) - _m.sqrt(self.Pb)
        B = _m.sqrt(self.Pb)
        super().__setattr__("A", A)
        super().__setattr__("B", B)
        
        # see from_carbon() in cpc.py
        kappa = self.yint**2 / self.A**2
        yasym_times_A = self.yint * B
        kappa_times_A = self.yint**2 / A
        x0 = kappa_times_A / (self.y * A + yasym_times_A) if self.y * A + yasym_times_A != 0 else 1e99
        y0 = _m.sqrt(kappa) * B # = sqrt(kappa) * sqrt(Pb) = L * sqrt(Pb)
            
        super().__setattr__("kappa", kappa)
        super().__setattr__("x0", x0)
        super().__setattr__("y0", y0)
        print("[CarbonFunction] x0, y0:", self.x0, self.y0)
    
    @classmethod
    def from_AB(cls, A, B, yint, y=None):
        """create a CarbonFunction from A, B"""
        Pa = (A+B)**2
        Pb = (B**2)
        return cls(Pa=Pa, Pb=Pb, yint=yint, y=y)
    
    @property
    def kbar(self):
        """kbar = sqrt(k), ie the properly scaling version of k"""
        return _m.sqrt(self.k)

    @property
    def k(self):
        """k = kappa"""
        return self.kappa
    
    def f(self, x):
        if x<0: return None
        y = self.k/(x+self.x0) - self.y0
        if y<0: return None
        return y
    
    # def p(self, x):
    #     p = self.k/(x+self.x0)**2
    #     if p < self.Pb or p > self.Pa:
    #         return None
    #     else:
    #         return p
    
    # def pp(self, x):
    #     return -2*self.k/(x+self.x0)**3
Carbon = CarbonFunction



@_dataclass(frozen=True)
class SolidlyFunction(_Function):
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
    def kbar(self):
        """kbar = k^(1/4), ie the properly scaling version of k"""
        return _m.sqrt(_m.sqrt(self.k))
    
    @property
    def method(self):
        """the method used to calculate y(x,k)"""
        return self._method
    
    @staticmethod    
    def _L1_float(x, k):
        """using float (precision issues)"""
        return -27*k/(2*x) + _m.sqrt(729*k**2/x**2 + 108*x**6)/2
    
    @staticmethod
    def _L1_dec(x, k, *, precision):
        """using decimal to avoid precision issues (slow)"""
        prec0 = _d.getcontext().prec
        _d.getcontext().prec = precision
        x,k = _D(x), _D(k)
        xi = (108 * x**8) / (729 * k**2)
        lam = (_D(1) + xi).sqrt() - _D(1)
        L = lam * (27 * k) / (2 * x)
        _d.getcontext().prec = prec0
        return float(L)
    
    @staticmethod
    def _L1_dec100(x, k):
        """using decimal 100 to avoid precision issues (slow; calls _L1_dec)"""
        return SolidlyFunction._L1_dec(x, k, precision=100)
    
    @staticmethod
    def _L1_dec1000(x, k):
        """using decimal 1000 to avoid precision issues (very slow; calls _L1_dec)"""
        return SolidlyFunction._L1_dec(x, k, precision=1000)
    
    @staticmethod
    def _L2_taylor(x, k):
        """
        using Taylor expansion for small x for avoid precision issues (transition artifacts)
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
Solidly = SolidlyFunction