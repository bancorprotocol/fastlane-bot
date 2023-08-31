"""
base class for representing a generic curve in the context of the optimizer*

(c) Copyright Bprotocol foundation 2023. 
Licensed under MIT

*whilst the name of the file ("cpc") alludes to constant product curves, this is for 
historical reasons only; this class deal with generic curves

NOTE: this class is not part of the API of the Carbon protocol, and you must expect breaking
changes even in minor version updates. Use at your own risk.
"""
from abc import ABC, abstractmethod
class CurveBase(ABC):
    """
    base class for representing a generic curve in the context of the optimizer
    """
    
    @abstractmethod
    def dxvecfrompvec_f(self, pvec, *, ignorebounds=False):
        """
        get token holding vector xvec from price vector pvec
        
        :pvec:      a dict containing all prices; the dict must contain the keys
                    for tknx and for tkny and the associated value must be the respective
                    price in any numeraire (only the ratio is used)
        :returns:   token difference amounts as dict {tknx: dx, tkny: dy}
        """
        raise NotImplementedError("dxvecfrompvec_f must be implemented by subclass")
    
    @abstractmethod  
    def xvecfrompvec_f(self, pvec, *, ignorebounds=False):
        """
        get change in token holding vector xvec, dxvec, from price vector pvec
        
        :pvec:      a dict containing all prices; the dict must contain the keys
                    for tknx and for tkny and the associated value must be the respective
                    price in any numeraire (only the ratio is used)
        :returns:   token amounts as dict {tknx: x, tkny: y}
        """
        raise NotImplementedError("dxvecfrompvec_f must be implemented by subclass")
    
    @abstractmethod
    def invariant(self, include_target=False):
        """
        returns the actual invariant of the curve (eg x*y for constant product)
        
        :include_target:    if True, the target invariant returned in addition to the actual invariant
        :returns:           invariant, or (invariant, target)
        """
        raise NotImplementedError("invariant must be implemented by subclass")