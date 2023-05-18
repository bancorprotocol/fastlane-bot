"""
analyzing CPC / CPCContainer based collections

(c) Copyright Bprotocol foundation 2023. 
Licensed under MIT

NOTE: this class is not part of the API of the Carbon protocol, and you must expect breaking
changes even in minor version updates. Use at your own risk.
"""
__VERSION__ = "1.5"
__DATE__ = "18/May/2023"

from typing import Any
from .cpc import ConstantProductCurve as CPC, CPCContainer, T, Pair
from .optimizer import CPCArbOptimizer

from dataclasses import dataclass, field, asdict, astuple, fields, InitVar
import math as m
import numpy as np
import pandas as pd
import itertools as it
import collections as cl


class AttrDict(dict):
    """
    A dictionary that allows for attribute-style access
    
    see https://stackoverflow.com/questions/4984647/accessing-dict-keys-like-an-attribute
    """
    def __init__(self, *args, **kwargs):
        super(AttrDict, self).__init__(*args, **kwargs)
        self.__dict__ = self
    
    def __getattr__(self, __name: str) -> Any:
        return None
    
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
    
    def curves(self):
        """all curves"""
        return self.CC.curves
    
    def curvesc(self, *, ascc=False):
        """all carbon curves"""
        result = [c for c in self.CC if c.P("exchange")=="carbon_v1"]
        if not ascc:
            return result
        return CPCContainer(result)
    
    def tokens(self):
        """all tokens in the curves"""
        return self.CC.tokens()
    
    def count_by_tokens(self, *, byexchange=True, asdict=False):
        """
        counts the number of times each token appears in the curves
        
        :byexchange:    if False only provides the global number from the CC object
        :asdict:        if True returns dict, otherwise dataframe
        
        NOTE: the exchanges are current hardcoded, and should be made dynamic
        """
        if not byexchange:
            return self.CC.token_count(asdict=asdict)
        
        CCu3    = self.CC.byparams(exchange="uniswap_v3")
        CCu2    = self.CC.byparams(exchange="uniswap_v2")
        CCs2    = self.CC.byparams(exchange="sushiswap_v2")
        CCc1    = self.CC.byparams(exchange="carbon_v1")
        tc_u3 = CCu3.token_count(asdict=True)
        tc_u2 = CCu2.token_count(asdict=True)
        tc_s2 = CCs2.token_count(asdict=True)
        tc_c1 = CCc1.token_count(asdict=True)
        rows = [
            (tkn, cnt, tc_c1.get(tkn,0), tc_u3.get(tkn,0), tc_u2.get(tkn,0), tc_s2.get(tkn,0))
            for tkn, cnt in self.CC.token_count()
        ]
        df = pd.DataFrame(rows,columns="token,total,carb,uni3,uni2,sushi".split(","))
        df = df.set_index("token")
        return df
    
    def count_by_pairs(self, *, minn=None, asdf=True):
        """
        counts the number of times each pair appears in the curves
        
        :minn:    filter the dataset to a minimum number of curves per pair (only df)
        """
        curves_by_pair = list(cl.Counter([c.pairo.primary for c in self.CC]).items())
        curves_by_pair = sorted(curves_by_pair, key=lambda x: x[1], reverse=True)
        if not asdf:
            return curves_by_pair
        df = pd.DataFrame(curves_by_pair, columns=["pair", "count"]).set_index("pair")
        if minn is None:
            return df
        df = df[df["count"]>=minn]
        return df
    
    
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
                primary = Pair.n(self.primary),
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
    
    def curve_data(self, curves=None, *, asdf=False):
        """return a CurveData object for the curve (or all curves of the pair if curve is None))"""
        if curves is None:
            curves = self.CC
        try:
            result = tuple(self.curve_data(c) for c in curves)
            if asdf:
                df = pd.DataFrame([c.info() for c in result])
                return df
            return result
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
            
        def curve_data(self, curves=None, *, asdf=False):
            """return a CurveData object for the curves (or all curves of the pair if curve is None)"""
            if curves is None:
                curves = self.CC
            return self.analyzer.curve_data(curves, asdf=asdf)
    
    def pair_data(self, pair=None):
        """return a PairData object for the pair (dict for all pairs if pair is None)"""
        if not pair is None:
            return self.PairData(pair, self)
        return {pair: self.PairData(pair, self) for pair in self.pairs()}
    
    def pair_analysis(self, pair, **params):
        """
        :pair:              pair to be analyzed, eg "WETH-6Cc2/USDC-eB48"
        :params:            optional parameters [see code for details]
        
        :returns:           an attributed dictionary with the following fields:
            :pair:          the input pair, eg "WETH-6Cc2/USDC-eB48"
            :tknb, tknq:    base and quote token of the pair
            :analyzer:      the analyzer object
            :paird:         PairData object
            :curved:        tuple of CurveData objects, as returns by PairData.curve_data
            :curvedf:       curve data as dataframe, as returned by PairData.curve_data
            :price:         price estimate of that pair, in the native quotation of the pair
            :vlc:           value locked for Carbon (in quote token units)
            :vlnc:          ditto non-carbon
            :curvedfx:      like curvedf, but with some fields moved to the index
            :ccurvedf:      like curvedfx, but all non-carbon curves replaced with single aggregate line
            :tib, tiq:      trade instruction data frames (target = base / quote token respecitvely)
            :tibq:          concatenation of the TOTAL NET line of tib, tiq
            :arbvalb/q:     arb value in base token / quote token units
            :xpairs:        extended pairs (tokens of the pair plus triangulation tokens)
            :tib/q_xnoc:    trade instruction data frames for the extended pairs (non-carbon curves only)
            :tib/q_xf:      ditto (including carbon curves)
            :xarbvalp/q:    extended arb results (AttrDict with :nc: non-carbon, :full: plus Carbon, :net: difference)
        """
        P = lambda x: params.get(x, None)
        
        paird   = self.pair_data(pair)
        curvedf = paird.curve_data(asdf=True)
        tknb, tknq = pair.split("/")
        
        
        ## PART1: TRIVIAL ANALYSIS
        d = AttrDict(
            pair    = pair,
            analyzer= self,
            tknb    = tknb,
            tknq    = tknq,
            paird   = paird,
            curved  = paird.curve_data(),
            curvedf = curvedf,
            price   = self.CC.price_estimate(pair=pair),
            vlc     = sum(curvedf[curvedf["exchange"]=="carbon_v1"]["vl"]),
            vlnc    = sum(curvedf[curvedf["exchange"]!="carbon_v1"]["vl"]),
        )
        
        
        ## PART 2: SIMPLE DATAFRAMES
        
        # indexed df
        curvedf1 = d.curvedf
        curvedf1 = curvedf1.drop(['pair', 'primary', 'cid'], axis=1)
        curvedf1 = curvedf1.sort_values(by=["exchange", "cid0"])
        curvedf1 = curvedf1.set_index(["exchange", "cid0"])
        d["curvedfx"] = curvedf1
        
        # carbon curve df (aggregating the other curves)
        aggrdf = pd.DataFrame.from_dict([dict(
            exchange="aggr",
            cid0=Pair.n(pair),
            price=d.price,
            vl=d.vlnc,
            itm="",
            bs="",
            bsv="",
        )]).set_index(["exchange", "cid0"])
        d["ccurvedf"] = pd.concat([d.curvedfx.loc[["carbon_v1"]], aggrdf], axis=0)
        
        
        ## PART 3: USING THE OPTIMIZER ON THE PAIR ("SIMPLE ARB")
        # trade instructions
        O = CPCArbOptimizer(paird.CC)
        
        r = O.margp_optimizer(tknb, params=dict(verbose=False, debug=False))
        d["tib"] = r.trade_instructions(ti_format=O.TIF_DFAGGR)
        
        r = O.margp_optimizer(tknq)
        d["tiq"] = r.trade_instructions(ti_format=O.TIF_DFAGGR)
        
        d["tibq"]    = pd.concat([d.tib.loc[["TOTAL NET"]], d.tiq.loc[["TOTAL NET"]]])
        d["arbvalb"] = -d.tibq.iloc[0][d.tknb]
        d["arbvalq"] = -d.tibq.iloc[1][d.tknq]
        
        if P("nocav"):
            # nocav --> no complex arb value calculation
            d["nocav"] = True
            return d
            
        ## PART 4: USING THE OPTIMIZER ON TRIANGULAR TOKENS ("COMPLEX ARB")
        
        # the carbon curves associated with the pair
        CC_crb  = self.curvesc(ascc=True).bypairs(pair)
        
        # the extended list of pairs (universe: tokens of the pair + triangulation tokens)
        d["xpairs"] = self.CC.filter_pairs(bothin=f"{d.tknb}, {d.tknq}, {CPCContainer.TRIANGTOKENS}")
        
        # all non-Carbon curves associated with the extended list of pairs 
        CCx_noc = self.CC.bypairs(d.xpairs).byparams(exchange="carbon_v1", _inv=True)
        #print("exchanges", {c.P("exchange") for c in CCx_noc})
        
        # the optimizer based on the extended list of pairs (non-carbon curves only!)
        O = CPCArbOptimizer(CCx_noc)
        r = O.margp_optimizer(d.tknb, params=dict(verbose=False, debug=False))
        d["tib_xnoc"] = r.trade_instructions(ti_format=O.TIF_DFAGGR)
        r = O.margp_optimizer(d.tknq)
        d["tiq_xnoc"] = r.trade_instructions(ti_format=O.TIF_DFAGGR)
        
        # the full set of curves (non-carbon on extended pairs, carbon on the pair)
        CCx = CCx_noc.copy()
        CCx += CC_crb
        
        # the optimizer based on the full set of curves
        O = CPCArbOptimizer(CCx)
        r = O.margp_optimizer(d.tknb, params=dict(verbose=False, debug=False))
        d["tib_xf"] = r.trade_instructions(ti_format=O.TIF_DFAGGR)
        r = O.margp_optimizer(d.tknq)
        d["tiq_xf"] = r.trade_instructions(ti_format=O.TIF_DFAGGR)
        
        try:
            xarbval_ncq = -d.tiq_xnoc.loc["TOTAL NET"][d.tknq]
            xarbval_fq = -d.tiq_xf.loc["TOTAL NET"][d.tknq]
            xarbval_netq = xarbval_fq - xarbval_ncq
            d["xarbvalq"] = AttrDict(
                nc   = xarbval_ncq,
                full = xarbval_fq,
                net  = xarbval_netq,           
            )
        except Exception as e:
            d["xarbvalq"] = AttrDict(err=str(e))
            
        try:
            xarbval_ncb = -d.tip_xnoc.loc["TOTAL NET"][d.tknb]
            xarbval_fb = -d.tip_xf.loc["TOTAL NET"][d.tknb]
            xarbval_netb = xarbval_fb - xarbval_ncb
            d["xarbvalb"] = AttrDict(
                nc   = xarbval_ncb,
                full = xarbval_fb,
                net  = xarbval_netb,           
            )
        except Exception as e:
            d["xarbvalb"] = AttrDict(err=str(e))
            
        ## FINALLY: return the result
        return d
    

    def _fmt_xarbval(self, xarbval, tkn):
        """format the extended arb value"""
        if xarbval.err is None:
            result = f"no-carb={xarbval.nc:,.2f} full={xarbval.full:,.2f} net={xarbval.net:,.2f} [{Pair.n(tkn)}]"
        else:
            result = f"error [{Pair.n(tkn)}]"
        return result

    def pair_analysis_pp(self, data, **parameters):
        """
        pretty-print the output `d` of pair_analysis (returns string)
        """
        P,d,s = lambda x: parameters.get(x, None), data, ""
        
        if not P("nosep"):
            s += "-"*80+"\n"
        
        if not P("nopair"):
            s += f"Pair:               {d.pair}\n"
        
        if not P("nosep"):
            s += "-"*80+"\n"
        
        if not P("noprice"):
            s += f"Price:              {d.price:,.6f}\n"
        
        if not P("nocurves"):
            s += f"Number of curves:   {d.paird.ncurves} [carbon: {d.paird.ncurvesc}]\n"
        
        if not P("novl"):
            s += f"Value locked:       {d.vlc+d.vlnc:,.2f} {Pair.n(d.tknq)} [carbon: {d.vlc:,.2f}, other: {d.vlnc:,.2f}]\n"
        
        if not P("nosav"):
            s += f"Simple arb value:   {d.arbvalb:,.2f} {Pair.n(d.tknb)} / {d.arbvalq:,.2f} {Pair.n(d.tknq)}\n"
        
        if not P("nocav"):
            s += f"Complex arb value:  {self._fmt_xarbval(d.xarbvalq, d.tknq)}\n"
            s += f"                    {self._fmt_xarbval(d.xarbvalb, d.tknb)}\n"
        
        return s
        
    POS_DICT = "dict"
    POS_LIST = "list"
    POS_DF = "df"
    def pool_arbitrage_statistics(self, result = None, *, sort_price=True, only_pairs_with_carbon=True):
        """
        returns arbirage statistics on all Carbon pairs
        
        :result:                    POS_DICT, POS_LIST, POS_DF (default)
        :only_pairs_with_carbon:    ignore all curves that don't have a Carbon pair
        :sort_price:                sort by price
        :returns:                   the statistics data in the requested format
        """
        # select all curves that have at least one Carbon pair...
        if only_pairs_with_carbon:
            curves_by_carbon_pair = {pair: self.CC.bypairs([pair]) for pair in self.pairsc()}
        else:
            curves_by_carbon_pair = {pair: self.CC.bypairs([pair]) for pair in self.pairs()}

        # ...calculate some statistics...
        prices_d = {pair: 
                    [(
                        Pair.n(pair), pair, c.primaryp(), c.cid, c.cid[-8:], c.P("exchange"), c.tvl(tkn=pair.split("/")[0]),
                        "x" if c.itm(cc) else "", c.buy(), c.sell(), c.buysell(verbose=True, withprice=True)
                    ) for c in cc 
                    ] 
                    for pair, cc in curves_by_carbon_pair.items()
                    }

        # ...and return them in the desired format
        if result is None:
            result = self.POS_DF
            
        if result == self.POS_DICT:
            #print("returning dict")
            return prices_d
        
        prices_l = tuple(it.chain(*prices_d.values()))
        if result == self.POS_LIST:
            #print("returning list")
            return prices_l
        
        pricedf0 = pd.DataFrame(prices_l, columns="pair,pairf,price,cid,cid0,exchange,vl,itm,b,s,bsv".split(","))
        if sort_price:
            pricedf = pricedf0.drop(['cid', 'pairf'], axis=1).sort_values(by=["pair", "price", "exchange", "cid0"])
        else:
            pricedf = pricedf0.drop(['cid', 'pairf'], axis=1).sort_values(by=["pair", "exchange", "cid0"])
        pricedf = pricedf.set_index(["pair", "exchange", "cid0"])
        if result == self.POS_DF:
            return pricedf
        
        raise ValueError(f"invalid result type {result}")

    PR_TUPLE = "tuple"
    PR_DICT = "dict"
    PR_DF = "df"
    def price_ranges(self, result=None, *, short=True):
            """
            returns dataframe with price information of all curves
            
            :result:    PR_TUPLE, PR_DICT, PR_DF (default)
            :short:     shorten cid and pair
            """
            if result is None: result = self.PR_DF
            price_l = ((
                c.primary if not short else Pair.n(c.primary), 
                c.cid if not short else c.cid[-10:], 
                c.P("exchange"), 
                c.buy(),
                c.sell(), 
                c.p_min_primary(), 
                c.p_max_primary(),
                c.pp,
            ) for c in self.CC)
            if result == self.PR_TUPLE:
                return tuple(price_l)
            if result == self.PR_DICT:
                return {c.cid: r for c, r in zip(self.CC, price_l)}
            df = pd.DataFrame(price_l, columns="pair,cid,exch,b,s,p_min,p_max,p_marg".split(","))
            df = df.sort_values(["pair", "p_marg", "exch", "cid"])
            df = df.set_index(["pair", "exch", "cid"])
            if result == self.PR_DF:
                return df
            raise ValueError(f"unknown result type {result}")
        
