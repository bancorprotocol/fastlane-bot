# coding=utf-8
"""
Triangle single arbitrage finder mode

(c) Copyright Bprotocol foundation 2023.
Licensed under MIT
"""
from typing import Union, List, Tuple, Any

from fastlane_bot.modes.base_triangle import ArbitrageFinderTriangleBase
from fastlane_bot.tools.cpc import CPCContainer
from fastlane_bot.tools.optimizer import CPCArbOptimizer


class ArbitrageFinderTriangleSingle(ArbitrageFinderTriangleBase):
    """
    Triangle single arbitrage finder mode
    """

    arb_mode = "single_triangle"

    def find_arbitrage(self, candidates: List[Any] = None, ops: Tuple = None, best_profit: float = 0, profit_src: float = 0) -> Union[List, Tuple]:
        """
        see base.py
        """

        if candidates is None:
            candidates = []

        # Get combinations of flashloan tokens
        combos = self.get_combos(
            self.flashloan_tokens, self.CCm, arb_mode=self.arb_mode
        )

        # Check each source token and miniverse combination
        for src_token, miniverse in combos:
            r = None

            # Instantiate the container and optimizer objects
            CC_cc = CPCContainer(miniverse)
            O = CPCArbOptimizer(CC_cc)

            try:
                # Perform the optimization
                r = O.margp_optimizer(src_token)

                # Get the profit in the source token
                profit_src = -r.result

                # Get trade instructions in different formats
                trade_instructions_df = r.trade_instructions(O.TIF_DFAGGR)
                trade_instructions_dic = r.trade_instructions(O.TIF_DICTS)
                trade_instructions = r.trade_instructions()
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
