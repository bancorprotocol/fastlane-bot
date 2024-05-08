"""
Defines the Bancor V3 triangular arbitrage finder class

[DOC-TODO-OPTIONAL-longer description in rst format]

---
(c) Copyright Bprotocol foundation 2023-24.
All rights reserved.
Licensed under MIT.
"""
import math
from typing import Union, List, Tuple, Any, Iterable

from arb_optimizer import CurveContainer, MargPOptimizer, ConstantProductCurve

from fastlane_bot.modes.base_triangle import ArbitrageFinderTriangleBase


class ArbitrageFinderTriangleBancor3TwoHop(ArbitrageFinderTriangleBase):
    """
    Bancor V3 triangular arbitrage finder mode
    """

    arb_mode = "b3_two_hop"

    def find_arbitrage(self, candidates: List[Any] = None, ops: Tuple = None, best_profit: float = 0, profit_src: float = 0) -> Union[List, Tuple]:
        """
        see base.py
        """
        if self.base_exchange != "bancor_v3":
            self.ConfigObj.logger.warning(
                f"base_exchange must be bancor_v3 for {self.arb_mode}, setting it to bancor_v3"
            )
            self.base_exchange = "bancor_v3"

        self.ConfigObj.logger.info(
            f"flashloan_tokens for arb_mode={self.arb_mode} will be overwritten. "
        )

        self._check_limit_flashloan_tokens_for_bancor3()

        if candidates is None:
            candidates = []

        # Get combinations of flashloan tokens
        combos = self.get_combos(
            self.flashloan_tokens, self.CCm, arb_mode=self.arb_mode
        )

        # Get the miniverse combinations
        all_miniverses = self.get_miniverse_combos(combos)

        if len(all_miniverses) == 0:
            return None

        # Check each source token and miniverse combination
        for src_token, miniverse in all_miniverses:
            r = None

            try:
                # Run main flow with the new set of curves
                (
                    profit_src,
                    trade_instructions,
                    trade_instructions_df,
                    trade_instructions_dic,
                ) = self.run_main_flow(miniverse, src_token)

            except Exception:
                continue
            if trade_instructions_dic is None:
                continue
            if len(trade_instructions_dic) < 3:
                continue
            # Get the candidate ids
            cids = [ti["cid"] for ti in trade_instructions_dic]

            # Calculate the profit
            profit = self.calculate_profit(src_token, profit_src, self.CCm, cids)

            if str(profit) == "nan":
                self.ConfigObj.logger.debug("profit is nan, skipping")
                continue

            # Handle candidates based on conditions
            candidates += self.handle_candidates(
                best_profit,
                profit,
                trade_instructions_df,
                trade_instructions_dic,
                src_token,
                trade_instructions,
            )

            # Find the best operations
            best_profit, ops = self.find_best_operations(
                best_profit,
                ops,
                profit,
                trade_instructions_df,
                trade_instructions_dic,
                src_token,
                trade_instructions,
            )

        return candidates if self.result == self.AO_CANDIDATES else ops

    def get_tkn(self, pool: Any, tkn_num: int) -> str:
        """
        Gets the token ID from a pool object

        Parameters
        ----------
        pool: ConstantProductCurve
            The ConstantProductCurve object
        tkn_num: int
            The token number to get, either 0 or 1

        Returns
        -------
        str
        """
        return pool.pair.split("/")[tkn_num]

    @staticmethod
    def get_fee_safe(fee: int or float):
        """
        Fixes the format of the fee if the fee is in PPM format

        Parameters
        ----------
        fee: int or float

        Returns
        -------
        float
        """
        if fee > 1:
            fee = fee / 1000000
        return fee

    def get_exact_pools(self, cids: List[str]) -> List[CurveContainer]:
        """
        Gets the specific pools that will be used for calculations. It does this inefficiently to preserve the order.

        Parameters
        ----------
        cids: List

        Returns
        -------
        List
        """

        pools = [curve for curve in self.CCm if curve.cid == cids[0]]
        pools += [curve for curve in self.CCm if curve.cid == cids[1]]
        pools += [curve for curve in self.CCm if curve.cid == cids[2]]
        return pools

    def get_optimal_arb_trade_amts(self, cids: List[str], flt: str) -> float:
        """
        Gets the optimal trade 0 amount for a triangular arb cycle

        Parameters
        ----------
        cids: List
        flt: str

        Returns
        -------
        float
        """
        pools = self.get_exact_pools(cids=cids)
        tkn1 = self.get_tkn(pool=pools[0], tkn_num=1) if self.get_tkn(pool=pools[0], tkn_num=1) != flt else self.get_tkn(pool=pools[0], tkn_num=0)
        p0t0 = pools[0].x if self.get_tkn(pool=pools[0], tkn_num=0) == flt else pools[0].y
        p0t1 = pools[0].y if self.get_tkn(pool=pools[0], tkn_num=0) == flt else pools[0].x
        p1t0 = pools[1].x if tkn1 == self.get_tkn(pool=pools[1], tkn_num=0) else pools[1].y
        p1t1 = pools[1].y if tkn1 == self.get_tkn(pool=pools[1], tkn_num=0) else pools[1].x
        p2t0 = pools[2].x if self.get_tkn(pool=pools[2], tkn_num=0) != flt else pools[2].y
        p2t1 = pools[2].y if self.get_tkn(pool=pools[2], tkn_num=0) != flt else pools[2].x
        fee0 = self.get_fee_safe(pools[0].fee)
        fee1 = self.get_fee_safe(pools[1].fee)
        fee2 = self.get_fee_safe(pools[2].fee)

        if pools[1].params.exchange in self.ConfigObj.CARBON_V1_FORKS:
            return self.get_exact_input_with_carbon(p0t0, p0t1, p2t0, p2t1, pools[1])

        return self.max_arb_trade_in_constant_product(p0t0, p0t1, p1t0, p1t1, p2t0, p2t1, fee0=fee0, fee1=fee1, fee2=fee2)

    def get_exact_input_with_carbon(self, p0t0: float, p0t1: float, p2t0: float, p2t1: float, carbon_pool: ConstantProductCurve) -> float:
        """
        Gets the optimal trade 0 amount for a triangular arb cycle with a single Carbon order in the middle

        Parameters
        ----------
        p0t0: float
        p0t1: float
        p2t0: float
        p2t1: float
        carbon_pool: ConstantProductCurve

        Returns
        -------
        float
        """
        y = carbon_pool.y
        z = carbon_pool.z
        A = carbon_pool.A
        B = carbon_pool.B
        C = (B * z + A * y) ** 2
        D = B * A * z + A ** 2 * y
        return self.max_arb_trade_in_cp_carbon_cp(p0t0, p0t1, p2t0, p2t1, C, D, z)

    @staticmethod
    def max_arb_trade_in_cp_carbon_cp(p0t0: float, p0t1: float, p2t0: float, p2t1: float, C: float, D: float, z: float) -> float:
        """
        Equation to solve optimal trade input for a constant product -> Carbon order -> constant product route.
        Parameters
        ----------
        p0t0: float
        p0t1: float
        p2t0: float
        p2t1: float
        C: float
        D: float
        z: float
        Returns
        -------
        float

        """
        trade_input = (z * (-p0t0 * p2t0 * z + math.sqrt(C * p0t0 * p2t0 * p0t1 * p2t1))) / (p0t1 * C + p0t1 * D * p2t0 + z ** 2 * p2t0)
        return trade_input

    @staticmethod
    def max_arb_trade_in_constant_product(p0t0, p0t1, p1t0, p1t1, p2t0, p2t1, fee0, fee1, fee2):
        """
        Equation to solve optimal trade input for a constant product -> constant product -> constant product route.
        Parameters
        ----------
        p0t0: float
        p0t1: float
        p1t0: float
        p1t1: float
        p2t0: float
        p2t1: float
        fee0: float
        fee1: float
        fee2: float
        Returns
        -------
        float

        """
        val = (-p1t0*p2t0*p0t0 + (p1t0*p2t0*p0t0*p1t1*p2t1*p0t1*(-fee1*fee2*fee0 + fee1*fee2 + fee1*fee0 - fee1 + fee2*fee0 - fee2 - fee0 + 1)) ** 0.5)/(p1t0*p2t0 - p2t0*p0t1*fee0 + p2t0*p0t1 + p1t1*p0t1*fee1*fee0 - p1t1*p0t1*fee1 - p1t1*p0t1*fee0 + p1t1*p0t1)
        return val

    def run_main_flow(self,
        miniverse: List, src_token: str
    ) -> Tuple[float, Any, Any, Any]:
        """
        Run the main flow of the arbitrage finder.

        Parameters
        ----------
        miniverse : list
            List of curves.
        src_token : str
            Source token.

        Returns
        -------
        tuple
            Tuple of profit, trade instructions, trade instructions dataframe and trade instructions dictionary.

        """

        # Instantiate the container and optimizer objects
        CC_cc = CurveContainer(miniverse)
        O = MargPOptimizer(CC_cc)
        pstart = self.build_pstart(CC_cc, CC_cc.tokens(), src_token)
        # Perform the optimization
        r = O.optimize(src_token, pstart=pstart, params=dict())

        # Get the profit in the source token
        profit_src = -r.result

        # Get trade instructions in different formats
        trade_instructions_df = r.trade_instructions(O.TIF_DFAGGR)
        trade_instructions_dic = r.trade_instructions(O.TIF_DICTS)
        trade_instructions = r.trade_instructions()

        return (
            profit_src,
            trade_instructions,
            trade_instructions_df,
            trade_instructions_dic,
        )

    def get_miniverse_combos(self, combos: Iterable) -> List[Tuple[str, List]]:
        """
        Get the miniverse combinations for a list of token pairs.

        Parameters
        ----------
        combos : list
            List of token pairs.

        Returns
        -------
        list
            List of miniverse combinations.

        """
        all_miniverses = []
        for tkn0, tkn1 in combos:
            external_curves = self.CCm.bypairs(f"{tkn0}/{tkn1}")
            external_curves += self.CCm.bypairs(f"{tkn1}/{tkn0}")
            external_curves = list(set(external_curves))
            carbon_curves = [
                curve
                for curve in external_curves
                if curve.params.get("exchange") in self.ConfigObj.CARBON_V1_FORKS
            ]
            external_curves = [
                curve
                for curve in external_curves
                if curve.params.get("exchange") not in self.ConfigObj.CARBON_V1_FORKS
            ]
            if not external_curves and not carbon_curves:
                continue

            bancor_v3_curve_0 = (
                self.CCm.bypairs(f"{self.ConfigObj.BNT}/{tkn0}")
                .byparams(exchange="bancor_v3")
                .curves
            )
            bancor_v3_curve_1 = (
                self.CCm.bypairs(f"{self.ConfigObj.BNT}/{tkn1}")
                .byparams(exchange="bancor_v3")
                .curves
            )
            if bancor_v3_curve_0 is None or bancor_v3_curve_1 is None:
                continue
            if len(bancor_v3_curve_0) == 0 or len(bancor_v3_curve_1) == 0:
                continue

            miniverses = []
            if len(external_curves) > 0:
                for curve in external_curves:
                    miniverses += [bancor_v3_curve_0 + bancor_v3_curve_1 + [curve]]
            if len(carbon_curves) > 0:

                if len(carbon_curves) > 0:
                    base_direction_pair = carbon_curves[0].pair
                    base_direction_one = [curve for curve in carbon_curves if curve.pair == base_direction_pair]
                    base_direction_two = [curve for curve in carbon_curves if curve.pair != base_direction_pair]

                    if len(base_direction_one) > 0:
                        miniverses += [bancor_v3_curve_0 + bancor_v3_curve_1 + base_direction_one]

                    if len(base_direction_two) > 0:
                        miniverses += [bancor_v3_curve_0 + bancor_v3_curve_1 + base_direction_two]

                miniverses += [bancor_v3_curve_0 + bancor_v3_curve_1 + carbon_curves]

            if len(miniverses) > 0:
                all_miniverses += list(zip([tkn1] * len(miniverses), miniverses))
        return all_miniverses
