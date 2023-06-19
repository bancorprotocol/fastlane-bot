"""
translating Uniswap v3 contract values

(c) Copyright Bprotocol foundation 2023. 
Licensed under MIT

NOTE: this class is not part of the API of the Carbon protocol, and you must expect breaking
changes even in minor version updates. Use at your own risk.
"""
__VERSION__ = "1.4" 
__DATE__ = "07/May/2023"

from math import sqrt
from dataclasses import dataclass, InitVar, asdict


@dataclass(frozen=True)
class Univ3Calculator():
    __VERSION__ = __VERSION__
    __DATE__ = __DATE__

    FEE100      = 100
    FEE500      = 500
    FEE3000     = 3000
    FEE10000    = 10000

    TICKSZ = {FEE100: 1, FEE500: 10, FEE3000: 60, FEE10000: 200}

    Q96 = 2**96
    Q192 = 2**192
    
    tkn0: str
    tkn1: str
    sp96: int # sqrt_price_q96
    tick: int
    liquidity: int
    fee_const: int 

    tkn0decv: InitVar[int] = None
    tkn1decv: InitVar[int] = None
    addrdec: InitVar[dict] = None
    ADDRDEC = dict(
        # only for testing
        USDC = ("0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48", 6),
        WETH = ("0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2", 18),
    )

    @classmethod
    def from_dict(cls, d, fee_const, *, addrdec=None, tkn0decv=None, tkn1decv=None):
        """
        alternative constructor from a dictionary
        
        :d:             dict with keys: token0 [address], token1 [address], sqrt_price_q96, tick, liquidity
        :fee_const:     fee constant (FEE100, ...)
        :tkn0decv:      optional token0 decimals value (eg 6, 18)
        :tkn1decv:      optional token1 decimals value (eg 6, 18)
        :addrdec:       optional dictionary of token address to decimals (eg {"0x123...": 18})
        """
        return cls(
            tkn0 = d["token0"],
            tkn1 = d["token1"],
            sp96 = d["sqrt_price_q96"],
            tick = d["tick"],
            liquidity = d["liquidity"],
            fee_const = fee_const,
            addrdec = addrdec,
            tkn0decv = tkn0decv,
            tkn1decv = tkn1decv,
        )


    ADDRR = {v[0]:k for k,v in ADDRDEC.items()}
    
    class DecimalsMissingError(Exception): pass
    
    def __post_init__(self, tkn0decv=None, tkn1decv=None, addrdec=None):
        
        #print("[Univ3Calculator] post_init", tkn0decv, tkn0decv)

        if addrdec is not None:
            self.ADDRDEC.update(addrdec)
            self.ADDRR.update({v[0]:k for k,v in addrdec.items()})

        try:
            super().__setattr__('tkn0', self.ADDRR[self.tkn0])
            super().__setattr__('tkn1', self.ADDRR[self.tkn1])
        except Exception as e:
            pass

        if tkn0decv is None:
            try:
                super().__setattr__('_tkn0dec', self.ADDRDEC[self.tkn0][1])
            except KeyError:
                raise self.DecimalsMissingError(f"must provide tkn0decv for {self.tkn0}")
        else:
            super().__setattr__('_tkn0dec', tkn0decv)
        
        if tkn1decv is None:
            try:
                super().__setattr__('_tkn1dec', self.ADDRDEC[self.tkn1][1])
            except KeyError:
                raise self.DecimalsMissingError(f"must provide tkn1decv for {self.tkn1}")
        else:
            super().__setattr__('_tkn1dec', tkn1decv)
        
        super().__setattr__('sp96', int(self.sp96)) 
        super().__setattr__('tick', int(self.tick)) 
        super().__setattr__('liquidity', int(self.liquidity)) 
        super().__setattr__('fee_const', int(self.fee_const)) 
        assert self.fee_const in {self.FEE100, self.FEE500, self.FEE3000, self.FEE10000}, "fee not one of the FEEXXX constants {self.fee_const}"
        assert not self.tkn0dec is None, "tkn0dec is None"
        assert not self.tkn1dec is None, "tkn1dec is None"

    @property
    def pair(self):
        """the directed pair tknb/tknq = tkn0/tkn1"""
        return f"{self.tkn0}/{self.tkn1}"
    
    @property
    def fee(self):
        """fee in basis points"""
        return self.fee_const/1000000
    
    @property
    def ticksize(self):
        """tick size"""
        return self.TICKSZ[self.fee_const]
    
    @property
    def tickab(self):
        """returns the tick values of Pa and Pb"""
        ticka = (self.tick // self.ticksize) * self.ticksize
        return ticka, ticka + self.ticksize
    
    @property
    def tkn0dec(self):
        """token 0 decimals"""
        return self._tkn0dec
    
    @property
    def tkn1dec(self):
        """token 1 decimals"""
        return self._tkn1dec
    
    @property
    def papb_raw(self):
        """raw Pa and Pb values (1.0001**tickab)"""
        ta, tb = self.tickab
        return (1.0001**ta, 1.0001**tb)
    
    @property
    def papb_tkn1_per_tkn0(self):
        """Pa and Pb values in units of token 1 per token 0"""
        par,pbr = self.papb_raw
        return (par*self.decf, pbr*self.decf) 
    papb = papb_tkn1_per_tkn0

    @property
    def papb_tkn0_per_tkn1(self):
        """Pa and Pb values in units of token 0 per token 1"""
        pa,pb = self.papb_tkn1_per_tkn0
        return (1/pa, 1/pb)
    
    @property
    def dec_factor_wei0_per_wei1(self):
        """token wei of token 0 per token wei of token 1 at price=1"""
        return 10**(self.tkn0dec-self.tkn1dec)
    decf = dec_factor_wei0_per_wei1

    @classmethod
    def _price_f(cls, sp96):
        """price tkn1 per tkn0 in wei units"""
        return sp96 ** 2 / cls.Q192
    
    @property
    def price_tkn1_per_tkn0(self):
        """price of token 1 per token 0 in token units"""
        return self._price_f(self.sp96) * self.decf
    p = price_tkn1_per_tkn0
    
    @property
    def price_tkn0_per_tkn1(self):
        """price of token 0 per token 1 in token units"""
        return 1/self.price_tkn1_per_tkn0

    @property
    def price_convention(self):
        return f"{self.tkn0}/{self.tkn1} [{self.tkn1} per {self.tkn0}]"
    
    @classmethod
    def sp96_from_price(cls, price):
        """calculate sp96 = sqrt(p) * Q96"""
        return sqrt(price) * cls.Q96
    
    @property
    def L(self):
        """the Uniswap L value, in token units; L**2=k, and k=xy where x,y are virtual token amounts"""
        return self.liquidity/10**(0.5*(self.tkn0dec+self.tkn1dec)) if self.liquidity!=0 else 0
    
    @property
    def Lsquared(self):
        """convenience methods for self.L**2 in token units"""
        return self.L**2
    L2 = Lsquared
    
    @property
    def k(self):
        """x*y=k, where x,y are virtual token amounts; k=L**2"""
        return self.L**2
    
    @property
    def kbar(self):
        """kbar = sqrt(k) = L; kbar = sqrt(xy)"""
        return self.L
    
    def tkn0reserve(self, *, incltoken=False):
        """returns the token 0 reserve in token units"""
        _, pb = self.papb
        sqrtPb = sqrt(pb)
        sqrtP = sqrt(self.p)
        tkn0reserve = self.liquidity * (sqrtPb - sqrtP) / (sqrtP * sqrtPb) if (sqrtP * sqrtPb)!=0 else 0
        tkn0reserve *= self.decf
        if not incltoken:
            return tkn0reserve
        return (tkn0reserve, self.tkn0)
    
    def tkn1reserve(self, *, incltoken=False):
        """returns the token 1 reserve in token units"""
        pa, _ = self.papb
        sqrtPa = sqrt(pa)
        sqrtP = sqrt(self.p)
        tkn1reserve = self.liquidity * (sqrtP - sqrtPa)
        tkn1reserve *= self.decf
        if not incltoken:
            return tkn1reserve
        return (tkn1reserve, self.tkn1)
    
    def tvl(self, *, astkn0=False, incltoken=False):
        """returns the total value locked in the pool"""
        tkn0reserve, tkn1reserve = self.tkn0reserve(), self.tkn1reserve()
        tvl_tkn0 = tkn0reserve + tkn1reserve*self.price_tkn0_per_tkn1
        tvl = tvl_tkn0 if astkn0 else tvl_tkn0*self.price_tkn1_per_tkn0
        if not incltoken:
            return tvl
        return (tvl, self.tkn0 if astkn0 else self.tkn1)
    
    def cpc_params(self, **kwargs):
        """
        returns a kwarg dict suitable for CPC.from_univ3
        
        :kwargs:        additional kwargs to return
        """
        pa,pb = self.papb
        pm = self.p
        pmar = pm/pa - 1
        pmbr = pm/pb - 1
        #print("[cpc_params]", pa, pm, pb, pmar, pmbr)
        if pmar < 0:
            #print("[cpc_params] pmar<0; asserting just rounding", pa, pm, pmar)
            assert pmar > -1e-10, f"pm below pa beyond rounding error [{pm}, {pa}, {pmar}]"
        if abs(pmar)<1e-10:
            #print("[cpc_params] setting pm to pa", pa, pm, pmar)
            pm = pa
        
        if pmbr < 0:
            #print("[cpc_params] pmbr>0; asserting just rounding", pm, pb, pmbr)
            assert pmbr < 1e-10, f"pm abve pb beyond rounding error [{pm}, {pb}, {pmbr}]"
        if abs(pmbr)<1e-10:
            #print("[cpc_params] setting pm to pb", pm, pb, pmbr)
            pm = pb
            
        result = dict(
            Pmarg = pm,
            uniL = self.L,
            uniPa = pa,
            uniPb = pb,
            pair = self.pair,
            fee = self.fee,
            **kwargs,
        )
        return result
    
    def info(self):
        pa, pb = self.papb
        p = self.p
        s  = f"Uniswap v3 Range {self.tkn0}/{self.tkn1} (fee={self.fee*100:.02f}%)\n"
        s += f"  Pa = {pa:12,.3f}   P={p:12,.3f}   Pb = {pb:12,.3f} {self.tkn1} per {self.tkn0}\n"
        s += f"1/Pa = {1/pa:12,.3f} 1/P={1/p:12,.3f} 1/Pb = {1/pb:12,.3f} {self.tkn0} per {self.tkn1}\n---\n"
    
        s += f" full P = {p}, full 1/P = {1/p}\n"
        return s

U3 = Univ3Calculator