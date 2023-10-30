# coding=utf-8
"""
Triangular arbitrage finder mode

(c) Copyright Bprotocol foundation 2023.
Licensed under MIT
"""
from typing import List, Any, Tuple, Union

from fastlane_bot.modes.base_triangle import ArbitrageFinderTriangleBase
from fastlane_bot.tools.cpc import CPCContainer
from fastlane_bot.tools.optimizer import MargPOptimizer


class ArbitrageFinderTriangleMulti(ArbitrageFinderTriangleBase):
    """
    Triangular arbitrage finder mode
    """

    arb_mode = "multi_triangle"

    def find_arbitrage(self, candidates: List[Any] = None, ops: Tuple = None, best_profit: float = 0, profit_src: float = 0) -> Union[List, Tuple]:
        """
        see base.py
        """

        if self.base_exchange != "carbon_v1":
            raise ValueError("base_exchange must be carbon_v1 for `multi` mode")

        if candidates is None:
            candidates = []

        combos = self.get_combos(
            self.flashloan_tokens, self.CCm, arb_mode=self.arb_mode
        )

        for src_token, miniverse in combos:

            r = None
            CC_cc = CPCContainer(miniverse)
            O = MargPOptimizer(CC_cc)
            #try:
            r = O.margp_optimizer(src_token)
            trade_instructions_dic = r.trade_instructions(O.TIF_DICTS)
            if len(trade_instructions_dic) < 3:
                # Failed to converge
                continue
            trade_instructions_df = r.trade_instructions(O.TIF_DFAGGR)
            #print(trade_instructions_df)
            trade_instructions = r.trade_instructions()
            """
            The following handles an edge case until parallel execution is available:
            1 Determine correct direction - opposite of non-Carbon pool
            2 Get cids of wrong-direction Carbon pools
            3 Create new CPCContainer with correct pools
            4 Rerun optimizer
            5 Resume normal flow
            """

            profit_src = -r.result

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
