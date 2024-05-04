"""
representing a levered constant product curve

---
(c) Copyright Bprotocol foundation 2023. 
Licensed under MIT
"""
__VERSION__ = "4.0-beta1"
__DATE__ = "04/May/2024"

from dataclasses import dataclass, field, asdict, InitVar
from .simplepair import SimplePair as Pair
from . import tokenscale as ts
import random
from math import sqrt
import numpy as np
import pandas as pd
import json
from matplotlib import pyplot as plt
from .params import Params
import itertools as it
import collections as cl
from sys import float_info
from hashlib import md5 as digest
import time
from .curvebase import CurveBase, AttrDict, DAttrDict, dataclass_


AD = DAttrDict



TOKENIDS = AttrDict(
    NATIVE_ETH="0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE",
    WETH="0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2",
    ETH="0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2",
    WBTC="0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599",
    BTC="0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599",
    USDC="0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48",
    USDT="0xdAC17F958D2ee523a2206206994597C13D831ec7",
    DAI="0x6B175474E89094C44Da98b954EedeAC495271d0F",
    LINK="0x514910771AF9Ca656af840dff83E8264EcF986CA",
    BNT="0x1F573D6Fb3F13d689FF844B4cE37794d79a7FF1C",
    HEX="0x2b591e99afE9f32eAA6214f7B7629768c40Eeb39",
    UNI="0x1f9840a85d5aF5bf1D1762F925BDADdC4201F984",
    FRAX="0x3432B6A60D23Ca0dFCa7761B7ab56459D9C964D0",
    ICHI="0x903bEF1736CDdf2A537176cf3C64579C3867A881",


)
T = TOKENIDS


@dataclass_
class ConstantProductCurve(CurveBase):
    """
    represents a, potentially levered, constant product curve

    :k:        pool invariant k (see NOTE2 below) 
    :x:        (virtual) pool state x (virtual number of base tokens for sale)
    :x_act:    actual pool state x (actual number of base tokens for sale)
    :y_act:    actual pool state y (actual number of quote tokens for sale)
    :alpha:    weight factor alpha of token x (default = 0.5; see NOTE3 below)
    :eta:      portfolio weight factor eta (default = 1; see NOTE3 below)
    :pair:     token pair in slash notation ("TKNB/TKNQ"); TKNB is on the x-axis, TKNQ on the y-axis
    :cid:      unique id (optional)
    :fee:      fee (optional); eg 0.01 for 1%
    :descr:    description (optional; eg. "UniV3 0.1%")
    :constr:   which (alternative) constructor was used (optional; user should not set)
    :params:   additional parameters (optional)

    NOTE1: always use the alternative constructors ``from_xx`` rather then the 
    canonical one; if you insist on using the canonical one then keep in mind
    that the order of the parameters may change in future versions, so you
    MUST use keyword arguments
    
    NOTE2: This class implements two distinct types of constant product curves:
    (1) the standard constant product curve xy=k
    (2) the weighted constant product curve x^al y^1-al = k^al
    Note that the case alpha=0.5 is equivalent to the standard constant product curve
    xy=k, including the value of k
    
    NOTE3: There are two different ways of specifying the weights of the tokens
    (1) alpha: the weight of the x token (equal weight = 0.5), such that x^al y^1-al = k^al
    (2) eta = alpha / (1-alpha): the relative weight (equal weight = 1; x overweight  > 1)
    """

    __VERSION__ = __VERSION__
    __DATE__ = __DATE__

    k: float
    x: float
    x_act: float = None
    y_act: float = None
    alpha: float = None
    pair: str = None
    cid: str = None
    fee: float = None
    descr: str = None
    constr: str = field(default=None, repr=True, compare=False, hash=False)
    params: AttrDict = field(default=None, repr=True, compare=False, hash=False)

    def __post_init__(self):
        
        if self.alpha is None:
            super().__setattr__("_is_symmetric", True) 
            super().__setattr__("alpha", 0.5) 
        else:
            super().__setattr__("_is_symmetric", self.alpha == 0.5) 
            #print(f"[ConstantProductCurve] _is_symmetric = {self._is_symmetric}")
            assert self.alpha > 0, f"alpha must be > 0 [{self.alpha}]"
            assert self.alpha < 1, f"alpha must be < 1 [{self.alpha}]"
    

        if self.constr is None:
            super().__setattr__("constr", "default")
            
        super().__setattr__("cid", str(self.cid))   

        if self.params is None:
            super().__setattr__("params", AttrDict())
        elif isinstance(self.params, str):
            data = json.loads(self.params.replace("'", '"'))
            super().__setattr__("params", AttrDict(data))
        elif isinstance(self.params, dict):
            super().__setattr__("params", AttrDict(self.params))

        if self.x_act is None:
            super().__setattr__("x_act", self.x)  # required because class frozen

        if self.y_act is None:
            super().__setattr__("y_act", self.y)  # ditto

        if self.pair is None:
            super().__setattr__("pair", "TKNB/TKNQ")

        super().__setattr__("pairo", Pair(self.pair))

        if self.isbigger(big=self.x_act, small=self.x):
            print(f"[ConstantProductCurve] x_act > x in {self.cid}", self.x_act, self.x)
            
        if self.isbigger(big=self.y_act, small=self.y):
            print(f"[ConstantProductCurve] y_act > y in {self.cid}", self.y_act, self.y)

        

        self.set_tokenscale(self.TOKENSCALE)

    def P(self, pstr, defaultval=None):
        """
        convenience function to access parameters

        :pstr:          parameter name as colon separated string (eg "exchange") (1)
        :defaultval:    default value if parameter not found
        :returns:       parameter value or defaultval*

        NOTE1: ``CC.pstr("exchange")`` is equivalent to ``CC.params["exchange"]`` if defined
        ``CC.pstr("a:b")`` is equivalent to ``CC.params["a"]["b"]`` if defined
        """
        fieldl = pstr.strip().split(":")
        val = self.params
        for field in fieldl:
            try:
                val = val[field]
            except KeyError:
                return defaultval
        return val

    @property
    def cid0(self):
        "short cid [last 8 characters]"
        return self.cid[-8:]
    
    @property
    def eta(self):
        "portfolio weight factor eta = alpha / (1-alpha)"
        return self.alpha / (1 - self.alpha)
    
    def is_constant_product(self):
        "True iff alpha == 0.5 (deprecated; use `is_symmetric`)"
        return self.is_symmetric()
    
    def is_symmetric(self):
        "True iff alpha == 0.5"
        return self._is_symmetric
    
    def is_asymmetric(self):
        "True iff alpha != 0.5"
        return not self.is_symmetric()
    
    def is_levered(self):
        "True iff x!=x_act or y!=y_act"
        return not self.is_unlevered()
    
    def is_unlevered(self):
        "True iff x==x_act and y==y_act"
        return self.x == self.x_act and self.y == self.y_act
    
    TOKENSCALE = ts.TokenScale1Data
    # default token scale object is the trivial scale (everything one)
    # change this to a different scale object be creating a derived class

    def set_tokenscale(self, tokenscale):
        """sets the tokenscale object (returns self)"""
        # print("setting tokenscale", self.cid, tokenscale)
        super().__setattr__("tokenscale", tokenscale)
        return self

    @property
    def scalex(self):
        """returns the scale of the x-axis token"""
        return self.tokenscale.scale(self.tknx)

    @property
    def scaley(self):
        """returns the scale of the y-axis token"""
        return self.tokenscale.scale(self.tkny)

    def scale(self, tkn):
        """returns the scale of tkn"""
        return self.tokenscale.scale(tkn)

    def asdict(self):
        "returns a dict representation of the curve"
        return asdict(self)

    @classmethod
    def fromdict(cls, d):
        "returns a curve from a dict representation"
        return cls(**d)
    
    from_dict = fromdict # DEPRECATED (use fromdict)

    def setcid(self, cid):
        """sets the curve id [can only be done once]"""
        assert self.cid is None, "cid can only be set once"
        super().__setattr__("cid", cid)
        return self

    class CPCValidationError(ValueError): pass
    
    @classmethod
    def from_kx(
        cls,
        k,
        x,
        *,
        x_act=None,
        y_act=None,
        pair=None,
        cid=None,
        fee=None,
        descr=None,
        params=None,
    ):
        "constructor: from k,x (and x_act, y_act)"
        return cls(
            k=k,
            x=x,
            x_act=x_act,
            y_act=y_act,
            pair=pair,
            cid=cid,
            fee=fee,
            descr=descr,
            constr="kx",
            params=params,
        )

    @classmethod
    def from_ky(
        cls,
        k,
        y,
        *,
        x_act=None,
        y_act=None,
        pair=None,
        cid=None,
        fee=None,
        descr=None,
        params=None,
    ):
        "constructor: from k,y (and x_act, y_act)"
        return cls(
            k=k,
            x=k / y,
            x_act=x_act,
            y_act=y_act,
            pair=pair,
            cid=cid,
            fee=fee,
            descr=descr,
            constr="ky",
            params=params,
        )

    @classmethod
    def from_xy(
        cls,
        x,
        y,
        *,
        x_act=None,
        y_act=None,
        pair=None,
        cid=None,
        fee=None,
        descr=None,
        params=None,
    ):
        "constructor: from x,y (and x_act, y_act)"
        return cls(
            k=x * y,
            x=x,
            x_act=x_act,
            y_act=y_act,
            pair=pair,
            cid=cid,
            fee=fee,
            descr=descr,
            constr="xy",
            params=params,
        )

    @classmethod
    def from_xyal(
        cls,
        x,
        y,
        *,
        alpha=None,
        eta=None,
        x_act=None,
        y_act=None,
        pair=None,
        cid=None,
        fee=None,
        descr=None,
        params=None,
    ):
        "constructor: from x,y,alpha/eta (and x_act, y_act)"
        if not alpha is None and not eta is None:
            raise ValueError(f"at most one of alpha and eta must be given [{alpha}, {eta}]")
        if not eta is None:
            alpha = eta / (eta + 1)
        if alpha is None:
            alpha = 0.5
        assert alpha > 0, f"alpha must be > 0 [{alpha}]"
        eta_inv = (1-alpha) / alpha
        k = x * (y**eta_inv)
        #print(f"[from_xyal] eta_inv = {eta_inv}")
        #print(f"[from_xyal] x={x}, y={y}, k = {k}")
        if not alpha == 0.5:
            assert x_act is None, f"currently not allowing levered curves for alpha != 0.5 [alpha={alpha}, x_act={x_act}]"
            assert y_act is None, f"currently not allowing levered curves for alpha != 0.5 [alpha={alpha}, x_act={y_act}]"
        return cls(
            #k=(x**alpha * y**(1-alpha))**(1/alpha),
            k=k,
            x=x,
            alpha=alpha,
            x_act=x_act,
            y_act=y_act,
            pair=pair,
            cid=cid,
            fee=fee,
            descr=descr,
            constr="xyal",
            params=params,
        )


    @classmethod
    def from_pk(
        cls,
        p,
        k,
        *,
        x_act=None,
        y_act=None,
        pair=None,
        cid=None,
        fee=None,
        descr=None,
        params=None,
    ):
        "constructor: from k,p (and x_act, y_act)"
        return cls(
            k=k,
            x=sqrt(k / p),
            x_act=x_act,
            y_act=y_act,
            pair=pair,
            cid=cid,
            fee=fee,
            descr=descr,
            constr="pk",
            params=params,
        )

    @classmethod
    def from_px(
        cls,
        p,
        x,
        x_act=None,
        y_act=None,
        pair=None,
        cid=None,
        fee=None,
        descr=None,
        params=None,
    ):
        "constructor: from x,p (and x_act, y_act)"
        return cls(
            k=x * x * p,
            x=x,
            x_act=x_act,
            y_act=y_act,
            pair=pair,
            cid=cid,
            fee=fee,
            descr=descr,
            constr="px",
            params=params,
        )

    @classmethod
    def from_py(
        cls,
        p,
        y,
        x_act=None,
        y_act=None,
        pair=None,
        cid=None,
        fee=None,
        descr=None,
        params=None,
    ):
        "constructor: from y,p (and x_act, y_act)"
        return cls(
            k=y * y / p,
            x=y / p,
            x_act=x_act,
            y_act=y_act,
            pair=pair,
            cid=cid,
            fee=fee,
            descr=descr,
            constr="py",
            params=params,
        )

    @classmethod
    def from_pkpp(
        cls,
        p,
        k,
        p_min=None,
        p_max=None,
        *,
        pair=None,
        cid=None,
        fee=None,
        descr=None,
        constr=None,
        params=None,
    ):
        "constructor: from k, p, p_min, p_max (default for last two is p)"
        if p_min is None:
            p_min = p
        if p_max is None:
            p_max = p
        x0 = sqrt(k / p)
        y0 = sqrt(k * p)
        xa = x0 - sqrt(k / p_max)
        ya = y0 - sqrt(k * p_min)
        constr = constr or "pkpp"
        return cls(
            k=k,
            x=x0,
            x_act=xa,
            y_act=ya,
            pair=pair,
            cid=cid,
            fee=fee,
            descr=descr,
            constr="pkpp",
            params=params,
        )

    @classmethod
    def from_univ2(
        cls,
        *,
        liq_tknb=None,
        liq_tknq=None,
        k=None,
        pair=None,
        fee=None,
        cid=None,
        descr=None,
        params=None,
    ):
        """
        constructor: from Uniswap V2 pool (see class docstring for other parameters)

        :liq_tknb:      current pool liquidity in tknb (base token of the pair; "x") (1)
        :liq_tknq:      current pool liquidity in tknq (quote token of the pair; "y") (1)
        :k:             uniswap liquidity parameter k = xy (1)

        NOTE 1: exactly one of k, liq_tknb, liq_tknq must be None; all other parameters 
        must not be None; a reminder that x is TKNB and y is TKNQ and pair is "TKNB/TKNQ"
        """
        assert not pair is None, "pair must not be None"
        assert not cid is None, "cid must not be None"
        assert not descr is None, "descr must not be None"
        assert not fee is None, "fee must not be None"

        x = liq_tknb
        y = liq_tknq
        if k is None:
            assert x is not None and y is not None, "k is not provided, so both liquidities must be"
            k = x * y
        elif x is None:
            assert y is not None, "k is provided, so must provide exactly one liquidity"
            x = k / y
        elif y is None:
            y = k / x
        else:
            assert False, "exactly one of k and the liquidities must be None"

        return cls(
            k=k,
            x=x,
            x_act=x,
            y_act=y,
            pair=pair,
            cid=cid,
            fee=fee,
            descr=descr,
            constr="uv2",
            params=params,
        )

    @classmethod
    def from_univ3(cls, Pmarg, uniL, uniPa, uniPb, pair, cid, fee, descr, params=None):
        """
        constructor: from Uniswap V3 pool (see class docstring for other parameters)

        :Pmarg:     current pool marginal price
        :uniL:      uniswap liquidity parameter (uniL**2 == L**2 == k)
        :uniPa:     uniswap price range lower bound Pa (Pa < P < Pb)
        :uniPb:     uniswap price range upper bound Pb (Pa < P < Pb)
        """

        P = Pmarg
        assert uniPa < uniPb, f"uniPa < uniPb required ({uniPa}, {uniPb})"
        assert (
            uniPa <= P <= uniPb
        ), f"uniPa < Pmarg < uniPb required ({uniPa}, {P}, {uniPb})"
        if params is None:
            params = AttrDict(L=uniL)
        else:
            params = AttrDict({**params, "L": uniL})
        k = uniL * uniL
        return cls.from_pkpp(
            p=P,
            k=k,
            p_min=uniPa,
            p_max=uniPb,
            pair=pair,
            cid=cid,
            fee=fee,
            descr=descr,
            constr="uv3",
            params=params,
        )
    
    SOLIDLY_PRICE_SPREAD = 0.06     # 0.06 gives pretty good results for m=2.6
    @classmethod
    def from_solidly(
        cls,
        *,
        k=None,
        x=None,
        y=None,
        price_spread=None,
        pair=None,
        fee=None,
        cid=None,
        descr=None,
        params=None,
        as_list=True,
    ):
        """
        constructor: from a Solidly curve (see class docstring for other parameters)*

        :k:             Solidly pool constant, x^3 y + x y^3 = k*
        :x:             current pool liquidity in token x*
        :y:             current pool liquidity in token y*
        :price_spread:  price spread to use for converting constant price -> constant product
        :as_list:       if True (default) returns a list of curves, otherwise a single curve
                        (see note below and note that as_list=False is deprecated)
        
        exactly 2 out of those three must be given; the third one is calculated
        
        The Solidly curve is NOT a constant product curve, as it follows the equation
        
            x^3 y + x y^3 = k
            
        where k is the pool invariant. This curve is a stable swap curve in the it is
        very flat in the middle, at a unity price (see the `invariants` module and the
        associated tests and notebooks). In fact, in the range
        
            1/2.6 < y/x < 2.6
            
        we find that the prices is essentially unity, and we therefore approximate it
        was an (almost) constant price curve, ie a constant product curve with a very
        large invariant k, and we will set the x_act and y_act parameters so that the
        curve only covers the above range.
        
        IMPORTANT: IF as_list is True (default) THEN THE RESULT IS RETURNED AS A LIST
        CURRENTLY CONTAINING A SINGLE CURVE, NOT THE CURVE ITSELF. This is because we 
        may in the future a list of curves, with additional curves matching the function
        in the wings. IT IS RECOMMENDED THAT ANY CODE IMPLEMENTING THIS FUNCTION USES
        as_list = True, AS IN THE FUTURE as_list = FALSE will raise an exception.
        """
        # rename the solidly parameters to avoid name confusion
        solidly_x = x
        solidly_y = y
        solidly_k = k
        del x, y, k
        price_spread = price_spread or cls.SOLIDLY_PRICE_SPREAD
        #print([_ for _ in [solidly_x, solidly_y, solidly_k] if not _ is None])
        assert len([_ for _ in [solidly_x, solidly_y, solidly_k] if not _ is None]) == 2, f"exactly 2 out of k,x,y must be given (x={solidly_x}, y={solidly_y}, k={solidly_x})"
        if solidly_k is None:
            solidly_k = solidly_x**3 * solidly_y + solidly_x * solidly_y**3
            # NOTE: this is currently the only implemented version, and it should be
            # enough for our purposes; the other two can be implemented using the 
            # y(x) function from the invariants module (note that y(x) and x(y) are 
            # the same as the function is symmetric). We do not want to implement it
            # at the moment as we do not think we need it, and we want to avoid this
            # external dependency for the time being.
        elif solidly_x is None:
            raise NotImplementedError("providing k, y not implemented yet")
        elif solidly_y is None:
            raise NotImplementedError("providing k, x not implemented yet")
        else:
            raise ValueError(f"should never get here")
        # kbar = (k/2)**(1/4) is the equivalent of kbar = sqrt(k) for constant product
        # center of the curve is (xy_c, xy_c) = (kbar, kbar)
        # we are looking for the intersects of y=mx for m=2.6 and m=1/2.6 (linear segment)
        # we know that within that range, x-y = const, so we can analytically solve for x and y
        # specifically, we have y = 2 xy_c - x = mx  
        # therefore x = 2 xy_c / (m+1)
        solidly_kbar = (solidly_k/2)**(1/4)
        solidly_xyc = solidly_kbar
        solidly_xmin = 2 * solidly_xyc / (2.6 + 1)
        solidly_xmax = 2 * solidly_xyc / (1/2.6 + 1)
        solidly_xrange = solidly_xmax - solidly_xmin
        # print(f"[from_solidly] k = {solidly_k}, kbar = {solidly_kbar}, xy_c = {xy_c}")
        # print(f"[from_solidly] x_min = {solidly_xmin}, x_max = {solidly_xmax}, x_range = {x_range}")
        
        # the curve has a unity price, which we spread to 1+price_spread at x_min,
        # and 1-price_spread at x_max; we set x_range = x_max - x_min and we get
        # the following equations
        #   k/x0**2 = (1+price_spread)
        #   k/(x0+xrange)**2 = 1/(1+price_spread)
        # solving this fo k, x0 we get
        #   k = (1+price_spread)*xrange**2 / price_spread**2
        #   x0 = xrange / price_spread
        cpc_k = (1+price_spread)*solidly_xrange**2 / price_spread**2
        cpc_x0 = solidly_xrange / price_spread
        
        # finally we need to see where in the range we are; we look at 
        #    del_x = x - x_min
        # and we must have
        #   del_x > 0
        #   del_x < x_range
        # for the approximation to be valid; we recall that x_min ~ cpc_x0, therefore
        #   x = cpc_x0 + del_x
        # Also, x_act is the x that is left to the right of the range, therefore 
        #   x_act = x_range - del_x
        # Finally, y_act is the amount of y that trades use from our current position
        # back to x=x_min; we slightly approximate this by ignoring the price spread
        # (which in any case is not real!) and assuming unity price, so del_y ~ del_y
        #   y_act = del_y = del_x
        solidly_delx = solidly_x - solidly_xmin
        if solidly_delx < 0 or solidly_delx > solidly_xrange:
            if as_list:
                #print(f"[cpc::from_solidly] x={solidly_x} is outside the range [{solidly_xmin}, {solidly_xmax}] and as_list=True")
                return []
            else:
                raise ValueError(f"x={solidly_x} is outside the range [{solidly_xmin}, {solidly_xmax}] and as_list=False")
        
        # now deal with the params, ie add the s_xxx parameters for solidly
        params0 = dict(s_x = solidly_x, s_y = solidly_y, s_k = solidly_k, s_kbar = solidly_kbar, s_cpck=cpc_k, s_cpcx0 = cpc_x0,
                    s_xmin = solidly_xmin, s_xmax = solidly_xmax, s_price_spread = price_spread)
        if params is None:
            params = AttrDict(params0)
        else:
            params = AttrDict({**params, **params0})
        
        result = cls(
            k=cpc_k,
            x=cpc_x0+solidly_delx,                # del_x = x - xmin
            # x_act=solidly_xrange-solidly_delx,
            # y_act=solidly_delx,
            x_act=solidly_delx,
            y_act=solidly_xrange-solidly_delx,
            pair=pair,
            cid=cid,
            fee=fee,
            descr=descr,
            constr="solidly",
            params=params,
        )
        if as_list:
            return [result]
        else:
            print("[cpc::from_solidly] returning curve directly is deprecated; prepare to accept a list of curves in the future")
            return result
        
    # minimun range width (pa/pb-1)  for carbon curves and sqrt thereof
    CARBON_MIN_RANGEWIDTH  = 1e-6 
    
    @classmethod
    def from_carbon(
        cls,
        *,
        yint=None,
        y=None,
        pa=None,
        pb=None,
        A=None,
        B=None,
        pair=None,
        tkny=None,
        fee=None,
        cid=None,
        descr=None,
        params=None,
        isdydx=True,
        minrw=None,
    ):
        """
        constructor: from a single Carbon order (see class docstring for other parameters) (1)

        :yint:      current pool y-intercept (also known as z)
        :y:         current pool liquidity in token y
        :pa:        carbon price range left bound (higher price in dy/dx)
        :pb:        carbon price range right bound (lower price in dy/dx)
        :A:         alternative to pa, pb: A = sqrt(pa) - sqrt(pb) in dy/dy
        :B:         alternative to pa, pb: B = sqrt(pb) in dy/dy
        :tkny:      token y
        :isdydx:    if True prices in dy/dx, if False in quote direction of the pair
        :minrw:     minimum perc width (pa/pb-1) of range (default CARBON_MIN_RANGEWIDTH)

        NOTE 1: that ALL parameters are mandatory, except that EITHER pa, bp OR A, B
        must be given but not both; we do not correct for incorrect assignment of
        pa and pb, so if pa <= pb IN THE DY/DX DIRECTION, MEANING THAT THE NUMBERS
        ENTERED MAY SHOW THE OPPOSITE RELATIONSHIP, then an exception will be raised
        """
        assert not yint is None, "yint must not be None"
        assert not y is None, "y must not be None"
        assert not pair is None, "pair must not be None"
        assert not tkny is None, "tkny must not be None"
        
        if minrw is None:
            minrw = cls.CARBON_MIN_RANGEWIDTH
        
        assert y <= yint, "y must be <= yint"
        assert y >= 0, "y must be >= 0"

        if A is None or B is None:
            # A,B is None, so we look at prices and isdydx
            # print("[from_carbon] A, B:", A, B, pa, pb)
            assert A is None and B is None, "A or B is None, so both must be None"
            assert pa is not None and pb is not None, "A,B is None, so pa,pb must not"

        if pa is None or pb is None:
            # pa,pb is None, so we look at A,B and isdydx must be True
            # print("[from_carbon] pa, pb:", A, B, pa, pb)
            assert pa is None and pb is None, "pa or pb is None, so both must be None"
            assert A is not None and B is not None, "pa,pb is None, so A,B must not"
            assert isdydx is True, "we look at A,B so isdydx must be True"
            assert (
                A >= 0
            ), "A must be non-negative"  # we only check for this one as it is a difference

        assert not (
            A is not None and B is not None and pa is not None and pb is not None
        ), "either A,B or pa,pb must be None"

        tknb, tknq = pair.split("/")
        assert tkny in (tknb, tknq), f"tkny must be in pair ({tkny}, {pair})"
        tknx = tknb if tkny == tknq else tknq

        if A is None or B is None:
            # A,B is None, so we look at prices and isdydx

            # pair quote direction is tknq per tknb; dy/dx is tkny per tknx
            # therefore, dy/dx equals pair quote direction if tkny == tknq, otherwise reverse
            if not isdydx:
                if not tkny == tknq:
                    pa, pb = 1 / pa, 1 / pb

            # small and zero-width ranges are extended for numerical stability
            pa0, pb0 = pa, pb
            if pa/pb-1 < minrw:
                pa = pb = sqrt(pa*pb)
                assert pa == pb, "just making sure"
            if pa == pb:
                # pa *= 1.0000001
                # pb /= 1.0000001
                rw_multiplier = sqrt(1+minrw)
                pa *= rw_multiplier
                pb /= rw_multiplier

            # validation
            if not pa/pb - 1 >= minrw*0.99:
                raise cls.CPCValidationError(f"pa > pb required ({pa}, {pb}, {pa/pb-1}, {minrw})")

            # finally set A, B
            A = sqrt(pa) - sqrt(pb)
            B = sqrt(pb)
            A0 = A if pa0 != pb0 else 0
        else:
            pb0 = B * B             # B = sqrt(pb), A = sqrt(pa) - sqrt(pb)
            pa0 = (A+B) * (A+B)     # A+B = sqrt(pa)
            A0 = A
            if A/B < 1e-7:
                A = B*1e-7

        # set some intermediate parameters (see handwritten notes in repo)
        # yasym = yint * B / A
        kappa = yint**2 / A**2
        yasym_times_A = yint * B
        kappa_times_A = yint**2 / A

        params0 = dict(y=y, yint=yint, A=A0, B=B, pa=pa0, pb=pb0, minrw=minrw)
        if params is None:
            params = AttrDict(params0)
        else:
            params = AttrDict({**params, **params0})

        # finally instantiate the pool

        return cls(
            k=kappa,
            x=kappa_times_A / (y * A + yasym_times_A) if y * A + yasym_times_A != 0 else 1e99,
            #x=kappa / (y + yasym) if y + yasym != 0 else 0,
            x_act=0,
            y_act=y,
            pair=f"{tknx}/{tkny}",
            cid=cid,
            fee=fee,
            descr=descr,
            constr="carb",
            params=params,
        )

    
    def execute(self, dx=None, dy=None, *, ignorebounds=False, verbose=False):
        """
        executes a transaction in the pool, returning a new curve object

        :dx:                amount of token x to be +added to/-removed from the pool (1)
        :dy:                amount of token y to be +added to/-removed from the pool (1)
        :ignorebounds:      if True, ignore bounds on x_act, y_act
        :returns:   new curve object

        NOTE1: at least one of ``dx, dy`` must be None
        """
        assert self.is_constant_product(), "only implemented for constant product curves"
        
        if not dx is None and not dy is None:
            raise ValueError(f"either dx or dy must be None dx={dx} dy={dy}")

        if dx is None and dy is None:
            dx = 0

        if not dx is None:
            if not dx >= -self.x_act:
                if not ignorebounds:
                    raise ValueError(
                        f"dx must be >= -x_act (dx={dx}, x_act={self.x_act} {self.tknx} [{self.cid}: {self.pair}])"
                    )
            newx = self.x + dx
            newy = self.k / newx

        else:
            if not dy >= -self.y_act:
                if not ignorebounds:
                    raise ValueError(
                        f"dy must be >= -y_act (dy={dy}, y_act={self.y_act} {self.tkny} [{self.cid}: {self.pair}])"
                    )
            newy = self.y + dy
            newx = self.k / newy

        if verbose:
            if dx is None:
                dx = newx - self.x
            if dy is None:
                dy = newy - self.y
            print(
                f"{self.pair} dx={dx:.2f} {self.tknx} dy={dy:.2f} {self.tkny} | x:{self.x:.1f}->{newx:.1f} xa:{self.x_act:.1f}->{self.x_act+newx-self.x:.1f} ya:{self.y_act:.1f}->{self.y_act+newy-self.y:.1f} k={self.k:.1f}"
            )

        return self.__class__(
            k=self.k,
            x=newx,
            x_act=self.x_act + newx - self.x,
            y_act=self.y_act + newy - self.y,
            pair=self.pair,
            cid=f"{self.cid}-x",
            fee=self.fee,
            descr=f"{self.descr} [dx={dx}]",
            params={**self.params, "traded": {"dx": dx, "dy": dy}},
        )

    @property
    def tknb(self):
        "base token"
        return self.pair.split("/")[0]

    tknx = tknb

    @property
    def tknq(self):
        "quote token"
        return self.pair.split("/")[1]

    tkny = tknq

    @property
    def tknbp(self):
        """prettified base token"""
        return Pair.n(self.tknb)

    tknxp = tknbp

    @property
    def tknqp(self):
        """prettified quote token"""
        return Pair.n(self.tknq)

    tknyp = tknqp

    @property
    def pairp(self):
        """prettified pair"""
        return f"{self.tknbp}/{self.tknqp}"

    def description(self):
        "description of the pool"
        assert self.is_constant_product(), "only implemented for constant product curves"
        
        s = ""
        s += f"cid      = {self.cid0} [{self.cid}]\n"
        s += f"primary  = {Pair.n(self.pairo.primary)} [{self.pairo.primary}]\n"
        s += f"pp       = {self.pp:,.6f} {self.pairo.pp_convention}\n"
        s += f"pair     = {Pair.n(self.pair)} [{self.pair}]\n"
        s += f"tknx     = {self.x_act:20,.6f} {self.tknx:10} [virtual: {self.x:20,.3f}]\n"
        s += f"tkny     = {self.y_act:20,.6f} {self.tkny:10} [virtual: {self.y:20,.3f}]\n"
        s += f"p        = {self.p} [min={self.p_min}, max={self.p_max}] {self.tknq} per {self.tknb}\n"
        s += f"fee      = {self.fee}\n"
        s += f"descr    = {self.descr}\n"
        return s

    @property
    def y(self):
        "(virtual) pool state x (virtual number of base tokens for sale)"
        
        if self.k == 0:
            return 0
        if self.is_constant_product():
            return self.k / self.x
        return (self.k / self.x)**(self.eta)
        
    @property
    def p(self):
        "pool price (in dy/dx)"
        if self.is_constant_product():
            return self.y / self.x 
        
        return self.eta * self.y / self.x
    
    def buysell(self, *, verbose=False, withprice=False):
        """
        returns b (buy primary tknb), s (sells primary tknb) or bs (buys and sells)
        """
        b,s = ("b", "s") if not verbose else ("buy-", "sell-")
        xa, ya = (self.x_act, self.y_act) if self.pairo.isprimary else (self.y_act, self.x_act)
        result  = b if ya > 0 else ""
        result += s if xa > 0 else ""
        if verbose:
            result += f"{self.pairo.primary_tknb}"
            if withprice:
                result += f" @ {self.primaryp(withconvention=True)}"
            return result
        if withprice:
            return result, self.primaryp()
        else:
            return result
    
    def buy(self):
        """returns 'b' if the curve buys the primary token, '' otherwise"""
        return self.buysell(verbose=False, withprice=False).replace("s", "")
    
    def sell(self):
        """returns 's' if the curve sells the primary token, '' otherwise"""
        return self.buysell(verbose=False, withprice=False).replace("b", "")
        
    ITM_THRESHOLDPC = 0.01
    @classmethod
    def itm0(cls, bsp1, bsp2, *, thresholdpc=None):
        """
        whether or not two positions are in the money against each other

        :bsp1:          first position ("bs", price) [from buysell]
        :bsp2:          ditto second position
        :thresholdpc:   in-the-money threshold in percent (default: ITM_THRESHOLD)
        """
        if thresholdpc is None:
            thresholdpc = cls.ITM_THRESHOLDPC
        bs1, p1 = bsp1
        bs2, p2 = bsp2
        
        # if  prices are equal (within threshold), positions are not in the money
        if abs(p2/p1-1) < thresholdpc:
            return False
        if bs1 == "bs" and bs2 == "bs":
            return True
        
        if p2 > p1:
            # if p2 > p1: amm1 must sell and amm2 must buy
            return "s" in bs1 and "b" in bs2
        else:
            # if p1 < p2: amm1 must buy and amm2 must sell
            return "b" in bs1 and "s" in bs2
    
    def itm(self, other, *, thresholdpc=None, aggr=True):
        """
        like itm0, but self against another curve object

        :other:         other curve object, or iterable thereof
        :thresholdpc:   in-the-money threshold in percent (default: ITM_THRESHOLD)
        :aggr:          if True, and an iterable is passed, True iff one is in the money
        """
        assert self.is_constant_product(), "only implemented for constant product curves"
        
        try:
            itm_t = tuple(self.itm(o) for o in other)
            if not aggr:
                return itm_t
            return np.any(itm_t)
        except:
            pass
        bss = self.buysell(verbose=False, withprice=True)
        bso = other.buysell(verbose=False, withprice=True)
        return self.itm0(bss, bso, thresholdpc=thresholdpc)
    
    
    def tvl(self, tkn=None, *, mult=1.0, incltkn=False, raiseonerror=True):
        """
        total value locked in the curve, expressed in the token tkn (default: tknq)

        :tkn:               the token in which the tvl is expressed (tknb or tknq)
        :mult:              multiplier applied to the tvl (eg to convert ETH to USD)
        :incltkn:           if True, returns a tuple (tvl, tkn, mult)
        :raiseonerror:      if True, raises ValueError if tkn is not tknb or tknq
        :returns:           tvl (in tkn) or (tvl, tkn, mult) if incltkn is True
        """
        if tkn is None:
            tkn = self.tknq
        if not tkn in {self.tknb, self.tknq}:
            if raiseonerror:
                raise ValueError(f"tkn must be {self.tknb} or {self.tknq}")
            return None

        tvl_tknq = (self.p * self.x_act + self.y_act) * mult
        if tkn == self.tknq:
            return tvl_tknq if not incltkn else (tvl_tknq, self.tknq, mult)
        tvl_tknb = tvl_tknq / self.p
        return tvl_tknb if not incltkn else (tvl_tknb, self.tknb, mult)

    def p_convention(self):
        """price convention for p (dy/dx)"""
        return f"{self.tknyp} per {self.tknxp}"
    
    @property
    def primary(self):
        "alias for self.pairo.primary"
        return self.pairo.primary
    
    @property
    def isprimary(self):
        "alias for self.pairo.isprimary"
        return self.pairo.isprimary
    
    def primaryp(self, *, withconvention=False):
        "pool price in the native quote of the curve Pair object"
        price = self.pairo.pp(self.p)
        if not withconvention:
            return price
        return f"{price:.2f} {self.pairo.pp_convention}"     
    
    @property
    def pp(self):
        """alias for self.primaryp()"""
        return self.primaryp()

    @property
    def kbar(self):
        """
        kbar is pool invariant the scales linearly with the pool size
        
        kbar = sqrt(k) for constant product
        kbar = k^alpha for general curves
        """
        if self.is_constant_product():
            return sqrt(self.k)
        return self.k**self.alpha

    def invariant(self, xvec=None, *, include_target=False):
        """
        returns the actual invariant of the curve (eg x*y for constant product)
        
        :xvec:              vector of x values (default: current)
        :include_target:    if True, the target invariant returned in addition to the actual invariant
        :returns:           invariant, or (invariant, target)
        """
        if xvec is None: 
            xvec = {self.tknx: self.x, self.tkny: self.y}
        x,y = xvec[self.tknx], xvec[self.tkny]
        if self.is_constant_product():
            invariant = sqrt(x * y)
        else:
            invariant = x**self.alpha * y**(1-self.alpha)
        if not include_target:
            return invariant
        return (invariant, self.kbar)
        
    @property
    def x_min(self):
        "minimum (virtual) x value"
        if self.is_unlevered():
            return 0
        assert self.is_constant_product(), "only implemented for constant product curves"
        
        return self.x - self.x_act

    @property
    def at_xmin(self):
        """True iff x is at x_min"""
        if self.x_min == 0:
            return False
        return abs(self.x / self.x_min - 1) < 1e-6

    at_ymax = at_xmin

    @property
    def at_xmax(self):
        """True iff x is at x_max"""
        if self.x_max is None:
            return False
        return abs(self.x / self.x_max - 1) < 1e-6

    at_ymin = at_xmax

    @property
    def at_boundary(self):
        """True iff x is at either x_min or x_max"""
        return self.at_xmin or self.at_xmax

    @property
    def y_min(self):
        "minimum (virtual) y value"
        if self.is_unlevered():
            return 0
        assert self.is_constant_product(), "only implemented for constant product curves"
        
        return self.y - self.y_act

    @property
    def x_max(self):
        "maximum (virtual) x value"
        if self.is_unlevered():
            return None
        assert self.is_constant_product(), "only implemented for constant product curves"
        
        if self.y_min > 0:
            return self.k / self.y_min
        else:
            return None

    @property
    def y_max(self):
        "maximum (virtual) y value"
        if self.is_unlevered():
            return None
        assert self.is_constant_product(), "only implemented for constant product curves"
        
        if self.x_min > 0:
            return self.k / self.x_min
        else:
            return None

    @property
    def p_max(self):
        "maximum pool price (in dy/dx; None if unlimited) = y_max/x_min"
        if self.is_unlevered():
            return None
        assert self.is_constant_product(), "only implemented for constant product curves"
        
        if not self.x_min is None and self.x_min > 0:
            return self.y_max / self.x_min
        else:
            return None
        
    def p_max_primary(self, swap=True):
        "p_max in the native quote of the curve Pair object (swap=True: p_min)"
        if self.is_unlevered():
            return None
        p = self.p_max if not (swap and not self.isprimary) else self.p_min
        if p is None: return None
        return p if self.isprimary else 1/p
    
    @property
    def p_min(self):
        "minimum pool price (in dy/dx; None if unlimited) = y_min/x_max"
        if self.is_unlevered():
            return 0
        assert self.is_constant_product(), "only implemented for constant product curves"
        
        if not self.x_max is None and self.x_max > 0:
            return self.y_min / self.x_max
        else:
            return None
    
    def p_min_primary(self, swap=True):
        "p_min in the native quote of the curve Pair object (swap=True: p_max)"
        if self.is_unlevered():
            return 0
        p = self.p_min if not (swap and not self.isprimary) else self.p_max
        if p is None: return None
        return p if self.isprimary else 1/p
    
    def format(self, *, heading=False, formatid=None):
        """returns info about the curve as a formatted string"""
        assert self.is_constant_product(), "only implemented for constant product curves"
        
        if formatid is None:
            formatid = 0
        assert formatid in [0], "only formatid in [0] is supported"
        c = self
        cid = str(c.cid)[-10:]
        if heading:
            s = f"{'CID':>12} {'PAIR':>10}"
            s += f"{'xact':>20} {'tknx':>5}  {'yact':>20} {'tkny':>5}"
            s += f"{'price':>10} {'inverse':>10}"
            s += "\n" + "=" * len(s)
            return s
        s = f"{cid:>12} {c.pairp:>10}"
        s += f"{c.x_act:20,.3f} {c.tknxp:>5}  {c.y_act:20,.3f} {c.tknyp:>5}"
        s += f"{c.p:10,.2f} {1/c.p:10,.2f}"
        return s

    def xyfromp_f(self, p=None, *, ignorebounds=False, withunits=False):
        r"""
        returns x,y,p for a given marginal price p (stuck at the boundaries if ignorebounds=False)

        :p:                 marginal price (in dy/dx)
        :ignorebounds:      if True, ignore x_act and y_act; if False, return the x,y values where
                            x_act and y_act are at zero (i.e. the pool is empty in this direction)
        :withunits:         if False, return x,y,p; if True, also return tknx, tkny, pair
        
        
        $$
        x(p) = \left( \frac{\eta}{p}   \right) ^ {1-\alpha} k^\alpha
        y(p) = \left( \frac{p}{\eta}   \right) ^ \alpha     k^\alpha
        $$     
        """
        if p is None:
            p = self.p
            
        if self.is_constant_product():
            sqrt_p = sqrt(p)
            sqrt_k = self.kbar
            x = sqrt_k / sqrt_p
            y = sqrt_k * sqrt_p
        else:
            eta = self.eta
            alpha = self.alpha
            x = (eta/p)**(1-alpha) * self.kbar
            y = (p/eta)**alpha * self.kbar
        
        if not ignorebounds:
            if not self.x_min is None:
                if x < self.x_min:
                    x = self.x_min
            if not self.x_max is None:
                if x > self.x_max:
                    x = self.x_max
            if not self.y_min is None:
                if y < self.y_min:
                    y = self.y_min
            if not self.y_max is None:
                if y > self.y_max:
                    y = self.y_max

        if withunits:
            return x, y, p, self.tknxp, self.tknyp, self.pairp

        return x, y, p

    def xvecfrompvec_f(self, pvec, *, ignorebounds=False):
        """
        alternative API to xyfromp_f
        
        :pvec:      a dict containing all prices; the dict must contain the keys
                    for tknx and for tkny and the associated value must be the respective
                    price in any numeraire (only the ratio is used)
        :returns:   token amounts as dict {tknx: x, tkny: y}
        """
        assert self.tknx in pvec, f"pvec must contain price for {self.tknx} [{pvec.keys()}]"
        assert self.tkny in pvec, f"pvec must contain price for {self.tkny} [{pvec.keys()}]"
        p = pvec[self.tknx] / pvec[self.tkny]
        x, y, _ = self.xyfromp_f(p, ignorebounds=ignorebounds)
        return {self.tknx: x, self.tkny: y}
    
    def dxdyfromp_f(self, p=None, *, ignorebounds=False, withunits=False):
        """like xyfromp_f, but returns dx,dy,p instead of x,y,p"""
        x, y, p = self.xyfromp_f(p, ignorebounds=ignorebounds)
        dx = x - self.x
        dy = y - self.y
        if withunits:
            return dx, dy, p, self.tknxp, self.tknyp, self.pairp
        return dx, dy, p
    
    def dxvecfrompvec_f(self, pvec, *, ignorebounds=False):
        """
        alternative API to dxdyfromp_f
        
        :pvec:      a dict containing all prices; the dict must contain the keys
                    for tknx and for tkny and the associated value must be the respective
                    price in any numeraire (only the ratio is used)
        :returns:   token difference amounts as dict {tknx: dx, tkny: dy}
        """
        assert self.tknx in pvec, f"pvec must contain price for {self.tknx} [{pvec.keys()}]"
        assert self.tkny in pvec, f"pvec must contain price for {self.tkny} [{pvec.keys()}]"
        p = pvec[self.tknx] / pvec[self.tkny]
        dx, dy, _ = self.dxdyfromp_f(p, ignorebounds=ignorebounds)
        return {self.tknx: dx, self.tkny: dy}

    def yfromx_f(self, x, *, ignorebounds=False):
        "y value for given x value (if in range; None otherwise)"
        if self.is_constant_product():
            y = self.k / x
        else:
            y = (self.k / x) ** self.eta
        
        if ignorebounds:
            return y
        if not self.inrange(y, self.y_min, self.y_max):
            return None
        return y

    def xfromy_f(self, y, *, ignorebounds=False):
        "x value for given y value (if in range; None otherwise)"
        if self.is_constant_product():
            x = self.k / y
        else:
            x = self.k / (y ** (1/self.eta))
        if ignorebounds:
            return x
        if not self.inrange(x, self.x_min, self.x_max):
            return None
        return x

    def dyfromdx_f(self, dx, *, ignorebounds=False):
        "dy value for given dx value (if in range; None otherwise)"
        y = self.yfromx_f(self.x + dx, ignorebounds=ignorebounds)
        if y is None:
            return None
        return y - self.y

    def dxfromdy_f(self, dy, *, ignorebounds=False):
        "dx value for given dy value (if in range; None otherwise)"
        x = self.xfromy_f(self.y + dy, ignorebounds=ignorebounds)
        if x is None:
            return None
        return x - self.x

    @property
    def dy_min(self):
        """minimum (=max negative) possible dy value of this pool (=-y_act)"""
        return -self.y_act

    @property
    def dx_min(self):
        """minimum (=max negative) possible dx value of this pool (=-x_act)"""
        return -self.x_act

    @property
    def dy_max(self):
        """maximum dy value of this pool (=dy(dx_min))"""
        if self.x_act < self.x:
            return self.dyfromdx_f(self.dx_min)
        else:
            return None

    @property
    def dx_max(self):
        """maximum dx value of this pool (=dx(dy_min))"""
        if self.y_act < self.y:
            return self.dxfromdy_f(self.dy_min)
        else:
            return None

    @staticmethod
    def inrange(v, minv=None, maxv=None):
        "True if minv <= v <= maxv; None means no boundary"
        if not minv is None:
            if v < minv:
                return False
        if not maxv is None:
            if v > maxv:
                return False
        return True

    EPS = 1e-6

    def isequal(self, x, y):
        "returns True if x and y are equal within EPS"
        if x == 0:
            return abs(y) < self.EPS
        return abs(y / x - 1) < self.EPS

    def isbigger(self, small, big):
        "returns True if small is bigger than big within EPS (small, big > 0)"
        if small == 0:
            return big > self.EPS
        return big / small > 1 + self.EPS

    def plot(self, xmin=None, xmax=None, steps=None, *, xvals=None, func=None, show=False, title=None, xlabel=None, ylabel=None, grid=True, **params):
        """
        plots the curve associated with this pool
        
        :xmin, xmax, steps:    x range (args for np.linspace)
        :xvals:                x values (alternative to xmin, xmax, steps)
        :func:                 function to plot (default: dyfrpmdx_f)
        :show:                 if True, call plt.show()
        :title:                plot title
        :xlabel, ylabel:       axis labels
        :grid:                 if True [False], [do not] show grid; None: ignore
        :params:               additional kwargs passed to plt.plot
        """
        if xvals is None:
            assert not xmin is None, "xmin must not be None if xv is None"
            assert not xmax is None, "xmin must not be None if xv is None"
            x_v = np.linspace(xmin, xmax, steps) if steps else np.linspace(xmin, xmax)
        else:
            assert xmin is None, "xmin must be None if xv is not None"
            assert xmax is None, "xmax must be None if xv is not None"
            assert steps is None, "steps must be None if xv is not None"
            x_v = xvals
            
        xlabel = xlabel or (f"dx [{self.tknx}]" if not func else "x")
        ylabel = ylabel or (f"dy [{self.tkny}]" if not func else "y")
        func = func or self.dyfromdx_f
        #print("moo", self.cid, self.cid is None, 'self.cid' if self.cid else 'NO')
        title = title or f"Invariance curve {self.pairp} {self.cid if (self.cid and not self.cid=='None') else ''}"
        
        y_v = [func(xx) for xx in x_v]
        result = plt.plot(x_v, y_v, **params)
        plt.title(title)
        plt.xlabel(xlabel)
        plt.ylabel(ylabel)
        if not grid is None:
            plt.grid(grid)
        if show:
            plt.show()
        return result
            
    @staticmethod
    def digest(datastr, len=4):
        """returns a digest of a string of a certain length"""
        return digest(str(datastr).encode()).hexdigest()[:len]



class AF:
    """aggregator functions (for pivot tables)"""

    @staticmethod
    def range(x):
        return np.max(x) - np.min(x)

    @staticmethod
    def rangepc(x):
        mx = np.max(x)
        if mx == 0:
            return 0
        return (mx - np.min(x)) / mx

    @classmethod
    def rangepc100(cls, x):
        return cls.rangepc(x) * 100

    @staticmethod
    def sdpc(x):
        return np.std(x) / np.mean(x)

    @classmethod
    def sdpc100(cls, x):
        return cls.sdpc(x) * 100

    @staticmethod
    def first(x):
        return x.iloc[0]

    @staticmethod
    def herfindahl(x):
        return np.sum(x**2) / np.sum(x) ** 2

    @classmethod
    def herfindahlN(cls, x):
        return 1 / cls.herfindahl(x)


