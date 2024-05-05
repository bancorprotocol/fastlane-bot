"""
representing a collection of bonding curves

---
(c) Copyright Bprotocol foundation 2023. 
Licensed under MIT
"""
__VERSION__ = "4.0-beta1"
__DATE__ = "04/May/2024"

from .simplepair import SimplePair as Pair
from . import tokenscale as ts
from .params import Params
from .curvebase import DAttrDict
from .cpc import ConstantProductCurve, T
from .cpcinverter import CPCInverter

from dataclasses import dataclass, field
import random
from math import sqrt
import numpy as np
import pandas as pd
import json
from matplotlib import pyplot as plt
import itertools as it
import collections as cl
import time


AD = DAttrDict

@dataclass
class CurveContainer:
    """
    container for ConstantProductCurve objects (use += to add items)

    :curves:        an iterable of CPC curves, possibly wrapped in CPCInverter objects
                    CPCInverter objects are unwrapped automatically, the resulting
                    list will ALWAYS be curves, possibly with inverted=True
    :tokenscale:    a TokenScaleBase object (or None, in which case the default)
                    this object contains indicative prices for the tokens which are
                    sometimes useful for numerical stability reasons; the default token
                    scale is unity across all tokens
    """

    __VERSION__ = __VERSION__
    __DATE__ = __DATE__
    Pair = Pair

    curves: list = field(default_factory=list)
    tokenscale: ts.TokenScaleBase = field(default=None, repr=False)

    def __post_init__(self):

        if self.tokenscale is None:
            self.tokenscale = self.TOKENSCALE
        # print("[CurveContainer] tokenscale =", self.tokenscale)

        # ensure that the curves are in a list (they can be provided as any
        # iterable, e.g. a generator); also unwraps CPCInverter objects
        # if need be
        self.curves = [c for c in CPCInverter.unwrap(self.curves)]

        for i, c in enumerate(self.curves):
            if c.cid is None:
                # print("[__post_init__] setting cid", i)
                c.setcid(i)
            else:
                # print("[__post_init__] cid already set", c.cid)
                pass
            c.set_tokenscale(self.tokenscale)

        self.curves_by_cid = {c.cid: c for c in self.curves}
        self.curveix_by_curve = {c: i for i, c in enumerate(self.curves)}
        # self.curves_by_primary_pair = {c.pairo.primary: c for c in self.curves}
        self.curves_by_primary_pair = {}
        for c in self.curves:
            try:
                self.curves_by_primary_pair[c.pairo.primary].append(c)
            except KeyError:
                self.curves_by_primary_pair[c.pairo.primary] = [c]

    TOKENSCALE = ts.TokenScale1Data
    # default token scale object is the trivial scale (everything one)
    # change this to a different scale object be creating a derived class

    def scale(self, tkn):
        """returns the scale of tkn"""
        return self.tokenscale.scale(tkn)

    def as_dicts(self):
        """returns list of dictionaries representing the curves"""
        return [c.asdict() for c in self.curves]
    asdicts = as_dicts # legacy name
    
    def as_json(self):
        """as_dicts as JSON string"""
        return json.dumps(self.as_dicts())
    
    def as_repr(self):
        """returns a string representation of the container"""
        return ",\n".join([repr(c) for c in self.curves])+","
    
    def as_df(self):
        """returns pandas dataframe representing the curves"""
        return pd.DataFrame.from_dict(self.asdicts()).set_index("cid")
    asdf = as_df # legacy name

    @classmethod
    def from_dicts(cls, dicts, *, tokenscale=None):
        """alternative constructor: creates a container from a list of dictionaries"""
        return cls(
            [ConstantProductCurve.from_dict(d) for d in dicts], tokenscale=tokenscale
        )

    @classmethod
    def from_df(cls, df, *, tokenscale=None):
        "alternative constructor: creates a container from a dataframe representation"
        if "cid" in df.columns:
            df = df.set_index("cid")
        return cls.from_dicts(
            df.reset_index().to_dict("records"), tokenscale=tokenscale
        )

    def add(self, item):
        """
        adds one or multiple ConstantProductCurves (+= operator is also supported)

        :item:      item can be the following types:
                    :ConstantProductCurve:  a single curve is added
                    :CPCInverter:           the curve underlying the inverter is added
                    :Iterable:              all items in the iterable are added one by one
        """

        # unwrap iterables...
        try:
            for c in item:
                self.add(c)
            return self
        except TypeError:
            pass

        # ...and CPCInverter objects
        if isinstance(item, CPCInverter):
            item = item.curve

        # at this point, item must be a ConstantProductCurve object
        assert isinstance(
            item, ConstantProductCurve
        ), f"item must be a ConstantProductCurve object {item}"

        if item.cid is None:
            # print("[add] setting cid to", len(self))
            item.setcid(len(self))
        else:
            pass
            # print("[add] item.cid =", item.cid)
        self.curves_by_cid[item.cid] = item
        self.curveix_by_curve[item] = len(self)
        self.curves += [item]
        # print("[add] ", self.curves_by_primary_pair)
        try:
            self.curves_by_primary_pair[item.pairo.primary].append(item)
        except KeyError:
            self.curves_by_primary_pair[item.pairo.primary] = [item]
        return self

    def price(self, tknb, tknq):
        """returns price of tknb in tknq (tknb per tknq)"""
        pairo = Pair.from_tokens(tknb, tknq)
        curves = self.curves_by_primary_pair.get(pairo.primary, None)
        if curves is None:
            return None
        pp = sum(c.pp for c in curves) / len(curves)
        return pp if pairo.isprimary else 1 / pp
    
    PR_TUPLE = "tuple"
    PR_DICT = "dict"
    PR_DF = "df"
    def prices(self, result=None, *, inclpair=None, primary=None):
        """
        returns tuple or dictionary of the prices of all curves in the container

        :primary:       if True (default), returns the price quoted in the convention of the primary pair
        :inclpair:      if True, includes the pair in the dictionary
        :result:        what result to return (PR_TUPLE, PR_DICT, PR_DF)
        """
        if primary is None: primary = True
        if inclpair is None: inclpair = True
        if result is None: result = self.PR_DICT
        price_g = ((
                c.cid,
                c.primaryp() if primary else c.p, 
                c.pairo.primary if primary else c.pair
            ) for c in self.curves
        )
        
        if result == self.PR_TUPLE:
            if inclpair:
                return tuple(price_g)
            else:
                return tuple(r[1] for r in price_g)
        
        if result == self.PR_DICT:
            if inclpair:
                return {r[0]: (r[1], r[2]) for r in price_g}
            else:
                return {r[0]: r[1] for r in price_g}
        
        if result == self.PR_DF:
            df = pd.DataFrame.from_records(price_g, columns=["cid", "price", "pair"])
            df = df.set_index("cid")
            return df
        raise ValueError(f"unknown result type {result}")

    def __iadd__(self, other):
        """alias for  self.add"""
        return self.add(other)

    def __iter__(self):
        return iter(self.curves)

    def __len__(self):
        return len(self.curves)

    def __getitem__(self, key):
        return self.curves[key]

    def __contains__(self, curve):
        return curve in self.curveix_by_curve

    def tknys(self, curves=None):
        """returns set of all base tokens (tkny) used by the curves"""
        if curves is None:
            curves = self.curves
        return {c.tkny for c in curves}

    def tknyl(self, curves=None):
        """returns list of all base tokens (tkny) used by the curves"""
        if curves is None:
            curves = self.curves
        return [c.tkny for c in curves]

    def tknxs(self, curves=None):
        """returns set of all quote tokens (tknx) used by the curves"""
        if curves is None:
            curves = self.curves
        return {c.tknx for c in curves}

    def tknxl(self, curves=None):
        """returns set of all quote tokens (tknx) used by the curves"""
        if curves is None:
            curves = self.curves
        return [c.tknx for c in curves]

    def tkns(self, curves=None):
        """returns set of all tokens used by the curves"""
        return self.tknxs(curves).union(self.tknys(curves))

    tokens = tkns

    def tokens_s(self, curves=None):
        """returns set of all tokens used by the curves as a string"""
        return ",".join(sorted(self.tokens(curves)))

    def token_count(self, asdict=False):
        """
        counts the number of times each token appears in the curves
        """
        tokens_l = (c.pair for c in self)
        tokens_l = (t.split("/") for t in tokens_l)
        tokens_l = (t for t in it.chain.from_iterable(tokens_l))
        tokens_l = list(cl.Counter([t for t in tokens_l]).items())
        tokens_l = sorted(tokens_l, key=lambda x: x[1], reverse=True)
        if not asdict:
            return tokens_l
        return dict(tokens_l)
    
    def pairs(self, *, standardize=True):
        """
        returns set of all pairs used by the curves

        :standardize:   if False, the pairs are returned as they are in the curves; eg if we have curves
                        for both ETH/USDT and USDT/ETH, both pairs will be returned; if True, only the
                        canonical pair will be returned
        """
        if standardize:
            return {c.pairo.primary for c in self}
        else:
            return {c.pair for c in self}

    def cids(self, *, asset=False):
        """returns list of all curve ids (as tuple, or set if asset=True)"""
        if asset:
            return set(c.cid for c in self)
        return tuple(c.cid for c in self)

    @staticmethod
    def pairset(pairs):
        """converts string, list or set of pairs into a set of pairs"""
        if isinstance(pairs, str):
            pairs = (p.strip() for p in pairs.split(","))
        return set(pairs)

    def make_symmetric(self, df):
        """converts df into upper triangular matrix by adding the lower triangle"""
        df = df.copy()
        fields = df.index.union(df.columns)
        df = df.reindex(index=fields, columns=fields)
        df = df + df.T
        df = df.fillna(0).astype(int)
        return df

    FP_ANY = "any"
    FP_ALL = "all"

    def filter_pairs(self, pairs=None, *, anyall=FP_ALL, **conditions):
        """
        filters the pairs according to the target conditions(s)
        
        :pairs:         list of pairs to filter; if None, all pairs are used
        :anyall:        how conditions are combined (FP_ANY or FP_ALL)
        :conditions:    determines the filtering condition; all or any must be met (1, 2)


        NOTE1: an arbitrary differentiator can be appended to the condition using "_"
        (eg onein_1, onein_2, onein_3, ...) allowing to specify multiple conditions
        of the same type
        
        NOTE2: see table below for conditions
                        
        =========   ========================================
        Condition   Description                         
        =========   ========================================
        bothin      both tokens must be in the list     
        onein       at least one token must be in the list
        notin       none of the tokens must be in the list
        contains    alias for onein                   
        tknbin      tknb must be in the list            
        tknbnotin   tknb must not be in the list     
        tknqin      tknq must be in the list            
        tknqnotin   tknq must not be in the list     
        =========   ========================================
        
        """
        if pairs is None:
            pairs = self.pairs()
        if not conditions:
            return pairs
        pairs = self.Pair.wrap(pairs)
        results = []
        for condition in conditions:
            cpairs = self.pairset(conditions[condition])
            condition0 = condition.split("_")[0]
            # print(f"condition: {condition} | {condition0} [{conditions[condition]}]")
            if condition0 == "bothin":
                results += [
                    {str(p) for p in pairs if p.tknb in cpairs and p.tknq in cpairs}
                ]
            elif condition0 == "contains" or condition0 == "onein":
                results += [
                    {str(p) for p in pairs if p.tknb in cpairs or p.tknq in cpairs}
                ]
            elif condition0 == "notin":
                results += [
                    {
                        str(p)
                        for p in pairs
                        if p.tknb not in cpairs and p.tknq not in cpairs
                    }
                ]
            elif condition0 == "tknbin":
                results += [{str(p) for p in pairs if p.tknb in cpairs}]
            elif condition0 == "tknbnotin":
                results += [{str(p) for p in pairs if p.tknb not in cpairs}]
            elif condition0 == "tknqin":
                results += [{str(p) for p in pairs if p.tknq in cpairs}]
            elif condition0 == "tknqnotin":
                results += [{str(p) for p in pairs if p.tknq not in cpairs}]
            else:
                raise ValueError(f"unknown condition {condition}")

        # print(f"results: {results}")
        if anyall == self.FP_ANY:
            # print(f"anyall = {anyall}: union")
            return set.union(*results)
        elif anyall == self.FP_ALL:
            # print(f"anyall = {anyall}: intersection")
            return set.intersection(*results)
        else:
            raise ValueError(f"unknown anyall {anyall}")

    def fp(self, pairs=None, **conditions):
        """alias for filter_pairs (for interactive use)"""
        return self.filter_pairs(pairs, **conditions)

    def fpb(self, bothin, pairs=None, *, anyall=FP_ALL, **conditions):
        """alias for filter_pairs bothin (for interactive use)"""
        return self.filter_pairs(
            pairs=pairs, bothin=bothin, anyall=anyall, **conditions
        )

    def fpo(self, onein, pairs=None, *, anyall=FP_ALL, **conditions):
        """alias for filter_pairs onein (for interactive use)"""
        return self.filter_pairs(pairs=pairs, onein=onein, anyall=anyall, **conditions)

    @classmethod
    def _record(cls, c=None):
        """returns the record (or headings, if none) for the pair c"""
        if not c is None:
            p = cls.Pair(c.pair)
            return (
                c.tknx,
                c.tkny,
                c.tknb,
                c.tknq,
                p.pair,
                p.primary,
                p.isprimary,
                c.p,
                p.pp(c.p),
                c.x,
                c.x_act,
                c.y,
                c.y_act,
                c.cid,
            )
        else:
            return (
                "tknx",
                "tkny",
                "tknb",
                "tknq",
                "pair",
                "primary",
                "isprimary",
                "p",
                "pp",
                "x",
                "xa",
                "y",
                "ya",
                "cid",
            )

    AT_LIST = "list"
    AT_LISTDF = "listdf"
    AT_VOLUMES = "volumes"
    AT_VOLUMESAGG = "vaggr"
    AT_VOLSAGG = "vaggr"
    AT_PIVOTXY = "pivotxy"
    AT_PIVOTXYS = "pivotxys"
    AT_PIVOTBQ = "pivotbq"
    AT_PIVOTBQS = "pivotbqs"
    AT_PRICES = "prices"
    AT_MAX = "max"
    AT_MIN = "min"
    AT_SD = "std"
    AT_SDPC = "stdpc"
    AT_PRICELIST = "pricelist"
    AT_PRICELISTAGG = "plaggr"
    AT_PLAGG = "plaggr"

    def pairs_analysis(self, *, target=AT_PIVOTBQ, pretty=False, pairs=None, **params):
        """
        returns a dataframe with the analysis of the pairs according to the analysis target

        :target:    :AT_LIST:       list of pairs and associated data
                    :AT_LISTDF:     ditto but as a dataframe
                    :AT_VOLUMES:    list of volume per token and curve
                    :AT_VOLSAGG:    ditto but also aggregated by curve
                    :AT_PIVOTXY:    pivot table number of pairs tknx/tkny
                    :AT_PIVOTBQ:    ditto but with tknb/tknq
                    :AT_PIVOTXYS:   above anlysis but symmetric matrix (1)
                    :AT_PIVOTBQS:   ditto
                    :AT_PRICES:     average prices per (directed) pair
                    :AT_MAX:        ditto max
                    :AT_MIN:        ditto min
                    :AT_SD:         ditto price standard deviation
                    :AT_SDPC:       ditto percentage standard deviation
                    :AT_PRICELIST:  list of prices per curve
                    :AT_PLAGG:      list of prices aggregated by pair
        :pretty:    in some cases, returns a prettier but less useful result
        :pairs:     list of pairs to analyze; if None, all pairs
        :params:    kwargs that some of the analysis targets may use

        NOTE1: eg ETH/USDC would appear in ETH/USDC and in USDC/ETH
        """
        record = self._record
        cols = self._record()

        if pairs is None:
            pairs = self.pairs()
        curvedata = (record(c) for c in self.bypairs(pairs))
        if target == self.AT_LIST:
            return tuple(curvedata)
        df = pd.DataFrame(curvedata, columns=cols)
        if target == self.AT_LISTDF:
            return df

        if target == self.AT_VOLUMES or target == self.AT_VOLSAGG:
            dfb = (
                df[["tknb", "cid", "x", "xa"]]
                .copy()
                .rename(columns={"tknb": "tkn", "x": "amtv", "xa": "amt"})
            )
            dfq = (
                df[["tknq", "cid", "y", "ya"]]
                .copy()
                .rename(columns={"tknq": "tkn", "y": "amtv", "ya": "amt"})
            )
            df1 = pd.concat([dfb, dfq], axis=0)
            df1 = df1.sort_values(["tkn", "cid"])
            if target == self.AT_VOLUMES:
                df1 = df1.set_index(["tkn", "cid"])
                df1["lvg"] = df1["amtv"] / df1["amt"]
                return df1
            df1["n"] = (1,) * len(df1)
            # df1 = df1.groupby(["tkn"]).sum()
            df1 = df1.pivot_table(
                index="tkn",
                values=["amtv", "amt", "n"],
                aggfunc={
                    "amtv": ["sum", AF.herfindahl, AF.herfindahlN],
                    "amt": ["sum", AF.herfindahl, AF.herfindahlN],
                    "n": "count",
                },
            )
            price_eth = (
                self.price(tknb=t, tknq=T.ETH) if t != T.ETH else 1 for t in df1.index
            )
            df1["price_eth"] = tuple(price_eth)
            df1["amtv_eth"] = df1[("amtv", "sum")] * df1["price_eth"]
            df1["amt_eth"] = df1[("amt", "sum")] * df1["price_eth"]
            df1["lvg"] = df1["amtv_eth"] / df1["amt_eth"]
            return df1

        if target == self.AT_PIVOTXY or target == self.AT_PIVOTXYS:
            pivot = (
                df.pivot_table(
                    index="tknx", columns="tkny", values="tknb", aggfunc="count"
                )
                .fillna(0)
                .astype(int)
            )
            if target == self.AT_PIVOTXY:
                return pivot
            return self.make_symmetric(pivot)

        if target == self.AT_PIVOTBQ or target == self.AT_PIVOTBQS:
            pivot = (
                df.pivot_table(
                    index="tknb", columns="tknq", values="tknx", aggfunc="count"
                )
                .fillna(0)
                .astype(int)
            )
            if target == self.AT_PIVOTBQ:
                if pretty:
                    return pivot.replace(0, "")
                return pivot
            pivot = self.make_symmetric(pivot)
            if pretty:
                return pivot.replace(0, "")
            return pivot

        if target == self.AT_PRICES:
            pivot = df.pivot_table(
                index="tknb", columns="tknq", values="p", aggfunc="mean"
            )
            pivot = pivot.fillna(0).astype(float)
            if pretty:
                return pivot.replace(0, "")
            return pivot

        if target == self.AT_MAX:
            pivot = df.pivot_table(
                index="tknb", columns="tknq", values="p", aggfunc=np.max
            )
            pivot = pivot.fillna(0).astype(float)
            if pretty:
                return pivot.replace(0, "")
            return pivot

        if target == self.AT_MIN:
            pivot = df.pivot_table(
                index="tknb", columns="tknq", values="p", aggfunc=np.min
            )
            pivot = pivot.fillna(0).astype(float)
            if pretty:
                return pivot.replace(0, "")
            return pivot

        if target == self.AT_SD:
            pivot = df.pivot_table(
                index="tknb", columns="tknq", values="p", aggfunc=np.std
            )
            pivot = pivot.fillna(0).astype(float)
            if pretty:
                return pivot.replace(0, "")
            return pivot

        if target == self.AT_SDPC:
            pivot = df.pivot_table(
                index="tknb", columns="tknq", values="p", aggfunc=AF.sdpc
            )
            if pretty:
                return pivot.replace(0, "")
            return pivot

        if target == self.AT_PRICELIST:
            pivot = df.pivot_table(
                index=["tknb", "tknq", "cid"],
                values=["primary", "pair", "pp", "p"],
                aggfunc={
                    "primary": AF.first,
                    "pair": AF.first,
                    "pp": "mean",
                    "p": "mean",
                },
            )
            return pivot

        if target == self.AT_PRICELISTAGG:  # AT_PLAGG
            aggfs = [
                "mean",
                "count",
                AF.sdpc100,
                min,
                max,
                AF.rangepc100,
                AF.herfindahl,
            ]
            pivot = df.pivot_table(
                index=["tknb", "tknq"],
                values=["primary", "pair", "pp"],
                aggfunc={"primary": AF.first, "pp": aggfs},
            )
            return pivot

        raise ValueError(f"unknown target {target}")

    def _convert(self, generator, *, asgenerator=None, ascc=None):
        """takes a generator and returns a tuple, generator or CC object"""
        if asgenerator is None:
            asgenerator = False
        if ascc is None:
            ascc = True
        if asgenerator:
            return generator
        if ascc:
            return self.__class__(generator, tokenscale=self.tokenscale)
        return tuple(generator)

    def curveix(self, curve):
        """returns index of curve in container"""
        return self.curveix_by_curve.get(curve, None)

    def bycid(self, cid):
        """returns curve by cid"""
        return self.curves_by_cid.get(cid, None)
    
    def bycids(self, include=None, *, endswith=None, exclude=None, asgenerator=None, ascc=None):
        """
        returns curves by cids (as tuple, generator or CC object)

        :include:   list of cids to include, if None all cids are included
        :endswith:  alternative to include, include all cids that end with this string
        :exclude:   list of cids to exclude, if None no cids are excluded
                    exclude beats include
        :returns:   tuple, generator or container object (default)
        """
        if not include is None and not endswith is None:
            raise ValueError(f"include and endswith cannot be used together")
        if exclude is None:
            exclude = set()
        if include is None and endswith is None:
            result = (c for c in self if not c.cid in exclude)
        else:
            if not include is None:
                result = (self.curves_by_cid[cid] for cid in include if not cid in exclude)
            else:
                result = (c for c in self if c.cid.endswith(endswith) and not c.cid in exclude)
        return self._convert(result, asgenerator=asgenerator, ascc=ascc)

    def bycid0(self, cid0, **kwargs):
        """alias for bycids(endswith=cid0)"""
        return self.bycids(endswith=cid0, **kwargs)
    
    def bypair(self, pair, *, directed=False, asgenerator=None, ascc=None):
        """returns all curves by (possibly directed) pair (as tuple, genator or CC object)"""
        result = (c for c in self if c.pair == pair)
        if not directed:
            pairr = "/".join(pair.split("/")[::-1])
            result = it.chain(result, (c for c in self if c.pair == pairr))
        return self._convert(result, asgenerator=asgenerator, ascc=ascc)

    def bp(self, pair, *, directed=False, asgenerator=None, ascc=None):
        """alias for bypair by with directed=False for interactive use"""
        return self.bypair(pair, directed=directed, asgenerator=asgenerator, ascc=ascc)

    def bypairs(self, pairs=None, *, directed=False, asgenerator=None, ascc=None):
        """
        returns all curves by (possibly directed) pairs (as tuple, generator or CC object)

        :pairs:     set, list or comma-separated string of pairs; if None all pairs are included
        :directed:  if True, pair direction is important (eg ETH/USDC will not return USDC/ETH
                    pairs); if False, pair direction is ignored and both will be returned
        :returns:   tuple, generator or container object (default)
        """
        if isinstance(pairs, str):
            pairs = set(pairs.split(","))
        if pairs is None:
            result = (c for c in self)
        else:
            pairs = set(pairs)
            if not directed:
                rpairs = set(f"{q}/{b}" for b, q in (p.split("/") for p in pairs))
                # print("[CC] bypairs: adding reverse pairs", rpairs)
                pairs = pairs.union(rpairs)
            result = (c for c in self if c.pair in pairs)
        return self._convert(result, asgenerator=asgenerator, ascc=ascc)

    def byparams(self, *, _asgenerator=None, _ascc=None, _inv=False, **params):
        """
        returns all curves by params (as tuple, generator or CC object)

        :_inv:      if True, returns all curves that do NOT match the params
        :params:    keyword arguments in the form param=value
        :returns:   tuple, generator or container object (default)
        """
        if not params:
            raise ValueError(f"no params given {params}")
        
        params_t = tuple(params.items())
        if len(params_t) > 1:
            raise NotImplementedError(f"currently only one param allowed {params}")
        
        pname, pvalue = params_t[0]
        if _inv:
            result = (c for c in self if c.P(pname) != pvalue)
        else:
            result = (c for c in self if c.P(pname) == pvalue)
        return self._convert(result, asgenerator=_asgenerator, ascc=_ascc)

    def copy(self):
        """returns a copy of the container"""
        return self.bypairs(ascc=True)

    def bytknx(self, tknx, *, asgenerator=None, ascc=None):
        """returns all curves by quote token tknx (tknq) (as tuple, generator or CC object)"""
        result = (c for c in self if c.tknx == tknx)
        return self._convert(result, asgenerator=asgenerator, ascc=ascc)

    bytknq = bytknx

    def bytknxs(self, tknxs=None, *, asgenerator=None, ascc=None):
        """returns all curves by quote token tknx (tknq) (as tuple, generator or CC object)"""
        if tknxs is None:
            return self.curves
        if isinstance(tknxs, str):
            tknxs = set(t.strip() for t in tknxs.split(","))
        tknxs = set(tknxs)
        result = (c for c in self if c.tknx in tknxs)
        return self._convert(result, asgenerator=asgenerator, ascc=ascc)

    bytknxs = bytknxs

    def bytkny(self, tkny, *, asgenerator=None, ascc=None):
        """returns all curves by base token tkny (tknb) (as tuple, generator or CC object)"""
        result = (c for c in self if c.tkny == tkny)
        return self._convert(result, asgenerator=asgenerator, ascc=ascc)

    bytknb = bytkny

    def bytknys(self, tknys=None, *, asgenerator=None, ascc=None):
        """returns all curves by quote token tkny (tknb) (as tuple, generator or CC object)"""
        if tknys is None:
            return self.curves
        if isinstance(tknys, str):
            tknys = set(t.strip() for t in tknys.split(","))
        tknys = set(tknys)
        result = (c for c in self if c.tkny in tknys)
        return self._convert(result, asgenerator=asgenerator, ascc=ascc)

    bytknys = bytknys

    @staticmethod
    def u(minx, maxx):
        """helper: returns uniform random var"""
        return random.uniform(minx, maxx)

    @staticmethod
    def u1():
        """helper: returns uniform [0,1] random var"""
        return random.uniform(0, 1)

    @dataclass
    class xystatsd:
        mean: any
        minv: any
        maxv: any
        sdev: any

    def xystats(self, curves=None):
        """calculates mean, min, max, stdev of x and y"""
        if curves is None:
            curves = self.curves
        tknx = {c.tknq for c in curves}
        tkny = {c.tknb for c in curves}
        assert len(tknx) != 0 and len(tkny) != 0, f"no curves found {tknx} {tkny}"
        assert (
            len(tknx) == 1 and len(tkny) == 1
        ), f"all curves must have same tknq and tknb {tknx} {tkny}"
        x = [c.x for c in curves]
        y = [c.y for c in curves]
        return (
            self.xystatsd(np.mean(x), np.min(x), np.max(x), np.std(x)),
            self.xystatsd(np.mean(y), np.min(y), np.max(y), np.std(y)),
        )

    PE_PAIR = "pair"
    PE_CURVES = "curves"
    PE_DATA = "data"

    def price_estimate(
        self, *, tknq=None, tknb=None, pair=None, result=None, raiseonerror=True, verbose=False
    ):
        """
        calculates price estimate in the reference token as base token

        :tknq:          quote token to calculate price for
        :tknb:          base token to calculate price for
        :pair:          alternative to tknq, tknb: pair to calculate price for
        :raiseonerror:  if True, raise exception if no price can be calculated
        :result:        what to return
                        :PE_PAIR:      slashpair
                        :PE_CURVES:    curves
                        :PE_DATA:      prices, weights
        :verbose:       whether to print some progress
        :returns:       price (quote per base)
        """
        assert tknq is not None and tknb is not None or pair is not None, (
            f"must specify tknq, tknb or pair [{tknq}, {tknb}, {pair}]"
        )
        assert not (not tknb is None and not pair is None), f"must not specify both tknq, tknb and pair [{tknq}, {tknb}, {pair}]"
        
        if not pair is None:
            tknb, tknq = pair.split("/")
        if tknq == tknb:
            return 1
        if result == self.PE_PAIR:
            return f"{tknb}/{tknq}"
        crvs = (
            c for c in self if not c.at_boundary and c.tknq == tknq and c.tknb == tknb
        )
        rcrvs = (
            c for c in self if not c.at_boundary and c.tknb == tknq and c.tknq == tknb
        )
        crvs = ((c, c.p, c.k) for c in crvs)
        rcrvs = ((c, 1 / c.p, c.k) for c in rcrvs)
        acurves = it.chain(crvs, rcrvs)
        if result == self.PE_CURVES:
            # return dict(curves=tuple(crvs), rcurves=tuple(rcrvs))
            return tuple(acurves)
        data = tuple((r[1], sqrt(r[2])) for r in acurves)
        if verbose:
            print(f"[price_estimate] {tknq}/{tknb} {len(data)} curves")
        if not len(data) > 0:
            if raiseonerror:
                raise ValueError(f"no curves found for {tknq}/{tknb}")
            return None
        prices, weights = zip(*data)
        prices, weights = np.array(prices), np.array(weights)
        if result == self.PE_DATA:
            return prices, weights
        return float(np.average(prices, weights=weights))

    TRIANGTOKENS = f"{T.USDT}, {T.USDC}, {T.DAI}, {T.BNT}, {T.ETH}, {T.WBTC}"

    def price_estimates(
        self,
        *,
        tknqs=None,
        tknbs=None,
        triangulate=True,
        unwrapsingle=True,
        pairs=False,
        stopatfirst=True,
        raiseonerror=True,
        verbose=False,
    ):
        """
        calculates prices estimates in the reference token as base token

        :tknqs:         list of quote tokens to calculate prices for
        :tknbs:         list of base tokens to calculate prices for
        :triangulate:   tokens used as intermediate token for triangulation; if True, a standard 
                        token list is used; if None or False, no triangulation
        :unwrapsingle:  if there is only one quote token, a 1-d array is returned
        :pairs:         if True, returns the slashpairs instead of the prices
        :raiseonerror:  if True, raise exception if no price can be calculated
        :stopatfirst:   it True, stop at first triangulation match
        :verbose:       if True, print some progress
        :return:        np.array of prices (quote outer, base inner; quote per base)
        """
        # NOTE: this code is relatively slow to compute, on the order of a few seconds
        # for go through the entire token list; the likely reason is that it keeps reestablishing
        # the CurveContainer objects whenever price_estimate is called; there may be a way to
        # speed this up by smartly computing the container objects once and storing them 
        # in a dictionary the is then passed to price_estimate.
        start_time = time.time()
        assert not tknqs is None, "tknqs must be set"
        assert not tknbs is None, "tknbs must be set"
        if isinstance(tknqs, str):
            tknqs = [t.strip() for t in tknqs.split(",")]
        if isinstance(tknbs, str):
            tknbs = [t.strip() for t in tknbs.split(",")]
        if verbose:
            print(f"[price_estimates] tknqs [{len(tknqs)}] = {tknqs} , tknbs [{len(tknbs)}] = {tknbs} ")
        resulttp = self.PE_PAIR if pairs else None
        result = np.array(
            [
                [
                    self.price_estimate(tknb=b, tknq=q, raiseonerror=False, result=resulttp, verbose=verbose)
                    for b in tknbs
                ] 
                for q in tknqs
            ]
        )
        #print(f"[price_estimates] PAIRS [{time.time()-start_time:.2f}s]")
        flattened = result.flatten()
        nmissing = len([r for r in flattened if r is None])
        if verbose:
            print(f"[price_estimates] pair estimates: {len(flattened)-nmissing} found, {nmissing} missing")
            if nmissing > 0 and not triangulate:
                print(f"[price_estimates] {nmissing} missing pairs may be triangulated, but triangulation disabled [{triangulate}]")
            if nmissing == 0 and triangulate:
                print(f"[price_estimates] no missing pairs, triangulation not needed")
        
        if triangulate and nmissing > 0:
            if triangulate is True:
                triangulate = self.TRIANGTOKENS
            if isinstance(triangulate, str):
                triangulate = [t.strip() for t in triangulate.split(",")]
            if verbose:
                print("[price_estimates] triangulation tokens", triangulate)
            for ib, b in enumerate(tknbs):
                #print(f"TOKENB={b:22} [{time.time()-start_time:.4f}s]")
                for iq, q in enumerate(tknqs):
                    #print(f" TOKENQ={q:21} [{time.time()-start_time:.4f}s]")
                    if result[iq][ib] is None:
                        result1 = []
                        for tkn in triangulate:
                            #print(f"  TKN={tkn:23} [{time.time()-start_time:.4f}s]")
                            #print(f"[price_estimates] triangulating tknb={b} tknq={q} via {tkn}")
                            b_tkn = self.price_estimate(tknb=b, tknq=tkn, raiseonerror=False)
                            q_tkn = self.price_estimate(tknb=q, tknq=tkn, raiseonerror=False)
                            #print(f"[price_estimates] triangulating {b}/{tkn} = {b_tkn}, {q}/{tkn} = {q_tkn}")
                            if not b_tkn is None and not q_tkn is None:
                                if verbose:
                                    print(f"[price_estimates] triangulated {b}/{q} via {tkn} [={b_tkn/q_tkn}]")
                                result1 += [b_tkn / q_tkn]
                                if stopatfirst:
                                    #print(f"[price_estimates] stop at first")
                                    break
                                # else:
                                #     print(f"[price_estimates] continue {stopatfirst}")
                        result2 = np.mean(result1) if len(result1) > 0 else None
                        #print(f"[price_estimates] final result {b}/{q} = {result2} [{len(result1)}]")
                        result[iq][ib] = result2
        
        flattened = result.flatten()
        nmissing = len([r for r in flattened if r is None])
        if verbose:
            if nmissing > 0:
                missing = {
                    f"{b}/{q}"
                    for ib, b in enumerate(tknbs)
                    for iq, q in enumerate(tknqs)
                    if result[iq][ib] is None
                }
                print(f"[price_estimates] after triangulation {nmissing} missing", missing)
            else:
                print("[price_estimates] no missing pairs after triangulation")  
        if raiseonerror:
            missing = {
                f"{b}/{q}"
                for ib, b in enumerate(tknbs)
                for iq, q in enumerate(tknqs)
                if result[iq][ib] is None
            }
            # print("[price_estimates] result", result)
            if not len(missing) == 0:
                raise ValueError(f"no price found for {len(missing)} pairs", missing, result)

        #print(f"[price_estimates] DONE [{time.time()-start_time:.2f}s]")
        if unwrapsingle and len(tknqs) == 1:
            result = result[0]
        return result

    @dataclass
    class TokenTableEntry:
        """
        associates a single token with the curves on which they appear
        """

        x: list
        y: list

        def __repr__(self):
            return f"TTE(x={self.x}, y={self.y})"

        def __len__(self):
            return len(self.x) + len(self.y)

    def tokentable(self, curves=None):
        """returns dict associating tokens with the curves on which they appeay"""

        if curves is None:
            curves = self.curves

        r = (
            (
                tkn,
                self.TokenTableEntry(
                    x=[i for i, c in enumerate(curves) if c.tknb == tkn],
                    y=[i for i, c in enumerate(curves) if c.tknq == tkn],
                ),
            )
            for tkn in self.tkns()
        )
        r = {r[0]: r[1] for r in r if len(r[1]) > 0}
        return r

    Params = Params
    PLOTPARAMS = Params(
        printline="pair = {c.pairp}",  # print line before plotting; {pair} is replaced
        title="{c.pairp}",  # plot title; {pair} and {c} are replaced
        xlabel="{c.tknxp}",  # x axis label; ditto
        ylabel="{c.tknyp}",  # y axis label; ditto
        label="[{c.cid}-{p.exchange}]: p={c.p:.1f}, 1/p={pinv:.1f}, k={c.k:.1f}",  # label for legend; ditto
        marker="*",  # marker for plot
        plotf=dict(
            color="lightgrey", linestyle="dotted"
        ),  # additional kwargs for plot of the _f_ull curve
        plotr=dict(color="grey"),  # ditto for the _r_ange
        plotm=dict(),  # dittto for the _m_arker
        grid=True,  # plot grid if True
        legend=True,  # plot legend if True
        show=True,  # finish with plt.show() if True
        xlim=None,  # x axis limits (as tuple)
        ylim=None,  # y axis limits (as tuple)
        npoints=500,  # number of points to plot
    )

    def plot(self, *, pairs=None, directed=False, curves=None, params=None):
        """
        plots the curves in curvelist or all curves if None

        :pairs:     list of pairs to plot
        :curves:    list of curves to plot
        :directed:  if True, only plot pairs provided; otherwise plot reverse pairs as well
        :params:    plot parameters, as params struct (see PLOTPARAMS)
        """
        p = Params.construct(params, defaults=self.PLOTPARAMS.params)

        if pairs is None:
            pairs = self.pairs()

        if isinstance(pairs, str):
            pairs = [pairs]  # necessary, lest we get a set of chars

        pairs = set(pairs)

        if not directed:
            rpairs = set(f"{q}/{b}" for b, q in (p.split("/") for p in pairs))
            # print("[CC] plot: adding reverse pairs", rpairs)
            pairs = pairs.union(rpairs)

        assert curves is None, "restricting curves not implemented yet"

        for pair in pairs:
            # pairp = Pair.prettify_pair(pair)
            curves = self.bypair(pair, directed=True, ascc=False)
            # print("plot", pair, [c.pair for c in curves])
            if len(curves) == 0:
                continue
            if p.printline:
                print(p.printline.format(c=curves[0], p=curves[0].params))
            statx, staty = self.xystats(curves)
            #print(f"[CC::plot] stats x={statx}, y={staty}")
            xr = np.linspace(0.0000001, statx.maxv * 1.2, int(p.npoints))
            for i, c in enumerate(curves):
                # plotf is the full curve
                plt.plot(
                    xr, [c.yfromx_f(x_, ignorebounds=True) for x_ in xr], **p.plotf
                )
                # plotr is the curve with bounds
                plt.plot(xr, [c.yfromx_f(x_) for x_ in xr], **p.plotr)

            plt.gca().set_prop_cycle(None)
            for c in curves:
                # plotm are the markers
                label = (
                    None
                    if not p.label
                    else p.label.format(c=c, p=AD(dct=c.params), pinv=1 / c.p)
                )
                plt.plot(c.x, c.y, marker=p.marker, label=label, **p.plotm)

            plt.title(p.title.format(c=c, p=c.params))
            if p.xlim:
                plt.xlim(p.xlim)
            if p.ylim:
                plt.ylim(p.ylim)
            else:
                plt.ylim((0, staty.maxv * 2))
            plt.xlabel(p.xlabel.format(c=c, p=c.params))
            plt.ylabel(p.ylabel.format(c=c, p=c.params))

            if p.legend:
                if isinstance(p.legend, dict):
                    plt.legend(**p.legend)
                else:
                    plt.legend()

            if p.grid:
                if isinstance(p.grid, dict):
                    plt.grid(**p.grid)
                else:
                    plt.grid(True)

            if p.show:
                if isinstance(p.show, dict):
                    plt.show(**p.show)
                else:
                    plt.show()

    def format(self, *, heading=True, formatid=None):
        """
        returns the results in the given (printable) format

        see help(CurveContainer.print_formatted) for details
        """
        assert len(self.curves) > 0, "no curves to print"
        s = "\n".join(c.format(formatid=formatid) for c in self.curves)
        if heading:
            s = f"{self.curves[0].format(heading=True, formatid=formatid)}\n{s}"
        return s


