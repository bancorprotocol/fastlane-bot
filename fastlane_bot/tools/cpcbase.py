"""
Abstract base class providing the ``Optimizer`` interface for a generic AMM curve


---
(c) Copyright Bprotocol foundation 2023. 
Licensed under MIT
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass, field, asdict, InitVar

try:
    dataclass_ = dataclass(frozen=True, kw_only=True)
except:
    dataclass_ = dataclass(frozen=True)


class AttrDict(dict):
    """
    A dictionary that allows for attribute-style access

    see https://stackoverflow.com/questions/4984647/accessing-dict-keys-like-an-attribute
    """

    def __init__(self, *args, **kwargs):
        super(AttrDict, self).__init__(*args, **kwargs)
        self.__dict__ = self


@dataclass_
class DAttrDict:
    """
    attribute-style access to a dictionary with default values
    """

    dct: dict = field(default_factory=dict)
    default: any = None

    def __getattr__(self, name):
        return self.dct.get(name, self.default)

    
class CurveBase(ABC):
    """
    base class for representing a generic curve in the context of the optimizer
    """
    
    @abstractmethod
    def dxvecfrompvec_f(self, pvec, *, ignorebounds=False):
        """
        Returns token holding vector ``xvec`` at price vector ``pvec``
        
        :pvec:      a dict containing all prices; the dict must contain the keys
                    for ``tknx`` and for ``tkny`` and the associated value must be the respective
                    price in any numeraire (only the ratio is used)
        :returns:   token difference amounts as dict ``{tknx: dx, tkny: dy}``
        
        EXAMPLE
        
        .. code-block:: python
        
            pvec = {"USDC": 1, "ETH": 2000, "WBTC": 40000}
            dxvec = curve.dxvecfrompvec_f(pvec) 
                # --> {"ETH": -20, "WBTC": 1.01}
        """
        raise NotImplementedError("dxvecfrompvec_f must be implemented by subclass")
    
    @abstractmethod  
    def xvecfrompvec_f(self, pvec, *, ignorebounds=False):
        """
        Returns change in token holding vector ``xvec``, ``dxvec``, at price vector ``pvec``
        
        :pvec:      a dict containing all prices; the dict must contain the keys
                    for ``tknx`` and for ``tkny`` and the associated value must be the respective
                    price in any numeraire (only the ratio is used)
        :returns:   token amounts as dict ``{tknx: x, tkny: y}``
        
        EXAMPLE
        
        .. code-block:: python
        
            pvec = {"USDC": 1, "ETH": 2000, "WBTC": 40000}
            xvec = curve.xvecfrompvec_f(pvec) 
                # --> {"ETH": 200, "WBTC": 10}
        """
        raise NotImplementedError("dxvecfrompvec_f must be implemented by subclass")
    
    @abstractmethod
    def invariant(self, include_target=False):
        """
        Returns the current invariant of the curve (1)
        
        :include_target:    if True, the target invariant returned in addition to the actual invariant
        :returns:           invariant, or (invariant, target) (1)
        
        NOTE 1: eg for constant product the invariant is :math:`k(x,y)=xy`
        """
        raise NotImplementedError("invariant must be implemented by subclass")