"""
analyzing CPC / CPCContainer based collections

(c) Copyright Bprotocol foundation 2023. 
Licensed under MIT

NOTE: this class is not part of the API of the Carbon protocol, and you must expect breaking
changes even in minor version updates. Use at your own risk.
"""
__VERSION__ = "0.1"
__DATE__ = "06/May/2023"

from .cpc import ConstantProductCurve as CPC, CPCContainer, T, Pair

from dataclasses import dataclass, field, asdict, astuple, fields, InitVar
import math as m
import numpy as np
import pandas as pd
import itertools as it

class _DCBase:
    """base class for all data classes, adding some useful methods"""

    def asdict(self):
        return asdict(self)

    def astuple(self):
        return astuple(self)

    def fields(self):
        return fields(self)

@dataclass
class CPCAnalyzer(_DCBase):
    """
    various analytics functions around a CPCContainer object
    """
    __VERSION__ = __VERSION__
    __DATE__ = __DATE__
    
    CC: CPCContainer = field(default=None)
    
    def __post_init__(self):
        if self.CC is None:
            self.CC = CPCContainer()
        assert isinstance(self.CC, CPCContainer), "CC must be a CPCContainer object"
    
    def pairs(self):
        """alias for CC.pairs(standardize=True)"""
        return self.CC.pairs(standardize=True)
    
    def pairsc(self):
        """all pairs with carbon curves"""
        return {c.pairo.primary for c in self.CC if c.P("exchange")=="carbon_v1"}
    
    def tokens(self):
        """all tokens in the curves"""
        return self.CC.tokens()
    
    @dataclass
    class CurveData(_DCBase):
        curve: InitVar[CPC]
        analyzer: InitVar = None
        CC: InitVar = None
        
        primary: str = field(init=False, repr=True, default=None)
        cid0: str = field(init=False, repr=True, default=None)

        def __post_init__(self, curve, analyzer=None, CC=None):
            self.curve = curve
            self.analyzer = analyzer
            if CC is None:
                CC = self.analyzer.CC.bypairs(curve.pair)
            self.CC = CC
            self.primary = Pair.n(self.curve.pairo.primary)
            self.cid0 = self.curve.cid[-8:]
            
        def info(self):
            c = self.curve
            cc = self.CC
            dct = dict(
                pair = Pair.n(c.pair), 
                price = c.primaryp(), 
                cid = c.cid, 
                cid0 = c.cid[-8:],
                exchange = c.P("exchange"), 
                vl = c.tvl(tkn=c.pair.split("/")[0]),
                itm = "x" if c.itm(cc) else "", 
                bs = c.buysell(verbose=False), 
                bsv = c.buysell(verbose=True, withprice=True),
            )
            return dct
    
    def curve_data(self, curves=None):
        """return a CurveData object for the curve (or all curves of the pair if curve is None))"""
        if curves is None:
            curves = self.CC
        try:
            return tuple(self.curve_data(c) for c in curves)
        except TypeError:
            pass
        return self.CurveData(curves, self)
    
    @dataclass
    class PairData(_DCBase):
        pair: InitVar[str]
        analyzer: InitVar = None
        CC: InitVar = None
        primary: str = field(init=False, repr=True, default=None)
        ncurves: int = field(init=False, repr=False, default=None)
        ncurvesc: int = field(init=False, repr=False, default=None)
        
        def __post_init__(self, pair, analyzer=None, CC=None):
            self.pairo = Pair(pair)
            self.analyzer = analyzer
            self.analyzer = analyzer
            if CC is None:
                CC = self.analyzer.CC.bypairs(pair)
            self.CC = CC
            self.primary = Pair.n(self.pairo.primary)
            self.ncurves = len(self.CC)
            self.ncurvesc = len(self.curves_by_exchange("carbon_v1"))
            
        def curves_by_exchange(self, exchange=None):
            """dict exchange -> curves if exchange is None, otherwise just the curves for that exchange"""
            if exchange is None:
                return {c.P("exchange"): c for c in self.CC}
            else:
                return [c for c in self.CC if c.P("exchange")==exchange]
            
        def curve_data(self, curves=None):
            """return a CurveData object for the curves (or all curves of the pair if curve is None)"""
            if curves is None:
                curves = self.CC
            return self.analyzer.curve_data(curves)
    
    def pair_data(self, pair=None):
        """return a PairData object for the pair (dict for all pairs if pair is None)"""
        if not pair is None:
            return self.PairData(pair, self)
        return {pair: self.PairData(pair, self) for pair in self.pairs()}
    
        


        

        
        
        
