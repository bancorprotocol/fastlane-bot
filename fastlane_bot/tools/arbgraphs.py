"""
objects for encapsulating arbitrage-related graphs

(c) Copyright Bprotocol foundation 2023. 
Licensed under MIT

NOTE: this class is not part of the API of the Carbon protocol, and you must expect breaking
changes even in minor version updates. Use at your own risk.
"""
__VERSION__ = "2.1"
__DATE__ = "16/Apr/2023"

from dataclasses import dataclass, field, asdict, astuple, InitVar
from .simplepair import SimplePair as Pair
import networkx as nx
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import math

EPS = 1e-9


class _DCBase:
    """base class for all data classes, adding some useful methods"""

    def asdict(self, *, exclude=None, include=None, dct=None):
        """
        converts this object to a dictionary

        :include:   comprehensive list of fields to include in the dataframe (default: all fields)
        :exclude:   list of fields to exclude from the dataframe (applied AFTER include)
        :dct:       dict used instead of contents of the dataclass (useful for subclasses
                    that want to add additional fields to the dict)
        """
        if dct is None:
            dct = asdict(self)
        if not include is None:
            dct = {k: dct[k] for k in include}
        if not exclude is None:
            dct = {k: dct[k] for k in dct if not k in exclude}
        return dct

    def astuple(self, **kwargs):
        """converts this object to a tuple (parameters are passed to asdict)"""
        return tuple(self.asdict(**kwargs).values())

    def asdf(self, *, index=None, **kwargs):
        """
        converts this object to a dataframe (kwargs are passed to asdict)

        :index:     the index of the dataframe (default: None)
        """
        dct = self.asdict(**kwargs)
        try:
            df = pd.DataFrame([dct])
            if not index is None:
                df.set_index(index, inplace=True)
            return df
        except Exception as e:
            return f"ERROR: {e}"

    @classmethod
    def l2df(cls, lst, **kwargs):
        """
        converts an iterable of dataclass objects to a dataframe

        :kwargs:    passed to the asdf method of each object in the list
        :returns:   a dataframe, or an error message if the conversion fails
        """
        try:
            return pd.concat([x.asdf(**kwargs) for x in lst])
        except Exception as e:
            return f"ERROR: {e}"


@dataclass
class TrackedStateFloat(_DCBase):
    """
    represents a single tracked float field in a (typical dataclass) record

    USAGE

        @ag.dataclass
        class MyState():
            myval_: ag.TrackedStateFloat = ag.field(default_factory=ag.TrackedStateFloat, init=False)
            myval: ag.InitVar=None

            def __post_init__(self, myval=0):
                self.myval = myval

            @property
            def myval(self):
                return self.myval_.value

            @myval.setter
            def myval(self, value):
                self.myval_.set(value)
        ...
        mystate = MyState(10)
        assert mystate.myval == 10
        mystate.myval_.incr(5)
        assert mystate.myval == 15
        mystate.myval_.incr(-4)
        assert mystate.myval == 11
        mystate.myval = 20
        assert mystate.myval == 20
        mystate.myval_.set(30)
        assert mystate.myval == 30
    """

    value: float = field(default=None, init=False)
    history: list = field(default_factory=list, repr=False, init=False)
    inital_value: InitVar = None

    def __post_init__(self, inital_value=None):
        if inital_value is None:
            inital_value = 0
        self.reset(inital_value, clear_history=True)

    def reset(self, value=None, clear_history=True):
        """
        sets value of the field, typically clearing history; if value is None, only clears history; returns self
        """
        if clear_history:
            self.history = []
        if not value is None:
            self.value = value
        self.history.append(self.value)
        return self

    def set(self, value):
        """
        sets value of the field, typically clearing history; if value is None, only clears history; returns self
        """
        return self.reset(value, clear_history=False)

    def __str__(self):
        return f"{self.value}"


@dataclass
class Node(_DCBase):
    """
    an arbitrage graph node, representing a token
    """

    tkn: str = field(default=None)
    ix: int = field(default=None)

    @dataclass
    class State(_DCBase):
        amount_: TrackedStateFloat = field(
            default_factory=TrackedStateFloat, init=False
        )
        amount: InitVar = None

        @property
        def amount(self):
            return self.amount_.value

        @amount.setter
        def amount(self, value):
            self.amount_.set(value)

    def __post_init__(self, amount=None):
        self.reset_state(amount)

    def reset_state(self, amount=None):
        """
        reset the state of the node
        """
        if amount is None:
            amount = 0
        self._state = self.State(amount=amount)

    @property
    def tkn_p(self):
        """
        "pretty" version of the token name (removes the index)
        """
        return self.tkn.split("(")[0]

    @property
    def state(self):
        return self._state

    def __eq__(self, other):
        return self is other

    def set_ix(self, ix):
        """
        set the index of the node
        """
        self.ix = ix

    @classmethod
    def create_node_list(cls, tkn_list):
        """
        create a list of nodes from a list or comma separated string of tokens
        """
        if isinstance(tkn_list, str):
            tkn_list = tkn_list.split(",")
            tkn_list = [s.strip() for s in tkn_list]
        return tuple(cls(tkn, ix=ix) for ix, tkn in enumerate(tkn_list))

    def __str__(self):
        return f"{self.tkn}({self.ix})"

    def __repr__(self):
        return self.__str__()


create_node_list = Node.create_node_list


@dataclass
class Amount(_DCBase):
    """
    represents an amount of a given token, the latter represented by a Node
    """

    amount: float
    node: Node

    @property
    def tkn(self):
        """
        alias for node
        """
        return self.node

    def __str__(self):
        return f"{self.amount} {self.node.tkn}"

    def __add__(self, other):
        if not isinstance(other, Amount):
            raise ValueError(f"can only add Amount to Amount")
        if self.node != other.node:
            raise ValueError(f"can only add Amounts of same node")
        return Amount(self.amount + other.amount, self.node)

    def __sub__(self, other):
        if not isinstance(other, Amount):
            raise ValueError(f"can only subtract Amount from Amount")
        if self.node != other.node:
            raise ValueError(f"can only subtract Amounts of same node")
        return Amount(self.amount - other.amount, self.node)

    def __mul__(self, other):
        if isinstance(other, Amount):
            raise ValueError(f"can only multiply Amount by scalar")
        return Amount(self.amount * other, self.node)

    def __truediv__(self, other):
        if isinstance(other, Amount):
            if self.node != other.node:
                raise ValueError(f"can only divide Amounts of same node")
            return self.amount / other.amount

        return Amount(self.amount / other, self.node)

    def __neg__(self):
        return Amount(-self.amount, self.node)

    def __pos__(self):
        return Amount(self.amount, self.node)

    def __abs__(self):
        return Amount(abs(self.amount), self.node)

    def __lt__(self, other):
        if not isinstance(other, Amount):
            raise ValueError(f"can only compare Amount to Amount")
        if self.node != other.node:
            raise ValueError(f"can only compare Amounts of same node")
        return self.amount < other.amount

    def __le__(self, other):
        if not isinstance(other, Amount):
            raise ValueError(f"can only compare Amount to Amount")
        if self.node != other.node:
            raise ValueError(f"can only compare Amounts of same node")
        return self.amount <= other.amount

    def __gt__(self, other):
        if not isinstance(other, Amount):
            raise ValueError(f"can only compare Amount to Amount")
        if self.node != other.node:
            raise ValueError(f"can only compare Amounts of same node")
        return self.amount > other.amount

    def __ge__(self, other):
        if not isinstance(other, Amount):
            raise ValueError(f"can only compare Amount to Amount")
        if self.node != other.node:
            raise ValueError(f"can only compare Amounts of same node")
        return self.amount >= other.amount

    def __copy__(self):
        return Amount(self.amount, self.node)

    def __deepcopy__(self, memo):
        return Amount(self.amount, self.node)

    def __format__(self, format_spec):
        return f"{self.amount:{format_spec}} {self.node.tkn}"

    def __round__(self, ndigits=None):
        return Amount(round(self.amount, ndigits), self.node)

    def __floor__(self):
        return Amount(math.floor(self.amount), self.node)

    def __ceil__(self):
        return Amount(math.ceil(self.amount), self.node)

    def __trunc__(self):
        return Amount(math.trunc(self.amount), self.node)

    def __radd__(self, other):
        return self + other

    def __rsub__(self, other):
        return -self + other

    def __rmul__(self, other):
        return self * other


FORMATTER = dict(
    # float=lambda x: f"{x:.4f}",
    # int=lambda x: f"{x:.0f}",
    # str=lambda x: x,
    # bool=lambda x: str(x),
    # Amount=lambda x: f"{x.amount:.4f} {x.node.tkn}",
    # Node=lambda x: f"{x.tkn}({x.ix})",
    # Edge=lambda x: f"{x.node_in.tkn}({x.node_in.ix}) -> {x.node_out.tkn}({x.node_out.ix})",
    # Path=lambda x: f"{' -> '.join([str(e) for e in x])}",
    int=lambda x: f"{x:.0f}",  # no decimals
    std=lambda x: f"{x:,.2f}",  # 2 decimals, commas
    std0=lambda x: "" if x == 0 else f"{x:,.2f}",  # ditto, and blank if 0
)


@dataclass
class Edge(_DCBase):
    """
    an arbitrage graph edge, representing a possible trade

    :node_in:       the input node, representing the token going into the AMM
    :amount_in:     the amount of the token going in (positive)
    :node_out:      the output node, representing the token coming out of the AMM
    :amount_out:    the amount of the token coming out (positive)
    :ix:            the index of the edge (in the graph)
    :inverse:       whether price quote of the edge is inverse
    :uid:           a unique identifier for the edge (optional; only use as kwarg)
    """

    node_in: Node
    amount_in: float
    node_out: Node
    amount_out: float
    ix: int = field(default=None)
    inverse: bool = field(default=False)
    uid: any = None

    def _replace_nodes(self, lookupdict):
        """
        replace nodes in edge with new nodes from lookupdict

        used by duplicate graph to relink the nodes; should not be used otherwise
        """
        self.node_in = lookupdict[self.node_in.tkn]
        self.node_out = lookupdict[self.node_out.tkn]
        return self

    EDGE_CONNECTION = "connection"
    EDGE_AMOUNT = "amount"

    @property
    def edgetype(self):
        """
        the type of edge (EDGE_CONNECTION = connection only, EDGE_AMOUNT = plus amount)
        """
        if self.amount_in < 0:
            return self.EDGE_CONNECTION
        return self.EDGE_AMOUNT

    @property
    def is_amounttype(self):
        """
        whether the edge is an amount edge
        """
        return self.edgetype == self.EDGE_AMOUNT

    def assert_edgetype(self, edgetype=EDGE_AMOUNT, msg=""):
        """
        assert that the edge is a connection edge
        """
        if not self.edgetype == edgetype:
            raise ValueError(f"Edge must be of type {edgetype} [{self.edgetype}]", msg)

    @classmethod
    def connection_edge(
        cls,
        node_in,
        node_out,
        *,
        price=None,
        inverse=False,
        weight=None,
        ix=None,
        uid=None,
    ):
        """
        alternative constructor for a connection edge (most arguments identical to main constructor)

        :price:     the price of the connection, with the quotation being determined by inverse
        :weight:    the weight of the connection; the weight is not used for capacity, but when
                    calculating the price of combined edges
        :inverse:   False: price = amount_out / amount_in, True: price = amount_in / amount_out
        """
        if price is None:
            price = 1
        if inverse:
            if price != 0:
                price = 1 / price

        if weight is None:
            weight = 1
        assert weight > 0, "weight must be positive"
        return cls(
            node_in=node_in,
            amount_in=-weight,
            node_out=node_out,
            amount_out=-price * weight,
            ix=ix,
            inverse=inverse,
            uid=uid,
        )

    @dataclass
    class State(_DCBase):
        """
        the state of an edge
        """

        amount_in_remaining: float

        @property
        def is_empty(self):
            """
            whether the edge is empty
            """
            return abs(self.amount_in_remaining) <= EPS

    def reset_state(self, amount_in_remaining=None):
        """
        reset the state of the edge
        """
        if not self.is_amounttype:
            return
        if amount_in_remaining is None:
            amount_in_remaining = self.amount_in
        self._state = self.State(amount_in_remaining=amount_in_remaining)

    @property
    def state(self):
        try:
            return self._state
        except:
            raise ValueError(
                "edge state not initialized (only available on Amount edges))"
            )

    @property
    def has_capacity(self):
        """
        whether the edge has still capacity left
        """
        return self.state.amount_in_remaining > EPS

    def __post_init__(self):
        if not isinstance(self.node_in, Node):
            raise ValueError(f"node_in must be a Node, not {self.node_in.__class__}")
        if not isinstance(self.node_out, Node):
            raise ValueError(f"node_out must be a Node, not {self.node_out.__class__}")
        self.pairo = Pair((self.node_in.tkn, self.node_out.tkn))
        self.reset_state()

    def __eq__(self, other):
        return self is other

    def __add__(self, other):
        """
        add two edges; both edges must have the same input and output nodes
        """
        if other == 0:
            return self.duplicate()  # required for sum() to work
        if not isinstance(other, self.__class__):
            raise ValueError(f"cannot add {self.__class__} and {other.__class__}")
        assert (
            self.edgetype == other.edgetype
        ), "arithmetic operations only allowed on edges of the same type"
        if not (self.node_out is other.node_out and self.node_in is other.node_in):
            raise ValueError(f"nodes do not match", self, other)
        return self.__class__(
            self.node_in,
            self.amount_in + other.amount_in,
            self.node_out,
            self.amount_out + other.amount_out,
            inverse=self.inverse,
        )

    def __radd__(self, other):
        """
        reverse add two edges; both edges must have the same input and output nodes
        """
        return self.__add__(other)

    def __mul__(self, other):
        """
        multiply an edge by a scalar
        """
        assert other > 0, f"cannot multiply edge by negative number or zero {other}"
        # self.assert_edgetype(self.EDGE_AMOUNT, "arithmetic operations only allowed on amount edges")
        if not isinstance(other, (int, float)):
            raise ValueError(f"cannot multiply {self.__class__} and {other.__class__}")
        return self.__class__(
            self.node_in,
            self.amount_in * other,
            self.node_out,
            self.amount_out * other,
            inverse=self.inverse,
        )

    def __rmul__(self, other):
        """
        reverse multiply an edge by a scalar
        """
        return self.__mul__(other)

    def duplicate(self):
        """
        duplicate an edge with all values the same except ix
        """
        return self.__class__(
            self.node_in,
            self.amount_in,
            self.node_out,
            self.amount_out,
            None,
            self.inverse,
        )

    def reverse(self):
        """
        duplicates an edge but reverses it
        """
        return self.__class__(
            self.node_out,
            self.amount_out,
            self.node_in,
            self.amount_in,
            None,
            not self.inverse,
        )

    R = reverse

    @property
    def tkn_in(self):
        """
        get the token name of the input node
        """
        return self.node_in.tkn

    @property
    def tkn_out(self):
        """
        get the token name of the output node
        """
        return self.node_out.tkn

    def pair(self, inverse=None):
        """
        get the slashpair of tokens represented by the edge

        :inverse:   if False, base token = out, quote token = in, otherwise reverse
                    default is the value of self.inverse
        """
        if inverse is None:
            inverse = self.inverse
        return (
            f"{self.tkn_in}/{self.tkn_out}"
            if not inverse
            else f"{self.tkn_out}/{self.tkn_in}"
        )

    def convention(self, inverse=None):
        """
        get the price convention of tokens represented by the edge

        :inverse:   if False, base token = out, quote token = in, otherwise reverse
                    default is the value of self.inverse
        """
        if inverse is None:
            inverse = self.inverse
        return (
            f"{self.tkn_in} per {self.tkn_out}"
            if inverse
            else f"{self.tkn_out} per {self.tkn_in}"
        )

    def convention_outperin(self):
        """
        get the price convention of tokens represented by the edge, in the convention of out per in
        """
        return self.convention(inverse=False)

    def price(self, inverse=None):
        """
        get the price of the edge, in the right convention

        :inverse:   if == False, price = amount_out / amount_in, otherwise reverse
                    default is the value of self.inverse
        """
        if inverse is None:
            inverse = self.inverse
        return (
            self.amount_in / self.amount_out
            if inverse
            else self.amount_out / self.amount_in
        )

    p = price

    @property
    def price_outperin(self):
        """
        get the price of the edge, in the convention of out per in
        """
        return self.price(inverse=False)

    p_outperin = price_outperin

    def set_ix(self, ix):
        """
        set the index of the edge
        """
        self.ix = ix

    def transport(self, amount_in=None, *, record=False, raiseonerror=True):
        """
        transport an amount of the input token through the edge, yielding output token

        :amount:            amount of input token (as float or Amount object);
                            if None: full edge capacity (or 1 if not amounttype)
        :record:            if True, record the transaction in the edge's and node's state
        :raiseonerror:      if True, raise an error if the amount is too large
        :returns:           amount of output token (as Amount object)
        """
        if record and not self.is_amounttype:
            raise ValueError(f"cannot record transaction on non-amounttype edge {self}")

        if amount_in is None:
            amount_in = self.amount_in if self.is_amounttype else 1

        if isinstance(amount_in, Amount):
            assert (
                amount_in.tkn is self.node_in
            ), f"amount token {amount_in.tkn} does not match input node {self.node_in}"
            amount_in = amount_in.amount

        if self.is_amounttype:
            # those checks only make sense for amounttype edges
            assert (
                amount_in <= self.amount_in + EPS
            ), f"amount {amount_in} exceeds edge capacity {self.amount_in}"
            assert amount_in >= -EPS, f"amount {amount_in} must be non-negative"
        amount_out = amount_in * self.amount_out / self.amount_in

        if record:
            self.state.amount_in_remaining -= amount_in
            if self.state.amount_in_remaining < -EPS:
                if raiseonerror:
                    raise ValueError(
                        f"amount {amount_in} exceeds remaining edge capacity {self.state.amount_in_remaining}"
                    )
            self.node_out.state.amount += amount_out
            self.node_in.state.amount -= amount_in
            if self.node_in.state.amount < -EPS:
                if raiseonerror:
                    raise ValueError(
                        f"amount {amount_in} exceeds node capacity {self.node_in.state.amount}"
                    )
        return Amount(amount_out, self.node_out)

    def __str__(self):
        arrow = "-->" if self.ix is None else f"--({self.ix})->"
        return (
            f"{self.amount_in} {self.node_in} {arrow} {self.amount_out} {self.node_out}"
        )

    @property
    def label(self):
        if self.is_amounttype:
            return (
                f"{self.amount_in} {self.node_in} --> {self.amount_out} {self.node_out}"
            )
        else:
            return f"{self.price_outperin} [{self.ix}]"


@dataclass
class Path(_DCBase):
    """
    a path of nodes that can be iterated over (use Cycles for closed paths)

    :data:   list of nodes; the nodes can be any type that allows for equality comparison
    :uid:    an optional unique identifier for the path
    """

    data: list
    uid: any = None
    graph: any = field(default=None, repr=False, compare=False)

    def __post_init__(self):
        if not self.graph is None:
            assert isinstance(
                self.graph, ArbGraph
            ), f"graph must be an ArbGraph, not {type(self.graph)}"

    def __str__(self):
        try:
            return f"path [{self.uid}]: " + "->".join([f"{d.tkn}" for d in self.data])
        except:
            return f"path [{self.uid}]: " + "->".join([f" {d} " for d in self.data])

    def items(self):
        """
        iterate over the cycle
        """
        return iter(self.data)

    def pairs(self):
        """
        iterate over the cycle, yielding pairs of adjacent items
        """
        items1 = self.items()
        items2 = self.items()
        next(items2)
        return zip(items1, items2)

    def pairs_s(self):
        """
        runs pairs and returns the results as slashpairs
        """
        return [f"{p[0].tkn}/{p[1].tkn}" for p in self.pairs()]


@dataclass
class Cycle(_DCBase):
    """
    a cycle of nodes, allowing arbitrary entry point for iteration

    :data:   list of nodes; the nodes can be any type that allows for equality comparison
    :uid:    an optional unique identifier for the cycle

    USAGE

        C = Cycle([1,2,3,4,5])
        for c in C.items(start_ix=2):
            print(c)
        # prints 3, 4, 5, 1, 2, 3
    """

    data: list
    uid: any = None
    graph: any = field(default=None, repr=False, compare=False)

    def __post_init__(self):
        if not self.graph is None:
            assert isinstance(
                self.graph, ArbGraph
            ), f"graph must be an ArbGraph, not {type(self.graph)}"

    def __str__(self):
        try:
            return (
                f"cycle [{self.uid}]: "
                + "->".join([f"{d.tkn}" for d in self.data])
                + "->..."
            )
        except:
            return (
                f"cycle [{self.uid}]: "
                + "->".join([f" {d} " for d in self.data])
                + "->..."
            )

    class CycleIterator:
        def __init__(self, cycle, start_ix=0):
            self.cycle = cycle
            self.start_ix = start_ix
            self.ix = start_ix - 1
            self._len = len(cycle)
            self._counter = self._len + 2

        def __iter__(self):
            return self

        def __next__(self):
            self._counter -= 1
            if self._counter == 0:
                raise StopIteration
            self.ix = (self.ix + 1) % self._len
            return self.cycle[self.ix]

    def __len__(self):
        return len(self.data)

    @classmethod
    def byid(cls, cycle_list, uid):
        """
        return the cycle in cycle_list with uid
        """
        for c in cycle_list:
            if c.uid == uid:
                return c
        return None

    def is_subcycle_of(self, other):
        """
        returns True iff self is a subcycle of other
        """
        if len(self) > len(other):
            return False
        try:
            supercycle = other.items(start_val=self.data[0])
        except:
            return False

        subcycle = self.items()
        for subc in subcycle:
            while True:
                try:
                    superc = next(supercycle)
                except StopIteration:
                    return False
                if superc == subc:
                    break
        return True

    def filter_subcycles(self, cycle_list):
        """
        filter out subcycles of self from cycle_list
        """
        if isinstance(cycle_list, Cycle):
            cycle_list = [cycle_list]
        return tuple(c for c in cycle_list if c.is_subcycle_of(self))

    def items(self, start_ix=None, start_val=None):
        """
        iterate over the cycle

        :start_ix:  start index*
        :start_val: start value*

        * only one of start_ix and start_val can be specified
        """
        if not start_val is None:
            if not start_ix is None:
                raise ValueError(
                    "only one of start_ix and start_val can be specified",
                    start_ix,
                    start_val,
                )
            start_ix = self.data.index(start_val)
        if start_ix is None:
            start_ix = 0
        return self.CycleIterator(self.data, start_ix)

    def pairs(self, start_ix=None, start_val=None):
        """
        iterate over the cycle, yielding pairs of adjacent items

        :start_ix:  start index*
        :start_val: start value*

        * only one of start_ix and start_val can be specified
        """
        items1 = self.items(start_ix=start_ix, start_val=start_val)
        items2 = self.items(start_ix=start_ix, start_val=start_val)
        next(items2)
        return zip(items1, items2)

    def pairs_s(self, start_ix=None, start_val=None):
        """
        runs pairs and returns the results as slashpairs
        """
        return [f"{p[0].tkn}/{p[1].tkn}" for p in self.pairs()]

    def run_arbitrage_cycle(self, token=None, **params):
        """
        convenience method to call run_arbitrage_cycle on self.graph

        see help(ArbGraph.run_arbitrage_cycle) for details
        """
        assert not self.graph is None, "graph must be set to run a cycle"
        return self.graph.run_arbitrage_cycle(self, token=token, **params)

    run = run_arbitrage_cycle


@dataclass
class ArbGraph(_DCBase):
    """
    a container object for Nodes and Edges, representing a graph
    """

    __VERSION__ = __VERSION__
    __DATE__ = __DATE__

    nodes: list = field(default_factory=list)
    edges: list = field(default_factory=list)

    def __post_init__(self):
        """
        post-initialization
        """
        for ix, node in enumerate(self.nodes):
            node.set_ix(ix)
        self._node_by_tkn = {node.tkn: node for node in self.nodes}

        for ix, edge in enumerate(self.edges):
            edge.set_ix(ix)

        edgetype = set(e.edgetype for e in self.edges)
        if len(edgetype) > 1:
            raise ValueError("Edges must all be of the same type")

    @classmethod
    def from_ccdxdy(cls, cc, dxv, dyv, *, ignorezero=True, verbose=False):
        """
        alternative constructor: from curves and trade vectors dxv, dyv

        :cc:    a CurveContainer object
        :dxv:   a vector of trade amounts in x (eg dx.values after an optimisation)
        :dyv:   ditto but for y amounts
        """
        AG = cls()
        for cpc, dx, dy in zip(cc, dxv, dyv):
            if verbose:
                print("[from_ccdxdy]", dx, cpc.tknx, dy, cpc.tkny, cpc.cid)
            if ignorezero and dx == 0 and dy == 0:
                continue
            AG.add_edge_dxdy(cpc.tknx, dx, cpc.tkny, dy, uid=cpc.cid)
        return AG

    @classmethod
    def from_r(cls, r, *, ignorezero=True, verbose=False):
        """
        alternative constructor: from an Optimizer result object

        :r:     Optimizer result object
        """
        return cls.from_ccdxdy(
            r.curves, r.dxvalues, r.dyvalues, ignorezero=ignorezero, verbose=False
        )

    @classmethod
    def from_cc(cls, cc):
        """
        alternative constructor: from a CurveContainer object alone

        :cc:    a CurveContainer object
        """
        AG = cls()
        return AG.add_edges_cpc(cc)

    def __len__(self):
        return len(self.edges)

    def len(self):
        """returns a tuple with number of edges and nodes (nedges, nnodes)"""
        return (len(self.edges), len(self.nodes))

    @property
    def _(self):
        """returns None (to stop chaining and to clean Jupyter output)"""
        return None

    EDGE_CONNECTION = Edge.EDGE_CONNECTION
    EDGE_AMOUNT = Edge.EDGE_AMOUNT

    @property
    def edgetype(self):
        """edgetype of the graph (all edges are of the same type; None if no edges)"""
        if len(self.edges) == 0:
            return None
        return self.edges[0].edgetype

    @property
    def is_amounttype(self):
        """True if the graph is an amount-type graph"""
        return self.edgetype == self.EDGE_AMOUNT

    def duplicate(self, consolidate=True):
        """
        creates a duplicate of the current object, duplicating all nodes and edges

        :consolidate:   if True, multiple edges between the same nodes are
                        consolidated into a single edge

        Note: there is an issue with this consolidation process in that when routing through
        edges, people would go lowest price first, not pro rata. This however is a problem
        that cannot really be solved here unless we expand the data structure of the edges
        at which stage we might as well just not consolidate them in the first place.
        """
        nodes = {node.tkn: Node(node.tkn) for node in self.nodes}
        if not consolidate:
            edges = (
                Edge(
                    edge.node_in,
                    edge.amount_in,
                    edge.node_out,
                    edge.amount_out,
                    edge.inverse,
                    uid=edge.uid,
                )
                for edge in self.edges
            )
        else:
            edges = (
                self.filter_edges(nin, nout)
                for nin in self.nodes
                for nout in self.nodes
                if nin != nout
            )
            edges = (sum(r) for r in edges)
            edges = (r for r in edges if not r == 0)

        edges = (r._replace_nodes(nodes) for r in edges)
        edges = tuple(edges)
        return self.__class__(nodes=nodes.values(), edges=edges)

    def reset_state(self):
        """
        resets the state of all nodes and edges in the graph (returns self)
        """
        for node in self.nodes:
            node.reset_state()
        for edge in self.edges:
            edge.reset_state()
        return self

    def has_capacity(self, tkn_in=None, tkn_out=None):
        """
        returns True iff any of the edges still have a capacity

        :tkn_in, tkn_out:    can be str, Node, or None; if None, None, all edges
        """
        node_in = self.node_by_tkn(tkn_in)
        node_out = self.node_by_tkn(tkn_out)
        edges = self.filter_edges(node_in, node_out)
        return any(edge.has_capacity for edge in edges)

    @dataclass
    class State(_DCBase):
        nodes: tuple
        edges: tuple

    @property
    def state(self):
        """
        returns State object consolidating the state objects of nodes and edges
        """
        return self.State(
            nodes=tuple(node.state for node in self.nodes),
            edges=tuple(edge.state for edge in self.edges),
        )

    def add_node_obj(self, node):
        """
        add a node object (of type Node) to the graph; returns self
        """
        node.set_ix(len(self.nodes))
        self.nodes.append(node)
        self._node_by_tkn[node.tkn] = node
        return self

    def add_node(self, tkn):
        """
        add a node to the graph, returns self
        """
        node = Node(tkn)
        self.add_node_obj(node)
        return self

    def add_edge_obj(self, edge):
        """
        add an edge object (of type Edge) to the graph; returns self
        """
        if edge.edgetype != self.edgetype and not self.edgetype is None:
            raise ValueError(
                "edge type does not match graph type", edge.edgetype, self.edgetype
            )
        edge.set_ix(len(self.edges))
        self.edges.append(edge)
        return self

    def add_edge(
        self, tkn_in, amount_in, tkn_out, amount_out, *, inverse=False, uid=None
    ):
        """
        add an amount-type* edge to the graph

        :tkn_in:        token name of the input node (as str)
        :amount_in:     amount of input token (as float)
        :tkn_out:       token name of the output node (as str)
        :amount_out:    amount of output token (as float)
        :inverse:       if True, use reverse quote convention
        :uid:           unique id of the edge

        *amount-type edges are edges that have a specific amount of input and output tokens,
        ie they correspond to a price AND a volume; connection type edges only have a price
        """
        assert amount_in > 0, f"amount_in must be positive {amount_in}"
        assert amount_out > 0, f"amount_out must be positive {amount_out}"
        edge = Edge(
            self.node_by_tkn(tkn_in, create=True),
            amount_in,
            self.node_by_tkn(tkn_out, create=True),
            amount_out,
            inverse=inverse,
            uid=uid,
        )
        self.add_edge_obj(edge)
        return self

    EPSDXDY = 1e-8

    def add_edge_dxdy(self, tknx, dx, tkny, dy, *, inverse=False, uid=None):
        """
        like add_edge, but in and out is determined by the sign of the amounts

        :tknx:      token name of the input node (as str)
        :dx:        amount of input token (as float; in=pos, out=neg)
        :tkny:      token name of the output node (as str)
        :dy:        amount of output token (as float; in=pos, out=neg)
        :inverse:   if True, use reverse quote convention
        :uid:       unique id of the edge
        """
        if not dx * dy < 0:

            msg = f"dx and dy must have opposite signs [dx={dx} dy={dy} dx*dy={dx*dy}]"
            if dx * dy > self.EPSDXDY:
                raise ValueError(msg)
            else:
                print(f"{msg}; not added (EPS={self.EPSDXDY}))")
                return self

        if dx > 0:
            amount_in = dx
            tkn_in = tknx
            amount_out = -dy
            tkn_out = tkny
        else:
            amount_in = dy
            tkn_in = tkny
            amount_out = -dx
            tkn_out = tknx
        # print("add_edge_dxdy in/out dx", amount_in, tkn_in, amount_out, tkn_out, dx)
        self.add_edge(tkn_in, amount_in, tkn_out, amount_out, inverse=inverse, uid=uid)
        return self

    def add_edge_connectiontype(
        self,
        tkn_in,
        tkn_out,
        *,
        price=None,
        inverse=False,
        price_outperin=None,
        weight=None,
        symmetric=True,
        uid=None,
    ):
        """
        add a connection-type* edge to the graph

        :tkn_in:            token name of the input node (as str)
        :tkn_out:           token name of the output node (as str)
        :price:             price of the connection (as float), according to convention
        :inverse:           if True, use reverse quote convention
        :price_outperin:    price in outperin convention (alternative to price)
        :weight:            weight of the connection (as float; default is 1)**
        :symmetric:         if True, add the inverse edge as well
        :uid:               unique id of the edge
        :returns:           self

        **amount-type edges are edges that have a specific amount of input and output tokens,
        ie they correspond to a price AND a volume; connection type edges only have a price

        **the weight of the connection is mostly useful to determine the prices of combined
        edges; essentially, the price of the combined edge is the weighted average of the
        prices of the individual edges
        """
        if price_outperin is not None:
            assert price is None, "cannot specify both price and price_outperin"
            assert (
                not inverse
            ), "inverse must be False (=default) if price_outperin is specified"
            price = price_outperin
        elif price is None:
            price = 1

        if weight is None:
            weight = 1
        assert weight > 0, "weight must be positive {weight}"

        edge = Edge.connection_edge(
            node_in=self.node_by_tkn(tkn_in, create=True),
            node_out=self.node_by_tkn(tkn_out, create=True),
            price=price,
            weight=weight,
            inverse=inverse,
            uid=f"{uid}",
        )
        self.add_edge_obj(edge)
        if not symmetric:
            return self
        edge = Edge.connection_edge(
            node_out=self.node_by_tkn(tkn_in, create=True),
            node_in=self.node_by_tkn(tkn_out, create=True),
            price=price,
            weight=weight,
            inverse=not inverse,
            uid=f"{uid}-r",
        )
        self.add_edge_obj(edge)
        return self

    add_edge_ct = add_edge_connectiontype

    def add_edges_cpc(self, curves, uid=None):
        """
        add an edge from a CPC curve object

        :curves:    specifies one or multiple curves, depending on the type:
                    :CPC:           a single curve of type ConstantProductCurve is added*
                    :iterable:      multiple curves of type CPC are added*
                    :CPCContainer:  all curves in the container are added*
        :uid:       unique id of the edge; should only be provided for singles curves

        *specifically the way the algo works AT THEM MOMENT (but don't rely on this),
        if the object has a curves method, it is assumed to be an iterable of CPCs;
        if the object is iterable, it is assumed to be an iterable of CPCs; otherwise
        it is assumbed to be a single CPC
        """
        try:
            try:
                # print("TRYING CONTAINER")
                self.add_edges_cpc(curves=curves.curves, uid=uid)
                return self
            except AttributeError as e:
                if not str(e).endswith("has no attribute 'curves'"):
                    raise e
                # print(f"CONTAINER FAILED {e}")

            # print("TRYING ITERABLE")
            for c in curves:
                # print("ITERABLE LOOP cid=", c.cid)
                self.add_edges_cpc(curves=c, uid=uid)
            # print("ITERABLE DONE")
            return self
        except TypeError as e:
            # print(f"ITERABLE FAILED {e}")
            if not str(e).endswith("object is not iterable"):
                raise e
            curve = curves
        self.add_edge_connectiontype(
            tkn_in=curve.tknb,
            tkn_out=curve.tknq,
            price_outperin=curve.p,
            symmetric=True,
            uid=uid if not uid is None else curve.cid,
        )
        return self

    def node_by_tkn(self, tkn, create=False):
        """
        get a node by its token name

        :tkn:       token name (as str) or a Node object (if None returns None)
        :create:    if True, create a new node if it doesn't exist
        """
        if tkn is None:
            return None
        if isinstance(tkn, Node):
            node = self.node_by_tkn(tkn.tkn, create=False)
            assert (
                tkn is node
            ), f"the tkn provided {tkn} does not match the node found {node}"
            return node
        try:
            return self._node_by_tkn[tkn]
        except KeyError:
            if create:
                self.add_node(tkn)
                return self._node_by_tkn[tkn]
            else:
                raise KeyError(f"node with token name {tkn} not found")

    n = node_by_tkn

    def node_by_ix(self, ix):
        """
        get a node by its index
        """
        return self.nodes[ix]

    node = node_by_ix

    def edge_by_ix(self, ix):
        """
        get an edge by its index
        """
        return self.edges[ix]

    edge = edge_by_ix

    def filter_edges(
        self, node_in=None, node_out=None, *, node=None, bothways=None, pair=None
    ):
        """
        gets a list of edges filtered by node_in and node_out

        :node_in:   input node (as Node object or str)
        :node_out:  output node (as Node object or str)
        :node:      input or output node (as Node object or str)
        :bothways:  if True, also include edges with node_in and node_out swapped
                    defaults to False if no pair is given, True otherwise
        :pair:      if True, use pair instead of the nodes
        """
        if not pair is None:
            assert (
                node_in is None and node_out is None
            ), "cannot specify both pair and node_in or node_out"
            assert node is None, "cannot specify both pair and node"
            node_in, node_out = pair.split("/")
        if bothways is None:
            bothways = False if pair is None else True
        if bothways:
            l1 = self.filter_edges(
                node_in=node_in, node_out=node_out, node=node, bothways=False
            )
            l2 = self.filter_edges(
                node_in=node_out, node_out=node_in, node=node, bothways=False
            )
            return l1 + l2
        if isinstance(node_in, str):
            node_in = self.node_by_tkn(node_in)
        if isinstance(node_out, str):
            node_out = self.node_by_tkn(node_out)
        if isinstance(node, str):
            node = self.node_by_tkn(node)
        if node is not None:
            assert (
                node_in is None and node_out is None
            ), "cannot specify both node and node_in or node_out"
        assert node_in is None or isinstance(
            node_in, Node
        ), f"node_in must be a Node object or None, not {node_in}"
        assert node_out is None or isinstance(
            node_out, Node
        ), f"node_out must be a Node object or None, not {node_out}"
        assert node is None or isinstance(
            node, Node
        ), f"node must be a Node object or None, not {node}"
        if not node is None:
            return [
                edge
                for edge in self.edges
                if edge.node_in == node or edge.node_out == node
            ]
        elif node_in is None and node_out is None:
            return self.edges
        elif node_in is None:
            return [edge for edge in self.edges if edge.node_out == node_out]
        elif node_out is None:
            return [edge for edge in self.edges if edge.node_in == node_in]
        else:
            return [
                edge
                for edge in self.edges
                if edge.node_in == node_in and edge.node_out == node_out
            ]

    fe = filter_edges

    def fep(self, pair, bothways=None):
        """alias for filter_edges(pair=pair, bothways=bothways)"""
        return self.filter_edges(pair=pair, bothways=bothways)

    def as_graph(self, *, directed=True, weighted=False):
        """
        convert the graph to a networkx graph

        :directed:  if True, return a directed graph, otherwise undirected
        :weighted:  if True, return a weighted graph, otherwise unweighted
        """
        assert weighted == False, "weighted graphs not yet implemented"

        if directed:
            G = nx.DiGraph()
        else:
            G = nx.Graph()
        for node in self.nodes:
            G.add_node(node.ix, label=str(node), tkn=node.tkn)
        for edge in self.edges:
            if weighted:
                # print("adding weighted edge", edge.node_in.ix, edge.node_out.ix, edge.price())
                G.add_edge(
                    edge.node_in.ix, edge.node_out.ix, weight="bla", label=str(edge)
                )
            else:
                # print("adding edge", edge.node_in.ix, edge.node_out.ix)
                G.add_edge(edge.node_in.ix, edge.node_out.ix, label=edge.label)
        return G

    @property
    def G(self):
        """alias for as_graph(directed=True, weighted=False)"""
        return self.as_graph(directed=True, weighted=False)

    def Laplacian(self, directed=False, weighted=False, include_eigenvalues=True):
        """
        computes the graph Laplacian (and its eigenvalues if requested)

        :returns:   the graph Laplacian L, or tuple (L, eigenvalues)*

        *L is a scipy sparse matrix; use toarray() to expand to a numpy array
        """
        G = self.as_graph(directed=directed, weighted=weighted)
        L = nx.laplacian_matrix(G)
        if not include_eigenvalues:
            return L
        eigenvalues = np.linalg.eigvals(L.toarray())
        return L, eigenvalues

    @property
    def L(self):
        """alias for Laplacian(directed=False, weighted=False, include_eigenvalues=False)"""
        return self.Laplacian(directed=False, weighted=False, include_eigenvalues=False)

    def Adjacency(self, *, directed=True, weighted=False, include_eigenvalues=True):
        """
        computes the graph adjacency matrix (and its eigenvalues if requested)

        :returns:   the graph adjacency matrix A, or tuple (A, eigenvalues)*

        *A is a scipy sparse matrix; use toarray() to expand to a numpy array
        """
        G = self.as_graph(directed=directed, weighted=weighted)
        A = nx.adjacency_matrix(G)
        if not include_eigenvalues:
            return A
        eigenvalues = np.linalg.eigvals(A.toarray())
        return A, eigenvalues

    @property
    def A(self):
        """alias for Adjacency(directed=True, weighted=False, include_eigenvalues=False)"""
        return self.Adjacency(directed=True, weighted=False, include_eigenvalues=False)

    def shortest_path(self, node_start, node_end):
        """
        get the shortest path between two nodes
        """
        G = self.as_graph(directed=True, weighted=False)
        path = nx.shortest_path(G, node_start.ix, node_end.ix)
        path = tuple(map(self.node_by_ix, path))
        path = Path(path)
        return path

    def price(self, node_tknb, node_tknq, *, with_units=False):
        """
        get the price (estimate) expressed in units of end per start [only on connection-type graphs]
        """
        assert not self.is_amounttype, "cannot get price on amount-type graphs"
        if node_tknb != node_tknq:
            node_tknb = self.node_by_tkn(node_tknb)
            node_tknq = self.node_by_tkn(node_tknq)
            price = self.ptransport(self.shortest_path(node_tknb, node_tknq)).multiplier
        else:
            price = 1
        if with_units:
            return (
                price,
                f"{node_tknq.tkn} per {node_tknb.tkn} [{node_tknb.tkn}/{node_tknq.tkn}]",
            )
        return price

    def pricetable(self, include=None, *, exclude=None, asdf=True):
        """
        calculates a price table for all pairs of nodes in the graph*

        :include:     nodes to include (default: all nodes)
        :exclude:     nodes to exclude (default: none); exclude beats include
        :returns:     a dict or pandas dataframe

        Note: this price table is calculated using the shortest paths in the graph;
        if the graph is not arbitrage free then those prices will not be self consistent
        this is a feature, not a bug, as this table allows to estimate the extent to
        which this graph is arbitrage free
        """
        if include is None:
            include = self.nodes
        # include = set(include)
        if not exclude is None:
            include = [n for n in include if not n in exclude]
            # TODO: those should really be sets, but for some reason
            # nodes are an unhashable type

        labels = [n.tkn for n in include]
        data = [[self.price(nj, ni) for ni in include] for nj in include]
        if asdf:
            df = pd.DataFrame(data, columns=labels, index=labels)
            df.index.name = "tknb"
            return df
        return dict(data=data, labels=labels)

    def cycles(self, *, asgenerator=False):
        """
        get all cycles in the graph
        """
        G = self.as_graph(directed=True, weighted=False)
        cycles = nx.simple_cycles(G)
        cycles = (list(map(self.node_by_ix, cycle)) for cycle in cycles)
        cycles = (Cycle(cycle, graph=self, uid=uid) for uid, cycle in enumerate(cycles))
        if asgenerator:
            return cycles
        return tuple(cycles)

    @property
    def is_weakly_connected(self):
        """
        check if the graph is weakly connected

        Note: if the graph is weakly connected, then all the cycles in the graph are subcycles
        of a single cycle*. This is important because this means that that they can be more
        easily aligned, which means that we can combined transactions of multiple cycles
        into a single transaction.

        *According to ChatGPT...
        """
        G = self.as_graph(directed=True, weighted=False)
        return nx.is_weakly_connected(G)

    DEGREE = None
    INDEGREE = "INDEGREE"
    OUTDEGREE = "OUTDEGREE"

    def degree(self, inout=DEGREE, as_matrix=False):
        """
        get the degree of the nodes in the graph, possibly as a matrix

        :inout:     None (= symmetric degree), or self.INDEGREE, self.OUTDEGREE
        """
        if inout is self.DEGREE:
            # degree = nx.degree(self.as_graph(directed=False))
            degree = self.as_graph(directed=False).degree()
        elif inout is self.INDEGREE:
            degree = self.as_graph(directed=True).in_degree()
        elif inout is self.OUTDEGREE:
            degree = self.as_graph(directed=True).out_degree()
        else:
            raise ValueError(f"invalid value for inout: {inout}")

        degree = dict(degree)
        if not as_matrix:
            return degree
        matrix = np.diag([degree.get(node, 0) for node in G.nodes()])
        return matrix

    def in_degree(self, as_matrix=False):
        """
        convenience function for self.degree(inout=self.INDEGREE)
        """
        return self.degree(inout=self.INDEGREE, as_matrix=as_matrix)

    def out_degree(self, as_matrix=False):
        """
        convenience function for self.degree(inout=self.OUTDEGREE)
        """
        return self.degree(inout=self.OUTDEGREE, as_matrix=as_matrix)

    PLOT_DEFAULTS = {
        "directed": True,
        "labels": True,
        "edge_labels": False,
        "node_color": "lightblue",
        "show": True,
    }

    def plot(self, **params):
        """
        plot the graph

        :directed:      if True (default), plot a directed graph, otherwise undirected
        :labels:        if True (default), plot node labels
        :edge_labels:   if True (default), plot edge labels
        :node_color:    color of the nodes (default: "lightblue")
        :show:          if True (default), show the plot
        :rnone:         if True, returns None, otherwise returns self
        """

        p = lambda name: params.get(name, self.PLOT_DEFAULTS.get(name))

        G = self.as_graph(directed=p("directed"))

        pos = nx.kamada_kawai_layout(G)
        # pos = nx.spring_layout(G) # works only in 2.6.3+
        nx.draw(
            G,
            pos,
            with_labels=p("labels"),
            labels=nx.get_node_attributes(G, "label"),
            node_color=p("node_color"),
        )

        if p("edge_labels"):
            edge_labels = nx.get_edge_attributes(G, "label")
            nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels)

        if p("show"):
            plt.show()
        if p("rnone"):
            return None
        return self

    RUNARBCYCLE_DEFAULTS = {
        "verbose": False,
        "allow_any_token": True,
    }

    @dataclass
    class RunArbCycleResult(_DCBase):
        cycle: Cycle = None
        start_ix: int = None
        token: str = None
        profit: float = None
        amount_in: float = None
        amount_out: float = None

        def __str__(self):
            return f"RACResult(profit: {self.profit:2.1f} [{self.token}], in: {self.amount_in:2.1f}, rpcs: {self.ppcs*100:.1f}%, ppcs: {self.ppcs:.1f}, len: {self.length},  uid: {self.cycle.uid})"

        def asdict(self, *, include_cycle=True, exclude=None, include=None):
            dct = {
                **asdict(self),
                "tokens": self.tokens(),
                "length": self.length,
                "r": self.r,
                "rpcs": self.rpcs,
                "ppcs": self.ppcs,
                "uid": self.cycle.uid,
            }
            if not include_cycle:
                del dct["cycle"]
            return super().asdict(dct=dct, exclude=exclude, include=include)

        def astuple(self, include_cycle=True):
            return tuple(self.asdict(include_cycle).values())

        def tokens(self):
            return ", ".join(str(t.tkn) for t in self.cycle.data)

        @property
        def length(self):
            return len(self.cycle)

        @property
        def r(self):
            """percentage overall return (out/in - 1)"""
            return self.amount_out / self.amount_in - 1

        @property
        def rpcs(self):
            """percentage return per cycle step (r/length)"""
            return self.r / self.length

        @property
        def ppcs(self):
            """profit per cycle step (in token units)"""
            return self.profit / self.length

    def run_arbitrage_cycle(self, cycle, token=None, **params):
        """
        takes a cycles and runs the arbitrage inherent in it

        :cycle:     a Cycle object as returned by the cycles() method
        :token:     the token around which the cycle is run (default: the first token in the cycle)
        :params:    additional parameters (see below)
                    :verbose:           if True, print some information when running the cycle
                    :allow_any_token:   if True, allow any token to be used as the token around which the cycle is run
        :returns:   a RunArbCycleResult object with the following properties:
                    :cycle:             cycle that was run
                    :start_ix:          index of the token around which the cycle was run
                    :token:             token around which the cycle was run
                    :profit:            profit made in the cycle (in token units)
                    :amount_in:         amount of token that was put into the cycle (in token units)
                    :amount_out:        amount of token that was taken out of the cycle (in token units)
                    :length:            length of the cycle
                    :r:                 percent overall return of the cycle (out/in - 1)
                    :rpcs:              return per cycle step (r/length)
                    :ppcs:              profit per cycle step (in token units)
        """
        P = lambda name: params.get(name, self.RUNARBCYCLE_DEFAULTS.get(name))

        current_multiplier = (
            1.0  # tracks how much of the initial amount can be pushed through the cycle
        )
        current_amount_in = (
            None  # tracks the amount currently being pushed (None: to be initialised)
        )

        # try to set the cycle to the token we want to use (if any)
        if not token is None:
            try:
                cycle_pairs = cycle.pairs(start_val=self.node_by_tkn(token))
            except:
                if P("allow_any_token"):
                    cycle_pairs = cycle.pairs()
                    if P("verbose"):
                        print(
                            f"token {token} not found in cycle {cycle}; first token of cycle used instead"
                        )
                else:
                    raise ValueError(
                        f"token {token} does not exist, or not found in cycle {cycle}"
                    )
        else:
            cycle_pairs = cycle.pairs()

        # iterate over all edges in the cycle
        for pair in cycle_pairs:

            # get all edges between the nodes of the cycle (e is eg for tokens)
            edges = self.filter_edges(*pair)
            e = edges[0]

            # get amounts in and out per edge, and sum them up
            capacities_in = [e.amount_in for e in edges]
            capacity_in = sum(capacities_in)
            capacities_out = [e.amount_out for e in edges]
            capacity_out = sum(capacities_out)

            # initialize current amount? Yes -> set to capacity_in
            if current_amount_in is None:
                current_amount_in = capacity_in
                current_amounts_in = capacities_in
                initial_amount_in = (
                    capacity_in  # we remember how much we had at the beginning...
                )
                initial_tkn_in = e.tkn_in  # ...and in which token we had it

            else:
                # current_amount_out was set in the previous edge; first we set in to previous out
                current_amount_in = current_amount_out

                # is the capacity of the route less than what we want to push through?
                if capacity_in < current_amount_in:
                    # print("capacity_in < current_amount_in: reducing push amount", capacity_in, current_amount_in)

                    # yes -> keep note of this in the multiplier, and used 100% of the capacity
                    current_multiplier *= capacity_in / current_amount_in
                    current_amounts_in = capacities_in
                    current_amount_in = capacity_in

                else:
                    # print("capacity_in >= current_amount_in: pushing everything", capacity_in, current_amount_in)

                    # no -> scale down the amounts to be pushed through this route
                    fctr = current_amount_in / capacity_in
                    current_amounts_in = [amt_in * fctr for amt_in in capacities_in]

            # push the amount through the edges
            current_amounts_out = [
                ee.transport(amt_in).amount
                for ee, amt_in in zip(edges, current_amounts_in)
            ]
            current_amount_out = sum(current_amounts_out)

            # print diagnostics
            if P("verbose"):
                s1 = f"{pair}: {len(edges)} edges, capacity {capacity_in} {e.tkn_in} -> {capacity_out} {e.tkn_out}"
                s2 = f"actual {current_amount_in} -> {current_amount_out} [{current_multiplier}x]"
                print(f"{s1}, {s2}")

        effective_amount_in = current_multiplier * initial_amount_in
        profit_amount = current_amount_out - effective_amount_in
        assert (
            initial_tkn_in == e.tkn_out
        ), f"In and out tokens do not match!! {initial_tkn_in}, {e.tkn_out}"

        if P("verbose"):
            inout_str = f"in: {effective_amount_in}; out: {current_amount_out}"
            profits_str = f"Profit: {profit_amount}"
            print(f"{profits_str} {e.tkn_out} [{inout_str}]")

        result = self.RunArbCycleResult(
            cycle=cycle,
            start_ix=0,
            token=e.tkn_out,
            profit=profit_amount,
            amount_in=effective_amount_in,
            amount_out=current_amount_out,
        )
        return result

    ACRET_GEN = "gen"
    ACRET_TUPLE = "tuple"
    ACRET_RAW = ACRET_TUPLE
    ACRET_DICTS = "dicts"
    ACRET_DF = "df"
    ACRET_AGGRDF = "aggrdf"
    ACRET_PRETTYADF = "prettyadf"

    def run_arbitrage_cycles(self, cycles, token=None, format=None, **params):
        """
        takes a list of cycles and runs run_arbitrage_cycle on each of them

        :cycles:    a list of Cycle objects, eg as returned by the cycles() method
        :token:     either a single token for all cycles, or a list of tokens, one for each cycle
        :params:    additional parameters that are being passed to run_arbitrage_cycle
        :returns:   depends on the `format` parameter which is one of ACRET_GEN, ACRET_TUPLE,
                    ACRET_DICTS, ACRET_DF or ACREF_PRETTYDF
        """
        if format is None:
            format = self.ACRET_TUPLE
        arbcycles = (
            self.run_arbitrage_cycle(cycle, token=token, **params) for cycle in cycles
        )
        if format == self.ACRET_GEN:
            return arbcycles
        if format == self.ACRET_TUPLE:
            return tuple(arbcycles)
        return self.run_arbitrage_cyclesf(arbcycles, format=format)

    def run_arbitrage_cyclesf(self, rawresults, *, format=None):
        """
        the formatting function for run_arbitrage_cycles to reformat the results

        :rawresults:    the ACRET_RAW result returned by run_arbitrage_cycles
        :format:       same as in `run_arbitrage_cycles`
        """
        if format is None:
            format = self.ACREF_DF

        arbcycles = rawresults
        if format == self.ACRET_GEN or format == self.ACRET_TUPLE:
            return rawresults
        arbcycles_dcts = tuple(r.asdict(False) for r in arbcycles)
        if format == self.ACRET_DICTS:
            return arbcycles_dcts
        df0 = pd.DataFrame.from_dict(arbcycles_dcts)
        if format == self.ACRET_DF:
            return df0.set_index("uid")

        df1 = df0.sort_values(["token", "uid"])
        df1["uid"] = df1["uid"].astype(str)
        dfa = df1.pivot_table(
            index="token", values=["profit", "amount_in", "amount_out"]
        )
        df2 = pd.concat([df1, dfa.reset_index()]).fillna("").set_index(["token", "uid"])
        if format == self.ACRET_AGGRDF:
            return df2
        if format == self.ACRET_PRETTYADF:
            return df2.style.format(
                {
                    "profit": "{:.4f}",
                    "amount_in": "{:.4f}",
                    "amount_out": "{:.4f}",
                }
            )

        raise ValueError(f"Invalid format parameter: {format}")

    @dataclass
    class TransportResult(_DCBase):
        amount_in: Amount
        amount_out: Amount
        amounts_in: tuple
        amounts_out: tuple
        edges: tuple

    TPROUT_PRORATA = "prorata"

    def transport(
        self,
        amount_in,
        tkn_in,
        tkn_out,
        *,
        record=True,
        routingalgo=None,
        raiseonerror=True,
    ):
        """
        transport an amount of tkn_in to tkn_out routing through the relevant edges

        :amount_in:     amount to be transported (as float or Amount)
        :tkn_in:        token to be transported (as str or Node)
        :tkn_out:       token to be transported to (as str or Node)
        :record:        if True, record the transport in the graph
        :routingalgo:   routing algo to be used (default: TPROUT_PRORATA)
        """
        if routingalgo is None:
            routingalgo = self.TPROUT_PRORATA
        if not routingalgo in [self.TPROUT_PRORATA]:
            raise ValueError(
                f"routingalgo {routingalgo} not supported; see TPROUT_* constants"
            )

        # get the nodes
        node_in = self.node_by_tkn(tkn_in)
        node_out = self.node_by_tkn(tkn_out)

        # if amount_in is a Amount, ensure the token is correct
        if isinstance(amount_in, Amount):
            if amount_in.token != node_in.token:
                raise ValueError(
                    f"amount_in token {amount_in.token} does not match node_in token {node_in.token}"
                )
            amount_in = amount_in.amount

        # get the edges
        edges = self.filter_edges(node_in, node_out)
        if len(edges) == 0:
            raise ValueError(f"no edge found between {node_in} and {node_out}")

        # get the amounts in per edge
        capacities_in = [e.state.amount_in_remaining for e in edges]
        capacity_in = sum(capacities_in)

        # execute the routing algo
        assert (
            routingalgo == self.TPROUT_PRORATA
        ), f"routingalgo {routingalgo} not supported; use TPROUT_PRORATA"
        routing_factor = amount_in / capacity_in
        amounts_in = [amt_in * routing_factor for amt_in in capacities_in]
        print(
            f"routing_factor: {routing_factor}; amounts_in: {amounts_in} {amount_in} {capacity_in}"
        )

        # transport the amounts through the edges
        amounts_out = []
        for edge, amt_in in zip(edges, amounts_in):
            amounts_out += [
                edge.transport(amt_in, record=record, raiseonerror=raiseonerror)
            ]

        return self.TransportResult(
            amount_in=Amount(amount_in, node_in.tkn),
            amount_out=Amount(
                sum([amt_out.amount for amt_out in amounts_out]), node_out.tkn
            ),
            amounts_in=tuple(amounts_in),
            amounts_out=tuple([amt_out.amount for amt_out in amounts_out]),
            edges=tuple(edges),
        )

    @dataclass
    class PTransportResult(_DCBase):
        multiplier: float
        prices: list
        numedges: list
        path: any  # Cycle or Path object

        @property
        def cycle(self):
            return self.path

    def ptransport(self, path):
        """
        transport an amount along a (usually closed) path, ignoring capacities

        :path:      typically a Cycle object, or another object the same API*
                    (Cycle paths will always be closed)

        *the function expect that path has a method called `pairs` that returns an
        iterator, and the iterator in turn yields tuples(node_in, node_out) where
        the previous node_out is the same as the next node_in
        """
        multiplier = 1
        prices = []
        numedges = []
        for edgenodes in path.pairs():
            node_in, node_out = edgenodes
            edges = self.filter_edges(node_in=node_in, node_out=node_out)
            p_outperin = np.mean([e.p_outperin for e in edges])
            # print(f"ptransport {node_in} --{p_outperin}--> {node_out} [{len(edges)}]")
            multiplier *= p_outperin
            prices += [p_outperin]
            numedges += [len(edges)]
        return self.PTransportResult(
            multiplier=multiplier,
            prices=prices,
            numedges=numedges,
            path=path,
        )

    def edgedf(self, edges=None, *, consolidated=True, resetindex=False):
        """
        returns edges (default: all edges) as a pandas dataframe
        """
        if edges is None:
            edges = self.edges

        if self.is_amounttype:

            # Amount-type graph
            df = pd.DataFrame.from_dict(
                [
                    dict(
                        pair=e.pairo.primary,
                        tkn_in=e.node_in.tkn,
                        tkn_out=e.node_out.tkn,
                        amount_in=e.amount_in,
                        amount_out=e.amount_out,
                    )
                    for e in edges
                ]
            )
            if not consolidated:
                df["uid"] = [e.uid for e in edges]
                return df.set_index("uid")
                return df
            df = df.groupby(["pair", "tkn_in", "tkn_out"]).sum()
            if resetindex:
                df = df.reset_index()
            return df

        else:
            # Connection-type graph
            df = pd.DataFrame.from_dict(
                [
                    dict(
                        pair=e.pairo.primary,
                        tkn_in=e.node_in.tkn,
                        tkn_out=e.node_out.tkn,
                        n=-e.amount_in,
                        is_reverse=not e.pairo.isprimary,
                        price_outin=e.amount_out / e.amount_in,
                        price=e.pairo.pp(e.amount_out / e.amount_in),
                    )
                    for e in edges
                ]
            )
            if not consolidated:
                return df
            df = df.pivot_table(
                index=["pair", "tkn_in", "tkn_out", "is_reverse"],
                values=["n", "price"],
                aggfunc={"n": np.sum, "price": np.mean},
            ).reset_index()
            dff = df[df["is_reverse"] == False]
            dft = df[df["is_reverse"] == True]
            df = pd.concat(
                [
                    dff.reset_index(drop=True),
                    dft[["n"]].rename(columns={"n": "n_rev"}).reset_index(drop=True),
                ],
                axis=1,
            )
            df = df[["pair", "n", "n_rev", "price"]]

            if not resetindex:
                df = df.set_index("pair")
            return df

    @dataclass
    class EdgeStatistics(_DCBase):
        len: int
        edges: tuple
        amount_in: Amount
        amount_in_remaining: Amount
        amount_out: Amount
        price: float
        utilization: float
        amounts_in: tuple
        amounts_in_remaining: tuple
        amounts_out: tuple
        prices: tuple
        utilizations: tuple

    def edge_statistics(
        self, node_in=None, node_out=None, *, edges=None, pair=None, bothways=False
    ):
        """
        get statistics about the list of edges between node_in, node_out (or sublist provided)

        :node_in:       node_in (as str or Node)
        :node_out:      node_out (as str or Node)
        :edges:         list of edges to be used (if not None, but have same node_in -> node_out)
        :pair:          the pair in the form "TKNB/TKBQ" as str
        :bothways:      if True, returns pair bothways
        :returns:       EdgeStatistics object node_in -> node_out; or pair thereof if bothways=True
        """
        if not self.is_amounttype:
            raise ValueError("edge_statistics only supported for AmountGraphs")
        if bothways:
            return (
                self.edge_statistics(node_in, node_out, edges=edges, bothways=False),
                self.edge_statistics(node_out, node_in, edges=edges, bothways=False),
            )
        if not pair is None:
            assert (
                node_in is None and node_out is None
            ), f"cannot specify both pair and node_in/node_out {pair}, {node_in}, {node_out}"
            node_in, node_out = pair.split("/")
            return self.edge_statistics(node_in, node_out, bothways=True)

        if isinstance(node_in, str):
            node_in = self.node_by_tkn(node_in)
        if isinstance(node_out, str):
            node_out = self.node_by_tkn(node_out)

        if not edges is None:
            assert (
                node_in is None and node_out is None
            ), "cannot specify both edges and node_in/node_out"
            node_in = {ee.node_in.tkn for ee in edges}
            if len(node_in) != 1:
                raise ValueError(f"edges have different node_in: {node_in}")
            node_in = node_in.pop()
            node_out = {ee.node_out.tkn for ee in edges}
            if len(node_out) != 1:
                raise ValueError(f"edges have different node_out: {node_out}")
            node_out = node_out.pop()
        else:
            edges = self.filter_edges(node_in=node_in, node_out=node_out)

        if len(edges) == 0:
            return None

        amounts_in = tuple(e.amount_in for e in edges)
        amount_in = sum(amounts_in)

        amounts_in_remaining = tuple(e.state.amount_in_remaining for e in edges)
        amount_in_remaining = sum(amounts_in_remaining)

        utilizations = tuple(
            1 - r / a for r, a in zip(amounts_in_remaining, amounts_in)
        )
        utilization = 1 - amount_in_remaining / amount_in if amount_in > 0 else None

        amounts_out = tuple(e.amount_out for e in edges)
        amount_out = sum(amounts_out)

        prices = tuple(outv / inv for outv, inv in zip(amounts_out, amounts_in))
        price = amount_out / amount_in

        return self.EdgeStatistics(
            len=len(edges),
            edges=tuple(edges),
            amount_in=Amount(amount_in, node_in),
            amount_in_remaining=Amount(amount_in_remaining, node_in),
            amount_out=Amount(amount_out, node_out),
            price=price,
            utilization=utilization,
            amounts_in=amounts_in,
            amounts_in_remaining=amounts_in_remaining,
            amounts_out=amounts_out,
            prices=prices,
            utilizations=utilizations,
        )

    @dataclass
    class NodeStatistics(_DCBase):
        """
        attention: in and out for nodes and edges is reversed

        :edges_in:     all edges that have this node as node_out
        :edges_out:    all edges that have this node as node_in
        :amount_in:    sum of all amounts_out of edges_in
        :amount_out:   sum of all amounts_in of edges_out
        """

        node: Node
        edges_in: tuple
        edges_out: tuple
        nodes_in: set
        nodes_out: set
        amount_in: Amount
        amount_out: Amount
        amount_out_remaining: Amount

    def node_statistics(self, node):
        """
        get statistics about the node provided
        """
        node = self.node_by_tkn(node)
        edges_out = self.filter_edges(node_in=node)
        edges_in = self.filter_edges(node_out=node)
        nodes_out = {e.node_out.tkn for e in edges_out}
        nodes_in = {e.node_in.tkn for e in edges_in}
        amount_in = sum(e.amount_out for e in edges_in)
        amount_out = sum(e.amount_in for e in edges_out)
        amount_out_remaining = sum(e.state.amount_in_remaining for e in edges_out)

        return self.NodeStatistics(
            node=node,
            edges_in=tuple(edges_in),
            edges_out=tuple(edges_out),
            nodes_in=set(nodes_in),
            nodes_out=set(nodes_out),
            amount_in=Amount(amount_in, node),
            amount_out=Amount(amount_out, node),
            amount_out_remaining=Amount(amount_out_remaining, node),
        )
