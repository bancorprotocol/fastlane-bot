"""
Defines the Single pairwise arbitrage finder class

[DOC-TODO-OPTIONAL-longer description in rst format]

---
(c) Copyright Bprotocol foundation 2023-24.
All rights reserved.
Licensed under MIT.
"""
from typing import List, Any, Tuple, Union

from tqdm.contrib import itertools

from arb_optimizer import CurveContainer, PairOptimizer

from fastlane_bot.modes.base_pairwise import ArbitrageFinderPairwiseBase


class FindArbitrageSinglePairwise(ArbitrageFinderPairwiseBase):
    """
    Single pairwise arbitrage finder mode
    """

    arb_mode = "single_pairwise"

    def find_arbitrage(self, candidates: List[Any] = None, ops: Tuple = None, best_profit: float = 0, profit_src: float = 0) -> Union[List, Tuple]:
        """
        see base.py
        """

        if candidates is None:
            candidates = []

        all_tokens, combos = self.get_combos(self.CCm, self.flashloan_tokens)

        if self.result == self.AO_TOKENS:
            return all_tokens, combos

        for tkn0, tkn1 in combos:
            r = None
            CC = self.CCm.bypairs(f"{tkn0}/{tkn1}")
            if len(CC) < 2:
                continue
            base_exchange_curves = [
                x for x in CC.curves if x.params.exchange == self.base_exchange
            ]
            not_base_exchange_curves = [
                x for x in CC.curves if x.params.exchange != self.base_exchange
            ]
            self.ConfigObj.logger.debug(
                f"base_exchange: {self.base_exchange}, base_exchange_curves: {len(base_exchange_curves)}, not_base_exchange_curves: {len(not_base_exchange_curves)}"
            )

            curve_combos = list(
                itertools.product(not_base_exchange_curves, base_exchange_curves)
            )

            if not curve_combos:
                continue

            for curve_combo in curve_combos:
                CC_cc = CurveContainer(curve_combo)
                O = PairOptimizer(CC_cc)
                src_token = tkn1
                try:
                    pstart = {tkn0: CC_cc.bypairs(f"{tkn0}/{tkn1}")[0].p}
                    r = O.optimize(src_token)
                    profit_src = -r.result
                    trade_instructions_df = r.trade_instructions(O.TIF_DFAGGR)
                    trade_instructions_dic = r.trade_instructions(O.TIF_DICTS)
                    trade_instructions = r.trade_instructions()
                except Exception as e:
                    print("[FindArbitrageSinglePairwise] Exception: ", e)
                    continue
                if trade_instructions_dic is None:
                    continue
                if len(trade_instructions_dic) < 2:
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
