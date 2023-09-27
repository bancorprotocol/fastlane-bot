# ------------------------------------------------------------
# Auto generated test file `test_004_GraphCode.py`
# ------------------------------------------------------------
# source file   = NBTest_004_GraphCode.py
# test id       = 004
# test comment  = GraphCode
# ------------------------------------------------------------



import fastlane_bot.tools.arbgraphs as ag
from fastlane_bot.tools.cpc import ConstantProductCurve as CPC, CPCContainer
print("{0.__name__} v{0.__VERSION__} ({0.__DATE__})".format(CPC))
print("{0.__name__} v{0.__VERSION__} ({0.__DATE__})".format(ag.ArbGraph))

from fastlane_bot.testing import *
#plt.style.use('seaborn-dark')
plt.rcParams['figure.figsize'] = [12,6]
from fastlane_bot import __VERSION__
require("2.0", __VERSION__)




# ------------------------------------------------------------
# Test      004
# File      test_004_GraphCode.py
# Segment   ArbGraphs test and demo
# ------------------------------------------------------------
def test_arbgraphs_test_and_demo():
# ------------------------------------------------------------
    
    nodes = lambda: ag.create_node_list("ETH, USDC, WBTC, BNT")
    assert [str(n) for n in nodes()] == ['ETH(0)', 'USDC(1)', 'WBTC(2)', 'BNT(3)']
    nodes()
    
    AG = ag.ArbGraph(nodes=nodes())
    N = AG.node_by_tkn
    assert str(N("ETH")) == "ETH(0)"
    assert str(N("BNT")) == "BNT(3)"
    assert str(AG.node_by_ix(1)) == "USDC(1)"
    assert str(AG.node_by_tkn("USDC")) == "USDC(1)"
    AG
    
    assert str(N("ETH")) == "ETH(0)"
    
    edge = ag.Edge(N("ETH"), 1, N("USDC"), 2000)
    edge1 = ag.Edge(N("ETH"), 1, N("USDC"), 2000, inverse=True, ix=10)
    assert (edge.pair(), edge.price(), edge.convention()) == ('ETH/USDC', 2000.0, 'USDC per ETH')
    assert (edge1.pair(), edge1.price(), edge1.convention()) == ('USDC/ETH', 0.0005, 'ETH per USDC')
    edge, str(edge), str(edge1)
    
    assert (edge+0).asdict() == edge.asdict()
    assert (edge+0) != edge # == means objects are the same
    assert not edge+0 is edge
    assert (2*edge).asdict() == (edge*2).asdict()
    assert (edge + 2*edge).asdict() == (3*edge).asdict()
    assert sum([edge,edge,edge]).asdict() == (3*edge).asdict()
    
    (edge+0).asdict()
    

# ------------------------------------------------------------
# Test      004
# File      test_004_GraphCode.py
# Segment   Paths and cycles
# ------------------------------------------------------------
def test_paths_and_cycles():
# ------------------------------------------------------------
    
    C = ag.Cycle([1,2,3,4,5])
    assert len(C) == 5
    assert [x for x in C.items()] == [1, 2, 3, 4, 5, 1]
    assert [x for x in C.items(start_ix=3)] == [4, 5, 1, 2, 3, 4]
    assert [x for x in C.items(start_val=3)] == [3, 4, 5, 1, 2, 3]
    assert [p for p in C.pairs()] == [(1, 2), (2, 3), (3, 4), (4, 5), (5, 1)]
    
    c1 = ag.Cycle([1,2,3,4,5,6], "c1")
    assert ag.Cycle([8,9]).is_subcycle_of(c1) == False
    assert ag.Cycle([1,5,6]).is_subcycle_of(c1) == True
    assert ag.Cycle([1,6,5]).is_subcycle_of(c1) == False
    assert c1.filter_subcycles([ag.Cycle([8,9]), ag.Cycle([1,5,6]), ag.Cycle([1,6,5])]) == (ag.Cycle([1, 5, 6]),)
    assert c1.filter_subcycles(ag.Cycle([1,5,6])) == (ag.Cycle([1, 5, 6]),)
    assert str(c1) == 'cycle [c1]:  1 -> 2 -> 3 -> 4 -> 5 -> 6 ->...'
    
    assert c1.asdict() == {'data': [1, 2, 3, 4, 5, 6], 'uid': 'c1', 'graph': None}
    assert c1.astuple() == ([1, 2, 3, 4, 5, 6], 'c1', None)
    assert (c1.asdf().set_index("uid")["data"] == c1.asdf(index="uid")["data"]).iloc[0]
    assert list(c1.asdf(exclude=["data"]).columns) == ['uid', 'graph']
    assert list(c1.asdf(include=["data", "graph"], exclude=["graph"]).columns) == ['data']
    
    import types
    nodes = ag.create_node_list("ETH, USDC, WBTC, BNT")
    c2 = ag.Cycle(nodes, "c2")
    assert c2.uid == "c2"
    assert str(c2) == 'cycle [c2]: ETH->USDC->WBTC->BNT->...'
    print(nodes)
    print(c2)
    gc2 = (c for c in c2.items())
    assert isinstance(gc2, types.GeneratorType)
    tc2 = tuple(gc2)
    assert str(tc2) == "(ETH(0), USDC(1), WBTC(2), BNT(3), ETH(0))"
    assert tuple(gc2) == tuple() # generator spent
    pc2 = (p for p in c2.pairs())
    assert isinstance(pc2, types.GeneratorType)
    tpc2 = tuple(pc2)
    assert len(tpc2) == 4
    assert str(tpc2[0]) == '(ETH(0), USDC(1))'
    assert str(tpc2[-1]) == '(BNT(3), ETH(0))'
    assert c2.pairs_s() == ['ETH/USDC', 'USDC/WBTC', 'WBTC/BNT', 'BNT/ETH']
    
    p1 = ag.Path([1,2,3,4,5,6], "p1")
    assert p1.uid == "p1"
    assert (str(p1)).strip() == 'path [p1]:  1 -> 2 -> 3 -> 4 -> 5 -> 6'
    gp1 = (p for p in p1.items())
    assert isinstance(gp1, types.GeneratorType)
    tp1 = tuple(gp1)
    assert tp1 == (1, 2, 3, 4, 5, 6)
    
    nodes = ag.create_node_list("ETH, USDC, WBTC, BNT")
    p2 = ag.Path(nodes, "p2")
    assert p2.uid == "p2"
    assert str(p2) == 'path [p2]: ETH->USDC->WBTC->BNT'
    gp2 = (c for c in p2.items())
    assert isinstance(gp2, types.GeneratorType)
    tp2 = tuple(gp2)
    assert str(tp2) == "(ETH(0), USDC(1), WBTC(2), BNT(3))"
    assert tuple(gp2) == tuple() # generator spent
    pp2 = (p for p in p2.pairs())
    assert isinstance(pp2, types.GeneratorType)
    tpp2 = tuple(pp2)
    assert len(tpp2) == 3
    assert str(tpp2[0]) == '(ETH(0), USDC(1))'
    assert str(tpp2[-1]) == '(WBTC(2), BNT(3))'
    assert p2.pairs_s() == ['ETH/USDC', 'USDC/WBTC', 'WBTC/BNT']
    

# ------------------------------------------------------------
# Test      004
# File      test_004_GraphCode.py
# Segment   Arbgraph transport test and demo
# ------------------------------------------------------------
def test_arbgraph_transport_test_and_demo():
# ------------------------------------------------------------
    
    n = ag.Node("ETH")
    assert isinstance(n.state, n.State)
    assert n.state == n.State(amount = 0)
    
    try:
        ag.Edge("ETH", 1, "USDC", 2000)
        raise
    except:
        pass
    
    ETH = ag.Node("ETH")
    USDC = ag.Node("USDC")
    assert ETH != n # nodes are only equal if they are the same object!
    assert ETH.asdict() == n.asdict()
    edge = ag.Edge(ETH, 1, USDC, 2000)
    edge2 = ag.Edge(ETH, 1, USDC, 2000)
    edge3 = ag.Edge(ETH, 2, USDC, 3500)
    assert (edge == edge2) == False
    assert edge != ag.Edge(ETH, 1, USDC, 2000)
    assert edge.asdict() == ag.Edge(ETH, 1, USDC, 2000).asdict()
    assert edge.node_in == ETH
    assert edge.node_out == USDC
    assert edge.amount_in == 1
    assert edge.amount_out == 2000
    assert edge.state == ag.Edge.State(amount_in_remaining=1)
    
    ETH.reset_state()
    USDC.reset_state()
    edge.reset_state()
    ETH.state.amount_.set(1)
    assert ETH.state.amount == 1
    edge.transport(1, record=True)
    assert ETH.state.amount == 0
    assert USDC.state.amount == 2000
    assert edge.state.amount_in_remaining == 0
    
    ETH.reset_state()
    USDC.reset_state()
    edge.reset_state()
    ETH.state.amount_.set(1)
    edge.transport(0.25, record=True)
    assert ETH.state.amount == 0.75
    assert USDC.state.amount == 500
    assert edge.state.amount_in_remaining == 0.75
    edge.transport(0.25, record=True)
    assert ETH.state.amount == 0.5
    assert USDC.state.amount == 1000
    assert edge.state.amount_in_remaining == 0.50
    
    ETH.reset_state()
    USDC.reset_state()
    edge.reset_state()
    ETH.state.amount = 1
    try:
        edge.transport(2, record=True)
    except Exception as e:
        print(e)
    
    ETH.reset_state()
    USDC.reset_state()
    edge.reset_state()
    ETH.state.amount = 0.5
    try:
        edge.transport(1, record=True)
    except Exception as e:
        print(e)
    
    ETH.reset_state()
    USDC.reset_state()
    edge.reset_state()
    ETH.state.amount = 2
    edge.transport(0.5, record=True)
    try:
        edge.transport(1, record=True)
    except Exception as e:
        print(e)
    
    ETH.state.amount = 10
    edge.state.amount_in_remaining = 10
    AG = ag.ArbGraph(nodes=[ETH, USDC], edges=[edge, edge2, edge3])
    assert AG.nodes == [ETH, USDC]
    assert AG.edges == [edge, edge2, edge3]
    assert AG.nodes[0].state.amount == 10
    assert AG.edges[0].state.amount_in_remaining == 10
    AG.reset_state()
    assert AG.nodes[0].state.amount == 0
    assert AG.edges[0].state.amount_in_remaining == 1
    assert AG.state.nodes[0] == ETH.state
    assert AG.state.edges[0] == edge.state
    
    assert AG.node_by_tkn("ETH") is ETH
    assert AG.node_by_tkn(ETH) is ETH
    try:
        AG.node_by_tkn(ag.Node("ETH"))
        raise
    except Exception as e:
        print(e)
    
    AG.reset_state()
    ETH.state.amount = 4
    r = AG.transport(2, "ETH", "USDC", record=True)
    assert ETH.state.amount == 2
    assert r.amount_in.amount == 2
    assert r.amount_in.tkn == "ETH"
    capacity_in = sum([e_.amount_in for e_ in r.edges])
    assert capacity_in == 4
    capacity_out = sum([e_.amount_out for e_ in r.edges])
    assert capacity_out == 7500
    assert r.amount_out.amount == r.amount_in.amount * capacity_out / capacity_in
    assert sum(r.amounts_in) == r.amount_in.amount
    assert sum(r.amounts_out) == r.amount_out.amount
    assert AG.has_capacity("ETH", "USDC")
    assert AG.has_capacity()
    AG.transport(2, "ETH", "USDC", record=True)
    assert AG.has_capacity() == False
    r
    
    rs = AG.edge_statistics(edges=r.edges)
    assert rs.len == 3
    assert rs.edges is r.edges
    assert rs.amounts_in == (1, 1, 2)
    assert rs.amounts_in_remaining == (0.0, 0.0, 0.0)
    assert rs.amounts_out == (2000, 2000, 3500)
    assert rs.prices == (2000.0, 2000.0, 1750.0)
    assert rs.utilizations == (1.0, 1.0, 1.0)
    assert rs.amount_in.amount == 4
    assert rs.amount_in_remaining.amount == 0.0
    assert rs.amount_out.amount == 7500
    assert rs.amount_in.tkn == "ETH"
    assert rs.amount_in_remaining.tkn == "ETH"
    assert rs.amount_out.tkn == "USDC"
    assert rs.utilization == 1.0
    assert rs.price == 1875.0
    rs
    
    rns = AG.node_statistics("ETH")
    assert len(rns.edges_out) == 3
    assert len(rns.edges_in) == 0
    assert rns.amount_in.amount == 0
    assert rns.amount_out.amount == 4
    assert rns.amount_out_remaining.amount == 0
    assert rns.nodes_in==set()
    assert rns.nodes_out=={"USDC"}
    rns
    
    rns2 = AG.node_statistics("USDC")
    assert len(rns2.edges_out) == 0
    assert len(rns2.edges_in) == 3
    assert rns2.amount_in.amount == 7500
    assert rns2.amount_out.amount == 0
    assert rns2.amount_out_remaining.amount == 0
    assert rns2.nodes_in==set(["ETH",])
    assert rns2.nodes_out==set()
    rns2
    
    

# ------------------------------------------------------------
# Test      004
# File      test_004_GraphCode.py
# Segment   Arbgraph transport test and demo 2
# ------------------------------------------------------------
def test_arbgraph_transport_test_and_demo_2():
# ------------------------------------------------------------
    
    @ag.dataclass
    class MyState():
        myval_: ag.TrackedStateFloat = ag.field(default_factory=ag.TrackedStateFloat, init=False)
        myval: ag.InitVar=None
            
        def __post_init__(self, myval):
            self.myval = myval
    
        @property
        def myval(self):
            return self.myval_.value
        
        @myval.setter
        def myval(self, value):
            self.myval_.set(value)
    
    
    mystate = MyState(0)
    mystate.myval_.set(10)
    assert mystate.myval == 10
    mystate.myval += 5
    assert mystate.myval == 15
    mystate.myval -= 4
    assert mystate.myval == 11
    assert mystate.myval_.history == [0, 0, 10, 15, 11]
    
    mystate = MyState(10)
    assert mystate.myval == 10
    assert mystate.myval_.history == [0,10]
    mystate.myval = 20
    assert mystate.myval == 20
    assert mystate.myval_.history == [0,10,20]
    mystate.myval += 5
    assert mystate.myval == 25
    mystate.myval -= 4
    assert mystate.myval == 21
    assert mystate.myval_.history == [0,10,20,25,21]
    assert mystate.myval_.reset(42)
    assert mystate.myval == 42
    assert mystate.myval_.history == [42]
    
    n = ag.Node("MEH")
    n.state.amount = 10
    n.state.amount += 5
    n.state.amount -= 4
    assert n.state.amount == 11
    assert n.state.amount_.history == [0, 10, 15, 11]
    n.reset_state()
    assert n.state.amount_.history == [0]
    
    nodes = ag.Node.create_node_list("USDC, LINK, ETH, WBTC")
    assert len(nodes)==4
    assert nodes[0].tkn == "USDC"
    AG = ag.ArbGraph(nodes)
    AG.add_edge("USDC", 10000, "ETH", 5)
    AG.add_edge_obj(AG.edges[-1].R())
    AG.add_edge("USDC", 10000, "WBTC", 1)
    AG.add_edge_obj(AG.edges[-1].R())
    AG.add_edge("USDC", 10000, "LINK", 1000)
    AG.add_edge_obj(AG.edges[-1].R())
    AG.add_edge("LINK", 1000, "ETH", 5)
    AG.add_edge_obj(AG.edges[-1].R())
    AG.add_edge("ETH", 5, "WBTC", 1)
    AG.add_edge_obj(AG.edges[-1].R())
    assert len(AG.edges)==10
    assert len(AG.cycles())==11
    ns = AG.node_statistics("USDC")
    assert ns.amount_in.amount == 30000
    assert ns.amount_out.amount == 30000
    assert ns.amount_out_remaining == ns.amount_out
    assert ns.nodes_out==set(['WBTC', 'ETH', 'LINK'])
    assert ns.nodes_in==set(['WBTC', 'ETH', 'LINK'])
    #_=AG.plot()
    

# ------------------------------------------------------------
# Test      004
# File      test_004_GraphCode.py
# Segment   Transport 3 and prices
# ------------------------------------------------------------
def test_transport_3_and_prices():
# ------------------------------------------------------------
    
    AG = ag.ArbGraph()
    prices = dict(USDC=1, LINK=5, AAVE=100, WETH=2000, BTC=10000)
    for t1,p1 in prices.items():
        for t2,p2 in prices.items():
            if t1<t2:
                AG.add_edge_ct(tkn_in=t1, tkn_out=t2, price_outperin=p1/p2, symmetric=True)
    USDC, WETH, LINK, AAVE, BTC = AG.nodes
    assert str(USDC) == "USDC(0)"
    assert str(AAVE) == "AAVE(3)"
    assert BTC.tkn == "BTC"
    assert AG.ptransport(ag.Path([USDC, WETH])).multiplier == prices[USDC.tkn]/prices[WETH.tkn]
    assert AG.ptransport(ag.Path([USDC, WETH, AAVE, LINK, BTC])).multiplier == AG.ptransport(ag.Path([USDC, BTC])).multiplier
    for n1 in AG.nodes:
        for n2 in AG.nodes:
            if n1 != n2:
                assert AG.ptransport(ag.Path([n1, n2])).multiplier == prices[n1.tkn]/prices[n2.tkn]
    #AG.plot(rnone=True)
    
    AG = ag.ArbGraph()
    prices = dict(USDC=1, LINK=5, AAVE=100, WETH=2000, BTC=10000)
    for t1,p1 in prices.items():
        for t2,p2 in prices.items():
            if t1=="USDC" and t2!=t1:
                AG.add_edge_ct(tkn_in=t1, tkn_out=t2, price_outperin=p1/p2, symmetric=True)
    assert str(AG.nodes) == "[USDC(0), LINK(1), AAVE(2), WETH(3), BTC(4)]"
    USDC, LINK, AAVE, WETH, BTC = AG.nodes
    assert str(USDC) == "USDC(0)"
    assert BTC.tkn == "BTC"
    assert AG.ptransport(ag.Path([USDC, WETH])).multiplier == prices[USDC.tkn]/prices[WETH.tkn]
    assert AG.ptransport(AG.shortest_path(USDC, WETH)).multiplier == prices[USDC.tkn]/prices[WETH.tkn]
    assert AG.ptransport(AG.shortest_path(BTC, WETH)).multiplier == prices[BTC.tkn]/prices[WETH.tkn]
    assert AG.price(node_tknb=WETH, node_tknq=USDC) == AG.price(WETH, USDC)
    assert AG.price(WETH, USDC, with_units=True) == (2000.0, 'USDC per WETH [WETH/USDC]')
    assert AG.price(WETH, WETH, with_units=True) == (1, 'WETH per WETH [WETH/WETH]')
    assert AG.price("WETH", "USDC", with_units = True) == AG.price(WETH, USDC, with_units =  True)
    assert raises(AG.price, "ETH", "USDC")
    for n1 in AG.nodes:
        for n2 in AG.nodes:
            if n1 != n2:
                assert AG.ptransport(AG.shortest_path(n1, n2)).multiplier == prices[n1.tkn]/prices[n2.tkn]
                assert AG.price(node_tknb=n1, node_tknq=n2) == prices[n1.tkn]/prices[n2.tkn]
    #AG.plot(rnone=True)
    
    AG.pricetable()
    
    pt = AG.pricetable(asdf=False)
    assert pt["labels"] == ['USDC', 'LINK', 'AAVE', 'WETH', 'BTC']
    assert len(pt["data"]) == len(pt["labels"])
    assert pt["data"][0] == [1, 0.2, 0.01, 0.0005, 0.0001]
    

# ------------------------------------------------------------
# Test      004
# File      test_004_GraphCode.py
# Segment   Arbraph connection only edges test
# ------------------------------------------------------------
def test_arbraph_connection_only_edges_test():
# ------------------------------------------------------------
    
    nodes = lambda: ag.create_node_list("ETH, USDC")
    ETH, USDC = nodes()
    
    e = e1 = ag.Edge.connection_edge(node_in=ETH, node_out=USDC, price=3000)
    e = e2 = ag.Edge.connection_edge(node_in=ETH, node_out=USDC, price=2000)
    assert e.convention() == 'USDC per ETH'
    assert e.convention_outperin() == 'USDC per ETH'
    assert e.price() == 2000
    assert e.price_outperin == 2000
    assert e.edgetype == e.EDGE_CONNECTION
    assert e.is_amounttype == False
    assert not raises(e.assert_edgetype, e.EDGE_CONNECTION)
    assert raises(e.assert_edgetype, e.EDGE_AMOUNT)
    assert e1.label == '3000.0 [None]'
    assert e2.label == '2000.0 [None]'
    assert (e1+e2).price() == 2500
    assert (e1+3*e2).price() == 2250
    assert raises(lambda: e1*0)
    assert raises(lambda: e1*(-10))
    assert raises(lambda: 0*e1)
    assert raises(lambda: -10*e1)
    
    e = e3 = ag.Edge.connection_edge(node_out=ETH, node_in=USDC, price=2000, inverse=True)
    assert e.convention() == 'USDC per ETH'
    assert e.convention_outperin() == 'ETH per USDC'
    assert e.price() == 2000
    assert e.price_outperin == 1/2000
    assert e.edgetype == e.EDGE_CONNECTION
    assert e.is_amounttype == False
    assert not raises(e.assert_edgetype, e.EDGE_CONNECTION)
    assert raises(e.assert_edgetype, e.EDGE_AMOUNT)
    assert e3.label == '0.0005 [None]'
    
    e= e4 = ag.Edge(node_in=ETH, node_out=USDC, amount_in=1, amount_out=2000, inverse=True)
    assert e.edgetype == e.EDGE_AMOUNT
    assert e.is_amounttype
    assert not raises(e.assert_edgetype, e.EDGE_AMOUNT)
    assert raises(e.assert_edgetype, e.EDGE_CONNECTION)
    e = e5 = 2*e4
    assert e.edgetype == e.EDGE_AMOUNT
    assert e.is_amounttype
    assert not raises(e.assert_edgetype, e.EDGE_AMOUNT)
    assert raises(e.assert_edgetype, e.EDGE_CONNECTION)
    e = e6 = ag.Edge(node_in=ETH, node_out=USDC, amount_in=1, amount_out=3000)
    assert e.price() == e1.price()
    assert e.price_outperin == e1.price_outperin
    assert e4.label == '1 ETH(0) --> 2000 USDC(1)'
    
    assert raises (lambda: e1+e3)
    assert raises (lambda: -2*e1)
    assert raises (lambda: e3*(-2))
    try:
        e1 += e3
        raise
    except ValueError as e:
        pass
    
    assert not raises (lambda: e4+e5)
    assert not raises (lambda: 2*e4)
    assert not raises (lambda: e4*2)
    e4 += e5
    
    assert e6.amount_in == 1
    assert e1.transport() == e6.transport()
    assert e1.transport(amount_in=1e6) == 1e6*e1.transport()
    
    AG = ag.ArbGraph(nodes = [ETH, USDC])
    assert AG.edgetype is None
    AG.add_edge_obj(e1)
    assert AG.edgetype == AG.EDGE_CONNECTION
    assert AG.edgetype == e1.EDGE_CONNECTION
    AG.add_edge_obj(e2)
    assert raises(AG.add_edge_obj, e4)
    assert AG.edgetype == e1.EDGE_CONNECTION
    
    AG = ag.ArbGraph(nodes = [ETH, USDC])
    assert AG.edgetype is None
    AG.add_edge_obj(e4)
    assert AG.edgetype == AG.EDGE_AMOUNT
    assert AG.edgetype == e1.EDGE_AMOUNT
    AG.add_edge_obj(e5)
    assert raises(AG.add_edge_obj, e1)
    assert AG.edgetype == e1.EDGE_AMOUNT
    
    AG = ag.ArbGraph()
    AG.add_edge_connectiontype(tkn_in="ETH", tkn_out="USDC", price=2000)
    AG.add_edge_connectiontype(tkn_in="ETH", tkn_out="BTC", price=1/5)
    AG.add_edge_connectiontype(tkn_in="BTC", tkn_out="USDC", price=10000)
    assert AG.edgetype == AG.EDGE_CONNECTION
    assert len(AG) == 6
    #_=AG.plot()
    
    AG = ag.ArbGraph()
    AG.add_edge_connectiontype(tkn_in="ETH", tkn_out="USDC", price=2000, symmetric=False)
    AG.add_edge_connectiontype(tkn_in="ETH", tkn_out="BTC", price=1/5, symmetric=False)
    AG.add_edge_connectiontype(tkn_in="BTC", tkn_out="USDC", price=10000, symmetric=False)
    assert AG.edgetype == AG.EDGE_CONNECTION
    assert len(AG) == 3
    #_=AG.plot()
    
    AG = ag.ArbGraph()
    assert raises (AG.add_edge_connectiontype, tkn_in="ETH", tkn_out="USDC", price=2000, price_outperin=2000)
    assert raises (AG.add_edge_connectiontype, tkn_in="ETH", tkn_out="USDC", inverse = True, price_outperin=2000)
    assert AG.add_edge_connectiontype == AG.add_edge_ct
    
    AG = ag.ArbGraph()
    for i in range(5):
        mul = 1+i/50
        AG.add_edge_ct(tkn_in="ETH", tkn_out="USDC", price=2000*mul)
        AG.add_edge_ct(tkn_in="WBTC", tkn_out="USDC", price=10000*mul)
        AG.add_edge_ct(tkn_in="ETH", tkn_out="WBTC", price=0.2/mul)
    assert AG.len() == (2*3*5, 3)
    assert len(AG.cycles()) == 5
    assert np.array_equal(AG.A.toarray(), np.array([[0, 1, 1], [1, 0, 1], [1, 1, 0]]))
    print(AG.A)
    AG2 = AG.duplicate()
    assert AG2.len() == (6,3)
    edges = AG.filter_edges("ETH", "USDC")
    assert len(edges) == 5
    edges2 = AG2.filter_edges("ETH", "USDC")
    assert len(edges2) == 1
    assert [e.p_outperin for e in edges] == [2000.0, 2040.0, 2080.0, 2120.0, 2160.0]
    assert edges2[0].p_outperin == np.mean([e.p_outperin for e in edges])
    

# ------------------------------------------------------------
# Test      004
# File      test_004_GraphCode.py
# Segment   Interaction with CPC
# ------------------------------------------------------------
def test_interaction_with_cpc():
# ------------------------------------------------------------
    
    c1  = CPC.from_univ2(x_tknb=1, y_tknq=2000, pair="ETH/USDC", fee=0, cid="1", descr="UniV2")
    c2  = CPC.from_univ2(x_tknb=1, y_tknq=10000, pair="WBTC/USDC", fee=0, cid="2", descr="UniV2")
    c3  = CPC.from_univ2(x_tknb=1, y_tknq=5, pair="WBTC/ETH", fee=0, cid="3", descr="UniV2")
    assert c1.p == 2000
    assert c2.p == 10000
    assert c3.p == 5
    
    AG = ag.ArbGraph()
    AG.add_edges_cpc(c1)
    AG.add_edges_cpc(c2)
    AG.add_edges_cpc(c3)
    #_=AG.plot()
    
    AG = ag.ArbGraph()
    AG.add_edges_cpc([c1, c2, c3])
    #_=AG.plot()
    
    AG = ag.ArbGraph()
    AG.add_edges_cpc(c for c in [c1, c2, c3])
    #_=AG.plot()
    
    AG = ag.ArbGraph()
    CC = CPCContainer([c1,c2,c3])
    AG.add_edges_cpc(CC)
    #_=AG.plot()
    
    print(AG.A)
    
    AG.cycles()
    

# ------------------------------------------------------------
# Test      004
# File      test_004_GraphCode.py
# Segment   With real data from CPC
# ------------------------------------------------------------
def test_with_real_data_from_cpc():
# ------------------------------------------------------------
    
    try:
        df = pd.read_csv("_data/NBTEST_002_Curves.csv.gz")
    except:
        df = pd.read_csv("fastlane_bot/tests/nbtest/_data/NBTEST_002_Curves.csv.gz")
    CC0 = CPCContainer.from_df(df)
    print("Num curves:", len(CC0))
    print("Num pairs:", len(CC0.pairs()))
    print("Num tokens:", len(CC0.tokens()))
    print(CC0.tokens_s())
    
    AG0 = ag.ArbGraph().add_edges_cpc(CC0)
    #AG0.plot()
    assert AG0.len() == (918, 141)
    
    assert str(AG0.A)[:60] =='  (0, 1)\t1\n  (1, 0)\t1\n  (2, 3)\t1\n  (2, 4)\t1\n  (2, 5)\t1\n  (2,'
    
    pairs = CC0.filter_pairs(bothin="WETH, USDC, UNI, AAVE, LINK")
    CC = CC0.bypairs(pairs, ascc=True)
    AG = ag.ArbGraph().add_edges_cpc(CC)
    #AG.plot()
    AG.len() == (24, 5)
    
    assert np.all(AG.A.toarray() == np.array(
          [[0, 1, 1, 0, 0],
           [1, 0, 1, 1, 1],
           [1, 1, 0, 1, 1],
           [0, 1, 1, 0, 0],
           [0, 1, 1, 0, 0]]))
    
    assert raises(AG.edge_statistics,"WETH", "USDC")
    
    AG.edgedf(consolidated=False)
    
    df = AG.edgedf(consolidated=True)
    df
    
    dx,dy = ((71.22, -0.28, 3.4, -10.82, 755278.31, -65.01, -5.93, -3.38, -0.02, 60.27, -49.45, 1507698.66, -2263343.63), 
             (-0.3, 1.99, -0.14, 0.04, -393.48, 0.27, 46.42, 0.13, 1.41, -0.2, 316.84, -786.1, 833.78))
    AG2 = ag.ArbGraph()
    for cpc, dx_, dy_ in zip(CC, dx, dy):
        print(dx_, cpc.tknx, dy_, cpc.tkny, cpc.cid)
        AG2.add_edge_dxdy(cpc.tknx, dx_, cpc.tkny, dy_, uid=cpc.cid)
        #print("---")
    
    #_=AG2.plot()
    assert AG2.len() == (12,5)
    
    assert np.all(AG2.A.toarray() == np.array(
          [[0, 1, 0, 0, 0],
           [1, 0, 0, 1, 1],
           [1, 1, 0, 1, 1],
           [0, 1, 0, 0, 0],
           [0, 1, 0, 0, 0]]))
    print(AG2.A.toarray())
    
    assert AG2.edge_statistics("WETH", "USDC", bothways=False) is None
    assert len(AG2.edge_statistics("WETH", "USDC", bothways=True)) == 2
    assert AG2.edge_statistics("WETH", "USDC", bothways=True)[1].asdict()["amounts_in_remaining"] == (755278.31, 1507698.66)
    AG2.edge_statistics("WETH", "USDC", bothways=True)[1].asdict()
    
    assert AG2.filter_edges("WETH", "USDC") == []
    assert AG2.filter_edges("WETH", "USDC", bothways=True)[0].amount_in == 755278.31
    assert AG2.filter_edges("WETH", "USDC", bothways=True) == AG2.filter_edges("USDC", "WETH")
    assert AG2.filter_edges(pair="WETH/USDC", bothways=False) == []
    assert AG2.filter_edges(pair="WETH/USDC") == AG2.filter_edges("WETH", "USDC", bothways=True)
    assert AG2.filter_edges == AG2.fe
    assert AG2.fep("WETH/USDC") == AG2.filter_edges(pair="WETH/USDC")
    assert AG2.fep("WETH/USDC", bothways=False) == AG2.filter_edges(pair="WETH/USDC", bothways=False)
    assert tuple(AG2.edgedf(consolidated=True, resetindex=False).iloc[0]) == (1.41, 0.02)
    assert len(AG2.edgedf(consolidated=False)) == len(AG2)
    
    assert len(AG2.edgedf(consolidated=False)) == 12
    AG2.edgedf(consolidated=False)
    
    assert len(AG2.edgedf(consolidated=True, resetindex=False)) == 10
    AG2.edgedf(consolidated=True, resetindex=False)
    

# ------------------------------------------------------------
# Test      004
# File      test_004_GraphCode.py
# Segment   Amount algebra
# ------------------------------------------------------------
def test_amount_algebra():
# ------------------------------------------------------------
    
    A = ag.Amount
    nodes = lambda: ag.create_node_list("ETH, USDC")
    ETH, USDC = nodes()
    
    ae1, ae2, au1 = A(1, ETH), A(2, ETH), A(1, USDC)
    
    assert ae1 + ae2 == 3*ae1
    assert ae2 - ae1 == ae1
    assert -ae1 + ae2 == ae1
    assert 2*ae1 == ae2
    assert ae1*2 == ae2
    assert ae1/2 +ae1/2 == ae1
    assert round(ae1/9,2) == round(1/9,2)*ae1
    assert round(ae1/9,4) == round(1/9,4)*ae1
    assert m.floor(ae1/9) == m.floor(1/9)*ae1
    assert m.ceil(ae1/9) == m.ceil(1/9)*ae1
    assert (ae1 + 2*ae1)/ae1 == 3
    
    assert raises (lambda: ae1 + 1)
    assert raises (lambda: ae1 - 1)
    assert raises (lambda: 1 + ae1)
    assert raises (lambda: 1 - ae1)
    
    assert 2*ae1 > ae1
    assert 2*ae1 >= ae1
    assert .2*ae1 < ae1
    assert .2*ae1 <= ae1
    assert ae1 <= ae1
    assert ae1 >= ae1
    assert not ae1 < ae1
    assert not ae1 > ae1
    

# ------------------------------------------------------------
# Test      004
# File      test_004_GraphCode.py
# Segment   Specific Arb examples
# ------------------------------------------------------------
def test_specific_arb_examples():
# ------------------------------------------------------------
    
    # ### USDC/ETH
    
    AG = ag.ArbGraph()
    AG.add_edge("ETH", 1, "USDC", 2000)
    AG.add_edge("USDC", 1800, "ETH", 1, inverse=True)
    G = AG.as_graph()
    print(AG.cycles())
    #_=AG.plot()
    
    for C in AG.cycles():
        print(f"==={C}===")
        for c in C.pairs(start_val=AG.n("ETH")): 
            print(c)
    
    c, AG.filter_edges(*c)
    
    AG.A.toarray()
    
    # ### USDC/LINK to ETH (oneway)
    
    AG = ag.ArbGraph()
    AG.add_edge("USDC", 100, "ETH", 100/2000)
    AG.add_edge("LINK", 100, "USDC", 1000)
    AG.add_edge("USDC", 900, "LINK", 100, inverse=True)
    G = AG.as_graph()
    print(AG.cycles())
    #_=AG.plot()
    
    # _=AG.duplicate().plot()
    
    for C in AG.cycles():
        print(f"==={C}===")
        for c in C.pairs(start_val=AG.n("USDC")): 
            print(c)
    
    c, AG.filter_edges(*c)
    
    AG.A.toarray()
    
    # ### USDD, LINK, ETH cycle
    
    AG = ag.ArbGraph()
    AG.add_edge("ETH", 1, "USDC", 2000)
    AG.add_edge("USDC", 1500, "LINK", 200, inverse=True)
    AG.add_edge("LINK", 200, "ETH", 1, inverse=True)
    G = AG.as_graph()
    print(AG.cycles())
    #_=AG.plot()
    
    for C in AG.cycles():
        print(f"==={C}===")
        for c in C.pairs(start_val=AG.n("USDC")): 
            print(c)
    
    c, AG.filter_edges(*c)
    
    AG.A.toarray()
    
    # ### USDD, LINK, ETH cycle plus ETH/USDC
    
    AG = ag.ArbGraph()
    AG.add_edge("ETH", 1, "USDC", 2000)
    AG.add_edge("ETH", 1, "USDC", 2000)
    AG.add_edge("USDC", 1500, "LINK", 200, inverse=True)
    AG.add_edge("LINK", 200, "ETH", 1, inverse=True)
    AG.add_edge("USDC", 1800, "ETH", 1, inverse=True)
    G = AG.as_graph()
    print(AG.cycles())
    #_=AG.plot()
    
    # +
    #_=AG.duplicate().plot()
    # -
    
    AG.edges
    
    AG.duplicate().edges
    
    AG.A.toarray()
    
    for C in AG.cycles():
        print(f"==={C}===")
        for c in C.pairs(start_val=AG.n("ETH")): 
            print(c)
    
    cycle = AG.cycles()[1]
    cycle
    
    for cycle in AG.cycles():
        result = AG.run_arbitrage_cycle(cycle=cycle, verbose=True)
        print(result)
        print("---")
    
    assert raises(AG.price, AG.nodes[0], AG.nodes[1])
    raises(AG.price, AG.nodes[0], AG.nodes[1])
    
    
    
    
    
    
    
    
    