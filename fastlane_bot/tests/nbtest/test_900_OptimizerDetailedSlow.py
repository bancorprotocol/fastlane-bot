# ------------------------------------------------------------
# Auto generated test file `test_900_OptimizerDetailedSlow.py`
# ------------------------------------------------------------
# source file   = NBTest_900_OptimizerDetailedSlow.py
# test id       = 900
# test comment  = OptimizerDetailedSlow
# ------------------------------------------------------------



#from fastlane_bot import Bot, Config, ConfigDB, ConfigNetwork, ConfigProvider
from fastlane_bot.tools.cpc import ConstantProductCurve as CPC, CPCContainer, T, Pair
from fastlane_bot.tools.analyzer import CPCAnalyzer
from fastlane_bot.tools.optimizer import PairOptimizer, MargPOptimizer, ConvexOptimizer
from fastlane_bot.tools.optimizer import OptimizerBase, CPCArbOptimizer
from fastlane_bot.tools.arbgraphs import ArbGraph
print("{0.__name__} v{0.__VERSION__} ({0.__DATE__})".format(CPC))
print("{0.__name__} v{0.__VERSION__} ({0.__DATE__})".format(CPCAnalyzer))
print("{0.__name__} v{0.__VERSION__} ({0.__DATE__})".format(OptimizerBase))
print("{0.__name__} v{0.__VERSION__} ({0.__DATE__})".format(CPCArbOptimizer))
print("{0.__name__} v{0.__VERSION__} ({0.__DATE__})".format(PairOptimizer))
print("{0.__name__} v{0.__VERSION__} ({0.__DATE__})".format(MargPOptimizer))
print("{0.__name__} v{0.__VERSION__} ({0.__DATE__})".format(ConvexOptimizer))
print("{0.__name__} v{0.__VERSION__} ({0.__DATE__})".format(ArbGraph))
#print("{0.__name__} v{0.__VERSION__} ({0.__DATE__})".format(Bot))
from fastlane_bot.testing import *
import itertools as it
import collections as cl
#plt.style.use('seaborn-dark')
plt.rcParams['figure.figsize'] = [12,6]
from fastlane_bot import __VERSION__
require("3.0", __VERSION__)



try:
    CCm = CPCContainer.from_df(pd.read_csv("_data/NBTest_006.csv.gz"))
except:
    CCm = CPCContainer.from_df(pd.read_csv("fastlane_bot/tests/nbtest/_data/NBTest_006.csv.gz"))

CCu3    = CCm.byparams(exchange="uniswap_v3")
CCu2    = CCm.byparams(exchange="uniswap_v2")
CCs2    = CCm.byparams(exchange="sushiswap_v2")
CCc1    = CCm.byparams(exchange="carbon_v1")
tc_u3   = CCu3.token_count(asdict=True)
tc_u2   = CCu2.token_count(asdict=True)
tc_s2   = CCs2.token_count(asdict=True)
tc_c1   = CCc1.token_count(asdict=True)
CAm     = CPCAnalyzer(CCm)
#CCm.asdf().to_csv("A011-test.csv.gz", compression = "gzip")

CA      = CAm
pairs0  = CA.CC.pairs(standardize=False)
pairs   = CA.pairs()
pairsc  = CA.pairsc()
tokens  = CA.tokens()


# ------------------------------------------------------------
# Test      900
# File      test_900_OptimizerDetailedSlow.py
# Segment   Market structure analysis [NOTEST]
# ------------------------------------------------------------
def notest_market_structure_analysis():
# ------------------------------------------------------------
    
    print(f"Total pairs:    {len(pairs0):4}")
    print(f"Primary pairs:  {len(pairs):4}")
    print(f"...carbon:      {len(pairsc):4}")
    print(f"Tokens:         {len(CA.tokens()):4}")
    print(f"Curves:         {len(CCm):4}")
    
    CA.count_by_pairs()
    
    CA.count_by_pairs(minn=2)
    
    # ### All crosses
    
    CCx = CCm.bypairs(
        CCm.filter_pairs(notin=f"{T.ETH},{T.USDC},{T.USDT},{T.BNT},{T.DAI},{T.WBTC}")
    )
    len(CCx), CCx.token_count()[:10]
    
    AGx=ArbGraph.from_cc(CCx)
    AGx.plot(labels=False, node_size=50, node_color="#fcc")._
    
    # ### Biggest crosses (HEX, UNI, ICHI, FRAX)
    
    CCx2 = CCx.bypairs(
        CCx.filter_pairs(onein=f"{T.HEX}, {T.UNI}, {T.ICHI}, {T.FRAX}")
    )
    ArbGraph.from_cc(CCx2).plot()
    len(CCx2)
    
    # ### Carbon
    
    ArbGraph.from_cc(CCc1).plot()._
    
    len(CCc1), len(CCc1.tokens())
    
    CCc1.token_count()
    
    
    len(CCc1.pairs()), CCc1.pairs()
    
    # ### Token subsets
    
    O = MargPOptimizer(CCm.bypairs(
        CCm.filter_pairs(bothin=f"{T.ETH},{T.USDC},{T.USDT},{T.BNT},{T.DAI},{T.WBTC}")
    ))
    r = O.margp_optimizer(f"{T.USDC}", params=dict(verbose=False, debug=False))
    r.trade_instructions(ti_format=O.TIF_DFAGGR).fillna("")
    
    # +
    #r.trade_instructions(ti_format=O.TIF_DFAGGR).fillna("").to_excel("ti.xlsx")
    # -
    
    ArbGraph.from_r(r).plot()._
    
    # +
    #O.CC.plot()
    # -
    

# ------------------------------------------------------------
# Test      900
# File      test_900_OptimizerDetailedSlow.py
# Segment   ABC Tests
# ------------------------------------------------------------
def test_abc_tests():
# ------------------------------------------------------------
    
    assert raises(OptimizerBase).startswith("Can't instantiate abstract class")
    assert raises(OptimizerBase.OptimizerResult).startswith("Can't instantiate abstract class")
    
    assert raises(CPCArbOptimizer).startswith("Can't instantiate abstract class")
    assert raises(CPCArbOptimizer.OptimizerResult).startswith("Can't instantiate abstract class")
    
    assert not raises(MargPOptimizer, CCm)
    assert not raises(PairOptimizer, CCm)
    assert not raises(ConvexOptimizer, CCm)
    
    assert MargPOptimizer(CCm).kind == "margp"
    assert PairOptimizer(CCm).kind == "pair"
    assert ConvexOptimizer(CCm).kind == "convex"
    
    CPCArbOptimizer.MargpOptimizerResult(None, time=0,errormsg="err", optimizer=None)
    

# ------------------------------------------------------------
# Test      900
# File      test_900_OptimizerDetailedSlow.py
# Segment   General and Specific Tests
# ------------------------------------------------------------
def test_general_and_specific_tests():
# ------------------------------------------------------------
    
    CA = CAm
    
    # ### General tests
    
    # #### General data integrity (should ALWAYS hold)
    
    assert len(pairs0) > 2500
    assert len(pairs) > 2500
    assert len(pairs0) > len(pairs)
    assert len(pairsc) > 10
    assert len(CCm.tokens()) > 2000
    assert len(CCm)>4000
    assert len(CCm.filter_pairs(onein=f"{T.ETH}")) > 1900 # ETH pairs
    assert len(CCm.filter_pairs(onein=f"{T.USDC}")) > 300 # USDC pairs
    assert len(CCm.filter_pairs(onein=f"{T.USDT}")) > 190 # USDT pairs
    assert len(CCm.filter_pairs(onein=f"{T.DAI}")) > 50 # DAI pairs
    assert len(CCm.filter_pairs(onein=f"{T.WBTC}")) > 30 # WBTC pairs
    
    xis0 = {c.cid: (c.x, c.y) for c in CCm if c.x==0}
    yis0 = {c.cid: (c.x, c.y) for c in CCm if c.y==0}
    assert len(xis0) == 0 # set loglevel debug to see removal of curves
    assert len(yis0) == 0
    
    # #### Data integrity
    
    assert len(CCm) == 4155
    assert len(CCu3) == 1411
    assert len(CCu2) == 2177
    assert len(CCs2) == 236
    assert len(CCm.tokens()) == 2233
    assert len(CCm.pairs()) == 2834
    assert len(CCm.pairs(standardize=False)) == 2864
    
    
    assert CA.pairs()  == CCm.pairs(standardize=True)
    assert CA.pairsc() == {c.pairo.primary for c in CCm if c.P("exchange")=="carbon_v1"}
    assert CA.tokens() == CCm.tokens()
    
    # #### prices
    
    r1 = CCc1.prices(result=CCc1.PR_TUPLE)
    r2 = CCc1.prices(result=CCc1.PR_TUPLE, primary=False)
    r3 = CCc1.prices(result=CCc1.PR_TUPLE, primary=False, inclpair=False)
    assert isinstance(r1, tuple)
    assert isinstance(r2, tuple)
    assert isinstance(r3, tuple)
    assert len(r1) == len(r2)
    assert len(r1) == len(r3)
    assert len(r1[0]) == 3
    assert isinstance(r1[0][0], str)
    assert isinstance(r1[0][1], float)
    assert len(r1[0][2].split("/"))==2
    
    r2[:2]
    
    r3[:2]
    
    r1a = CCc1.prices(result=CCc1.PR_DICT)
    r2a = CCc1.prices(result=CCc1.PR_DICT, primary=False)
    r3a = CCc1.prices(result=CCc1.PR_DICT, primary=False, inclpair=False)
    assert isinstance(r1a, dict)
    assert isinstance(r2a, dict)
    assert isinstance(r3a, dict)
    assert len(r1a) == len(r1)
    assert len(r1a) == len(r2a)
    assert len(r1a) == len(r3a)
    assert list(r1a.keys()) == list(x[0] for x in r1)
    assert r1a.keys() == r2a.keys()
    assert r1a.keys() == r3a.keys()
    assert set(len(x) for x in r1a.values()) == {2},  "all records must be of of length 2"
    assert set(type(x[0]) for x in r1a.values()) == {float},  "all records must have first type float"
    assert set(type(x[1]) for x in r1a.values()) == {str},  "all records must have second type str"
    assert tuple(r3a.values()) == r3
    
    df =  CCc1.prices(result=CCc1.PR_DF, primary=False)
    assert len(df) == len(r1)
    assert tuple(df.index) == tuple(x[0] for x in r1)
    assert tuple(df["price"]) == r3
    df
    
    # #### more prices
    
    CCt = CCm.bypairs(f"{T.USDC}/{T.ETH}")
    
    r = CCt.prices(result=CCt.PR_TUPLE)
    assert isinstance(r, tuple)
    assert len(r) == len(CCt)
    assert r[0] == ('6c988ffdc9e74acd97ccfb16dd65c110', 1833.9007005259564, 'WETH-6Cc2/USDC-eB48')
    assert CCt.prices() == CCt.prices(result=CCt.PR_DICT)
    r = CCt.prices(result=CCt.PR_DICT)
    assert len(r) == len(CCt)
    assert isinstance(r, dict)
    assert r['6c988ffdc9e74acd97ccfb16dd65c110'] == (1833.9007005259564, 'WETH-6Cc2/USDC-eB48')
    df = CCt.prices(result=CCt.PR_DF)
    assert len(df) == len(CCt)
    assert tuple(df.loc["1701411834604692317316873037158841057339-0"]) == (1799.9999997028303, 'WETH-6Cc2/USDC-eB48')
    
    # #### price_ranges
    
    CCt = CCm.bypairs(f"{T.USDC}/{T.ETH}")
    CAt = CPCAnalyzer(CCt)
    
    r = CAt.price_ranges(result=CAt.PR_TUPLE)
    assert len(r) == len(CCt)
    assert r[0] == (
        'WETH/USDC',        # pair
        '16dd65c110',       # cid
        'sushiswap_v2',     # exchange
        'b',                # buy
        's',                # sell
        0,                  # min_primary
        None,               # max_primary
        1833.9007005259564  # pp
    )
    assert r[1] == (
        'WETH/USDC',
        '41057334-0',
        'carbon_v1',
        'b',
        '',
        1699.999829864358,
        1700.000169864341,
        1700.000169864341
    )
    r = CAt.price_ranges(result=CAt.PR_TUPLE, short=False)
    assert r[0] == (
        'WETH-6Cc2/USDC-eB48',
        '6c988ffdc9e74acd97ccfb16dd65c110',
        'sushiswap_v2',
        'b',
        's',
        0,
        None,
        1833.9007005259564
    )
    r = CAt.price_ranges(result=CAt.PR_DICT)
    assert len(r) == len(CCt)
    assert r['6c988ffdc9e74acd97ccfb16dd65c110'] == (
        'WETH/USDC',
        '16dd65c110',
        'sushiswap_v2',
        'b',
        's',
        0,
        None,
        1833.9007005259564
    )
    df = CAt.price_ranges(result=CAt.PR_DF)
    assert len(df) == len(CCt)
    assert tuple(df.index.names) == ('pair', 'exch', 'cid')
    assert tuple(df.columns) == ('b', 's', 'p_min', 'p_max', 'p_marg')
    assert set(df["p_marg"]) == set(x[-1] for x in CAt.price_ranges(result=CCt.PR_TUPLE))
    for p1, p2 in zip(df["p_marg"], df["p_marg"][1:]):
        assert p2 >= p1
    df
    
    # #### count_by_pairs
    
    assert len(CA.count_by_pairs()) == len(CA.pairs())
    assert sum(CA.count_by_pairs()["count"])==len(CA.CC)
    assert np.all(CA.count_by_pairs() == CA.count_by_pairs(asdf=True))
    assert len(CA.count_by_pairs()) == len(CA.count_by_pairs(asdf=False))
    assert type(CA.count_by_pairs()).__name__ == "DataFrame"
    assert type(CA.count_by_pairs(asdf=False)).__name__ == "list"
    assert type(CA.count_by_pairs(asdf=False)[0]).__name__ == "tuple"
    for i in range(10):
        assert len(CA.count_by_pairs(minn=i)) >= len(CA.count_by_pairs(minn=i)), f"failed {i}"
    
    # #### count_by_tokens
    
    r = CA.count_by_tokens()
    assert len(r) == len(CA.tokens())
    assert sum(r["total"]) == 2*len(CA.CC)
    assert tuple(r["total"]) == tuple(x[1] for x in CA.CC.token_count())
    for ix, row in r[:10].iterrows():
        assert row[0] >= sum(row[1:]), f"failed at {ix} {tuple(row)}"
    CA.count_by_tokens()
    
    # #### pool_arbitrage_statistics
    
    pas = CAm.pool_arbitrage_statistics()
    assert np.all(pas == CAm.pool_arbitrage_statistics(CAm.POS_DF))
    assert len(pas)==165
    assert list(pas.columns) == ['price', 'vl', 'itm', 'b', 's', 'bsv']
    assert list(pas.index.names) == ['pair', 'exchange', 'cid0']
    assert {x[0] for x in pas.index} == {Pair.n(x) for x in CAm.pairsc()}
    assert {x[1] for x in pas.index} == {'bancor_v2', 'bancor_v3','carbon_v1','sushiswap_v2','uniswap_v2','uniswap_v3'}
    pas
    
    pasd = CAm.pool_arbitrage_statistics(CAm.POS_DICT)
    assert isinstance(pasd, dict)
    assert len(pasd) == 26
    assert len(pasd['WETH-6Cc2/DAI-1d0F']) == 7
    pd0 = pasd['WETH-6Cc2/DAI-1d0F'][0]
    assert pd0[:2] == ('WETH/DAI', 'WETH-6Cc2/DAI-1d0F')
    assert iseq(pd0[2], 1840.1216491367131)
    assert pd0[3:6] == ('594', '594', 'uniswap_v3')
    assert iseq(pd0[6], 8.466598820198278)
    assert pd0[7:] == ('', 'b', 's', 'buy-sell-WETH @ 1840.12 DAI per WETH')
    pd0
    
    pasl = CAm.pool_arbitrage_statistics(result = CAm.POS_LIST)
    assert isinstance(pasl, tuple)
    assert len(pasl) == len(pas)
    pd0 = [(ix, x) for ix, x in enumerate(pasl) if x[2]==1840.1216491367131]
    pd0 = pasl[pd0[0][0]]
    assert pd0[:2] == ('WETH/DAI', 'WETH-6Cc2/DAI-1d0F')
    assert iseq(pd0[2], 1840.1216491367131)
    assert pd0[3:6] == ('594', '594', 'uniswap_v3')
    assert iseq(pd0[6], 8.466598820198278)
    assert pd0[7:] == ('', 'b', 's', 'buy-sell-WETH @ 1840.12 DAI per WETH')
    pd0
    
    # ### MargP Optimizer
    
    # #### margp optimizer
    
    tokenlist = f"{T.ETH},{T.USDC},{T.USDT},{T.BNT},{T.DAI},{T.WBTC}"
    targettkn = f"{T.USDC}"
    O = MargPOptimizer(CCm.bypairs(CCm.filter_pairs(bothin=tokenlist)))
    r = O.margp_optimizer(targettkn, params=dict(verbose=False, debug=False))
    r.trade_instructions(ti_format=O.TIF_DFAGGR).fillna("")
    
    # #### MargpOptimizerResult
    
    assert type(r) == MargPOptimizer.MargpOptimizerResult
    assert iseq(r.result, -4606.010157294979)
    assert r.time > 0.001
    assert r.time < 0.1
    assert r.method == O.METHOD_MARGP
    assert r.targettkn == targettkn
    assert set(r.tokens_t)==set(['USDT-1ec7', 'WETH-6Cc2', 'WBTC-C599', 'DAI-1d0F', 'BNT-FF1C'])
    p_opt_d0 = {t:x for x, t in zip(r.p_optimal_t, r.tokens_t)}
    p_opt_d = {t:round(x,6) for x, t in zip(r.p_optimal_t, r.tokens_t)}
    print("optimal p", p_opt_d)
    assert p_opt_d == {'WETH-6Cc2': 1842.67228, 'WBTC-C599': 27604.143472, 
                    'BNT-FF1C': 0.429078, 'USDT-1ec7': 1.00058, 'DAI-1d0F': 1.000179}
    assert r.p_optimal[r.targettkn] == 1
    po = [(k,v) for k,v in r.p_optimal.items()][:-1]
    assert len(po)==len(r.p_optimal_t)
    for k,v in po:
        assert p_opt_d0[k] == v, f"error at {k}, {v}, {p_opt_d0[k]}"
    
    # #### TradeInstructions
    
    assert r.trade_instructions() == r.trade_instructions(ti_format=O.TIF_OBJECTS)
    ti = r.trade_instructions(ti_format=O.TIF_OBJECTS)
    cids = tuple(ti_.cid for ti_ in ti)
    assert isinstance(ti, tuple)
    assert len(ti) == 86
    ti0=[x for x in ti if x.cid=="357"]
    assert len(ti0)==1
    ti0=ti0[0]
    assert ti0.cid == ti0.curve.cid
    assert type(ti0).__name__ == "TradeInstruction"
    assert type(ti[0]) == MargPOptimizer.TradeInstruction
    assert ti0.tknin == f"{T.USDT}"
    assert ti0.tknout == f"{T.USDC}"
    assert round(ti0.amtin, 8)  == 1214.45596849
    assert round(ti0.amtout, 8) == -1216.41933959
    assert ti0.error is None
    ti[:2]
    
    tid = r.trade_instructions(ti_format=O.TIF_DICTS)
    assert isinstance(tid, tuple)
    assert len(tid) == len(ti)
    tid0=[x for x in tid if x["cid"]=="357"]
    assert len(tid0)==1
    tid0=tid0[0]
    assert type(tid0)==dict
    assert tid0["tknin"] == f"{T.USDT}"
    assert tid0["tknout"] == f"{T.USDC}"
    assert round(tid0["amtin"], 8)  == 1214.45596849
    assert round(tid0["amtout"], 8) == -1216.41933959
    assert tid0["error"] is None
    tid[:2]
    
    df = r.trade_instructions(ti_format=O.TIF_DF).fillna("")
    assert tuple(df.index) == cids
    assert np.all(r.trade_instructions(ti_format=O.TIF_DFRAW).fillna("")==df)
    assert len(df) == len(ti)
    assert list(df.columns)[:4] == ['pair', 'pairp', 'tknin', 'tknout']
    assert len(df.columns) == 4 + len(r.tokens_t) + 1
    tif0 = dict(df.loc["357"])
    assert tif0["pair"] == "USDC-eB48/USDT-1ec7"
    assert tif0["pairp"] == "USDC/USDT"
    assert tif0["tknin"] == tid0["tknin"]
    assert tif0[tif0["tknin"]] == tid0["amtin"]
    assert tif0[tif0["tknout"]] == tid0["amtout"]
    df[:2]
    
    dfa = r.trade_instructions(ti_format=O.TIF_DFAGGR).fillna("")
    assert tuple(dfa.index)[:-4] == cids
    assert len(dfa) == len(df)+4
    assert len(dfa.columns) == len(r.tokens_t) + 1
    assert set(dfa.columns) == set(r.tokens_t).union(set([r.targettkn]))
    assert list(dfa.index)[-4:] == ['PRICE', 'AMMIn', 'AMMOut', 'TOTAL NET']
    dfa[:10]
    
    dfpg = r.trade_instructions(ti_format=O.TIF_DFPG)
    assert set(x[1] for x in dfpg.index) == set(cids)
    assert np.all(dfpg["gain_tknq"]>=0)
    assert np.all(dfpg["gain_r"]>=0)
    assert round(np.max(dfpg["gain_r"]),8) == 0.04739068
    assert round(np.min(dfpg["gain_r"]),8) == 1.772e-05
    assert len(dfpg) == len(ti)
    for p, t in zip(tuple(dfpg["pair"]), tuple(dfpg["tknq"])):
        assert p.split("/")[1] == t, f"error in {p} [{t}]"
    print(f"total gains: {sum(dfpg['gain_ttkn']):,.2f} {r.targettkn} [result={-r.result:,.2f}]")
    assert abs(sum(dfpg["gain_ttkn"])/r.result+1)<0.01
    dfpg[:10]
    
    # ### Convex Optimizer
    
    tokens = f"{T.DAI},{T.USDT},{T.HEX},{T.WETH},{T.LINK}"
    CCo  = CCu2.bypairs(CCu2.filter_pairs(bothin=tokens))
    CCo += CCs2.bypairs(CCu2.filter_pairs(bothin=tokens))
    CA   = CPCAnalyzer(CCo)
    O = ConvexOptimizer(CCo)
    #ArbGraph.from_cc(CCo).plot()._
    
    CA.count_by_tokens()
    
    # +
    #CCo.plot()
    # -
    
    # #### convex optimizer
    
    targettkn = T.USDT
    # r = O.margp_optimizer(targettkn, params=dict(verbose=True, debug=False))
    # r
    
    SFC = O.SFC(**{targettkn:O.AMMPays})
    r = O.convex_optimizer(SFC, verbose=False, solver=O.SOLVER_SCS)
    r
    
    # #### NofeesOptimizerResult
    
    round(r.result,-5)
    
    assert type(r) == ConvexOptimizer.NofeesOptimizerResult
    # assert round(r.result,-5) <= -1500000.0
    # assert round(r.result,-5) >= -2500000.0
    # assert r.time < 8
    assert r.method == "convex"
    assert set(r.token_table.keys()) == set(['USDT-1ec7', 'WETH-6Cc2', 'LINK-86CA', 'DAI-1d0F', 'HEX-eb39'])
    assert len(r.token_table[T.USDT].x)==0
    assert len(r.token_table[T.USDT].y)==10
    lx = list(it.chain(*[rr.x for rr in r.token_table.values()]))
    lx.sort()
    ly = list(it.chain(*[rr.y for rr in r.token_table.values()]))
    ly.sort()
    assert lx == [_ for _ in range(21)]
    assert ly == lx
    
    # #### trade instructions
    
    ti = r.trade_instructions()
    assert type(ti[0]) == ConvexOptimizer.TradeInstruction
    
    assert r.trade_instructions() == r.trade_instructions(ti_format=O.TIF_OBJECTS)
    ti = r.trade_instructions(ti_format=O.TIF_OBJECTS)
    cids = tuple(ti_.cid for ti_ in ti)
    assert isinstance(ti, tuple)
    assert len(ti) == 21
    ti0=[x for x in ti if x.cid=="175"]
    assert len(ti0)==1
    ti0=ti0[0]
    assert ti0.cid == ti0.curve.cid
    assert type(ti0).__name__ == "TradeInstruction"
    assert type(ti[0]) == ConvexOptimizer.TradeInstruction
    assert ti0.tknin == f"{T.LINK}"
    assert ti0.tknout == f"{T.DAI}"
    # assert round(ti0.amtin, 8)  == 8.50052943
    # assert round(ti0.amtout, 8) == -50.40963779
    assert ti0.error is None
    ti[:2]
    
    tid = r.trade_instructions(ti_format=O.TIF_DICTS)
    assert isinstance(tid, tuple)
    assert type(tid[0])==dict
    assert len(tid) == len(ti)
    tid0=[x for x in tid if x["cid"]=="175"]
    assert len(tid0)==1
    tid0=tid0[0]
    assert tid0["tknin"] == f"{T.LINK}"
    assert tid0["tknout"] == f"{T.DAI}"
    # assert round(tid0["amtin"], 8)  == 8.50052943
    # assert round(tid0["amtout"], 8) == -50.40963779
    assert tid0["error"] is None
    tid[:2]
    
    df = r.trade_instructions(ti_format=O.TIF_DF).fillna("")
    assert tuple(df.index) == cids
    assert np.all(r.trade_instructions(ti_format=O.TIF_DFRAW).fillna("")==df)
    assert len(df) == len(ti)
    assert list(df.columns)[:4] == ['pair', 'pairp', 'tknin', 'tknout']
    assert len(df.columns) == 4 + 4 + 1
    tif0 = dict(df.loc["175"])
    assert tif0["pair"] == 'LINK-86CA/DAI-1d0F'
    assert tif0["pairp"] == "LINK/DAI"
    assert tif0["tknin"] == tid0["tknin"]
    assert tif0[tif0["tknin"]] == tid0["amtin"]
    assert tif0[tif0["tknout"]] == tid0["amtout"]
    df[:2]
    
    assert raises(r.trade_instructions, ti_format=O.TIF_DFAGGR).startswith("TIF_DFAGGR not implemented for")
    assert raises(r.trade_instructions, ti_format=O.TIF_DFPG).startswith("TIF_DFPG not implemented for")
    
    # ### Simple Optimizer
    
    pair = f"{T.ETH}/{T.USDC}"
    CCs  = CCm.bypairs(pair)
    CA   = CPCAnalyzer(CCs)
    O = PairOptimizer(CCs)
    #ArbGraph.from_cc(CCs).plot()._
    
    CA.count_by_tokens()
    
    # +
    #CCs.plot()
    # -
    
    # #### simple optimizer
    
    r = O.optimize(T.USDC)
    r
    
    # #### result
    
    assert type(r) == PairOptimizer.MargpOptimizerResult
    assert round(r.result, 5) == -1217.24416
    assert r.time < 0.1
    assert r.method == "margp-pair"
    assert r.errormsg is None
    
    round(r.result,5)
    
    # #### trade instructions
    
    ti = r.trade_instructions()
    assert type(ti[0]) == PairOptimizer.TradeInstruction
    
    assert r.trade_instructions() == r.trade_instructions(ti_format=O.TIF_OBJECTS)
    ti = r.trade_instructions(ti_format=O.TIF_OBJECTS)
    cids = tuple(ti_.cid for ti_ in ti)
    assert isinstance(ti, tuple)
    assert len(ti) == 12
    ti0=[x for x in ti if x.cid=="6c988ffdc9e74acd97ccfb16dd65c110"]
    assert len(ti0)==1
    ti0=ti0[0]
    assert ti0.cid == ti0.curve.cid
    assert type(ti0).__name__ == "TradeInstruction"
    assert type(ti[0]) == PairOptimizer.TradeInstruction
    assert ti0.tknin == f"{T.USDC}"
    assert ti0.tknout == f"{T.WETH}"
    assert round(ti0.amtin, 5)  == 48153.80865
    assert round(ti0.amtout, 5) == -26.18300
    assert ti0.error is None
    ti[:2]
    
    tid = r.trade_instructions(ti_format=O.TIF_DICTS)
    assert isinstance(tid, tuple)
    assert type(tid[0])==dict
    assert len(tid) == len(ti)
    tid0=[x for x in tid if x["cid"]=="6c988ffdc9e74acd97ccfb16dd65c110"]
    assert len(tid0)==1
    tid0=tid0[0]
    assert tid0["tknin"] == f"{T.USDC}"
    assert tid0["tknout"] == f"{T.WETH}"
    assert round(tid0["amtin"], 5)  == 48153.80865
    assert round(tid0["amtout"], 5) == -26.183
    assert tid0["error"] is None
    tid[:2]
    
    # trade instructions of format `TIF_DFRAW` (same as `TIF_DF`): raw dataframe
    
    df = r.trade_instructions(ti_format=O.TIF_DF).fillna("")
    assert tuple(df.index) == cids
    assert np.all(r.trade_instructions(ti_format=O.TIF_DFRAW).fillna("")==df)
    assert len(df) == len(ti)
    assert list(df.columns)[:4] == ['pair', 'pairp', 'tknin', 'tknout']
    assert len(df.columns) == 4 + 1 + 1
    tif0 = dict(df.loc["6c988ffdc9e74acd97ccfb16dd65c110"])
    assert tif0["pair"] == 'WETH-6Cc2/USDC-eB48'
    assert tif0["pairp"] == "WETH/USDC"
    assert tif0["tknin"] == tid0["tknin"]
    assert tif0[tif0["tknin"]] == tid0["amtin"]
    assert tif0[tif0["tknout"]] == tid0["amtout"]
    df[:2]
    
    # trade instructions of format `TIF_DFAGGR` (aggregated data frame)
    
    df = r.trade_instructions(ti_format=O.TIF_DFAGGR)
    assert len(df) == 16 
    assert tuple(df.index[-4:]) == ('PRICE', 'AMMIn', 'AMMOut', 'TOTAL NET')
    assert tuple(df.columns) == ('USDC-eB48', 'WETH-6Cc2')
    df
    
    
    
    # prices and gains analysis data frame `TIF_DFPG`
    
    df = r.trade_instructions(ti_format=O.TIF_DFPG)
    assert len(df) == 12
    assert set(x[0] for x in tuple(df.index)) == {'carbon_v1', 'sushiswap_v2', 'uniswap_v2', 'uniswap_v3'}
    assert max(df["margp"]) == min(df["margp"]) 
    assert tuple(df.index.names) == ('exch', 'cid')
    assert tuple(df.columns) == (
        'fee',
        'pair',
        'amt_tknq',
        'tknq',
        'margp0',
        'effp',
        'margp',
        'gain_r',
        'gain_tknq',
        'gain_ttkn'
    )
    df
    

# ------------------------------------------------------------
# Test      900
# File      test_900_OptimizerDetailedSlow.py
# Segment   Analysis by pair
# ------------------------------------------------------------
def test_analysis_by_pair():
# ------------------------------------------------------------
    
    # +
    # CCm1 = CAm.CC.copy()
    # CCm1 += CPC.from_carbon(
    #     pair=f"{T.WETH}/{T.USDC}",
    #     yint = 1,
    #     y = 1,
    #     pa = 1500,
    #     pb = 1501,
    #     tkny = f"{T.WETH}",
    #     cid = "test-1",
    #     isdydx=False,
    #     params=dict(exchange="carbon_v1"),
    # )
    # CAm1 = CPCAnalyzer(CCm1)
    # CCm1.asdf().to_csv("NBTest_006-augmented.csv.gz", compression = "gzip")
    # -
    
    pricedf = CAm.pool_arbitrage_statistics()
    assert len(pricedf)==165
    pricedf
    
    # ### WETH/USDC
    
    pair = "WETH-6Cc2/USDC-eB48"
    print(f"Pair = {pair}")
    
    df = pricedf.loc[Pair.n(pair)]
    assert len(df)==24
    df
    
    pi = CAm.pair_data(pair)
    O = MargPOptimizer(pi.CC)
    
    # #### Target token = base token
    
    targettkn = pair.split("/")[0]
    print(f"Target token = {targettkn}")
    r = O.margp_optimizer(targettkn, params=dict(verbose=False, debug=False))
    r.trade_instructions(ti_format=O.TIF_DFAGGR)
    
    dfti1 = r.trade_instructions(ti_format=O.TIF_DFPG8)
    print(f"Total gain: {sum(dfti1['gain_ttkn']):.4f} {targettkn}")
    dfti1
    
    # #### Target token = quote token
    
    targettkn = pair.split("/")[1]
    print(f"Target token = {targettkn}")
    r = O.margp_optimizer(targettkn, params=dict(verbose=False, debug=False))
    r.trade_instructions(ti_format=O.TIF_DFAGGR)
    
    dfti2 = r.trade_instructions(ti_format=O.TIF_DFPG8)
    print(f"Total gain: {sum(dfti2['gain_ttkn']):.4f}", targettkn)
    dfti2