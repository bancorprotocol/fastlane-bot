# -*- coding: utf-8 -*-
# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:light
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.13.1
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from dataclasses import dataclass, field, InitVar
import os

# # Strategy Evaluation [A017]

# ## Data

FPATH = "."
FNAME = "Analysis_017.csv"
FFN = os.path.join(FPATH, FNAME)

# !ls {FPATH}/*.csv

datadf = pd.read_csv(FFN, index_col=0)
datadf

# ## Code

class AttrDict(dict):
    """
    A dictionary that allows for attribute-style access

    see https://stackoverflow.com/questions/4984647/accessing-dict-keys-like-an-attribute
    """

    def __init__(self, *args, **kwargs):
        super(AttrDict, self).__init__(*args, **kwargs)
        self.__dict__ = self


# +
class Prices():
    """
    simple class dealing with token prices
    
    :pricedata:   dict token -> price (in any common numeraire)
    :defaulttkn:  the default quote token for prices
    """
    def __init__(self, pricedata=None, defaulttkn=None, **kwargs):
        if pricedata is None:
            pricedata = dict()
        pricedata = {**pricedata, **kwargs}
        self._pricedata = {k.upper(): v for k,v in pricedata.items()}
        if defaulttkn is None:
            defaulttkn = list(pricedata.keys())[0]
        self.defaulttkn = defaulttkn.upper()
        assert defaulttkn in pricedata, f"defaulttkn [{defaulttkn}] must be in pricedata [{pricedata.keys()}]"
        if not isinstance(pricedata, dict):
            raise ValueError("pricedata must be a dictionary", pricedata)

    def tokens(self):
        """returns set of all tokens"""
        return set(self._pricedata.keys())
    
    def price(self, tknb, tknq=None):
        """
        returns the price of tknb in tknq
        """
        if tknq is None:
            tknq = self.defaulttkn
        return self._pricedata[tknb.upper()] / self._pricedata[tknq.upper()]
    
    def __call__(self, *args, **kwargs):
        """alias for price"""
        return self.price(*args, **kwargs)
    
    def __repr__(self):
        return f"{self.__class__.__name__}(pricedata={self._pricedata}, defaulttkn='{self.defaulttkn}')"
    
P = Prices(usd=1, dai=1, eth=2000)
P


# -

@dataclass
class CashFlow():
    """
    represents a single cashflow
    
    :blocknumber:   block number
    :tkn:           token
    :amt:           amount
    """
    blocknumber: int
    tkn: str
    amt: float

@dataclass
class StrategyAnalyzer():
    """
    Analyze performance of Carbon strategies (wrapper object for multiple strategies)
    """
    
    df: InitVar
    datadf: any = field(init=False, repr=False, default=None)
    prices: Prices = field(default=None)

    def __post_init__(self, df):
        df[self.CIDFIELD] = df[self.CIDFIELD].astype(str)
        self.datadf = df
    
    CIDFIELD = "cid0"
    REASONFIELD = "reason"
    RS_CREATE = "create"
    RS_TRADE = "trade"
    RS_CHANGE = "user_change"   
    def cids(self):
        """returns set of all cids"""
        return set(self.datadf[self.CIDFIELD])
    
    BYCID_RAW = "raw"
    BYCID_CHANGES = "changes"
    BYCID_FLOWS = "flows"
    
    def value(self, series, tknq=None):
        """returns the value of the series (in tknq, calculated using self.prices)"""
        val = [amt*self.prices(tkn, tknq) for tkn,amt in zip(series.index, series)]
        return sum(val)
    
    def bycid(self, cid, *, result=None):
        """
        returns dataframe for a given CID only
        
        :cid:      the cid in question
        :result:   BYCID_RAW or BYCID_FLOWS (default)
        :returns:  the requested result
        """
        if result is None:
            result = self.BYCID_FLOWS
            
        df = self.datadf.query(f"{self.CIDFIELD} == '{str(cid)}'").set_index("blockNumber")
        if result == self.BYCID_RAW:
            return df
        
        assert len(df["tkn0"].unique()) == 1, f"must have exactly one tkn0 [{df['tkn0'].unique()}]"
        assert len(df["tkn1"].unique()) == 1, f"must have exactly one tkn1 [{df['tkn1'].unique()}]"
        tkn0 = df["tkn0"].iloc[0]
        tkn1 = df["tkn1"].iloc[0]
        dfd0 = df[["y0_real", "y1_real"]].rename(columns={"y0_real": tkn0, "y1_real": tkn1})
        dfd = dfd0.diff()
        dfd.iloc[0] = dfd0.iloc[0]
        dfd["reason"] = df["reason"]
        assert dfd["reason"].iloc[0] == "create", f"first event must be create [{dfd['reason'].iloc[0]}]"
        events = set(dfd["reason"].iloc[1:])
        assert not "create" in events, f"must not have create event after first [{events}]"
        if result == self.BYCID_CHANGES:
            return dfd
        if result == self.BYCID_FLOWS:
            return dfd.query("reason != 'trade' and reason != 'delete'").drop("reason", axis=1)
        
        raise ValueError("Unknown result", result)


# ## Analysis

SA = StrategyAnalyzer(datadf, prices=P)

SA.prices

analysis_data = AttrDict()
ad = analysis_data

ad.flowdf = SA.bycid(11570)
ad.flowdf


ad.tknq = P.defaulttkn

ad.initial_amounts = ad.flowdf.iloc[0]
ad.initial_amounts_val = SA.value(ad.initial_amounts)
ad.initial_amounts_val

ad.final_amounts = -ad.flowdf.iloc[1:].sum()
ad.final_amounts_val = SA.value(ad.final_amounts)
ad.final_amounts_val

ad.change_amounts = ad.final_amounts - ad.initial_amounts
ad.change_amounts_val = SA.value(ad.change_amounts)
ad.change_amounts_val

ad




