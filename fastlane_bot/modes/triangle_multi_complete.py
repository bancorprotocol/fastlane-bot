"""
Defines the Triangular arbitrage finder class

[DOC-TODO-OPTIONAL-longer description in rst format]

---
(c) Copyright Bprotocol foundation 2023-24.
All rights reserved.
Licensed under MIT.
"""
from typing import List, Any, Tuple, Union

from arb_optimizer import CurveContainer, MargPOptimizer

from fastlane_bot.modes.base_triangle import ArbitrageFinderTriangleBase


class ArbitrageFinderTriangleMultiComplete(ArbitrageFinderTriangleBase):
    """
    Triangular arbitrage finder mode
    """

    arb_mode = "multi_triangle_complete"

    def find_arbitrage(self, candidates: List[Any] = None, ops: Tuple = None, best_profit: float = 0, profit_src: float = 0) -> Union[List, Tuple]:
        """
        see base.py
        """

        if candidates is None:
            candidates = []

        combos = self.get_comprehensive_triangles(self.flashloan_tokens, self.CCm)

        for src_token, miniverse in combos:
            try:
                CC_cc = CurveContainer(miniverse)
                O = MargPOptimizer(CC_cc)
                pstart = self.build_pstart(CC_cc, CC_cc.tokens(), src_token)
                r = O.optimize(src_token, params=dict(pstart=pstart))
                trade_instructions_dic = r.trade_instructions(O.TIF_DICTS)
                if trade_instructions_dic is None or len(trade_instructions_dic) < 3:
                    # Failed to converge
                    continue
                trade_instructions_df = r.trade_instructions(O.TIF_DFAGGR)
                trade_instructions = r.trade_instructions()

            except Exception as e:
                self.ConfigObj.logger.info(f"[triangle multi] {e}")
                continue
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
