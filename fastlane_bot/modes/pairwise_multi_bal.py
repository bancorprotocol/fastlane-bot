# coding=utf-8
"""
Multi-pairwise arbitrage finder mode

(c) Copyright Bprotocol foundation 2023.
Licensed under MIT
"""
import itertools
from typing import List, Any, Tuple, Union, Hashable

import pandas as pd

from fastlane_bot.modes.base_pairwise import ArbitrageFinderPairwiseBase
from fastlane_bot.tools.cpc import CPCContainer
from fastlane_bot.tools.optimizer import MargPOptimizer, PairOptimizer


class FindArbitrageMultiPairwiseBalancer(ArbitrageFinderPairwiseBase):
    """
    Multi-pairwise arbitrage finder mode.
    """

    arb_mode = "multi_pairwise_bal"

    def find_arbitrage(self, candidates: List[Any] = None, ops: Tuple = None, best_profit: float = 0, profit_src: float = 0) -> Union[List, Tuple]:
        """
        see base.py
        """
        if self.base_exchange != "carbon_v1":
            raise ValueError("base_exchange must be carbon_v1 for `multi` mode")

        if candidates is None:
            candidates = []

        combos = self.get_balancer_combos(self.CCm, self.flashloan_tokens)

        candidates = []
        self.ConfigObj.logger.debug(
            f"\n ************ combos: {len(combos)} ************\n"
        )
        for tkn0, tkn1 in combos:
            r = None
            CC = self.CCm.bypairs(f"{tkn0}/{tkn1}")
            if len(CC) < 2:
                continue
            carbon_curves = [x for x in CC.curves if x.params.exchange == "carbon_v1"]
            not_bal_curves = [
                x for x in CC.curves if x.params.exchange != "balancer"
            ]

            bal_curves = [x for x in CC.curves if x.params.exchange == "balancer"]
            curve_combos = [[bal_curve] + [curve] for curve in not_bal_curves for bal_curve in bal_curves]
            curve_combos += [[bal_curve] + carbon_curves for bal_curve in bal_curves]

            for curve_combo in curve_combos:
                src_token = tkn1
                if len(curve_combo) < 2:
                    continue

                (
                    O,
                    profit_src,
                    r,
                    trade_instructions_df,
                ) = self.run_main_flow(curves=curve_combo, src_token=src_token, tkn0=tkn0, tkn1=tkn1)


                non_carbon_cids = [
                    curve.cid
                    for curve in curve_combo
                    if curve.params.get("exchange") != "carbon_v1"
                ]
                carbon_cids = [
                    curve.cid
                    for curve in curve_combo
                    if curve.params.get("exchange") == "carbon_v1"
                ]

                if len(carbon_cids) > 0:
                    if non_carbon_cids[0] in trade_instructions_df.index and carbon_cids[0] in trade_instructions_df.index:
                        non_carbon_row = trade_instructions_df.loc[non_carbon_cids[0]]
                        tkn0_into_carbon = non_carbon_row[0] < 0
                        wrong_direction_cids = self.get_wrong_direction_cids(
                            tkn0_into_carbon, trade_instructions_df
                        )
                        if len(wrong_direction_cids) > 0:
                            filtered_curves = self.process_wrong_direction_pools(
                                curve_combo=curve_combo, wrong_direction_cids=wrong_direction_cids
                            )
                            if len(filtered_curves) < 2:
                                continue
                            (
                                O,
                                profit_src,
                                r,
                                trade_instructions_df,
                            ) = self.run_main_flow(curves=filtered_curves, src_token=src_token, tkn0=tkn0, tkn1=tkn1)

                trade_instructions_dic = r.trade_instructions(O.TIF_DICTS)
                trade_instructions = r.trade_instructions()

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
                (tkn0_into_carbon and row[0] < 0)
                or (not tkn0_into_carbon and row[0] > 0)
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

    @staticmethod
    def get_balancer_combos(CCm, flashloan_tokens):
        balancer_curves = CCm.byparams(exchange="balancer").curves
        bal_tkns_raw = [curve.tkny for curve in balancer_curves]
        bal_tkns_raw += [curve.tknx for curve in balancer_curves]
        bal_tkns_raw = list(set(bal_tkns_raw))

        if "WETH-6Cc2" in flashloan_tokens:
            flashloan_tokens = ["WETH-6Cc2"]
        else:
            flashloan_tokens = [flashloan_tokens[0]]
        combos = [(tkn0, tkn1) for tkn0, tkn1 in itertools.product(bal_tkns_raw, flashloan_tokens) if tkn0 != tkn1]
                # note that the pair is tkn0/tkn1, ie tkn1 is the quote token

        return combos

