"""
optimization library -- CPCCarbOptimizer (intermediate optimizer class)

(c) Copyright Bprotocol foundation 2023. 
Licensed under MIT

This module is still subject to active research, and comments and suggestions are welcome. 
The corresponding author is Stefan Loesch <stefan@bancor.network>
"""
__VERSION__ = "5.1"
__DATE__ = "15/Sep/2023"

from dataclasses import dataclass, field, fields, asdict, astuple, InitVar
import pandas as pd
import numpy as np

try:
    import cvxpy as cp
except:
    # if cvxpy is not installed on the system then the convex optimization methods will not work
    # however, the (superior) marginal price based methods will still work and we do not want to
    # force installation of an otherwise unused package onto the user's system
    cp = None

import time
import math
import numbers
import pickle
from ..cpc import ConstantProductCurve as CPC, CPCInverter, CPCContainer, Pair
from sys import float_info

from .dcbase import DCBase
from .base import OptimizerBase



FORMATTER = lambda x: "" if ((abs(x) < 1e-10) or math.isnan(x)) else f"{x:,.2f}"

F = OptimizerBase.F

TIF_OBJECTS = "objects"
TIF_DICTS = "dicts"
TIF_DFRAW = "dfraw"
TIF_DF = TIF_DFRAW
TIFDF8 = "df8"
TIF_DFAGGR = "dfaggr"
TIF_DFAGGR8 = "dfaggr8"
TIF_DFPG = "dfgain"
TIF_DFPG8 = "dfgain8"

class CPCArbOptimizer(OptimizerBase):
    """
    intermediate class for CPC arbitrage optimization
    
    :curves:         the CPCContainer object (or the curves therein) the optimizer is using
    
    NOTE
    the old argument name `curve_container` is still supported but deprecated
    """
    __VERSION__ = __VERSION__
    __DATE__ = __DATE__

    def __init__(self, curves=None, *, curve_container=None):
        if not curve_container is None:
            if not curves is None:
                raise ValueError("must not uses curves and curve_container at the same time")
            curves = curve_container
        if curves is None:
            raise ValueError("must provide curves")
        if not isinstance(curves, CPCContainer):
            curve_container = CPCContainer(curves)
        self._curve_container = curves
        
    @property
    def curve_container(self):
        """the curve container (CPCContainer)"""
        return self._curve_container

    CC = curve_container
    curves = curve_container

    @property
    def tokens(self):
        return self.curve_container.tokens

    @dataclass
    class SelfFinancingConstraints(DCBase):
        """
        describes self financing constraints and determines optimization variable

        :data:      a dict TKN -> amount, or AMMPays, AMMReceives
                    :amount:            from the AMM perspective, total inflows (>0) or outflows (<0)
                                        for all items not present in data the value is assumed zero
                    :AMMPays:           the AMM payout should be maximized [from the trader (!) perspective]
                    :AMMReceives:       the money paid into the AMM should be minimized [ditto]
                    :OptimizationVar:   like AMMPays and AMMReceives, but if the direction of the payout is
                                        not known at the beginning [not all methods allow this]
                    :OV:                alias for OptimizationVar
        :tokens:    set of all tokens in the problem (if None, use data.keys())

        """

        AMMPays = "AMMPays"
        AMMReceives = "AMMReceives"
        OptimizationVar = "OptimizationVar"
        OV = OptimizationVar

        data: dict
        tokens: set = None

        def __post_init__(self):
            optimizationvars = tuple(
                k
                for k, v in self.data.items()
                if v in {self.AMMPays, self.AMMReceives, self.OptimizationVar}
            )
            assert (
                len(optimizationvars) == 1
            ), f"there must be EXACTLY one AMMPays, AMMReceives, OptimizationVar {self.data}"
            self._optimizationvar = optimizationvars[0]
            if self.tokens is None:
                self.tokens = set(self.data.keys())
            else:
                if isinstance(self.tokens, str):
                    self.tokens = set(t.strip() for t in self.tokens.split(","))
                else:
                    self.tokens = set(self.tokens)
                assert (
                    set(self.data.keys()) - self.tokens == set()
                ), f"constraint keys {set(self.data.keys())} > {self.tokens}"

        @property
        def optimizationvar(self):
            """optimization variable, ie the in that is set to AMMPays, AMMReceives or OptimizationVar"""
            return self._optimizationvar

        @property
        def tokens_s(self):
            """tokens as a comma-separated string"""
            return ", ".join(self.tokens_l)

        @property
        def tokens_l(self):
            """tokens as a list"""
            return sorted(list(self.tokens))

        def asdict(self, *, short=False):
            """dict representation including zero-valued tokens (unless short)"""
            if short:
                return {**self.data}
            return {k: self.get(k) for k in self.tokens}

        def items(self, *, short=False):
            return self.asdict(short=short).items()

        @classmethod
        def new(cls, tokens, **data):
            """alternative constructor: data as kwargs"""
            return cls(data=data, tokens=tokens)

        @classmethod
        def arb(cls, targettkn):
            """alternative constructor: arbitrage constraint, ie all other constraints are zero"""
            return cls(data={targettkn: cls.OptimizationVar})

        def get(self, item):
            """gets the constraint, or 0 if not present"""
            assert item in self.tokens, f"item {item} not in {self.tokens}"
            return self.data.get(item, 0)

        def is_constraint(self, item):
            """
            returns True iff item is a constraint (ie not an optimisation variable)
            """
            return not self.is_optimizationvar(item)

        def is_optimizationvar(self, item):
            """
            returns True iff item is the optimization variable
            """
            assert item in self.tokens, f"item {item} not in {self.tokens}"
            return item == self.optimizationvar

        def is_arbsfc(self):
            """
            returns True iff the constraint is an arbitrage constraint
            """
            if len(self.data) == 1:
                return True
            data1 = [v for v in self.data.values() if v != 0]
            return len(data1) == 1

        def __call__(self, item):
            """alias for get"""
            return self.get(item)

    def SFC(self, **data):
        """alias for SelfFinancingConstraints.new"""
        return self.SelfFinancingConstraints.new(self.curve_container.tokens(), **data)

    def SFCd(self, data_dct):
        """alias for SelfFinancingConstraints.new, with data as a dict"""
        return self.SelfFinancingConstraints.new(
            self.curve_container.tokens(), **data_dct
        )

    def SFCa(self, targettkn):
        """alias for SelfFinancingConstraints.arb"""
        return self.SelfFinancingConstraints.arb(targettkn)

    arb = SFCa

    AMMPays = SelfFinancingConstraints.AMMPays
    AMMReceives = SelfFinancingConstraints.AMMReceives
    OptimizationVar = SelfFinancingConstraints.OptimizationVar
    OV = SelfFinancingConstraints.OV

    
    def price_estimates(self, *, tknq, tknbs, **kwargs):
        """
        convenience function to access CPCContainer.price_estimates

        :tknq:      can only be a single token
        :tknbs:     list of tokens

        see help(CPCContainer.price_estimate) for details
        """
        return self.curve_container.price_estimates(tknqs=[tknq], tknbs=tknbs, **kwargs)

    
    @dataclass
    class TradeInstruction(DCBase):
        """
        encodes a specific trade one a specific curve

        seen from the AMM; in numbers must be positive, out numbers negative
        
        :cid:               the curve id
        :tknin:             token in
        :amtin:             amount in (>0)
        :tknout:            token out
        :amtout:            amount out (<0)
        :error:             error message (if any; None means no error)
        :curve:             the curve object (optional); note: users of this object need
                            to decide whether they trust the preparing code to set curve
                            or whether they fetch it via the cid themselves
        :raiseonerror:      if True, raise an error if the trade instruction is invalid
                            otherwise just set the error message
        """

        cid: any
        tknin: str
        amtin: float
        tknout: str
        amtout: float
        error: str = field(repr=True, default=None)
        curve: InitVar = None
        raiseonerror: InitVar = False

        POSNEGEPS = 1e-8

        def __post_init__(self, curve=None, raiseonerror=False):
            self.curve = curve
            if curve is not None:
                if self.cid != curve.cid:
                    err = f"curve/cid mismatch [{self.cid} vs {curve.cid}]"
                    self.error = err
                    if raiseonerror:
                        raise ValueError(err)
            if self.tknin == self.tknout:
                err = f"tknin and tknout must be different [{self.tknin} {self.tknout}]"
                self.error = err
                if raiseonerror:
                    raise ValueError(err)
            self.cid = str(self.cid)
            self.tknin = str(self.tknin)
            self.tknout = str(self.tknout)
            self.amtin = float(self.amtin)
            self.amtout = float(self.amtout)
            if not self.amtin * self.amtout < 0:
                if (
                    abs(self.amtin) < self.POSNEGEPS
                    and abs(self.amtout) < self.POSNEGEPS
                ):
                    self.amtin = 0
                    self.amtout = 0
                else:
                    err = f"amtin and amtout must be of different sign [{self.amtin} {self.tknin}, {self.amtout} {self.tknout}]"
                    self.error = err
                    if raiseonerror:
                        raise ValueError(err)

            if not self.amtin >= 0:
                err = f"amtin must be positive [{self.amtin}]"  # seen from AMM
                self.error = err
                if raiseonerror:
                    raise ValueError(err)
            
            if not self.amtout <= 0:
                err = f"amtout must be negative [{self.amtout}]"  # seen from AMM
                self.error = err
                if raiseonerror:
                    raise ValueError(err)

        TIEPS = 1e-10

        @classmethod
        def new(cls, curve_or_cid, tkn1, amt1, tkn2, amt2, *, eps=None, raiseonerror=False):
            """automatically determines which is in and which is out"""
            try:
                cid = curve_or_cid.cid
                curve = curve_or_cid
            except:
                cid = curve_or_cid
                curve = None
            if eps is None:
                eps = cls.TIEPS
            if amt1 > 0:
                newobj = cls(
                    cid=cid,
                    tknin=tkn1,
                    amtin=amt1,
                    tknout=tkn2,
                    amtout=amt2,
                    curve=curve,
                    raiseonerror=raiseonerror,
                )
            else:
                newobj = cls(
                    cid=cid,
                    tknin=tkn2,
                    amtin=amt2,
                    tknout=tkn1,
                    amtout=amt1,
                    curve=curve,
                    raiseonerror=raiseonerror,
                )

            return newobj

        @property
        def is_empty(self):
            """returns True if this is an empty trade instruction (too close to zero)"""
            return self.amtin == 0 or self.amtout == 0

        @classmethod
        def to_dicts(cls, trade_instructions):
            """converts iterable ot TradeInstruction objects to a tuple of dicts"""
            #print("[TradeInstruction.to_dicts]")
            return tuple(ti.asdict() for ti in trade_instructions)

        @classmethod
        def to_df(cls, trade_instructions, robj, ti_format=None):
            """
            converts iterable ot TradeInstruction objects to a pandas dataframe
            
            :trade_instructions:    iterable of TradeInstruction objects
            :robj:                  OptimizationResult object generating the trade instructions
            :ti_format:             format (TIF_DFP, TIF_DFRAW, TIF_DFAGGR, TIF_DF, TIF_DFPG)     
            """
            if ti_format is None:
                ti_format = cls.TIF_DF
            cid8 = ti_format in set([cls.TIF_DF8, cls.TIF_DFAGGR8, cls.TIF_DFPG8])
            dicts = (
                {
                    "cid": ti.cid if not cid8 else ti.cid[-10:],
                    "pair": ti.curve.pair if not ti.curve is None else "",
                    "pairp": ti.curve.pairp if not ti.curve is None else "",
                    "tknin": ti.tknin,
                    "tknout": ti.tknout,
                    ti.tknin: ti.amtin,
                    ti.tknout: ti.amtout,
                }
                for ti in trade_instructions
            )
            df = pd.DataFrame.from_dict(list(dicts)).set_index("cid")
            if ti_format in set([cls.TIF_DF, cls.TIF_DF8]):
                return df
            if ti_format in set([cls.TIF_DFAGGR, cls.TIF_DFAGGR8]):
                df1r = df[df.columns[4:]]
                df1  = df1r.fillna(0)
                dfa  = df1.sum().to_frame(name="TOTAL NET").T
                dfp  = df1[df1 > 0].sum().to_frame(name="AMMIn").T
                dfn  = df1[df1 < 0].sum().to_frame(name="AMMOut").T
                dfpr = pd.Series(robj.p_optimal).to_frame(name="PRICE").T
                #dfpr = pd.Series(r.p_optimal).to_frame(name="PRICES POST").T
                df = pd.concat([df1r, dfpr, dfp, dfn, dfa], axis=0)
                df.loc["PRICE"].fillna(1, inplace=True)
                return df
            if ti_format in set([cls.TIF_DFPG, cls.TIF_DFPG8]):
                ti = trade_instructions
                r = robj
                eff_p_out_per_in = [-ti_.amtout/ti_.amtin for ti_ in ti]
                data = dict(
                    exch = [ti_.curve.P("exchange") for ti_ in ti],
                    cid = [ti_.cid if ti_format == cls.TIF_DFPG else ti_.cid[-10:] for ti_ in ti],
                    fee = [ti_.curve.fee for ti_ in ti], # if split here must change conversion below
                    pair = [ti_.curve.pair if ti_format == cls.TIF_DFPG else Pair.n(ti_.curve.pair) for ti_ in ti],
                    amt_tknq = [ti_.amtin if ti_.tknin == ti_.curve.tknq else ti_.amtout for ti_ in ti],
                    tknq = [ti_.curve.tknq for ti_ in ti],
                    margp0 = [ti_.curve.p for ti_ in ti],
                    effp = [p if ti_.tknout==ti_.curve.tknq else 1/p for p,ti_ in zip(eff_p_out_per_in, ti)],
                    margp = [r.price(tknb=ti_.curve.tknb, tknq=ti_.curve.tknq) for ti_ in ti],
                )
                df = pd.DataFrame(data)
                df["gain_r"] = np.abs(df["effp"]/df["margp"] - 1)
                df["gain_tknq"] = -df["amt_tknq"] * (df["effp"]/df["margp"] - 1)
                
                cgt_l = ((cid, gain, tkn) for cid, gain, tkn in zip(df.index, df["gain_tknq"], df["tknq"]))
                cgtp_l = ((cid, gain, tkn, r.price(tknb=tkn, tknq=r.targettkn)) for cid, gain, tkn in cgt_l)
                cg_l = ((cid, gain*price) for cid, gain, tkn, price in cgtp_l)
                df["gain_ttkn"] = tuple(gain for cid, gain in cg_l)
                df = df.sort_values(["exch", "gain_ttkn"], ascending=False)
                df = df.set_index(["exch", "cid"])
                return df
            
            raise ValueError(f"unknown format {ti_format}")

        TIF_OBJECTS = TIF_OBJECTS
        TIF_DICTS = TIF_DICTS
        TIF_DFRAW = TIF_DFRAW
        TIF_DFAGGR = TIF_DFAGGR
        TIF_DFAGGR8 = TIF_DFAGGR8
        TIF_DF = TIF_DF
        TIF_DF8 = TIFDF8
        TIF_DFPG = TIF_DFPG
        TIF_DFPG8 = TIF_DFPG8
        
        @classmethod
        def to_format(cls, trade_instructions, robj=None, *, ti_format=None):
            """
            converts iterable ot TradeInstruction objects to the given format
            
            :trade_instructions:    iterable of TradeInstruction objects
            :robj:                  OptimizationResult object generating the trade instructions
            :ti_format:             format to convert to TIF_OBJECTS, TIF_DICTS, TIF_DFP, 
                                    TIF_DFRAW, TIF_DFAGGR, TIF_DF
            """
            #print("[TradeInstruction] to_format", ti_format)
            if ti_format is None:
                ti_format = cls.TIF_OBJECTS
            if ti_format == cls.TIF_OBJECTS:
                return tuple(trade_instructions)
            elif ti_format == cls.TIF_DICTS:
                return cls.to_dicts(trade_instructions)
            elif ti_format[:2] == "df":
                trade_instructions = tuple(trade_instructions)
                if len(trade_instructions) == 0:
                    return pd.DataFrame()
                return cls.to_df(trade_instructions, robj=robj, ti_format=ti_format)
            else:
                raise ValueError(f"unknown format {ti_format}")

        @property
        def price_outperin(self):
            return -self.amtout / self.amtin

        p = price_outperin

        @property
        def price_inperout(self):
            return -self.amtin / self.amtout

        pr = price_inperout

        @property
        def prices(self):
            return (self.price_outperin, self.price_inperout)

        pp = prices

    TIF_OBJECTS = TIF_OBJECTS
    TIF_DICTS = TIF_DICTS
    TIF_DFRAW = TIF_DFRAW
    TIF_DFAGGR = TIF_DFAGGR
    TIF_DFAGGR8 = TIF_DFAGGR8
    TIF_DF = TIF_DF
    TIF_DF8 = TIFDF8
    TIF_DFPG = TIF_DFPG
    TIF_DFPG8 = TIF_DFPG8
    
    METHOD_MARGP = "margp"
    @dataclass
    class MargpOptimizerResult(OptimizerBase.OptimizerResult):
        """
        results of the marginal price optimizer

        :curves:        curve objects underlying the optimization (as CPCContainer)
        :targetkn:      target token (=profit token) of the optimization
        :p_optimal_t:   optimal price vector (as tuple)
        :dtokens:       change in token amounts (as dict)
        :dtokens_t:     change in token amounts (as tuple)
        :tokens_t:      list of tokens
        :errormsg:      error message if an error occured (None=no error)
        
        PROPERTIES
        :p_optimal:     optimal price vector (as dict)
        
        """
        TIF_OBJECTS = TIF_OBJECTS
        TIF_DICTS = TIF_DICTS
        TIF_DFRAW = TIF_DFRAW
        TIF_DFAGGR = TIF_DFAGGR
        TIF_DFAGGR8 = TIF_DFAGGR8
        TIF_DF = TIF_DF
        TIF_DF8 = TIFDF8
        TIF_DFPG = TIF_DFPG
        TIF_DFPG8 = TIF_DFPG8
        
        curves: any = field(repr=False, default=None)
        targettkn: str = field(repr=True, default=None)
        #p_optimal: dict = field(repr=False, default=None)
        p_optimal_t: tuple = field(repr=True, default=None)
        n_iterations: int = field(repr=False, default=None)
        dtokens: dict = field(repr=False, default=None)
        dtokens_t: tuple = field(repr=True, default=None)
        tokens_t: tuple = field(repr=True, default=None)
        errormsg: str = field(repr=True, default=None)
        method: str = field(repr=True, default=None)

        def __post_init__(self, *args, **kwargs):
            #print(f"[MargpOptimizerResult] method = {self.method} [1]")
            super().__post_init__(*args, **kwargs)
            #print(f"[MargpOptimizerResult] method = {self.method} [2]")
            # #print("[MargpOptimizerResult] post_init")
            assert (
                self.p_optimal_t is not None or self.errormsg is not None
            ), "p_optimal_t must be set unless errormsg is set"
            if not self.p_optimal_t is None:
                self.p_optimal_t = tuple(self.p_optimal_t)
                self._p_optimal_d = {
                    **{tkn: p for tkn, p in zip(self.tokens_t, self.p_optimal_t)},
                    self.targettkn: 1.0,
                }
                    
            if self.method is None:
                self.method = CPCArbOptimizer.METHOD_MARGP
            #print(f"[MargpOptimizerResult] method = {self.method} [3]")
            self.raiseonerror = False

        @property
        def p_optimal(self):
            """the optimal price vector as dict (last entry is target token)"""
            return self._p_optimal_d
        
        @property
        def is_error(self):
            return self.errormsg is not None

        def detailed_error(self):
            return self.errormsg

        def status(self):
            return "error" if self.is_error else "converged"

        def price(self, tknb, tknq):
            """returns the optimal price of tknb/tknq based on p_optimal [in tknq per tknb]"""
            assert (
                self.p_optimal is not None
            ), "p_optimal must be set [do not use minimal results]"
            return self.p_optimal.get(tknb, 1) / self.p_optimal.get(tknq, 1)

        def dxdyvalues(self, asdict=False):
            """
            returns a vector of (dx, dy) values for each curve (see also dxvecvalues)
            """
            assert not self.curves is None, "curves must be set [do not use minimal results]"
            assert self.is_error is False, "cannot get this data from an error result"
            result = (
                (c.cid, c.dxdyfromp_f(self.price(c.tknb, c.tknq))[0:2])
                for c in self.curves
            )
            if asdict:
                return {cid: dxdy for cid, dxdy in result}
            return tuple(dxdy for cid, dxdy in result)

        def dxvecvalues(self, asdict=False):
            """
            returns a dict {tkn: dtknk} of changes for each curve (see also dxdyvalues)
            """
            assert not self.curves is None, "curves must be set [do not use minimal results]"
            assert self.is_error is False, "cannot get this data from an error result"
            result = (
                (c.cid, c.dxvecfrompvec_f(self.p_optimal))
                for c in self.curves
            )
            if asdict:
                return {cid: dxvec for cid, dxvec in result}
            return tuple(dxvec for cid, dxvec in result)

        @property
        def dxvalues(self):
            return tuple(dx for dx, dy in self.dxdyvalues())

        @property
        def dyvalues(self):
            return tuple(dy for dx, dy in self.dxdyvalues())

        @property
        def curves_new(self):
            """returns a list of Curve objects the trade instructions implemented"""
            assert (
                self.optimizer is not None
            ), "optimizer must be set [do not use minimal results]"
            assert self.is_error is False, "cannot get this data from an error result"
            return self.optimizer.adjust_curves(dxvals=self.dxvalues)

        def trade_instructions(self, ti_format=None):
            """
            returns list of TradeInstruction objects
            
            :ti_format:     TIF_OBJECTS, TIF_DICTS, TIF_DFP, TIF_DFRAW, TIF_DFAGGR, TIF_DF
            """
            try:
                assert self.curves is not None, "curves must be set [do not use minimal results]"
                assert self.is_error is False, "cannot get this data from an error result"
                result = (
                    CPCArbOptimizer.TradeInstruction.new(
                        curve_or_cid=c, tkn1=c.tknx, amt1=dx, tkn2=c.tkny, amt2=dy
                    )
                    for c, dx, dy in zip(self.curves, self.dxvalues, self.dyvalues)
                    if dx != 0 or dy != 0
                )
                return CPCArbOptimizer.TradeInstruction.to_format(result, robj=self, ti_format=ti_format)
            except AssertionError:
                if self.raiseonerror:
                    raise
                return None

    def adjust_curves(self, dxvals, *, verbose=False, raiseonerror=False):
        """
        returns a new curve container with the curves shifted by the given dx values
        """
        # print("[adjust_curves]", dxvals)
        if dxvals is None:
            if raiseonerror:
                raise ValueError("dxvals is None")
            else:
                print("[adjust_curves] dxvals is None")
                return None
        curves = self.curve_container
        try:
            newcurves = [
                c.execute(dx=dx, verbose=verbose, ignorebounds=True)
                for c, dx in zip(curves, dxvals)
            ]
            return CPCContainer(newcurves)
        except Exception as e:
            if raiseonerror:
                raise e
            else:
                print(f"Error in adjust_curves: {e}")
                # raise e
                return None

    def plot(self, *args, **kwargs):
        """
        convenience for self.curve_container.plot()

        see help(CPCContainer.plot) for details
        """
        return self.curve_container.plot(*args, **kwargs)

    def format(self, *args, **kwargs):
        """
        convenience for self.curve_container.format()

        see help(CPCContainer.format) for details
        """
        return self.curve_container.format(*args, **kwargs)
