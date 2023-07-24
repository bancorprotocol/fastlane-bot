"""
object encapsulating various optimization methods, including convex optimization

(c) Copyright Bprotocol foundation 2023. 
Licensed under MIT

NOTE: this class is not part of the API of the Carbon protocol, and you must expect breaking
changes even in minor version updates. Use at your own risk.


Convex and Marginal Price Optimization for Arbitrage and Routing
================================================================

This module implements a number of methods that allow for routing* and arbitrage amongst a set
of AMMs. Most methods allow, subject to convergence, for the optimization and routing within
an arbitrary multi-token context. The _subject to convergence_ part is important, as the in 
particular the convex optimization methods with the solvers available to us to do not seem to
be able to handle leveraged liquidity well.

This module is still subject to active research, and comments and suggestions are welcome. 
The corresponding author is Stefan Loesch <stefan@bancor.network>


*routing is not implemented yet, but it is a trivial extension of the arbitrage methods that
only needs to be connected and properly parameterized
"""
__VERSION__ = "3.6"
__DATE__ = "06/May/2023"

from dataclasses import dataclass, field, fields, asdict, astuple, InitVar
import pandas as pd
import numpy as np

try:
    import cvxpy as cp
except:
    # if cvxpy is not installed the convex optimization methods will not work; however, the
    # the marginal price based methods will still work
    cp = None
import time
import math
import numbers
import pickle
from .cpc import ConstantProductCurve as CPC, CPCInverter, CPCContainer
from sys import float_info


class _DCBase:
    """base class for all data classes, adding some useful methods"""

    def asdict(self):
        return asdict(self)

    def astuple(self):
        return astuple(self)

    def fields(self):
        return fields(self)

    # def pickle(self, filename, addts=True):
    #     """
    #     pickles the object to a file
    #     """
    #     if addts:
    #         filename = f"{filename}.{time.time()}.pickle"
    #     with open(filename, 'wb') as f:
    #         pickle.dump(self, f)

    # @classmethod
    # def unpickle(cls, filename):
    #     """
    #     unpickles the object from a file
    #     """
    #     with open(filename, 'rb') as f:
    #         object = pickle.load(f)
    #     assert isinstance(object, cls), f"unpickled object is not of type {cls}"
    #     return object


@dataclass
class ScaledVariable(_DCBase):
    """
    wraps a cvxpy variable to allow for scaling
    """

    variable: cp.Variable
    scale: any = 1.0
    token: list = None

    def __post_init__(self):
        try:
            len_var = len(self.variable.value)
        except TypeError as e:
            print("[ScaledVariable] variable.value is None", self.variable)
            return

        if not isinstance(self.scale, numbers.Number):
            self.scale = np.array(self.scale)
            if not len(self.scale) == len_var:
                raise ValueError(
                    "scale and variable must have same length or scale must be a number",
                    self.scale,
                    self.variable.value,
                )
        if not self.token is None:
            if not len(self.token) == len_var:
                raise ValueError(
                    "token and variable must have same length",
                    self.token,
                    self.variable.value,
                )

    @property
    def value(self):
        """
        converts value from USD to token units*

        Note: with scaling, the calculation is set up in a way that the values of the raw variables
        dx, dy correspond approximately to USD numbers, so their relative scale is natural and only
        determined by the problem, not by units.

        The scaling factor is the PRICE in USD PER TOKEN, therefore

            self.variable.value = USD value of the token
            self.variable.value / self.scale = number of tokens
        """
        try:
            return np.array(self.variable.value) / self.scale
        except Exception as e:
            print("[value] exception", e, self.variable.value, self.scale)
            return self.variable.value

    @property
    def v(self):
        """alias for variable"""
        return self.variable


class OptimizerBase:
    """
    base class for all optimizers

    :problem:       the problem object (eg allowing to read `problem.status`)
    :result:        the return value of problem.solve
    :time:          the time it took to solve this problem (optional)
    :optimizer:     the optimizer object that created this result
    """

    __VERSION__ = __VERSION__
    __DATE__ = __DATE__

    def pickle(self, basefilename, addts=True):
        """
        pickles the object to a file
        """
        if addts:
            filename = f"{basefilename}.{int(time.time()*100)}.optimizer.pickle"
        else:
            filename = f"{basefilename}.optimizer.pickle"
        with open(filename, "wb") as f:
            pickle.dump(self, f)

    @classmethod
    def unpickle(cls, basefilename):
        """
        unpickles the object from a file
        """
        with open(f"{basefilename}.optimizer.pickle", "rb") as f:
            object = pickle.load(f)
        assert isinstance(object, cls), f"unpickled object is not of type {cls}"
        return object

    @dataclass
    class OptimizerResult(_DCBase):
        result: float
        time: float
        method: str = None
        optimizer: InitVar

        def __post_init__(self, optimizer):
            self._optimizer = optimizer
            # print("[OptimizerResult] post_init", optimizer)

        @property
        def optimizer(self):
            return self._optimizer

        def __float__(self):
            return float(self.result)

        @property
        def status(self):
            """problem status"""
            raise NotImplementedError("must be implemented in derived class")

        @property
        def is_error(self):
            """True if problem status is not OPTIMAL"""
            raise NotImplementedError("must be implemented in derived class")

        def detailed_error(self):
            """detailed error analysis"""
            raise NotImplementedError("must be implemented in derived class")

        @property
        def error(self):
            """problem error"""
            if not self.is_error:
                return None
            return self.detailed_error()

    @dataclass
    class SimpleResult(_DCBase):
        result: float
        method: str = None
        errormsg: str = None
        context_dct: dict = None

        def __float__(self):
            if self.is_error:
                raise ValueError("cannot convert error result to float")
            return float(self.result)

        @property
        def is_error(self):
            return not self.errormsg is None

        @property
        def context(self):
            return self.context_dct if not self.context_dct is None else {}

    DERIVEPS = 1e-6

    @classmethod
    def deriv(cls, func, x):
        """
        computes the derivative of `func` at point `x`
        """
        h = cls.DERIVEPS
        return (func(x + h) - func(x - h)) / (2 * h)

    @classmethod
    def deriv2(cls, func, x):
        """
        computes the second derivative of `func` at point `x`
        """
        h = cls.DERIVEPS
        return (func(x + h) - 2 * func(x) + func(x - h)) / (h * h)

    @classmethod
    def findmin_gd(cls, func, x0, *, learning_rate=0.1, N=100):
        """
        finds the minimum of `func` using gradient descent starting at `x0`
        """
        x = x0
        for _ in range(N):
            x -= learning_rate * cls.deriv(func, x)
        return cls.SimpleResult(result=x, method="findmin_gd")

    @classmethod
    def findmax_gd(cls, func, x0, *, learning_rate=0.1, N=100):
        """
        finds the maximum of `func` using gradient descent, starting at `x0`
        """
        x = x0
        for _ in range(N):
            x += learning_rate * cls.deriv(func, x)
        return cls.SimpleResult(result=x, method="findmax_gd")

    @classmethod
    def findminmax_nr(cls, func, x0, *, N=20):
        """
        finds the minimum or maximum of func using Newton Raphson, starting at x0
        """
        x = x0
        for _ in range(N):
            # print("[NR]", x, func(x), cls.deriv(func, x), cls.deriv2(func, x))
            try:
                x -= cls.deriv(func, x) / cls.deriv2(func, x)
            except Exception as e:
                return cls.SimpleResult(
                    result=None,
                    errormsg=f"Newton Raphson failed: {e} [x={x}, x0={x0}]",
                    method="findminmax_nr",
                )
        return cls.SimpleResult(result=x, method="findminmax_nr")

    findmin = findminmax_nr
    findmax = findminmax_nr

    GOALSEEKEPS = 1e-6

    @classmethod
    def goalseek(cls, func, a, b):
        """
        finds the value of `x` where `func(x)` x is zero, using binary search between a,b
        """
        if func(a) * func(b) > 0:
            cls.SimpleResult(
                result=None,
                errormsg=f"function must have different signs at a,b [{a}, {b}, {func(a)} {func(b)}]",
                method="findminmax_nr",
            )
            raise ValueError("function must have different signs at a,b")
        while (b - a) > cls.GOALSEEKEPS:
            c = (a + b) / 2
            if func(c) == 0:
                return c
            elif func(a) * func(c) < 0:
                b = c
            else:
                a = c
        return cls.SimpleResult(result=(a + b) / 2, method="findminmax_nr")

    @staticmethod
    def posx(vector):
        """
        returns the positive elements of the vector, zeroes elsewhere
        """
        if isinstance(vector, np.ndarray):
            return np.maximum(0, vector)
        return tuple(max(0, x) for x in vector)

    @staticmethod
    def negx(vector):
        """
        returns the negative elements of the vector, zeroes elsewhere
        """
        if isinstance(vector, np.ndarray):
            return np.minimum(0, vector)
        return tuple(min(0, x) for x in vector)

    @staticmethod
    def a(vector):
        """helper: returns vector as np.array"""
        return np.array(vector)

    @staticmethod
    def t(vector):
        """helper: returns vector as tuple"""
        return tuple(vector)

    @staticmethod
    def F(func, rg):
        """helper: returns list of [func(x) for x in rg]"""
        return [func(x) for x in rg]


FORMATTER = lambda x: "" if ((abs(x) < 1e-10) or math.isnan(x)) else f"{x:,.2f}"

F = OptimizerBase.F

TIF_OBJECTS = "objects"
TIF_DICTS = "dicts"
TIF_DFP = "dfp"
TIF_DFRAW = "dfraw"
TIF_DFAGGR = "dfaggr"
TIF_DF = "dfraw"

class CPCArbOptimizer(OptimizerBase):
    """
    main optimizer class for CPC arbitrage optimzisation
    """

    def __init__(self, curve_container):
        if not isinstance(curve_container, CPCContainer):
            curve_container = CPCContainer(curve_container)
        self._curve_container = curve_container
        
    @property
    def curve_container(self):
        """the curve container (CPCContainer)"""
        return self._curve_container

    CC = curve_container

    @property
    def tokens(self):
        return self.curve_container.tokens

    @dataclass
    class ConvexOptimizerResult(OptimizerBase.OptimizerResult):

        problem: InitVar

        def __post_init__(self, optimizer=None, problem=None, *args, **kwargs):
            super().__post_init__(*args, optimizer=optimizer, **kwargs)
            # print("[ConvexOptimizerResult] post_init")
            assert not problem is None, "problem must be set"
            self._problem = problem
            if self.method is None:
                self.method = "convex"

        @property
        def problem(self):
            return self._problem

        @property
        def status(self):
            """problem status"""
            return self.problem.status

        @property
        def is_error(self):
            """True if problem status is not OPTIMAL"""
            return self.status != cp.OPTIMAL or isinstance(self.result, str)

        @property
        def error(self):
            """problem error"""
            if not self.is_error:
                return None
            if isinstance(self.result, str):
                return f"{self.result} [{self.status}]"
            return f"{self.status}"

    @dataclass
    class NofeesOptimizerResult(ConvexOptimizerResult):
        """
        results of the nofees optimizer
        """

        token_table: dict = None
        sfc: any = field(repr=False, default=None)  # SelfFinancingConstraints
        curves: CPCContainer = field(repr=False, default=None)
        # curves_new: CPCContainer = field(repr=False,  default=None)
        # dx: cp.Variable = field(repr=False, default=None)
        # dy: cp.Variable = field(repr=False, default=None)
        dx: InitVar
        dy: InitVar

        def __post_init__(
            self, optimizer=None, problem=None, dx=None, dy=None, *args, **kwargs
        ):
            super().__post_init__(*args, optimizer=optimizer, problem=problem, **kwargs)
            # print("[NofeesOptimizerResult] post_init")
            assert not self.token_table is None, "token_table must be set"
            assert not self.sfc is None, "sfc must be set"
            assert not self.curves is None, "curves must be set"
            # assert not self.curves_new is None, "curves_new must be set"
            assert not dx is None, "dx must be set"
            assert not dy is None, "dy must be set"
            self._dx = dx
            self._dy = dy

        @property
        def dx(self):
            return self._dx

        @property
        def dy(self):
            return self._dy

        @property
        def curves_new(self):
            """returns a list of Curve objects the trade instructions implemented"""
            assert self.is_error is False, "cannot get this data from an error result"
            return self.optimizer.adjust_curves(dxvals=self.dxvalues)

        def trade_instructions(self, ti_format=None):
            """
            returns list of TradeInstruction objects

            :ti_format:     format of the TradeInstruction objects, see TradeInstruction.to_format
                            :TIF_OBJECTS:       a list of TradeInstruction objects (default)
                            :TIF_DICTS:         a list of TradeInstruction dictionaries
                            :TIF_DFRAW:         raw dataframe (holes are filled with NaN)
                            :TIF_DFP:           returns a "pretty" dataframe (holes are spaces)
                            :TIF_DFAGRR:        aggregated dataframe
                            :TIF_DF:            alias for :TIF_DFRAW:
            """
            result = (
                CPCArbOptimizer.TradeInstruction.new(
                    curve_or_cid=c, tkn1=c.tknx, amt1=dx, tkn2=c.tkny, amt2=dy
                )
                for c, dx, dy in zip(self.curves, self.dxvalues, self.dyvalues)
                if dx != 0 or dy != 0
            )
            return CPCArbOptimizer.TradeInstruction.to_format(result, ti_format)

        @property
        def dxvalues(self):
            """returns dx values"""
            return self.dx.value

        @property
        def dyvalues(self):
            """returns dy values"""
            return self.dy.value

        def dxdydf(self, *, asdict=False, pretty=True, inclk=False):
            """returns dataframe with dx, dy per curve"""
            if inclk:
                dct = [
                    {
                        "cid": c.cid,
                        "pair": c.pair,
                        "tknx": c.tknx,
                        "tkny": c.tkny,
                        "x": c.x,
                        "y": c.y,
                        "xa": c.x_act,
                        "ya": c.y_act,
                        "k": c.k,
                        "kpost": (c.x + dxv) * (c.y + dyv),
                        "kk": (c.x + dxv) * (c.y + dyv) / c.k,
                        c.tknx: dxv,
                        c.tkny: dyv,
                    }
                    for dxv, dyv, c in zip(self.dx.value, self.dy.value, self.curves)
                ]
            else:
                dct = [
                    {
                        "cid": c.cid,
                        "pair": c.pair,
                        "tknx": c.tknx,
                        "tkny": c.tkny,
                        "x": c.x,
                        "y": c.y,
                        "xa": c.x_act,
                        "ya": c.y_act,
                        "kk": (c.x + dxv) * (c.y + dyv) / c.k,
                        c.tknx: dxv,
                        c.tkny: dyv,
                    }
                    for dxv, dyv, c in zip(self.dx.value, self.dy.value, self.curves)
                ]
            if asdict:
                return dct
            df = pd.DataFrame.from_dict(dct).set_index("cid")
            df0 = df.fillna(0)
            dfa = df0[df0.columns[8:]].sum().to_frame(name="total").T
            dff = pd.concat([df, dfa], axis=0)
            if pretty:
                try:
                    dff = dff.style.format({col: FORMATTER for col in dff.columns[3:]})
                except Exception as e:
                    print("[dxdydf] exception", e, dff.columns)
            return dff

    @dataclass
    class SelfFinancingConstraints(_DCBase):
        """
        describes self financing constraints and determines optimization variable

        :data:      a dict TKN -> amount, or AMMPays, AMMReceives
                    :amount:            from the AMM perspective, total inflows (>0) or outflows (<0)
                                        for all items not present in data the value is assumed zero
                    :AMMPays:           the AMM payout should be maximized [from the trader (!) perspective]
                    :AMMReceives:       the money paid into the AMM should be minimized [ditto]
                    :OptimizationVar:   like AMMPays and AMMReceives, but if the direction of the payout is
                                        not known at the beginning [not all methods allow this]
                    :OV:                alias for OptimizationVar
        :tokens:    set of all tokens in the problem (if None, use data.keys())

        """

        AMMPays = "AMMPays"
        AMMReceives = "AMMReceives"
        OptimizationVar = "OptimizationVar"
        OV = OptimizationVar

        data: dict
        tokens: set = None

        def __post_init__(self):
            optimizationvars = tuple(
                k
                for k, v in self.data.items()
                if v in {self.AMMPays, self.AMMReceives, self.OptimizationVar}
            )
            assert (
                len(optimizationvars) == 1
            ), f"there must be EXACTLY one AMMPays, AMMReceives, OptimizationVar {self.data}"
            self._optimizationvar = optimizationvars[0]
            if self.tokens is None:
                self.tokens = set(self.data.keys())
            else:
                if isinstance(self.tokens, str):
                    self.tokens = set(t.strip() for t in self.tokens.split(","))
                else:
                    self.tokens = set(self.tokens)
                assert (
                    set(self.data.keys()) - self.tokens == set()
                ), f"constraint keys {set(self.data.keys())} > {self.tokens}"

        @property
        def optimizationvar(self):
            """optimization variable, ie the in that is set to AMMPays, AMMReceives or OptimizationVar"""
            return self._optimizationvar

        @property
        def tokens_s(self):
            """tokens as a comma-separated string"""
            return ", ".join(self.tokens_l)

        @property
        def tokens_l(self):
            """tokens as a list"""
            return sorted(list(self.tokens))

        def asdict(self, *, short=False):
            """dict representation including zero-valued tokens (unless short)"""
            if short:
                return {**self.data}
            return {k: self.get(k) for k in self.tokens}

        def items(self, *, short=False):
            return self.asdict(short=short).items()

        @classmethod
        def new(cls, tokens, **data):
            """alternative constructor: data as kwargs"""
            return cls(data=data, tokens=tokens)

        @classmethod
        def arb(cls, targettkn):
            """alternative constructor: arbitrage constraint, ie all other constraints are zero"""
            return cls(data={targettkn: cls.OptimizationVar})

        def get(self, item):
            """gets the constraint, or 0 if not present"""
            assert item in self.tokens, f"item {item} not in {self.tokens}"
            return self.data.get(item, 0)

        def is_constraint(self, item):
            """
            returns True iff item is a constraint (ie not an optimisation variable)
            """
            return not self.is_optimizationvar(item)

        def is_optimizationvar(self, item):
            """
            returns True iff item is the optimization variable
            """
            assert item in self.tokens, f"item {item} not in {self.tokens}"
            return item == self.optimizationvar

        def is_arbsfc(self):
            """
            returns True iff the constraint is an arbitrage constraint
            """
            if len(self.data) == 1:
                return True
            data1 = [v for v in self.data.values() if v != 0]
            return len(data1) == 1

        def __call__(self, item):
            """alias for get"""
            return self.get(item)

    def SFC(self, **data):
        """alias for SelfFinancingConstraints.new"""
        return self.SelfFinancingConstraints.new(self.curve_container.tokens(), **data)

    def SFCd(self, data_dct):
        """alias for SelfFinancingConstraints.new, with data as a dict"""
        return self.SelfFinancingConstraints.new(
            self.curve_container.tokens(), **data_dct
        )

    def SFCa(self, targettkn):
        """alias for SelfFinancingConstraints.arb"""
        return self.SelfFinancingConstraints.arb(targettkn)

    arb = SFCa

    AMMPays = SelfFinancingConstraints.AMMPays
    AMMReceives = SelfFinancingConstraints.AMMReceives
    OptimizationVar = SelfFinancingConstraints.OptimizationVar
    OV = SelfFinancingConstraints.OV

    SOLVER_ECOS = "ECOS"
    SOLVER_SCS = "SCS"
    SOLVER_OSQP = "OSQP"
    SOLVER_CVXOPT = "CVXOPT"
    SOLVER_CBC = "CBC"
    SOLVERS = {
        SOLVER_ECOS: cp.ECOS,
        SOLVER_SCS: cp.SCS,
        SOLVER_OSQP: cp.OSQP,
        SOLVER_CVXOPT: cp.CVXOPT,
        SOLVER_CBC: cp.CBC,
        # those solvers will usually have to be installed separately
        "ECOS_BB": cp.ECOS_BB,
        "OSQP": cp.OSQP,
        "GUROBI": cp.GUROBI,
        "MOSEK": cp.MOSEK,
        "GLPK": cp.GLPK,
        "GLPK_MI": cp.GLPK_MI,
        "CPLEX": cp.CPLEX,
        "XPRESS": cp.XPRESS,
        "SCIP": cp.SCIP,
    }

    def nofees_optimizer(self, sfc, **params):
        """
        convex optimization for determining the arbitrage opportunities

        :sfc:       a SelfFinancingConstraints object (or str passed to SFC.arb)
        :params:    additional parameters to be passed to the solver
                    :verbose:       if True, generate verbose output
                    :solver:        the solver to be used (default: "CVXOPT"; see SOLVERS)
                    :nosolve:       if True, do not solve the problem, but return the problem object
                    :nominconstr:   if True, do NOT add the minimum constraints
                    :maxconstr:     if True, DO add the (reundant) maximum constraints
                    :retcurves:     if True, also return the curves object (default: False)
                    :s_xxx:         pass the parameter `xxx` to the solver (eg s_verbose)
                    :s_verbose:     if True, generate verbose output from the solver


        note: CVXOPT is a pip install (pip install cvxopt); OSQP is not suitable for this problem,
        ECOS and SCS do work sometimes but can go dramatically wrong
        """

        # This code runs the actual optimization. It has two major parts

        # 1. the **constraints**, and
        # 2. the **objective function** to be optimized (min or max)

        # The objective function is to either maximize the number of tokens
        # received from the AMM (which is a negative number, hence formally the
        # condition is `cp.Minimize` or to minimize the number of tokens paid to
        # the AMM which is a positive number. Therefore `cp.Minimize` is the
        # correct choice in each case.

        # The constraints come in three types:

        # - **curve constraint**: the curve constraints correspond to the
        #   $x\cdot y=k$ invariant of the respective AMM; the constraint is
        #   formally `>=` but it has been shown eg by Angeris et al that the
        #   constraint will always be optimal on the boundary

        # - **range constraints**: the range constraints correspond to the
        #   tokens actually available on curve; for the full-curve AMM those
        #   constraints would formally be `dx >= -c.x` and the same for `y`, but
        #   those constraint are automatically fulfilled because of the
        #   asymptotic behaviour of the curves so could be omitted

        # - **self-financing constraints**: the self-financing constraints
        #   corresponds to the condition that all `dx` and `dy` corresponding to
        #   a specific token other than the token in the objective function must
        #   sum to the target amount provided in `inputs` (or zero if not
        #   provided)

        assert not cp is None, "cvxpy not installed [pip install cvxpy]]"
        if isinstance(sfc, str):
            sfc = self.SelfFinancingConstraints.arb(sfc)

        curves_t = self.curve_container.curves
        c0 = curves_t[0]
        tt = self.curve_container.tokentable()
        prtkn = sfc.optimizationvar

        P = lambda x: params.get(x)

        start_time = time.time()

        # set up the optimization variables
        if P("verbose"):
            print(f"Setting up dx[0..{len(curves_t)-1}] and dy[0..{len(curves_t)-1}]")
        dx = cp.Variable(len(curves_t), value=[0] * len(curves_t))
        dy = cp.Variable(len(curves_t), value=[0] * len(curves_t))

        # the geometric mean of objects in a list
        gmean = lambda lst: cp.geo_mean(cp.hstack(lst))

        ## assemble the constraints...
        constraints = []

        # curve constraints
        for i, c in enumerate(curves_t):
            constraints += [
                gmean([c.x + dx[i] / c.scalex, c.y + dy[i] / c.scaley]) >= c.kbar
            ]
            if P("verbose"):
                print(
                    f"CC {i} [{c.cid}]: {c.pair} x={c.x:.1f} {c.tknx } (s={c.scalex}), y={c.y:.1f} {c.tkny} (s={c.scaley}), k={c.k:2.1f}, p_dy/dx={c.p:2.1f}, p_dx/dy={1/c.p:2.1f}"
                )

        if P("verbose"):
            print("number of constraints: ", len(constraints))

        # range constraints (min)
        for i, c in enumerate(curves_t):

            pass

            if not P("nominconstr"):
                constraints += [
                    dx[i] / c.scalex >= c.dx_min,
                    dy[i] / c.scaley >= c.dy_min,
                ]
                if P("verbose"):
                    print(
                        f"RC {i} [{c.cid}]: dx>{c.dx_min:.4f} {c.tknx} (s={c.scalex}), dy>{c.dy_min:.4f} {c.tkny} (s={c.scaley}) [{c.pair}]"
                    )

            if P("maxconstr"):
                if not c.dx_max is None:
                    constraints += [
                        dx[i] / c.scalex <= c.dx_max,
                    ]
                if not c.dy_max is None:
                    constraints += [
                        dy[i] / c.scaley <= c.dy_max,
                    ]
                if P("verbose"):
                    print(
                        f"RC {i} [{c.cid}]: dx<{c.dx_max} {c.tknx} (s={c.scalex}), dy<{c.dy_max} {c.tkny} (s={c.scaley}) [{c.pair}]"
                    )

        if P("verbose"):
            print("number of constraints: ", len(constraints))

        # self-financing constraints
        for tkn, tknvalue in sfc.items():
            if not isinstance(tknvalue, str):
                constraints += [
                    cp.sum([dy[i] for i in tt[tkn].y])
                    + cp.sum([dx[i] for i in tt[tkn].x])
                    == tknvalue * c0.scale(tkn)
                    # note: we can access the scale from any curve as it is a class method
                ]
                if P("verbose"):
                    print(
                        f"SFC [{tkn}={tknvalue}, s={c0.scale(tkn)}]: y={[i for i in tt[tkn].y]}, x={[i for i in tt[tkn].x]}"
                    )

        if P("verbose"):
            print("number of constraints: ", len(constraints))

        # objective function  (note: AMM out is negative, AMM in is positive)
        if P("verbose"):
            print(
                f"O: y={[i for i in tt[prtkn].y]}, x={[i for i in tt[prtkn].x]}, {prtkn}"
            )

        objective = cp.Minimize(
            cp.sum([dy[i] for i in tt[prtkn].y]) + cp.sum([dx[i] for i in tt[prtkn].x])
        )

        # run the optimization
        problem = cp.Problem(objective, constraints)
        solver = self.SOLVERS.get(P("solver"), cp.CVXOPT)
        if not P("nosolve"):
            sp = {k[2:]: v for k, v in params.items() if k[:2] == "s_"}
            print("Solver params:", sp)
            if P("verbose"):
                print(f"Solving the problem with {solver}...")
            try:
                problem_result = problem.solve(solver=solver, **sp)
                # problem_result = problem.solve(solver=solver)
            except cp.SolverError as e:
                if P("verbose"):
                    print(f"Solver error: {e}")
                problem_result = str(e)
            if P("verbose"):
                print(
                    f"Problem solved in {time.time()-start_time:.2f} seconds; result: {problem_result}"
                )
        else:
            problem_result = None

        dx_ = ScaledVariable(
            dx, [c.scalex for c in curves_t], [c.tknx for c in curves_t]
        )
        dy_ = ScaledVariable(
            dy, [c.scaley for c in curves_t], [c.tkny for c in curves_t]
        )

        return self.NofeesOptimizerResult(
            problem=problem,
            sfc=sfc,
            result=problem_result,
            time=time.time() - start_time,
            dx=dx_,
            dy=dy_,
            token_table=tt,
            curves=self.curve_container,
            # curves_new=self.adjust_curves(dxvals = dx_.value),
            optimizer=self,
        )

    SO_DXDYVECFUNC = "dxdyvecfunc"
    SO_DXDYSUMFUNC = "dxdysumfunc"
    SO_DXDYVALXFUNC = "dxdyvalxfunc"
    SO_DXDYVALYFUNC = "dxdyvalyfunc"
    SO_PMAX = "pmax"
    SO_GLOBALMAX = "globalmax"
    SO_TARGETTKN = "targettkn"

    @dataclass
    class SimpleOptimizerResult(OptimizerBase.OptimizerResult):
        """
        results of the simple optimizer

        :curves:            list of curves used in the optimization, possibly wrapped in CPCInverter objects*
        :dxdyfromp_vec_f:   vector of tuples (dx, dy), as a function of p
        :dxdyfromp_sum_f:   sum of the above, also as a function of p
        :dxdyfromp_valx_f:  valx = dy/p + dx, also as a function of p
        :dxdyfromp_valy_f:  valy = dy + p*dx/p, also as a function of p
        :p_optimal:         optimal p value

        *the CPCInverter object ensures that all curves in the list correspond to the same quote
        conventions, according to the primary direction of the pair (as determined by the Pair
        object). Accordingly, tknx and tkny are always the same for all curves in the list, regardless
        of the quote direction of the pair. The CPCInverter object abstracts this away, but of course
        only for functions that are accessible through it.
        """

        NONEFUNC = lambda x: None

        curves: list = field(repr=False, default=None)
        dxdyfromp_vec_f: any = field(repr=False, default=NONEFUNC)
        dxdyfromp_sum_f: any = field(repr=False, default=NONEFUNC)
        dxdyfromp_valx_f: any = field(repr=False, default=NONEFUNC)
        dxdyfromp_valy_f: any = field(repr=False, default=NONEFUNC)
        p_optimal: float = field(repr=False, default=None)
        errormsg: str = field(repr=True, default=None)

        def __post_init__(self, *args, **kwargs):
            super().__post_init__(*args, **kwargs)
            # print("[SimpleOptimizerResult] post_init")
            assert (
                self.p_optimal is not None or self.errormsg is not None
            ), "p_optimal must be set unless errormsg is set"
            if self.method is None:
                self.method = "simple"

        @property
        def is_error(self):
            return self.errormsg is not None

        def detailed_error(self):
            return self.errormsg

        def status(self):
            return "error" if self.is_error else "converged"

        def dxdyfromp_vecs_f(self, p):
            """returns dx, dy as separate vectors instead as a vector of tuples"""
            return tuple(zip(*self.dxdyfromp_vec_f(p)))

        @property
        def tknx(self):
            return self.curves[0].tknx

        @property
        def tkny(self):
            return self.curves[0].tkny

        @property
        def tknxp(self):
            return self.curves[0].tknxp

        @property
        def tknyp(self):
            return self.curves[0].tknyp

        @property
        def pair(self):
            return self.curves[0].pair

        @property
        def pairp(self):
            return self.curves[0].pairp

        @property
        def dxdy_vecs(self):
            return self.dxdyfromp_vecs_f(self.p_optimal)

        @property
        def dxvalues(self):
            return self.dxdy_vecs[0]

        dxv = dxvalues

        @property
        def dyvalues(self):
            return self.dxdy_vecs[1]

        dyv = dyvalues

        @property
        def dxdy_vec(self):
            return self.dxdyfromp_vec_f(self.p_optimal)

        @property
        def dxdy_sum(self):
            return self.dxdyfromp_sum_f(self.p_optimal)

        @property
        def dxdy_valx(self):
            return self.dxdyfromp_valx_f(self.p_optimal)

        valx = dxdy_valx

        @property
        def dxdy_valy(self):
            return self.dxdyfromp_valy_f(self.p_optimal)

        valy = dxdy_valy

        def trade_instructions(self, ti_format=None):
            """returns list of TradeInstruction objects"""
            result = (
                CPCArbOptimizer.TradeInstruction.new(
                    curve_or_cid=c, tkn1=self.tknx, amt1=dx, tkn2=self.tkny, amt2=dy
                )
                for c, dx, dy in zip(self.curves, self.dxvalues, self.dyvalues)
                if dx != 0 or dy != 0
            )
            return CPCArbOptimizer.TradeInstruction.to_format(result, ti_format)

    def simple_optimizer(self, targettkn=None, result=None, *, params=None):
        """
        a simple optimizer that does not use cvxpy and the works only on curves on one pair

        :result:            determines what to return
                            :SO_DXDYVECFUNC:    function of p returning vector of dx,dy values
                            :SO_DXDYSUMFUNC:    function of p returning sum of dx,dy values
                            :SO_DXDYVALXFUNC:   function of p returning value of dx,dy sum in units of tknx
                            :SO_DXDYVALYFUNC:   ditto tkny
                            :SO_PMAX:           optimal p value for global max
                            :SO_GLOBALMAX:      global max of sum dx*p + dy
                            :SO_TARGETTKN:      optimizes for one token, the other is zero
        :targettkn:         token to optimize for (if result==SO_TARGETTKN); must be None if
                            result==SO_GLOBALMAX; result defaults to the corresponding value
                            depending on whether or not targettkn is None
        :params:            dict of parameters (not currently used)
        """
        start_time = time.time()
        curves_t = CPCInverter.wrap(self.curve_container)
        assert len(curves_t) > 0, "no curves found"
        c0 = curves_t[0]
        pairs = set(c.pair for c in curves_t)
        assert len(pairs) != 0, f"no pairs found, probably empty curves [{curves_t}]"
        assert (
            len(pairs) == 1
        ), f"simple_optimizer only works on curves of one pair [{pairs}]"
        assert not (
            targettkn is None and result == self.SO_TARGETTKN
        ), "targettkn must be set if result==SO_TARGETTKN"
        assert not (
            targettkn is not None and result == self.SO_GLOBALMAX
        ), f"targettkn must be None if result==SO_GLOBALMAX {targettkn}"

        dxdy = lambda r: (np.array(r[0:2]))

        dxdyfromp_vec_f = lambda p: tuple(dxdy(c.dxdyfromp_f(p)) for c in curves_t)
        if result == self.SO_DXDYVECFUNC:
            return dxdyfromp_vec_f

        dxdyfromp_sum_f = lambda p: sum(dxdy(c.dxdyfromp_f(p)) for c in curves_t)
        if result == self.SO_DXDYSUMFUNC:
            return dxdyfromp_sum_f

        dxdyfromp_valy_f = lambda p: np.dot(dxdyfromp_sum_f(p), np.array([p, 1]))
        if result == self.SO_DXDYVALYFUNC:
            return dxdyfromp_valy_f

        dxdyfromp_valx_f = lambda p: dxdyfromp_valy_f(p) / p
        if result == self.SO_DXDYVALXFUNC:
            return dxdyfromp_valx_f

        if result is None:
            if targettkn is None:
                result = self.SO_GLOBALMAX
            else:
                result = self.SO_TARGETTKN

        if not result == self.SO_TARGETTKN:
            p_avg = np.mean([c.p for c in curves_t])
            p_optimal = self.findmax(dxdyfromp_valx_f, p_avg)
            opt_result = dxdyfromp_valx_f(float(p_optimal))
            if result == self.SO_PMAX:
                return p_optimal
            elif result != self.SO_GLOBALMAX:
                raise ValueError(f"unknown result type {result}")
            method = "simple-globalmax"
        else:
            p_min = np.min([c.p for c in curves_t])
            p_max = np.max([c.p for c in curves_t])
            assert targettkn in {
                c0.tknx,
                c0.tkny,
            }, f"targettkn {targettkn} not in {c0.tknx}, {c0.tkny}"
            # we are now running a goalseek == 0 on the token that is NOT the target token
            if targettkn == c0.tknx:
                func = lambda p: dxdyfromp_sum_f(p)[1]
                p_optimal = self.goalseek(func, p_min * 0.99, p_max * 1.01)
                opt_result = dxdyfromp_sum_f(float(p_optimal))[0]
            else:
                func = lambda p: dxdyfromp_sum_f(p)[0]
                p_optimal = self.goalseek(func, p_min * 0.99, p_max * 1.01)
                opt_result = dxdyfromp_sum_f(float(p_optimal))[1]
            method = "simple-targettkn"

        if p_optimal.is_error:
            return self.SimpleOptimizerResult(
                result=None,
                time=time.time() - start_time,
                curves=curves_t,
                dxdyfromp_vec_f=dxdyfromp_vec_f,
                dxdyfromp_sum_f=dxdyfromp_sum_f,
                dxdyfromp_valx_f=dxdyfromp_valx_f,
                dxdyfromp_valy_f=dxdyfromp_valy_f,
                p_optimal=None,
                errormsg=p_optimal.errormsg,
                method=method,
                optimizer=self,
            )
        return self.SimpleOptimizerResult(
            result=opt_result,
            time=time.time() - start_time,
            curves=curves_t,
            dxdyfromp_vec_f=dxdyfromp_vec_f,
            dxdyfromp_sum_f=dxdyfromp_sum_f,
            dxdyfromp_valx_f=dxdyfromp_valx_f,
            dxdyfromp_valy_f=dxdyfromp_valy_f,
            p_optimal=float(p_optimal),
            method=method,
            optimizer=self,
        )

    def price_estimates(self, *, tknq, tknbs):
        """
        convenience function to access CPCContainer.price_estimate

        :tknq:      can only be a single token
        :tknbs:     list of tokens

        see help(CPCContainer.price_estimate) for details
        """
        return self.curve_container.price_estimates(tknqs=[tknq], tknbs=tknbs)

    JACEPS = 1e-5

    @classmethod
    def jacobian(cls, func, x, *, eps=None):
        """
        computes the Jacobian of func at point x

        :func:    a callable x=(x1..xn) -> (y1..ym), taking and returning np.arrays
        :x:       a vector x=(x1..xn) as np.array
        """
        if eps is None:
            eps = cls.JACEPS
        n = len(x)
        y = func(x)
        jac = np.zeros((n, n))
        for j in range(n):  # through columns to allow for vector addition
            Dxj = abs(x[j]) * eps if x[j] != 0 else eps
            x_plus = [(xi if k != j else xi + Dxj) for k, xi in enumerate(x)]
            jac[:, j] = (func(x_plus) - y) / Dxj
        return jac

    J = jacobian

    MO_DEBUG = "debug"
    MO_PSTART = "pstart"
    MO_P = MO_PSTART
    MO_DTKNFROMPF = "dtknfrompf"
    MO_MINIMAL = "minimal"
    MO_FULL = "full"

    MOEPS = 1e-6
    MOMAXITER = 50
    
    class OptimizationError(Exception): pass
    class ConvergenceError(OptimizationError): pass
    class ParameterError(OptimizationError): pass

    def margp_optimizer(self, sfc=None, result=None, *, params=None):
        """
        optimal transactions across all curves in the optimizer, extracting targettkn*

        :sfc:               the self financing constraint to use**
        :result:            the result type
                            :MO_DEBUG:         a number of items useful for debugging
                            :MO_PSTART:        price estimates (as dataframe)
                            :MO_PE:            alias for MO_ESTPRICE
                            :MO_DTKNFROMPF:    the function calculating dtokens from p
                            :MO_MINIMAL:       minimal result (omitting some big fields)
                            :MO_FULL:          full result
                            :None:             alias for MO_FULL
        :params:            dict of parameters
                            :eps:              precision parameter for accepting the result (default: 1e-6)
                            :maxiter:          maximum number of iterations (default: 100)
                            :verbose:          if True, print some high level output
                            :progress:         if True, print some basic progress output
                            :debug:            if True, print some debug output
                            :debug2:           more debug output
                            :raiseonerror:     if True, raise an OptimizationError exception on error
                            :pstart:           starting price for optimization, either as dict {tkn:p, ...},
                                                or as df as price estimate as returned by MO_PSTART;
                                                excess tokens can be provided but all required tokens must be present

        :returns:           MargpOptimizerResult on the default path, others depending on the
                            chosen result

        *this optimizer uses the marginal price method, ie it solves the equation

            dx_i (p) = 0 for all i != targettkn, and the whole price vector

        **at the moment only the trivial self-financing constraint is allowed, ie the one that
        only specifies the target token, and where all other constraints are zero; if sfc is
        a string then this is interpreted as the target token
        """
        # data conversion: string to SFC object; note that anything but pure arb not currently supported
        if isinstance(sfc, str):
            sfc = self.arb(targettkn=sfc)
        assert sfc.is_arbsfc(), "only pure arbitrage SFC are supported at the moment"
        targettkn = sfc.optimizationvar
        
        # lambdas
        P      = lambda item: params.get(item, None) if params is not None else None
        get    = lambda p, ix: p[ix] if ix is not None else 1       # safe get from tuple
        dxdy_f = lambda r: (np.array(r[0:2]))                       # extract dx, dy from result
        tn     = lambda t: t.split("-")[0]                          # token name, eg WETH-xxxx -> WETH
        
        # initialisations
        eps = P("eps") or self.MOEPS
        maxiter = P("maxiter") or self.MOMAXITER
        start_time = time.time()
        curves_t = self.curve_container
        alltokens_s = self.curve_container.tokens()
        tokens_t = tuple(t for t in alltokens_s if t != targettkn) # all _other_ tokens...
        tokens_ix = {t: i for i, t in enumerate(tokens_t)}         # ...with index lookup
        pairs = self.curve_container.pairs(standardize=False)
        curves_by_pair = { 
            pair: tuple(c for c in curves_t if c.pair == pair) for pair in pairs }
        pairs_t = tuple(tuple(p.split("/")) for p in pairs)
        
        try:
        
            # assertions
            if len (curves_t) == 0:
                raise self.ParameterError("no curves found")
            if len (curves_t) == 1:
                raise self.ParameterError(f"can't run arbitrage on single curve {curves_t}")
            if not targettkn in alltokens_s:
                raise self.ParameterError(f"targettkn {targettkn} not in {alltokens_s}")
                
            # calculating the start price for the iteration process
            if not P("pstart") is None:
                pstart = P("pstart")
                if P("verbose") or P("debug"):
                    print(f"[margp_optimizer] using pstartd [{len(P('pstart'))} tokens]")
                if isinstance(P("pstart"), pd.DataFrame):
                    try:
                        pstart = pstart.to_dict()[targettkn]
                    except Exception as e:
                        raise Exception(
                            f"error while converting dataframe pstart to dict: {e}",
                            pstart,
                            targettkn,
                        )
                    assert isinstance(
                        pstart, dict
                    ), f"pstart must be a dict or a data frame [{pstart}]"
                price_estimates_t = tuple(pstart[t] for t in tokens_t)
            else:
                if P("verbose") or P("debug"):
                    print("[margp_optimizer] calculating price estimates")
                try:
                    price_estimates_t = self.price_estimates(tknq=targettkn, tknbs=tokens_t)
                except Exception as e:
                    if P("verbose") or P("debug"):
                        print(
                            "[margp_optimizer] error while calculating price estimates:", e
                        )
                    price_estimates_t = None
            if P("debug"):
                print("[margp_optimizer] pstart:", price_estimates_t)
            if result == self.MO_PSTART:
                df = pd.DataFrame(price_estimates_t, index=tokens_t, columns=[targettkn])
                df.index.name = "tknb"
                return df
            
            ## INNER FUNCTION: CALCULATE THE TARGET FUNCTION
            def dtknfromp_f(p, *, islog10=True, asdct=False):
                """
                calculates the aggregate change in token amounts for a given price vector

                :p:         price vector, where prices use the reference token as quote token
                            this vector is an np.array, and the token order is the same as in tokens_t
                :islog10:   if True, p is interpreted as log10(p)
                :asdct:     if True, the result is returned as dict AND tuple, otherwise as np.array
                :returns:   if asdct is False, a tuple of the same length as tokens_t detailing the
                            change in token amounts for each token except for the target token (ie the
                            quantity with target zero; if asdct is True, that same information is
                            returned as dict, including the target token.
                """
                p = np.array(p, dtype=np.float64)
                if islog10:
                    p = np.exp(p * np.log(10))
                assert len(p) == len(
                    tokens_t
                ), f"p and tokens_t have different lengths [{p}, {tokens_t}]"
                if P("debug"):
                    print(f"\n[dtknfromp_f] =====================>>>")
                    print(f"prices={p}")
                    print(f"tokens={tokens_t}")

                sum_by_tkn = {t: 0 for t in alltokens_s}
                for pair, (tknb, tknq) in zip(pairs, pairs_t):
                    price = get(p, tokens_ix.get(tknb)) / get(p, tokens_ix.get(tknq))
                    curves = curves_by_pair[pair]
                    c0 = curves[0]
                    dxdy = tuple(dxdy_f(c.dxdyfromp_f(price)) for c in curves)
                    if P("debug2"):
                        print(f"\n{c0.pairp} --->>")
                        print(f"  price={price:,.4f}, 1/price={1/price:,.4f}")
                        for r, c in zip(dxdy, curves):
                            s = f"  cid={c.cid:15}"
                            s += f" dx={float(r[0]):15,.3f} {c.tknxp:>5}"
                            s += f" dy={float(r[1]):15,.3f} {c.tknyp:>5}"
                            s += f" p={c.p:,.2f} 1/p={1/c.p:,.2f}"
                            print(s)
                        print(f"<<--- {c0.pairp}")

                    sumdx, sumdy = sum(dxdy)
                    sum_by_tkn[tknq] += sumdy
                    sum_by_tkn[tknb] += sumdx

                    if P("debug"):
                        print(
                            f"pair={c0.pairp}, {sumdy:,.4f} {tn(tknq)}, {sumdx:,.4f} {tn(tknb)}, price={price:,.4f} {tn(tknq)} per {tn(tknb)} [{len(curves)} funcs]"
                        )

                result = tuple(sum_by_tkn[t] for t in tokens_t)
                if P("debug"):
                    print(f"sum_by_tkn={sum_by_tkn}")
                    print(f"result={result}")
                    print(f"<<<===================== [dtknfromp_f]")

                if asdct:
                    return sum_by_tkn, np.array(result)

                return np.array(result)
            ## END INNER FUNCTION

            # return the inner function if requested
            if result == self.MO_DTKNFROMPF:
                return dtknfromp_f

            # return debug info if requested
            if result == self.MO_DEBUG:
                return dict(
                    # price_estimates_all = price_estimates_all,
                    # price_estimates_d = price_estimates_d,
                    price_estimates_t=price_estimates_t,
                    tokens_t=tokens_t,
                    tokens_ix=tokens_ix,
                    pairs=pairs,
                    sfc=sfc,
                    targettkn=targettkn,
                    pairs_t=pairs_t,
                    dtknfromp_f=dtknfromp_f,
                    optimizer=self,
                )


            # setting up the optimization variables (note: we optimize in log space)
            if price_estimates_t is None:
                raise Exception(f"price estimates not found; try setting pstart")
            p = np.array(price_estimates_t, dtype=float)
            plog10 = np.log10(p)
            if P("verbose"):
                # dtkn_d, dtkn = dtknfromp_f(plog10, islog10=True, asdct=True)
                print("[margp_optimizer] pe  ", p)
                print("[margp_optimizer] p   ", ", ".join(f"{x:,.2f}" for x in p))
                print("[margp_optimizer] 1/p ", ", ".join(f"{1/x:,.2f}" for x in p))
                # print("[margp_optimizer] dtkn", dtkn)
                # if P("tknd"):
                #     print("[margp_optimizer] dtkn_d", dtkn_d)

            ## MAIN OPTIMIZATION LOOP
            for i in range(maxiter):

                if P("progress"):
                    print(
                        f"Iteration [{i:2.0f}]: time elapsed: {time.time()-start_time:.2f}s"
                    )

                # calculate the change in token amounts (also as dict if requested)
                if P("tknd"):
                    dtkn_d, dtkn = dtknfromp_f(plog10, islog10=True, asdct=True)
                else:
                    dtkn = dtknfromp_f(plog10, islog10=True, asdct=False)

                # calculate the Jacobian
                if P("debug"):
                    print("\n[margp_optimizer] ============= JACOBIAN =============>>>")
                J = self.J(dtknfromp_f, plog10)  
                    # ATTENTION: dtknfromp_f takes log10(p) as input
                if P("debug"):
                    print("==== J ====>")
                    print(J)
                    print("<=== J =====")
                    print("<<<============= JACOBIAN ============= [margp_optimizer]\n")
                
                # Update p, dtkn using the Newton-Raphson formula
                try:
                    dplog10 = np.linalg.solve(J, -dtkn)
                except np.linalg.LinAlgError:
                    if P("verbose") or P("debug"):
                        print("[margp_optimizer] singular Jacobian, using lstsq instead")
                    dplog10 = np.linalg.lstsq(J, -dtkn, rcond=None)[0]
                    # https://numpy.org/doc/stable/reference/generated/numpy.linalg.solve.html
                    # https://numpy.org/doc/stable/reference/generated/numpy.linalg.lstsq.html
                
                # update log prices, prices and determine the criterium...
                p0log10 = [*plog10]
                plog10 += dplog10
                p = np.exp(plog10 * np.log(10))
                criterium = np.linalg.norm(dplog10)
                
                # ...print out some info if requested...
                if P("verbose"):
                    print(f"\n[margp_optimizer] ========== cycle {i} =======>>>")
                    print("log p0", p0log10)
                    print("log dp", dplog10)
                    print("log p ", plog10)
                    print("p     ", tuple(p))
                    print("p     ", ", ".join(f"{x:,.2f}" for x in p))
                    print("1/p   ", ", ".join(f"{1/x:,.2f}" for x in p))
                    print("tokens_t", tokens_t)
                    # print("dtkn", dtkn)
                    print("dtkn", ", ".join(f"{x:,.3f}" for x in dtkn))
                    print(
                        f"[criterium={criterium:.2e}, eps={eps:.1e}, c/e={criterium/eps:,.0e}]"
                    )
                    if P("tknd"):
                        print("dtkn_d", dtkn_d)
                    if P("J"):
                        print("J", J)
                    print(f"<<<========== cycle {i} ======= [margp_optimizer]")

                # ...and finally check the criterium (percentage changes this step) for convergence
                if criterium < eps:
                    if i != 0:
                        # we don't break in the first iteration because we need this first iteration
                        # to establish a common baseline price, therefore d logp ~ 0 is not good
                        # in the first step                      
                        break
                    # else:
                    #     # we break in the first loop, so we restore the initial price estimates
                    #     # (if we do log10 / 10**p then we get results that are slightly off zero)
                    #     p = np.array(price_estimates_t, dtype=float)
            ## END MAIN OPTIMIZATION LOOP
            
            if i >= maxiter - 1:
                raise self.ConvergenceError(f"maximum number of iterations reached [{i}]")
            
            NOMR = lambda f: f if not result == self.MO_MINIMAL else None
                # this function screens out certain results when MO_MINIMAL [minimal output] is chosen
            dtokens_d, dtokens_t = dtknfromp_f(p, asdct=True, islog10=False)
            return self.MargpOptimizerResult(
                optimizer=NOMR(self),
                result=dtokens_d[targettkn],
                time=time.time() - start_time,
                targettkn=targettkn,
                curves=NOMR(curves_t),
                p_optimal=NOMR({tkn: p_ for tkn, p_ in zip(tokens_t, p)}),
                p_optimal_t=tuple(p),
                dtokens=NOMR(dtokens_d),
                dtokens_t=tuple(dtokens_t),
                tokens_t=tokens_t,
                n_iterations=i,
            )
        
        except self.OptimizationError as e:
            if P("debug") or P("verbose"):
                print(f"[margp_optimizer] exception occured {e}")
                
            if P("raiseonerror"):
                raise
            
            NOMR = lambda f: f
            return self.MargpOptimizerResult(
                optimizer=NOMR(self),
                result=None,
                time=time.time() - start_time,
                targettkn=targettkn,
                curves=NOMR(curves_t),
                p_optimal=None,
                p_optimal_t=None,
                dtokens=None,
                dtokens_t=None,
                tokens_t=tokens_t,
                n_iterations=i,
                errormsg=e,
            )

    @dataclass
    class TradeInstruction(_DCBase):
        """
        encodes a trade

        seen from the AMM; in numbers must be positive, out numbers negative
        """

        cid: any
        tknin: str
        amtin: float
        tknout: str
        amtout: float
        error: str = field(repr=True, default=None)
        curve: InitVar = None
        raiseonerror: InitVar = False

        POSNEGEPS = 1e-8

        def __post_init__(self, curve=None, raiseonerror=False):
            self.curve = curve
            if curve is not None:
                if self.cid != curve.cid:
                    err = f"curve/cid mismatch [{self.cid} vs {curve.cid}]"
                    self.error = err
                    if raiseonerror:
                        raise ValueError(err)
            if self.tknin == self.tknout:
                err = f"tknin and tknout must be different [{self.tknin} {self.tknout}]"
                self.error = err
                if raiseonerror:
                    raise ValueError(err)
            self.cid = str(self.cid)
            self.tknin = str(self.tknin)
            self.tknout = str(self.tknout)
            self.amtin = float(self.amtin)
            self.amtout = float(self.amtout)
            if not self.amtin * self.amtout < 0:
                if (
                    abs(self.amtin) < self.POSNEGEPS
                    and abs(self.amtout) < self.POSNEGEPS
                ):
                    self.amtin = 0
                    self.amtout = 0
                else:
                    err = f"amtin and amtout must be of different sign [{self.amtin} {self.tknin}, {self.amtout} {self.tknout}]"
                    self.error = err
                    if raiseonerror:
                        raise ValueError(err)

            if not self.amtin >= 0:
                err = f"amtin must be positive [{self.amtin}]"  # seen from AMM
                self.error = err
                if raiseonerror:
                    raise ValueError(err)
            
            if not self.amtout <= 0:
                err = f"amtout must be negative [{self.amtout}]"  # seen from AMM
                self.error = err
                if raiseonerror:
                    raise ValueError(err)

        TIEPS = 1e-10

        @classmethod
        def new(cls, curve_or_cid, tkn1, amt1, tkn2, amt2, *, eps=None, raiseonerror=False):
            """automatically determines which is in and which is out"""
            try:
                cid = curve_or_cid.cid
                curve = curve_or_cid
            except:
                cid = curve_or_cid
                curve = None
            if eps is None:
                eps = cls.TIEPS
            if amt1 > 0:
                newobj = cls(
                    cid=cid,
                    tknin=tkn1,
                    amtin=amt1,
                    tknout=tkn2,
                    amtout=amt2,
                    curve=curve,
                    raiseonerror=raiseonerror,
                )
            else:
                newobj = cls(
                    cid=cid,
                    tknin=tkn2,
                    amtin=amt2,
                    tknout=tkn1,
                    amtout=amt1,
                    curve=curve,
                    raiseonerror=raiseonerror,
                )

            return newobj

        @property
        def is_empty(self):
            """returns True if this is an empty trade instruction (too close to zero)"""
            return self.amtin == 0 or self.amtout == 0

        @classmethod
        def to_dicts(cls, trade_instructions):
            """converts iterable ot TradeInstruction objects to a list of dicts"""
            return [ti.asdict() for ti in trade_instructions]

        @classmethod
        def to_df(cls, trade_instructions, ti_format=None):
            """converts iterable ot TradeInstruction objects to a pandas dataframe"""
            if ti_format is None:
                ti_format = cls.TIF_DF
            dicts = (
                {
                    "cid": ti.cid,
                    "pair": ti.curve.pair if not ti.curve is None else "",
                    "pairp": ti.curve.pairp if not ti.curve is None else "",
                    "tknin": ti.tknin,
                    "tknout": ti.tknout,
                    ti.tknin: ti.amtin,
                    ti.tknout: ti.amtout,
                }
                for ti in trade_instructions
            )
            df = pd.DataFrame.from_dict(list(dicts)).set_index("cid")
            if ti_format == cls.TIF_DFRAW:
                return df
            if ti_format == cls.TIF_DFAGGR:
                df1r = df[df.columns[4:]]
                df1 = df1r.fillna(0)
                dfa = df1.sum().to_frame(name="TOTAL NET").T
                dfp = df1[df1 > 0].sum().to_frame(name="AMMIn").T
                dfn = df1[df1 < 0].sum().to_frame(name="AMMOut").T
                return pd.concat([df1r, dfp, dfn, dfa], axis=0)
                return df1, dfa
            if ti_format == cls.TIF_DFP:
                return df.fillna("")
            raise ValueError(f"unknown format {ti_format}")

        TIF_OBJECTS = TIF_OBJECTS
        TIF_DICTS = TIF_DICTS
        TIF_DFP = TIF_DFP
        TIF_DFRAW = TIF_DFRAW
        TIF_DFAGGR = TIF_DFAGGR
        TIF_DF = TIF_DF

        @classmethod
        def to_format(cls, trade_instructions, ti_format=None):
            """converts iterable ot TradeInstruction objects to the given format (TIF_XXX)"""
            if ti_format is None:
                ti_format = cls.TIF_OBJECTS
            if ti_format == cls.TIF_OBJECTS:
                return tuple(trade_instructions)
            elif ti_format == cls.TIF_DICTS:
                return cls.to_dicts(trade_instructions)
            elif ti_format[:2] == "df":
                trade_instructions = tuple(trade_instructions)
                if len(trade_instructions) == 0:
                    return pd.DataFrame()
                return cls.to_df(trade_instructions, ti_format=ti_format)
            else:
                raise ValueError(f"unknown format {ti_format}")

        @property
        def price_outperin(self):
            return -self.amtout / self.amtin

        p = price_outperin

        @property
        def price_inperout(self):
            return -self.amtin / self.amtout

        pr = price_inperout

        @property
        def prices(self):
            return (self.price_outperin, self.price_inperout)

        pp = prices

    TIF_OBJECTS = TIF_OBJECTS
    TIF_DICTS = TIF_DICTS
    TIF_DFP = TIF_DFP
    TIF_DFRAW = TIF_DFRAW
    TIF_DFAGGR = TIF_DFAGGR
    TIF_DF = TIF_DF
    
    @dataclass
    class MargpOptimizerResult(OptimizerBase.OptimizerResult):
        """
        results of the simple optimizer

        :p_optimal:         optimal p values

        """
        TIF_OBJECTS = TIF_OBJECTS
        TIF_DICTS = TIF_DICTS
        TIF_DFP = TIF_DFP
        TIF_DFRAW = TIF_DFRAW
        TIF_DFAGGR = TIF_DFAGGR
        TIF_DF = TIF_DF

        curves: list = field(repr=False, default=None)
        targettkn: str = field(repr=True, default=None)
        p_optimal: dict = field(repr=False, default=None)
        p_optimal_t: tuple = field(repr=True, default=None)
        n_iterations: int = field(repr=False, default=None)
        dtokens: dict = field(repr=False, default=None)
        dtokens_t: tuple = field(repr=True, default=None)
        tokens_t: tuple = field(repr=True, default=None)
        errormsg: str = field(repr=True, default=None)

        def __post_init__(self, *args, **kwargs):
            super().__post_init__(*args, **kwargs)
            # #print("[MargpOptimizerResult] post_init")
            assert (
                self.p_optimal_t is not None or self.errormsg is not None
            ), "p_optimal_t must be set unless errormsg is set"
            if self.method is None:
                self.method = "margp"
            self.raiseonerror = False

        @property
        def is_error(self):
            return self.errormsg is not None

        def detailed_error(self):
            return self.errormsg

        def status(self):
            return "error" if self.is_error else "converged"

        def price(self, tknb, tknq):
            """returns the optimal price of tknb/tknq based on p_optimal [in tknq per tknb]"""
            assert (
                self.p_optimal is not None
            ), "p_optimal must be set [do not use minimal results]"
            return self.p_optimal.get(tknb, 1) / self.p_optimal.get(tknq, 1)

        def dxdyvalues(self, asdict=False):
            """
            returns a vector of (dx, dy) values for each curve
            """
            assert (
                self.curves is not None
            ), "curves must be set [do not use minimal results]"
            assert self.is_error is False, "cannot get this data from an error result"
            result = (
                (c.cid, c.dxdyfromp_f(self.price(c.tknb, c.tknq))[0:2])
                for c in self.curves
            )
            if asdict:
                return {cid: dxdy for cid, dxdy in result}
            return tuple(dxdy for cid, dxdy in result)

        @property
        def dxvalues(self):
            return tuple(dx for dx, dy in self.dxdyvalues())

        @property
        def dyvalues(self):
            return tuple(dy for dx, dy in self.dxdyvalues())

        @property
        def curves_new(self):
            """returns a list of Curve objects the trade instructions implemented"""
            assert (
                self.optimizer is not None
            ), "optimizer must be set [do not use minimal results]"
            assert self.is_error is False, "cannot get this data from an error result"
            return self.optimizer.adjust_curves(dxvals=self.dxvalues)

        def trade_instructions(self, ti_format=None):
            """
            returns list of TradeInstruction objects
            
            :ti_format:     TIF_OBJECTS, TIF_DICTS, TIF_DFP, TIF_DFRAW, TIF_DFAGGR, TIF_DF
            """
            try:
                assert self.curves is not None, "curves must be set [do not use minimal results]"
                assert self.is_error is False, "cannot get this data from an error result"
                result = (
                    CPCArbOptimizer.TradeInstruction.new(
                        curve_or_cid=c, tkn1=c.tknx, amt1=dx, tkn2=c.tkny, amt2=dy
                    )
                    for c, dx, dy in zip(self.curves, self.dxvalues, self.dyvalues)
                    if dx != 0 or dy != 0
                )
                return CPCArbOptimizer.TradeInstruction.to_format(result, ti_format)
            except AssertionError:
                if self.raiseonerror:
                    raise
                return None

    def adjust_curves(self, dxvals, *, verbose=False, raiseonerror=False):
        """
        returns a new curve container with the curves shifted by the given dx values
        """
        # print("[adjust_curves]", dxvals)
        if dxvals is None:
            if raiseonerror:
                raise ValueError("dxvals is None")
            else:
                print("[adjust_curves] dxvals is None")
                return None
        curves = self.curve_container
        try:
            newcurves = [
                c.execute(dx=dx, verbose=verbose, ignorebounds=True)
                for c, dx in zip(curves, dxvals)
            ]
            return CPCContainer(newcurves)
        except Exception as e:
            if raiseonerror:
                raise e
            else:
                print(f"Error in adjust_curves: {e}")
                # raise e
                return None

    def plot(self, *args, **kwargs):
        """
        convenience for self.curve_container.plot()

        see help(CPCContainer.plot) for details
        """
        return self.curve_container.plot(*args, **kwargs)

    def format(self, *args, **kwargs):
        """
        convenience for self.curve_container.format()

        see help(CPCContainer.format) for details
        """
        return self.curve_container.format(*args, **kwargs)

