"""
simple representation of a pair of tokens, used by cpc and arbgraph

(c) Copyright Bprotocol foundation 2023. 
Licensed under MIT
"""
__version__ = "1.1"
__date__ = "09/Apr/2022"

from dataclasses import dataclass, field, asdict, InitVar


@dataclass
class SimplePair:
    """
    a pair in notation TKNB/TKNQ; can also be provided as list (but NOT: tkn=, tknq=)
    """
    tknb: str=field(init=False)
    tknq: str=field(init=False)
    pair: InitVar[str]=None

    def __post_init__(self, pair):
        if isinstance(pair, self.__class__):
            self.tknb = pair.tknb
            self.tknq = pair.tknq
        elif isinstance(pair, str):
            self.tknb, self.tknq = pair.split("/")
        elif pair is False:
            # used in alternative constructors
            pass
        else:
            try:
                self.tknb, self.tknq = pair
            except:
                raise ValueError(f"pair must be a string or list of two strings {pair}")

    @classmethod
    def from_tokens(cls, tknb, tknq):
        pair = cls(False)
        pair.tknb = tknb
        pair.tknq = tknq
        return pair
    
    def __str__(self):
        return f"{self.tknb}/{self.tknq}"
    
    @property
    def pair(self):
        """string representation of the pair"""
        return str(self)
    
    @property
    def pairt(self):
        """tuple representation of the pair"""
        return (self.tknb, self.tknq)
    
    @property
    def pairr(self):
        """returns the reversed pair"""
        return f"{self.tknq}/{self.tknb}"
    
    @property
    def pairrt(self):
        """tuple representation of the reverse pair"""
        return (self.tknq, self.tknb)
    
    @property
    def tknx(self):
        return self.tknb
    
    @property
    def tkny(self):
        return self.tknq
    
    NUMERAIRE_TOKENS = {
        tkn:i for i, tkn in enumerate(["USDC", "USDT", "DAI", "TUSD", "BUSD", "PAX", "GUSD", 
            "USDS", "sUSD", "mUSD", "HUSD", "USDN", "USDP", "USDQ", "ETH", "WETH", "WBTC", "BTC"])}

    def n(self, tkn):
        """normalize the token name (remove the id, if any)"""
        return tkn.split("-")[0].split("(")[0]
    
    @property
    def tknb_n(self):
        return self.n(self.tknb)
    
    @property
    def tknq_n(self):
        return self.n(self.tknq)
    
    @property
    def tknx_n(self):
        return self.n(self.tknx)
    
    @property
    def tkny_n(self):
        return self.n(self.tkny)
    
    @property
    def isprimary(self):
        """whether the representation is primary or secondary"""
        tknqix = self.NUMERAIRE_TOKENS.get(self.tknq_n, 1e10)
        tknbix = self.NUMERAIRE_TOKENS.get(self.tknb_n, 1e10)
        if tknqix == tknbix:
            return self.tknb < self.tknq
        return tknqix < tknbix
    
    def primary_price(self, p):
        """returns the primary price (p if primary, 1/p if secondary)"""
        if p == 0: return float("nan")
        return p if self.isprimary else 1/p
    pp = primary_price
        
    @property
    def primary(self):
        """returns the primary pair"""
        return self.pair if self.isprimary else self.pairr
    
    @property
    def secondary(self):
        """returns the secondary pair"""
        return self.pairr if self.isprimary else self.pair
    
    @classmethod
    def wrap(cls, pairlist):
        """wraps a list of strings into Pairs"""
        return tuple(cls(p) for p in pairlist)
    
    @classmethod
    def unwrap(cls, pairlist):
        """unwraps a list of Pairs into strings"""
        return tuple(str(p) for p in pairlist)

