"""
Testing utilities for the fastlane_bot package

USAGE

    from fastlane_bot.testing import *
"""
__VERSION__ = "1.2"
__DATE__ = "07/May/2023"

import math as m
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
import os
import sys
from decimal import Decimal
import time
from itertools import zip_longest


def iseq(arg0, *args, eps=1e-6):
    """checks whether all arguments are equal to arg0, within tolerance eps if numeric"""
    if not args:
        raise ValueError("Must provide at least one arg", args)
    try:
        arg0+1
        isnumeric = True
    except:
        isnumeric = False
    #if isinstance(arg0, int) or isinstance(arg0, float):
    if isnumeric:
        # numeric testing
        if arg0 == 0:
            for arg in args:
                if abs(arg) > eps: 
                    return False
                return True
        for arg in args:
            if abs(arg/arg0-1) > eps:
                return False
            return True
    else:
        for arg in args:
            if not arg == arg0:
                return False
        return True

def raises(func, *args, **kwargs):
    """
    returns exception message if func(*args, **kwargs) raises, else False

    USAGE

        assert raises(func, 1, 3, three=3), "func(1, 2, three=3) should raise"
    """
    try:
        func(*args, **kwargs)
        return False
    except Exception as e:
        return str(e)


import re as _re

class VersionRequirementNotMetError(RuntimeError): pass

def _split_version_str(vstr):
    """splits version mumber string into tuple (int, int, int, ...)"""
    m = _re.match("^([0-9\.]*)", vstr.strip())
    if m is None:
        raise ValueError("Invalid version number string", vstr)
    vlst = tuple(int(x) for x in m.group(0).split("."))
    return vlst

def require(required, actual, raiseonfail=True, printmsg=True):
    """
    checks whether required version is smaller or equal actual version
    
    :required:      the required version, eg "1.2.1"
    :actual:        the actual version, eg "1.3-beta2"
    :raiseonfail:   if True, raises VersionRequirementNotMetError if requirements are not met
    :printmsg:      if True, prints message
    :returns:       True if requirements are met, False else*
    
    *note: "1.3-beta1" MEETS the requirement "1.3"!
    """
    rl, al = _split_version_str(required), _split_version_str(actual)
    #print(f"required={rl}, actual={al}")

    result = _require_version(rl,al)
    if printmsg:
        m1 = "" if result else "NOT "
        print(f"Version = {actual} [requirements >= {required} is {m1}met]")
    if not raiseonfail:
        return result
    if not result:
        raise VersionRequirementNotMetError(f"Version requirements not met (required = {rl}, actual = {al})", required, actual)

def _require_version(rl, al):
    """
    checks whether required version is smaller or equal actual version
    
    :rl:        the required version eg (1,2,1)
    :al:        the actual version, eg (1,3)
    :returns:   True if requirements are met, False else*
    """
    for r,a in zip_longest(rl, al, fillvalue=0):
        #print(f"r={r}, a={a}")
        if r > a:
            return False
        elif r < a:
            return True
    return True
    
    
print("imported m, np, pd, plt, os, sys, decimal; defined iseq, raises, require")
