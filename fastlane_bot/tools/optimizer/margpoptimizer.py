"""
Implements the "Marginal Price Optimization" method for arbitrage and routing


The marginal price optimizer implicitly solves the
optimization problem by always operating on the optimal
hyper surface, which is the surface where all marginal
prices of the same pair are equal, and all marginal prices
across pairs follow the usual no arbitrage condition.
Therefore the problem reduces to a goal seek -- we need to
find the point on that hyper surface that satisfies the
desired boundary conditions.

This method employs a Newton-Raphson algorithm to solve the
aforementioned goal seek problem.

---
This module is still subject to active research, and
comments and suggestions are welcome. The corresponding
author is Stefan Loesch <stefan@bancor.network>

(c) Copyright Bprotocol foundation 2023. 
Licensed under MIT
"""
__VERSION__ = "6.0-beta01"
__DATE__ = "04/May/2024"

import pandas as pd
import numpy as np
import time

from .cpcarboptimizer import CPCArbOptimizer

class MargPOptimizer(CPCArbOptimizer):
    """
    implements the marginal price optimization method
    """
    __VERSION__ = __VERSION__
    __DATE__ = __DATE__
    
    @property
    def kind(self):
        return "margp"
    
    @classmethod
    def jacobian(cls, func, x, *, jach=None):
        """
        computes the Jacobian of func at point x

        :func:  a callable x=(x1..xn) -> (y1..ym), taking and returning np.arrays
                must also take a `quiet` parameter, which, if True suppresses output
        :x:     a vector x=(x1..xn) as np.array
        :jach:  the h value for the derivative (Jacobian) calculation (default: cls.MOJACH)
        """
        h = cls.MO_JACH if jach is None else jach
        n = len(x)
        y = func(x, quiet=True)
        jac = np.zeros((n, n))
        for j in range(n):  # through columns to allow for vector addition
            Dxj = abs(x[j]) * h if x[j] != 0 else h
            x_plus = [(xi if k != j else xi + Dxj) for k, xi in enumerate(x)]
            jac[:, j] = (func(x_plus, quiet=True) - y) / Dxj
        return jac
    J = jacobian
    
    MO_DEBUG = "debug"
    MO_PSTART = "pstart"
    MO_P = MO_PSTART
    MO_DTKNFROMPF = "dtknfrompf"
    MO_MINIMAL = "minimal"
    MO_FULL = "full"
    
    MO_MODE_REL = "rel"      # relative convergence criterion used
    MO_MODE_ABS = "abs"      # ditto absolute
    MO_NORML1 = 1            # L1 norm (sum of absolute values)
    MO_NORML2 = 2            # L2 norm (Euclidean distance)
    MO_NORMLINF = np.inf     # L-infinity norm (maximum absolute value)
    
    MO_JACH = 1e-5           # default step size for calculating Jacobian
    MO_MAXITER = 50          # maximum number of iterations
    MO_EPSR = 1e-6           # relative convergence threshold
    MO_EPSA = 1              # absolute convergence threshold (unit: MOCAUNIT)
    MO_EPSAUNIT = "USD"      # absolute convergence unit
    
    
    class OptimizationError(Exception): pass
    class ConvergenceError(OptimizationError): pass
    class ParameterError(OptimizationError): pass
    
    @classmethod
    def norml1_f(cls, x):
        """the L1 norm of a vector x"""
        return np.linalg.norm(x, ord=1)
    
    @classmethod
    def norml2_f(cls, x):
        """the L2 norm of a vector x"""
        return np.linalg.norm(x, ord=2)
    
    @classmethod
    def normlinf_f(cls, x):
        """the Linf norm of a vector x"""
        return np.linalg.norm(x, ord=np.inf)

    def optimize(self, sfc=None, *, pstart=None, mode=None, result=None, params=None):
        """
        optimal transactions across all curves in the optimizer, extracting targettkn (1)

        :sfc:               the self financing constraint to use (2)
        :pstart:            dict or tuple of starting price for optimization (3)
        :mode:              mode of operation (MO_MODE_REL for relative convergence, or 
                            MO_MODE_ABS for absolute)
        :result:            the result type (see MO_XXX constants below) (4)
        :params:            dict of optional parameters (see table below) (4)


        :returns:           MargpOptimizerResult on the default path, others depending on the
                            chosen result
        
        Meaning of the `result` parameter:    
                        
        ==============  ============================================================
        `result`        returns
        ==============  ============================================================
        None            alias for MO_FULL (default; use unless you know better)
        MO_FULL         full result
        MO_MINIMAL      minimal result (omitting some big fields)
        MO_DEBUG        a number of items useful for debugging
        MO_PSTART       price estimates (as dataframe)
        MO_DTKNFROMPF   the function calculating dtokens from p
        ==============  ============================================================
        
        
        Meaning of the `params` parameter:
        
        ==================  =========================================================================
        parameter           meaning
        ==================  =========================================================================
        jach                step size for calculating Jacobian (default: MO_JACH)
        maxiter             maximum number of iterations (default: 100)
        epsr                relative convergence threshold (default: MO_EPSR)
        epsa                absolute convergence threshold (default: MO_EPSA)
        epsaunit            unit for epsa (default: MO_EPSAUNIT)
        norm                norm for convergence crit (MO_NORML1, MO_NORML2, MO_NORMLINF)
        progress            if True, print progress output
        verbose             ditto, high level output
        debug               ditto, basic debug output
        debug_j             ditto, additional debug output (Jacobian)
        debug_dtkn          ditto (d Token)
        debug_dtkn2         ditto (more d Token; requires debug_dtkn)
        debug_dtknd         ditto, d Token as dict  
        debug_pe            ditto, price estimates
        debug_curves        dump curves to stdout (takes DC_XXX constants)
        raiseonerror        if True, raise an OptimizationError exception on error
        ==================  =========================================================================
    
        NOTE 1: this optimizer uses the marginal price method, ie it solves the equation

            dx_i (p) = 0 for all i != targettkn, and the whole price vector p

        NOTE 2: at the moment only the trivial self-financing constraint is allowed, ie the one that
        only specifies the target token, and where all other constraints are zero; if sfc is
        a string then this is interpreted as the target token and this currently the expected use
        
        NOTE 3: ``pstart`` can be provided either as dict {tkn:p, ...}, or as df as price estimate as 
        returned by MO_PSTART; excess tokens can be provided but all required tokens 
        must be present
        
        NOTE 4: In production use, the `result` parameter should always be set to None to ensure
        that the default pathway is taken. Similarly, the `params` dict should be empty, except
        for the `debug` related options for debug output
        """
        start_time = time.time()
        
        # data conversion: string to SFC object; note that anything but pure arb not currently supported
        if isinstance(sfc, str):
            sfc = self.arb(targettkn=sfc)
        assert sfc.is_arbsfc(), "only pure arbitrage SFC are supported at the moment"
        targettkn = sfc.optimizationvar
        
        # lambdas
        P      = lambda item: params.get(item, None) if params is not None else None
        #get     = lambda p, ix: p[ix] if ix is not None else 1       # safe get from tuple
        # dxdy_f = lambda r: (np.array(r[0:2]))                       # extract dx, dy from result
        # tn     = lambda t: t.split("-")[0]                          # token name, eg WETH-xxxx -> WETH
        
        
        # epsilons and maxiter
        epsr = P("epsr") or self.MO_EPSR
        epsa = P("epsa") or self.MO_EPSA
        epsaunit = P("epsaunit") or self.MO_EPSAUNIT
        jach = P("jach") or self.MO_JACH
        maxiter = P("maxiter") or self.MO_MAXITER
        
        # curves, tokens and pairs
        curves_t = self.curve_container
        if len (curves_t) == 0:
            raise self.ParameterError("no curves found")
        if len (curves_t) == 1:
            raise self.ParameterError(f"can't run arbitrage on single curve {curves_t}")
            
        alltokens_s = self.curve_container.tokens()
        if not targettkn in alltokens_s:
            raise self.ParameterError(f"targettkn {targettkn} not in {alltokens_s}")
            
        tokens_t = tuple(t for t in alltokens_s if t != targettkn) # all _other_ tokens...
        tokens_ix = {t: i for i, t in enumerate(tokens_t)}         # ...with index lookup
        pairs = self.curve_container.pairs(standardize=False)
        curves_by_pair = {pair: tuple(c for c in curves_t if c.pair == pair) for pair in pairs }
        pairs_t = tuple(tuple(p.split("/")) for p in pairs)

        # dump curves if requested
        if P("debug_curves"):
            print("\n[margp_optimizer]\n================ CURVES ================>>>")
            print("[")
            self.dump_curves(mode=P("dump_curves"))
            print("]")
            print("<<<<<================ CURVES ================\n")

        if P("verbose") or P("debug"):
            print(f"[margp_optimizer] targettkn = {targettkn}")
        
        # legacy paramters handling (pstart, crit)
        if not pstart is None:
            assert P("pstart") is None, "pstart must not be in params dict if pstart is provided as argument"
        else:
            pstart = P("pstart")
            if not P("pstart") is None:
                print(f"[margp_optimizer] WARNING - providing `pstart` as parameter is deprecated; use `pstart` variable instead")

        # pstart
        if not pstart is None:
            if P("debug"):
                print(f"[margp_optimizer] using pstart [{len(P('pstart'))} tokens]")
            if isinstance(pstart, pd.DataFrame):
                try:
                    pstart = pstart.to_dict()[targettkn]
                except Exception as e:
                    raise Exception(f"error while converting dataframe pstart to dict: {e}", pstart, targettkn)
                assert isinstance(pstart, dict), f"pstart must be a dict or a data frame [{pstart}]"
            try: 
                price_estimates_t = tuple(pstart[t] for t in tokens_t)
            except KeyError as e:
                raise Exception(f"pstart does not contain all required tokens [{e}; pstart={pstart}, tokens_t={tokens_t}]")
        else:
            if P("debug"):
                print("[margp_optimizer] calculating price estimates")
                print(f"[margp_optimizer] tknq={targettkn}, tknbs={tokens_t}")
            
            try:
                price_estimates_t = self.price_estimates(
                    tknq=targettkn, 
                    tknbs=tokens_t, 
                    verbose=P("debug_pe"),
                    triangulate=True,
                )
            except Exception as e:
                if P("verbose") or P("debug"):
                    print(f"[margp_optimizer] error calculating price estimates: [{e}]")
                price_estimates_t = None
                if not result in [self.MO_PSTART, self.MO_DEBUG]:
                    raise
        
        if P("debug"):
            print("[margp_optimizer] price estimates = ", price_estimates_t)
        
        if result == self.MO_PSTART:
            df = pd.DataFrame(price_estimates_t, index=tokens_t, columns=[targettkn])
            df.index.name = "tknb"
            return df
            
        # criterion and norm
        assert P("crit") is None, "crit must not be in params dict; use `mode`"
        crit = mode or self.MO_MODE_REL
        assert crit in set((self.MO_MODE_REL, self.MO_MODE_ABS)), f"crit must be {self.MO_MODE_REL} or {self.MO_MODE_ABS}"
        if crit == self.MO_MODE_ABS:
            assert not pstart is None, "pstart must be provided if crit is MO_MODE_ABS"
            assert epsaunit in pstart, f"epsaunit {epsaunit} not in pstart {P('pstart')}"
            p_targettkn_per_epsaunit = pstart[epsaunit]/pstart[targettkn]
            if P("debug"):
                print(f"[margp_optimizer] 1 epsaunit [{epsaunit}] = {p_targettkn_per_epsaunit:,.4f} target [{targettkn}]")
        crit_is_relative = crit == self.MO_MODE_REL
        eps_used = epsr if crit_is_relative else epsa
        eps_unit = 1 if crit_is_relative else epsaunit
        
        norm = P("norm") or self.MO_NORML2
        assert norm in set((self.MO_NORML1, self.MO_NORML2, self.MO_NORMLINF)), f"norm must be MO_NORML1, MO_NORML2 or MO_NORMLINF [{norm}]"
        normf = lambda x: np.linalg.norm(x, ord=norm)
        
        if P("verbose") or P("debug"):
            print(f"[margp_optimizer] crit={crit} (eps={eps_used}, unit={eps_unit}, norm=L{norm})")
                
        ## INNER FUNCTION: CALCULATE THE TARGET FUNCTION
        def dtknfromp_f(p, *, islog10=True, asdct=False, quiet=False):
            """
            calculates the aggregate change in token amounts for a given price vector

            :p:         price vector, where prices use the reference token as quote token
                        this vector is an np.array, and the token order is the same as in tokens_t
            :islog10:   if True, p is interpreted as log10(p)
            :asdct:     if True, the result is returned as dict AND tuple, otherwise as np.array
            :quiet:     if overrides P("debug") etc, eg for calc of Jacobian
            :returns:   if asdct is False, a tuple of the same length as tokens_t detailing the
                        change in token amounts for each token except for the target token (ie the
                        quantity with target zero; if asdct is True, that same information is
                        returned as dict, including the target token.
            """
            p = np.array(p, dtype=np.float64)
            if islog10:
                p = np.exp(p * np.log(10))
            assert len(p) == len(tokens_t), f"p and tokens_t have different lengths [{p}, {tokens_t}]"
            if P("debug_dtkn") and not quiet:
                print(f"\n[dtknfromp_f]\ndtkn=================>>>")
                print(f"{targettkn:6}", ", ".join(tokens_t))
                print( "p     ", ", ".join(f"{x:,.2f}" for x in p))
                print( "1/p   ", ", ".join(f"{1/x:,.2f}" for x in p))
            
            # pvec is dict {tkn -> (log) price} for all tokens in p
            pvec = {tkn: p_ for tkn, p_ in zip(tokens_t, p)}
            pvec[targettkn] = 1
            
            sum_by_tkn = {t: 0 for t in alltokens_s}
            for pair in pairs:
                #for pair, (tknb, tknq) in zip(pairs, pairs_t):
                # if get(p, tokens_ix.get(tknq)) > 0:
                #     price = get(p, tokens_ix.get(tknb)) / get(p, tokens_ix.get(tknq))
                # else:
                #     #print(f"[dtknfromp_f] warning: price for {pair} is unknown, using 1 instead")
                #     price = 1
                #curves = curves_by_pair[pair]
                # c0 = curves[0]
                #dxdy = tuple(dxdy_f(c.dxdyfromp_f(price)) for c in curves)
                
                dxvecs = (c.dxvecfrompvec_f(pvec) for c in curves_by_pair[pair])
                
                # if P("debug_dtkn2") and not quiet:
                #     dxdy = tuple(dxdy_f(c.dxdyfromp_f(price)) for c in curves)
                #         # TODO: rewrite this using the dxvec
                #         # there is no need to extract dy dx; just iterate over dict
                #         # however not urgent because this is debug code
                #     print(f"\n{c0.pairp} --->>")
                #     print(f" price={price:,.4f}, 1/price={1/price:,.4f}")
                #     for r, c in zip(dxdy, curves):
                #         s =  f" cid={c.cid[2:6]}{c.cid[-2:]}"
                #         s += f" dx={float(r[0]):15,.3f} {c.tknxp:>5}"
                #         s += f" dy={float(r[1]):15,.3f} {c.tknyp:>5}"
                #         s += f" p={c.p:,.2f} 1/p={1/c.p:,.2f}"
                #         print(s)
                #     print(f"<<--- {c0.pairp}")

                for dxvec in dxvecs:
                    for tkn, dx_ in dxvec.items():
                        sum_by_tkn[tkn] += dx_

            result = tuple(sum_by_tkn[t] for t in tokens_t)
            if P("debug_dtkn") and not quiet:
                print(f"\nsum_by_tkn={sum_by_tkn}")
                print(f"result={result}")
                print("      >", ", ".join(tokens_t))
                print(f"<<<=================dtkn")

            if asdct:
                return sum_by_tkn, np.array(result)

            return np.array(result)
        ## END INNER FUNCTION
        
        # return debug info if requested
        if result == self.MO_DEBUG:
            return dict(
                tokens_t=tokens_t,
                tokens_ix=tokens_ix,
                price_estimates_t = price_estimates_t,
                pairs=pairs,
                sfc=sfc,
                targettkn=targettkn,
                pairs_t=pairs_t,
                crit=dict(crit=crit, epsr=epsr, epsa=epsa, epsaunit=epsaunit, pstart=P("pstart")),
                dtknfromp_f = dtknfromp_f,
                optimizer=self,
            )
        
        # return the inner function if requested
        if result == self.MO_DTKNFROMPF:
            return dtknfromp_f
        
        
        try:
            
            # setting up the optimization variables (note: we optimize in log space)
            if price_estimates_t is None:
                raise Exception(f"price estimates not found; try setting pstart")
            p = np.array(price_estimates_t, dtype=float)
            plog10 = np.log10(p)
            if P("verbose") or P("debug"):
                print(f"\n[margp_optimizer] {targettkn} <-", ", ".join(tokens_t))
                print( "[margp_optimizer] p   ", ", ".join(f"{x:,.2f}" for x in p))
                print( "[margp_optimizer] 1/p ", ", ".join(f"{1/x:,.2f}" for x in p))
            
            if P("debug_j"):
                    print("\n[margp_optimizer]\n============= JACOBIAN% =============>>>")
                    print("tknq", targettkn)
                    for t in tokens_t:  
                        print(", ".join([f"d{t}/d%p{tt}" for tt in tokens_t]))
                    print("<<<============= JACOBIAN% =============\n")
                    
            # This outputs the explainer for the Jacobian which is defined as the change in token
            # flows with respect to change in log10 prices. The prices are all quoted in terms of 
            # the target token, here referred to as `tknq``. 
            
            # The Jacobian is multiplied by $log(1.01)$ to normalize for a 1% change in prices.
            # In the printout, 
                
            #     dUSDP/d%pLINK
                
            # corresponds to the change of USDP token amounts (measured in USDP tokens) with respect
            # to changes in price of LINK vs ETH for a 1% change in price.
            
            
            # For example, take this output here
            
            #     [margp_optimizer]
            #     ============= JACOBIAN% =============>>>
            #     tknq ETH
            #     dUSDP/d%pUSDP, dUSDP/d%pLINK
            #     dLINK/d%pUSDP, dLINK/d%pLINK
            #     <<<============= JACOBIAN% =============


            #     [margp_optimizer]
            #     ============= JACOBIAN% =============>>>
            #     [[-1704.90616999    98.21599834]
            #     [    6.93538284  -121.04274482]]
            #     <<<============= JACOBIAN% ============= 
                
            # It implies the if USDP increase by 1% against ETH (and LINK remains constant
            # against ETH) then the change in USDP token amounts is -1704.9 USDP tokens
            # and the change in LINK token amounts is 6.9 LINK tokens.  
            
            
            ## MAIN OPTIMIZATION LOOP
            for i in range(maxiter):

                if P("progress"):
                    print(f"\n[margp_optimizer] Iteration [{i:2.0f}]: time elapsed: {time.time()-start_time:.2f}s")
                
                # calculate the change in token amounts (also as dict if requested)
                if P("debug_dtknd"):
                    dtkn_d, dtkn = dtknfromp_f(plog10, islog10=True, asdct=True)
                else:
                    dtkn = dtknfromp_f(plog10, islog10=True, asdct=False)

                # calculate the Jacobian
                
                J = self.J(dtknfromp_f, plog10, jach=jach)  
                    # ATTENTION: dtknfromp_f takes log10(p) as input by default
                
                if P("debug_j"):
                    print("\n[margp_optimizer]\n============= JACOBIAN% =============>>>")
                    print(J*np.log10(1.01)) # normalises for 1% change in price
                    print("<<<============= JACOBIAN% =============\n")
                
                # Update p, dtkn using the Newton-Raphson formula
                try:
                    dplog10 = np.linalg.solve(J, -dtkn)
                
                except np.linalg.LinAlgError:
                    
                    if P("verbose") or P("debug"):
                        print("\n[margp_optimizer] singular Jacobian, using lstsq instead")
                    
                    dplog10 = np.linalg.lstsq(J, -dtkn, rcond=None)[0]
                        # https://numpy.org/doc/stable/reference/generated/numpy.linalg.solve.html
                        # https://numpy.org/doc/stable/reference/generated/numpy.linalg.lstsq.html
                
                # #### TODO: EXPERIMENTAL: ADD A DAMPING FACTOR TO THE JACOBIAN
                
                # #dplog10 = np.clip(dplog10, -0.1, 0.1)
                # nrm = normf(dplog10)
                # if nrm > 0.1:
                #     dplog10 /= nrm
                
                # #### END EXPERIMENTAL
                
                # update log prices, prices...
                p0log10 = [*plog10]                 # remember current log prices (deep copy)
                plog10 += dplog10                   # update log prices
                p = np.exp(plog10 * np.log(10))     # expand log to actual prices
                
                # determine the convergence criterium
                if crit_is_relative:
                    criterium = normf(dplog10)
                    # the relative criterium is the norm of the change in log prices
                    # in other words, it is something like an "average percentage change" of prices
                    # this may not quite what we want though because if we have highly levered curves,
                    # then even small percentage changes in prices can be important
                    # eg for limit orders the whole liquidity is by default distributed
                    # over a small range that may only be minrw=1e-6 wide
                    
                else:
                    p_in_epsaunit = p / p_targettkn_per_epsaunit 
                        # p is denominated in targettkn
                        # p_in_epsaunit in epsaunit
                    criterium = normf(dtkn*p_in_epsaunit)
                    if P("debug"):
                        print(f"[margp_optimizer] tokens_t={tokens_t} [{targettkn}]")
                        print(f"[margp_optimizer] dtkn={dtkn}")
                        print(f"[margp_optimizer] p={p} {targettkn}")
                        print(f"[margp_optimizer] p={p_in_epsaunit} {epsaunit}")
                        print(f"[margp_optimizer] crit=normf({dtkn*p_in_epsaunit}) = {criterium} {epsaunit}")
                
                # ...print out some info if requested...
                if P("verbose") or P("debug"):
                    print(f"\n[margp_optimizer]\n========== cycle {i} =======>>>")
                    print(f"{targettkn} <-", ", ".join(tokens_t))
                    print("dtkn  ", ", ".join(f"{x:,.3f}" for x in dtkn))
                    print("log p0", p0log10) # previous log prices
                    print("d logp", dplog10) # change in log prices
                    print("log p ", plog10)  # current log prices
                    print("p_t     ", tuple(p), targettkn)
                    print("p       ", ", ".join(f"{x:,.2f}" for x in p))
                    print("1/p     ", ", ".join(f"{1/x:,.2f}" for x in p))
                    print(f"crit     {criterium:.2e} [{eps_unit}; L{norm}], eps={eps_used}, c/e={criterium/eps_used:,.0e}]")
                    
                    if P("debug_dtknd"):
                        print("dtkn_d  ", dtkn_d)

                    print(f"<<<========== cycle {i} =======")

                # ...and finally check the criterium (percentage changes this step) for convergence
                if criterium < eps_used:
                    if i != 0:
                        # we don't break in the first iteration because we need this first iteration
                        # to establish a common baseline price, therefore d logp ~ 0 is not good
                        # in the first step                      
                        break
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
                #p_optimal=NOMR({tkn: p_ for tkn, p_ in zip(tokens_t, p)}),
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
            
            NOMR = lambda f: f if not result == self.MO_MINIMAL else None
            return self.MargpOptimizerResult(
                optimizer=NOMR(self),
                result=None,
                time=time.time() - start_time,
                targettkn=targettkn,
                curves=NOMR(curves_t),
                #p_optimal=None,
                p_optimal_t=None,
                dtokens=None,
                dtokens_t=None,
                tokens_t=tokens_t,
                n_iterations=None,
                errormsg=e,
            )
    margp_optimizer = optimize # margp_optimizer is deprecated
