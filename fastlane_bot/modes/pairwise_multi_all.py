"""
Defines the Multi-pairwise arbitrage finder class

[DOC-TODO-OPTIONAL-longer description in rst format]

---
(c) Copyright Bprotocol foundation 2023-24.
All rights reserved.
Licensed under MIT.
"""
import itertools
from typing import List, Any, Tuple, Union, Hashable

import pandas as pd

from fastlane_bot.modes.base_pairwise import ArbitrageFinderPairwiseBase
from fastlane_bot.tools.cpc import CPCContainer
from fastlane_bot.tools.optimizer import MargPOptimizer, PairOptimizer


class FindArbitrageMultiPairwiseAll(ArbitrageFinderPairwiseBase):
    """
    Multi-pairwise arbitrage finder mode.
    """

    arb_mode = "multi_pairwise_all"

    def find_arbitrage(self, candidates: List[Any] = None, ops: Tuple = None, best_profit: float = 0, profit_src: float = 0) -> Union[List, Tuple]:
        """
        see base.py
        """

        if candidates is None:
            candidates = []

        all_tokens, combos = self.get_combos(self.CCm, self.flashloan_tokens)
        if self.result == self.AO_TOKENS:
            return all_tokens, combos
        #print(f"combos = {combos}")

        candidates = []
        self.ConfigObj.logger.debug(
            f"\n ************ combos: {len(combos)} ************\n"
        )

        for tkn0, tkn1 in combos:
            r = None
            CC = self.CCm.bypairs(f"{tkn0}/{tkn1}")
            if len(CC) < 2:
                continue
            carbon_curves = [x for x in CC.curves if x.params.exchange in self.ConfigObj.CARBON_V1_FORKS]
            not_carbon_curves = [
                x for x in CC.curves if x.params.exchange not in self.ConfigObj.CARBON_V1_FORKS
            ]

            curve_combos = [[_curve0] + [_curve1] for _curve0 in not_carbon_curves for _curve1 in not_carbon_curves if (_curve0 != _curve1)]

            if len(carbon_curves) > 0:
                base_direction_pair = carbon_curves[0].pair
                base_direction_one = [curve for curve in carbon_curves if curve.pair == base_direction_pair]
                base_direction_two = [curve for curve in carbon_curves if curve.pair != base_direction_pair]
                curve_combos = []

                if len(base_direction_one) > 0:
                    curve_combos += [[curve] + base_direction_one for curve in not_carbon_curves]

                if len(base_direction_two) > 0:
                    curve_combos += [[curve] + base_direction_two for curve in not_carbon_curves]

                if len(carbon_curves) >= 2:
                    curve_combos += [carbon_curves]

            for curve_combo in curve_combos:
                src_token = tkn1
                if len(curve_combo) < 2:
                    continue
                try:
                    (
                        O,
                        profit_src,
                        r,
                        trade_instructions_df,
                    ) = self.run_main_flow(curves=curve_combo, src_token=src_token, tkn0=tkn0, tkn1=tkn1)
                except ValueError:
                    #Optimizer did not converge
                    continue


                trade_instructions_dic = r.trade_instructions(O.TIF_DICTS)
                trade_instructions = r.trade_instructions()
                if trade_instructions_dic is None:
                    continue
                if len(trade_instructions_dic) < 2:
                    continue
                # Get the cids
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

    @staticmethod
    def get_wrong_direction_cids(
        tkn0_into_carbon: bool, trade_instructions_df: pd.DataFrame
    ) -> List[Hashable]:
        """
        Get the cids of the wrong direction curves

        Parameters
        ----------
        tkn0_into_carbon : bool
            True if tkn0 is being converted into carbon, False otherwise
        trade_instructions_df : pd.DataFrame
            The trade instructions dataframe

        Returns
        -------
        List[str]
            The cids of the wrong direction curves
        """
        return [
            idx
            for idx, row in trade_instructions_df.iterrows()
            if (
                (tkn0_into_carbon and row.iloc[0] < 0)
                or (not tkn0_into_carbon and row.iloc[0] > 0)
            )
            and ("-0" in idx or "-1" in idx)
        ]

    @staticmethod
    def run_main_flow(
        curves: List[Any], src_token: str, tkn0: str, tkn1: str
    ) -> Tuple[Any, float, Any, pd.DataFrame]:
        """
        Run main flow to find arbitrage.
        """
        CC_cc = CPCContainer(curves)
        O = PairOptimizer(CC_cc)
        pstart = {
            tkn0: CC_cc.bypairs(f"{tkn0}/{tkn1}")[0].p
        }  # this intentionally selects the non_carbon curve

        r = O.optimize(src_token, params=dict(pstart=pstart))

        profit_src = -r.result
        trade_instructions_df = r.trade_instructions(O.TIF_DFAGGR)
        return O, profit_src, r, trade_instructions_df

    @staticmethod
    def process_wrong_direction_pools(
        curve_combo: List[Any], wrong_direction_cids: List[Hashable]
    ) -> [str]:
        """
        Process curves with wrong direction pools.
        """
        new_curves = [
            curve for curve in curve_combo if curve.cid not in wrong_direction_cids
        ]
        return new_curves

