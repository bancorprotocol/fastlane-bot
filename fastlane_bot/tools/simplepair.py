"""
simple representation of a pair of tokens, used by cpc and arbgraph

(c) Copyright Bprotocol foundation 2023. 
Licensed under MIT
"""
__VERSION__ = "2.0"
__DATE__ = "5/May/2023"

from dataclasses import dataclass, field, asdict, InitVar


@dataclass
class SimplePair:
    """
    a pair in notation TKNB/TKNQ; can also be provided as list (but NOT: tknb=, tknq=)
    """
    __VERSION__ = __VERSION__
    __DATE__ = __DATE__

    tknb: str = field(init=False)
    tknq: str = field(init=False)
    pair: InitVar[str] = None

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
        tkn: i
        for i, tkn in enumerate(
            [
                "USDC",
                "USDT",
                "DAI",
                "TUSD",
                "BUSD",
                "PAX",
                "GUSD",
                "USDS",
                "sUSD",
                "mUSD",
                "HUSD",
                "USDN",
                "USDP",
                "USDQ",
                "ETH",
                "WETH",
                "WBTC",
                "BTC",
            ]
        )
    }

    @classmethod
    def n(cls, tkn):
        """normalize the token name (remove the id, if any)"""
        if len(tkn.split("/")) > 1:
            return "/".join([cls.n(t) for t in tkn.split("/")])
        return tkn.split("-")[0].split("(")[0]

    @property
    def tknb_n(self):
        return self.n(self.tknb)

    @property
    def tknq_n(self):
        return self.n(self.tknq)
    
    @property
    def pair_n(self):
        """normalized pair"""
        return f"{self.tknb_n}/{self.tknq_n}"

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
        if self.isprimary:
            return p
        else:
            if p == 0:
                return float("nan")
        return 1 / p
    pp = primary_price
    
    @property
    def pp_convention(self):
        """returns the primary price convention"""
        tknb, tknq = self.primary_n.split("/")
        return f"{tknq} per {tknb}"

    @property
    def primary(self):
        """returns the primary pair"""
        return self.pair if self.isprimary else self.pairr
    
    @property
    def primary_n(self):
        """the primary pair, normalized"""
        tokens = self.primary.split("/")
        tokens = [self.n(t) for t in tokens]
        return "/".join(tokens)
    
    @property
    def primary_tknb(self):
        """returns the primary normailised tknb"""
        return self.tknb_n if self.isprimary else self.tknq_n

    @property
    def primary_tknq(self):
        """returns the primary normailised tknq"""
        return self.tknq_n if self.isprimary else self.tknb_n
    
    @property
    def secondary(self):
        """returns the secondary pair"""
        return self.pairr if self.isprimary else self.pair
    
    @property
    def secondary_n(self):
        """the secondary pair, normalized"""
        tokens = self.secondary.split("/")
        tokens = [self.n(t) for t in tokens]
        return "/".join(tokens)

    @classmethod
    def wrap(cls, pairlist):
        """wraps a list of strings into Pairs"""
        return tuple(cls(p) for p in pairlist)

    @classmethod
    def unwrap(cls, pairlist):
        """unwraps a list of Pairs into strings"""
        return tuple(str(p) for p in pairlist)
