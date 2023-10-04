"""
simple representation of a pair of tokens, used by cpc and arbgraph

(c) Copyright Bprotocol foundation 2023. 
Licensed under MIT
"""
__VERSION__ = "2.1"
__DATE__ = "18/May/2023"

from dataclasses import dataclass, field, asdict, InitVar

from fastlane_bot.config.profiler import lp


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
    @lp
    def from_tokens(cls, tknb, tknq):
        pair = cls(False)
        pair.tknb = tknb
        pair.tknq = tknq
        return pair

    def __str__(self):
        return f"{self.tknb}/{self.tknq}"

    @property
    @lp
    def pair(self):
        """string representation of the pair"""
        return str(self)

    @property
    @lp
    def pairt(self):
        """tuple representation of the pair"""
        return (self.tknb, self.tknq)

    @property
    @lp
    def pairr(self):
        """returns the reversed pair"""
        return f"{self.tknq}/{self.tknb}"

    @property
    @lp
    def pairrt(self):
        """tuple representation of the reverse pair"""
        return (self.tknq, self.tknb)

    @property
    @lp
    def tknx(self):
        return self.tknb

    @property
    @lp
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
                "BNT",
                "ETH",
                "WETH",
                "WBTC",
                "BTC",
            ]
        )
    }

    @classmethod
    @lp
    def n(cls, tkn):
        """normalize the token name (remove the id, if any)"""
        if len(tkn.split("/")) > 1:
            return "/".join([cls.n(t) for t in tkn.split("/")])
        return tkn.split("-")[0].split("(")[0]

    @property
    @lp
    def tknb_n(self):
        return self.n(self.tknb)

    @property
    @lp
    def tknq_n(self):
        return self.n(self.tknq)
    
    @property
    @lp
    def pair_n(self):
        """normalized pair"""
        return f"{self.tknb_n}/{self.tknq_n}"

    @property
    @lp
    def tknx_n(self):
        return self.n(self.tknx)

    @property
    @lp
    def tkny_n(self):
        return self.n(self.tkny)

    @property
    @lp
    def isprimary(self):
        """whether the representation is primary or secondary"""
        tknqix = self.NUMERAIRE_TOKENS.get(self.tknq_n, 1e10)
        tknbix = self.NUMERAIRE_TOKENS.get(self.tknb_n, 1e10)
        if tknqix == tknbix:
            return self.tknb < self.tknq
        return tknqix < tknbix

    @lp
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
    @lp
    def pp_convention(self):
        """returns the primary price convention"""
        tknb, tknq = self.primary_n.split("/")
        return f"{tknq} per {tknb}"

    @property
    @lp
    def primary(self):
        """returns the primary pair"""
        return self.pair if self.isprimary else self.pairr
    
    @property
    @lp
    def primary_n(self):
        """the primary pair, normalized"""
        tokens = self.primary.split("/")
        tokens = [self.n(t) for t in tokens]
        return "/".join(tokens)
    
    @property
    @lp
    def primary_tknb(self):
        """returns the primary normailised tknb"""
        return self.tknb_n if self.isprimary else self.tknq_n

    @property
    @lp
    def primary_tknq(self):
        """returns the primary normailised tknq"""
        return self.tknq_n if self.isprimary else self.tknb_n
    
    @property
    @lp
    def secondary(self):
        """returns the secondary pair"""
        return self.pairr if self.isprimary else self.pair
    
    @property
    @lp
    def secondary_n(self):
        """the secondary pair, normalized"""
        tokens = self.secondary.split("/")
        tokens = [self.n(t) for t in tokens]
        return "/".join(tokens)

    @classmethod
    @lp
    def wrap(cls, pairlist):
        """wraps a list of strings into Pairs"""
        return tuple(cls(p) for p in pairlist)

    @classmethod
    @lp
    def unwrap(cls, pairlist):
        """unwraps a list of Pairs into strings"""
        return tuple(str(p) for p in pairlist)
