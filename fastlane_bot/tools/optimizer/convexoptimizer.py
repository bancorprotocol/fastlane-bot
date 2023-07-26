"""
optimization library -- Convex Optimizer module [final optimizer class]

The convex optimizer explicitly solves the optimization problem by exploiting the fact
that the problem is convex. Whilst theoretically interesting, this method is complex,
slow and, importantly, converges badly on levered curves (eg Uniswap v3, Carbon). Whilst
we may continue research into this method, at this stage it is recommended to use the 
marginal price optimizer instead.

(c) Copyright Bprotocol foundation 2023. 
Licensed under MIT

This module is still subject to active research, and comments and suggestions are welcome. 
The corresponding author is Stefan Loesch <stefan@bancor.network>
"""
__VERSION__ = "5.0"
__DATE__ = "26/Jul/2023"

from dataclasses import dataclass, field, fields, asdict, astuple, InitVar
#import pandas as pd
import numpy as np

import time
# import math
import numbers
# import pickle
from ..cpc import ConstantProductCurve as CPC, CPCInverter, CPCContainer
# from sys import float_info

try:
    import cvxpy as cp
except:
    # if cvxpy is not installed on the system then the convex optimization methods will not work
    # however, the (superior) marginal price based methods will still work and we do not want to
    # force installation of an otherwise unused package onto the user's system
    cp = None

from .dcbase import DCBase
from .base import OptimizerBase
from .cpcarboptimizer import CPCArbOptimizer


@dataclass
class ScaledVariable(DCBase):
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



class ConvexOptimizer(CPCArbOptimizer):
    """
    implements the marginal price optimization method
    """
    
    @property
    def kind(self):
        return "convex"
    
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
        def detailed_error(self):
            """detailed error message"""
            if self.is_error:
                return f"ERROR: {self.status} {self.result}"
            return

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
                            :TIF_DF:            alias for :TIF_DFRAW:
                            :TIF_DFAGRR:        aggregated dataframe
                            :TIF_DFPG:          prices-and-gains analyis dataframe

            """
            result = (
                CPCArbOptimizer.TradeInstruction.new(
                    curve_or_cid=c, tkn1=c.tknx, amt1=dx, tkn2=c.tkny, amt2=dy
                )
                for c, dx, dy in zip(self.curves, self.dxvalues, self.dyvalues)
                if dx != 0 or dy != 0
            )
            #print("[trade_instructions] ti_format", ti_format)
            assert ti_format != CPCArbOptimizer.TIF_DFAGGR, "TIF_DFAGGR not implemented for convex optimization"
            assert ti_format != CPCArbOptimizer.TIF_DFPG, "TIF_DFPG not implemented for convex optimization"
            return CPCArbOptimizer.TradeInstruction.to_format(result, ti_format=ti_format)

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
        # "ECOS_BB": cp.ECOS_BB,
        # "OSQP": cp.OSQP,
        # "GUROBI": cp.GUROBI,
        # "MOSEK": cp.MOSEK,
        # "GLPK": cp.GLPK,
        # "GLPK_MI": cp.GLPK_MI,
        # "CPLEX": cp.CPLEX,
        # "XPRESS": cp.XPRESS,
        # "SCIP": cp.SCIP,
    }

    def convex_optimizer(self, sfc, **params):
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
    nofees_optimizer = convex_optimizer
    



    