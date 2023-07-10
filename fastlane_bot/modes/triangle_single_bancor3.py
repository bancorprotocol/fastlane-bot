# coding=utf-8
"""
Bancor V3 triangular arbitrage finder mode

(c) Copyright Bprotocol foundation 2023.
Licensed under MIT
"""
import math
from typing import Union, List, Tuple, Any, Iterable

from fastlane_bot.modes.base_triangle import ArbitrageFinderTriangleBase
from fastlane_bot.tools.cpc import CPCContainer, T
from fastlane_bot.tools.optimizer import CPCArbOptimizer


class ArbitrageFinderTriangleSingleBancor3(ArbitrageFinderTriangleBase):
    """
    Bancor V3 triangular arbitrage finder mode
    """

    arb_mode = "single_triangle_bancor3"

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
        self.flashloan_tokens = self.CCm.byparams(exchange="bancor_v3").tknys()

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

                # Get the cids of the carbon pools
                carbon_cids = [
                    curve.cid
                    for curve in miniverse
                    if curve.params.get("exchange") == "carbon_v1"
                ]

                if carbon_cids:

                    # Get the new set of curves
                    new_curves = self.get_mono_direction_carbon_curves(
                        miniverse=miniverse, trade_instructions_df=trade_instructions_df
                    )

                    # Rerun main flow with the new set of curves
                    (
                        profit_src,
                        trade_instructions,
                        trade_instructions_df,
                        trade_instructions_dic,
                    ) = self.run_main_flow(new_curves, src_token)
            except Exception:
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

    def get_optimal_arb_trade_amts(self, cids: [], flt: str):
        pools = []
        pools = [curve for curve in self.CCm if curve.cid == cids[0]]
        pools += [curve for curve in self.CCm if curve.cid == cids[1]]
        pools += [curve for curve in self.CCm if curve.cid == cids[2]]

        tkn0 = pools[0].pair.split("/")[0]
        tkn1 = pools[0].pair.split("/")[1]
        tkn2 = pools[1].pair.split("/")[0]
        tkn3 = pools[1].pair.split("/")[1]
        tkn4 = pools[2].pair.split("/")[1]
        tkn5 = pools[2].pair.split("/")[0]

        p0t0 = pools[0].x_act if tkn0 == flt else pools[0].y_act
        p0t1 = pools[0].y_act if tkn0 == flt else pools[0].x_act
        p2t1 = pools[2].x_act if tkn5 == flt else pools[2].y_act
        p2t0 = pools[2].y_act if tkn5 == flt else pools[2].x_act
        fee0 = 0
        fee2 = 0

        mid_exchange = pools[1].params.exchange

        if mid_exchange == "uniswap_v3":
            p1t0 = pools[1].x if tkn1 == tkn2 else pools[1].y
            p1t1 = pools[1].y if tkn1 == tkn2 else pools[1].x
            fee1 = pools[1].fee
            if fee1 > 1:
                fee1 = fee1 / 1000000
            return self.max_arb_trade_in_constant_product(p0t0, p0t1, p1t0, p1t1, p2t0, p2t1, fee0=fee0, fee1=fee1,
                                                          fee2=fee2)
        elif mid_exchange == "carbon_v1":
            carbon_pool = pools[1]
            y = carbon_pool.y
            z = carbon_pool.z
            A = carbon_pool.A
            B = carbon_pool.B
            C = (B * z + A * y) ** 2
            D = B * A * z + A ** 2 * y
            return self.max_arb_trade_in_cp_carbon_cp(p0t0, p0t1, p2t0, p2t1, C, D, z)

        else:
            p1t0 = pools[1].x_act if tkn1 == tkn2 else pools[1].y_act
            p1t1 = pools[1].y_act if tkn1 == tkn2 else pools[1].x_act
            fee1 = pools[1].fee
            if fee1 > 1:
                fee1 = fee1 / 1000000
            max_trade = self.max_arb_trade_in_constant_product(p0t0=p0t0, p0t1=p0t1, p1t0=p1t0, p1t1=p1t1, p2t0=p2t0, p2t1=p2t1, fee0=fee0, fee1=fee1, fee2=fee2)
            return max_trade



    def max_arb_trade_in_cp_carbon_cp(self, p0t0, p0t1, p2t0, p2t1, C, D, z):
        trade_input = (z * (-p0t0 * p2t0 * z + math.sqrt(C * p0t0 * p2t0 * p0t1 * p2t1))) / (p0t1 * C + p0t1 * D * p2t0 + z ** 2 * p2t0)
        return trade_input


    def max_arb_trade_in_constant_product(self, p0t0, p0t1, p1t0, p1t1, p2t0, p2t1, fee0, fee1, fee2):
        val = (-p1t0*p2t0*p0t0 + (p1t0*p2t0*p0t0*p1t1*p2t1*p0t1*(-fee1*fee2*fee0 + fee1*fee2 + fee1*fee0 - fee1 + fee2*fee0 - fee2 - fee0 + 1)) ** 0.5)/(p1t0*p2t0 - p2t0*p0t1*fee0 + p2t0*p0t1 + p1t1*p0t1*fee1*fee0 - p1t1*p0t1*fee1 - p1t1*p0t1*fee0 + p1t1*p0t1)
        return val



    @staticmethod
    def run_main_flow(
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
        CC_cc = CPCContainer(miniverse)
        O = CPCArbOptimizer(CC_cc)

        # Perform the optimization
        r = O.margp_optimizer(src_token)

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
                if curve.params.get("exchange") == "carbon_v1"
            ]
            external_curves = [
                curve
                for curve in external_curves
                if curve.params.get("exchange") != "carbon_v1"
            ]
            if not external_curves and not carbon_curves:
                continue

            bancor_v3_curve_0 = (
                self.CCm.bypairs(f"{T.BNT}/{tkn0}")
                .byparams(exchange="bancor_v3")
                .curves
            )
            bancor_v3_curve_1 = (
                self.CCm.bypairs(f"BNT-FF1C/{tkn1}")
                .byparams(exchange="bancor_v3")
                .curves
            )
            if bancor_v3_curve_0 is None or bancor_v3_curve_1 is None:
                continue
            if len(bancor_v3_curve_0) == 0 or len(bancor_v3_curve_1) == 0:
                continue

            miniverses = []
            if external_curves:
                for curve in external_curves:
                    miniverses += [bancor_v3_curve_0 + bancor_v3_curve_1 + [curve]]
            if carbon_curves:
                miniverses += [bancor_v3_curve_0 + bancor_v3_curve_1 + carbon_curves]

            if len(miniverses) > 0:
                all_miniverses += list(zip([T.BNT] * len(miniverses), miniverses))
        return all_miniverses
