# ------------------------------------------------------------
# Auto generated test file `test_005_Uniswap.py`
# ------------------------------------------------------------
# source file   = NBTest_005_Uniswap.py
# test id       = 005
# test comment  = Uniswap
# ------------------------------------------------------------
from dataclasses import dataclass, asdict

from arb_optimizer import ConstantProductCurve as CPC

from fastlane_bot.helpers.univ3calc import Univ3Calculator as U3

print("{0.__name__} v{0.__VERSION__} ({0.__DATE__})".format(CPC))
print("{0.__name__} v{0.__VERSION__} ({0.__DATE__})".format(U3))

from fastlane_bot.testing import *
#plt.style.use('seaborn-dark')
plt.rcParams['figure.figsize'] = [12,6]
from fastlane_bot import __VERSION__
require("2.0", __VERSION__)




# ------------------------------------------------------------
# Test      005
# File      test_005_Uniswap.py
# Segment   u3 standalone
# ------------------------------------------------------------
def test_u3_standalone():
# ------------------------------------------------------------
    
    data = {
        "token0": "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48", # USDC
        "token1": "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2", # WETH 
        "sqrt_price_q96": "1725337071198080486317035748446190", 
        "tick": "199782", 
        "liquidity": "36361853546581410773"
    }
    
    help(U3.from_dict)
    
    u1 = U3(
        tkn0="0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48", 
        tkn0decv=6, 
        tkn1="0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2", 
        tkn1decv=18,
        sp96=data["sqrt_price_q96"],
        tick=data["tick"],
        liquidity=data["liquidity"],
        fee_const = U3.FEE500,
    )
    u2 = U3.from_dict(data, U3.FEE500)
    #assert u1 == u2
    u = u2
    assert asdict(u) == {
        'tkn0': '0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48',
        'tkn1': '0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2',
        'sp96': int(data["sqrt_price_q96"]),
        'tick': int(data["tick"]),
        'liquidity': int(data["liquidity"]),
        'fee_const': U3.FEE500
    }, f"{asdict(u)}"
    assert u.tkn0 == "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48"
    assert u.tkn1 == "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2"
    assert u.tkn0dec == 6
    assert u.tkn1dec == 18
    assert u.decf == 1e-12
    assert u.dec_factor_wei0_per_wei1 == u.decf
    assert iseq(u.p, 0.00047422968986928404)
    assert iseq(1/u.p, 2108.6828205033694)
    assert u.p == u.price_tkn1_per_tkn0
    assert 1/u.p == u.price_tkn0_per_tkn1
    assert u.price_convention == '0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48/0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2 [0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2 per 0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48]'
    assert iseq(u._price_f(1725337071198080486317035748446190), 474229689.86928403)
    assert iseq(u._price_f(u.sp96), 474229689.86928403)
    assert u.ticksize == 10
    ta, tb =  u.tickab
    par, pbr = u.papb_raw
    pa, pb = u.papb_tkn1_per_tkn0
    pai, pbi = u.papb_tkn0_per_tkn1
    assert ta <= u.tick
    assert tb >= u.tick
    assert ta % u.ticksize == 0
    assert tb % u.ticksize == 0
    assert tb-ta == u.ticksize
    assert iseq(par, 474134297.0246954)
    assert iseq(pbr, 474608644.73905975)
    assert iseq(pbr/par, 1.0001**u.ticksize)
    assert iseq(pa, 0.0004741342970246954)
    assert iseq(pb, 0.00047460864473905973)
    assert iseq(pbr/par, pb/pa)
    assert iseq(pbr/par, pai/pbi)
    assert pa<pb
    assert pai>pbi
    assert pa == par * u.decf
    assert pb == pbr * u.decf
    assert iseq(pai, 2109.1070742514007)
    assert iseq(pbi, 2106.999126722188)
    assert pai == 1/pa
    assert pbi == 1/pb
    assert u.p >= pa
    assert u.p <= pb
    assert u.fee_const == 500
    assert u.fee == 0.0005
    assert u.info()
    print(u.info())
    
    assert u.liquidity == int(data["liquidity"])
    assert u.L == 36361853.54658141
    assert u.liquidity/u.L == 1e18/1e6
    assert u.L2 == u.L**2
    assert u.Lsquared == u.L**2
    assert u.k == u.L2
    assert u.kbar == u.L
    u.tkn0reserve(incltoken=True), u.tkn1reserve(incltoken=True), u.tvl(incltoken=True)
    
    data1 = {**data}
    data1["token0"] = data["token0"]+"_"
    data1["token1"] = data["token1"]+"_"
    data1
    
    assert raises (U3.from_dict, data1, U3.FEE500).startswith("must provide tkn0decv")
    u3 = U3.from_dict(data1, U3.FEE500, tkn0decv=6, tkn1decv=18)
    assert u3.liquidity == u2.liquidity
    assert u3.tick == u2.tick
    assert u3.sp96 == u2.sp96
    assert u3.sp96 == u2.sp96
    

# ------------------------------------------------------------
# Test      005
# File      test_005_Uniswap.py
# Segment   Univ3 Issue
# ------------------------------------------------------------
def test_univ3_issue():
# ------------------------------------------------------------
    
    u3data = dict(
        sqrt_price_q96=Decimal('79204503519896773685362'), 
        tick=-276330, 
        tick_spacing=10, 
        liquidity=Decimal('420303555647537236581'), 
        address='0x5720EB958685dEEEB5AA0b34F677861cE3a8c7F5', 
        anchor='NaN', tkn0='0x8E870D67F660D95d5be530380D0eC0bd388289E1', 
        tkn1='0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48', 
        tkn0_address='0x8E870D67F660D95d5be530380D0eC0bd388289E1', 
        tkn0_decimals=18, 
        tkn1_address='0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48', 
        tkn1_decimals=6, 
        tkn0_key='0x8E870D67F660D95d5be530380D0eC0bd388289E1',
        tkn1_key='0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48'
    )
    u3data["token0"] = u3data["tkn0_address"]
    u3data["token1"] = u3data["tkn1_address"]
    
    u3 = U3.from_dict(u3data, tkn0decv=u3data["tkn0_decimals"], 
                      tkn1decv=u3data["tkn1_decimals"], fee_const=U3.FEE100)
    
    u3d = u3.cpc_params()
    u3d
    
    pa,pb = u3.papb
    pm = u3.p
    r = u3.cpc_params()
    assert r["uniPa"] == pa
    assert r["uniPb"] == pb
    assert r["uniPa"] <= r["Pmarg"]
    assert r["uniPb"] >= r["Pmarg"]
    print(r["Pmarg"]/pm-1)
    assert abs(r["Pmarg"]/pm-1)<1e-10
    

# ------------------------------------------------------------
# Test      005
# File      test_005_Uniswap.py
# Segment   with cpc
# ------------------------------------------------------------
def test_with_cpc():
# ------------------------------------------------------------
    
    data = {
        "token0": "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48", 
        "token1": "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2", 
        "sqrt_price_q96": "1727031172247131125466697684053376", 
        "tick": "199801", 
        "liquidity": "37398889145617323159"
    }
    u = U3.from_dict(data, U3.FEE500)
    
    pa, pb = u.papb_tkn1_per_tkn0
    curve = CPC.from_univ3(
        Pmarg = u.p,
        uniL = u.L,
        uniPa = pa,
        uniPb = pb,
        pair = u.pair,
        fee = u.fee,
        descr = "",
        params = dict(uv3raw=asdict(u)),
        cid = "0",
    )
    curve
    
    c = curve
    print(f"Reserve: {c.x_act:,.3f} {c.tknx}, {c.y_act:,.3f} {c.tkny}")
    print(f"TVL = {c.tvl(tkn=c.tknx):,.3f} {c.tknx} = {c.tvl(tkn=c.tkny):,.3f} {c.tkny}")
    assert iseq(c.x_act, 716877.5715601444)
    assert iseq(c.y_act, 66.88731140131131)
    assert iseq(c.tvl(tkn=c.tknx), 857645.1222000704)
    assert iseq(c.tvl(tkn=c.tkny), 407.51988721569177)
    
    print(f"Reserve: {u.tkn0reserve():,.3f} {c.tknx}, {u.tkn1reserve():,.3f} {c.tkny}")
    print(f"TVL = {u.tvl(astkn0=True):,.3f} {c.tknx} = {u.tvl(astkn0=False):,.3f} {c.tkny}")
    assert iseq(u.tkn0reserve(), c.x_act)
    assert iseq(u.tkn1reserve(), c.y_act)
    assert iseq(u.tvl(astkn0=False), c.tvl(tkn=c.tkny))
    assert iseq(u.tvl(astkn0=True), c.tvl(tkn=c.tknx))
    assert u.tkn0reserve(incltoken=True)[1] == u.tkn0
    assert u.tkn1reserve(incltoken=True)[1] == u.tkn1
    assert u.tvl(astkn0=True, incltoken=True)[1] == u.tkn0
    assert u.tvl(astkn0=False, incltoken=True)[1] == u.tkn1
    u.tkn0reserve(incltoken=True), u.tkn1reserve(incltoken=True), u.tvl(incltoken=True)
    
    curve = CPC.from_univ3(
        **u.cpc_params(),
        descr = "",
        params = dict(uv3raw=asdict(u)),
        cid = "0",
    )
    curve
    
    c = curve
    print(f"Reserve: {c.x_act:,.3f} {c.tknx}, {c.y_act:,.3f} {c.tkny}")
    print(f"TVL = {c.tvl(tkn=c.tknx):,.3f} {c.tknx} = {c.tvl(tkn=c.tkny):,.3f} {c.tkny}")
    
    curve = CPC.from_univ3(
        **u.cpc_params(
            cid = "0",
            descr = "",
            #params = dict(uv3raw=asdict(u)),
        ),
    )
    curve
    
    
    c = curve
    print(f"Reserve: {c.x_act:,.3f} {c.tknx}, {c.y_act:,.3f} {c.tkny}")
    print(f"TVL = {c.tvl(tkn=c.tknx):,.3f} {c.tknx} = {c.tvl(tkn=c.tkny):,.3f} {c.tkny}")
    
    