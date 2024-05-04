"""
adaptor class inverting the pair of a ConstantProductCurve

---
(c) Copyright Bprotocol foundation 2023. 
Licensed under MIT
"""
from dataclasses import dataclass
#from dataclasses import field, asdict, InitVar
from .simplepair import SimplePair as Pair
#from . import tokenscale as ts
#import random
#from math import sqrt
#import numpy as np
#import pandas as pd
#import json
#from matplotlib import pyplot as plt
#from .params import Params
#import itertools as it
#import collections as cl
#from sys import float_info
##from hashlib import md5 as digest
import time
from .curvebase import DAttrDict
from .cpc import ConstantProductCurve

AD = DAttrDict


__VERSION__ = "1.0"
__DATE__ = "04/May/2024"

@dataclass
class CPCInverter:
    """
    adaptor class the allows for reverse-pair functions to be used as if they were of the same pair
    """

    curve: ConstantProductCurve

    @classmethod
    def wrap(cls, curves, *, asgenerator=False):
        """
        wraps an iterable of curves in CPCInverters if needed and returns a tuple (or generator)

        NOTE: only curves with ``c.pairo.isprimary == False`` are wrapped, the other ones are included
        as they are; this ensures that for all returned curves that correspond to the same actual
        pair, the primary pair is the same
        """
        result = (cls(c) if not c.pairo.isprimary else c for c in curves)
        if asgenerator:
            return result
        return tuple(result)

    @classmethod
    def unwrap(cls, wrapped_curves, *, asgenerator=False):
        """
        unwraps an iterable of curves from CPCInverters if needed and returns a tuple (or generator)
        """
        result = (c.curve if isinstance(c, cls) else c for c in wrapped_curves)
        if asgenerator:
            return result
        return tuple(result)

    @property
    def cid(self):
        return self.curve.cid

    @property
    def tknxp(self):
        return self.curve.tknyp

    @property
    def tknyp(self):
        return self.curve.tknxp

    @property
    def tknx(self):
        return self.curve.tkny

    @property
    def tkny(self):
        return self.curve.tknx

    @property
    def tknb(self):
        return self.curve.tknq

    @property
    def tknq(self):
        return self.curve.tknb

    @property
    def tknbp(self):
        return self.curve.tknqp

    @property
    def tknqp(self):
        return self.curve.tknbp

    @property
    def p(self):
        return 1 / self.curve.p
    
    def P(self, *args, **kwargs):
        return self.curve.P(*args, **kwargs)
    
    @property
    def fee(self):
        return self.curve.fee

    def p_convention(self):
        """price convention for p (dy/dx)"""
        return f"{self.tknyp} per {self.tknxp}"

    @property
    def x(self):
        return self.curve.y

    @property
    def y(self):
        return self.curve.x

    @property
    def k(self):
        return self.curve.k

    @property
    def pair(self):
        return f"{self.tknb}/{self.tknq}"
    
    @property
    def primary(self):
        "alias for self.pairo.primary [pair]"
        return self.pairo.primary
    
    @property
    def pairp(self):
        "prety pair (without the -xxx part)"
        return f"{self.tknbp}/{self.tknqp}"

    @property
    def primaryp(self):
        "pretty primary pair (without the -xxx part)"
        tokens = self.primary.split("/")
        tokens = [t.split("-")[0] for t in tokens]
        return "/".join(tokens)
    
    @property
    def x_min(self):
        return self.curve.y_min

    @property
    def x_max(self):
        return self.curve.y_max

    @property
    def y_min(self):
        return self.curve.x_min

    @property
    def y_max(self):
        return self.curve.x_max

    @property
    def x_act(self):
        return self.curve.y_act

    @property
    def p_min(self):
        return 1 / self.curve.p_max

    @property
    def p_max(self):
        return 1 / self.curve.p_min

    @property
    def y_act(self):
        return self.curve.x_act

    @property
    def pairo(self):
        return Pair.from_tokens(tknb=self.tknb, tknq=self.tknq)

    def yfromx_f(self, x, *, ignorebounds=False):
        return self.curve.xfromy_f(x, ignorebounds=ignorebounds)

    def xfromy_f(self, y, *, ignorebounds=False):
        return self.curve.yfromx_f(y, ignorebounds=ignorebounds)

    def dyfromdx_f(self, dx, *, ignorebounds=False):
        return self.curve.dxfromdy_f(dx, ignorebounds=ignorebounds)

    def dxfromdy_f(self, dy, *, ignorebounds=False):
        return self.curve.dyfromdx_f(dy, ignorebounds=ignorebounds)

    def xyfromp_f(self, p=None, *, ignorebounds=False, withunits=False):
        r = self.curve.xyfromp_f(
            1 / p if not p is None else None, ignorebounds=ignorebounds, withunits=False
        )
        if withunits:
            return (r[1], r[0], 1 / r[2], self.tknxp, self.tknyp, self.pairp)
        return (r[1], r[0], 1 / r[2])

    def dxdyfromp_f(self, p=None, *, ignorebounds=False, withunits=False):
        r = self.curve.dxdyfromp_f(
            1 / p if not p is None else None, ignorebounds=ignorebounds, withunits=False
        )
        if withunits:
            return (r[1], r[0], 1 / r[2], self.tknxp, self.tknyp, self.pairp)
        return (r[1], r[0], 1 / r[2])

    def execute(self, dx=None, dy=None, *, ignorebounds=False, verbose=False):
        """returns a new curve object that is then again wrapped in a CPCInverter"""
        curve = self.curve.execute(
            dx=dy, dy=dx, ignorebounds=ignorebounds, verbose=verbose
        )
        return CPCInverter(curve)



