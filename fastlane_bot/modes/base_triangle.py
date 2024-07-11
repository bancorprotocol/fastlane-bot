"""
Defines the base class for triangular arbitrage finder modes

[DOC-TODO-OPTIONAL-longer description in rst format]

---
(c) Copyright Bprotocol foundation 2023-24.
All rights reserved.
Licensed under MIT.
"""
from typing import Any, List, Dict
from fastlane_bot.tools.cpc import CPCContainer
from fastlane_bot.tools.optimizer import MargPOptimizer
from fastlane_bot.modes.base import ArbitrageFinderBase

class ArbitrageFinderTriangleBase(ArbitrageFinderBase):
    def find_arbitrage(self) -> Dict[List[Any], List[Any]]:
        arb_opps = []
        combos = self.get_combos()

        for src_token, miniverse in combos:
            container = CPCContainer(miniverse)
            optimizer = MargPOptimizer(container)
            params = self.get_params(container, container.tokens(), src_token)

            try:
                optimization = optimizer.optimize(src_token, params=params)
            except Exception as e:
                self.ConfigObj.logger.debug(f"[base_triangle] {e}")
                continue

            trade_instructions_dic = optimization.trade_instructions(optimizer.TIF_DICTS)
            if trade_instructions_dic is None or len(trade_instructions_dic) < 3:
                # Failed to converge
                continue

            profit = self.get_profit(src_token, optimization, trade_instructions_dic)
            if profit is not None:
                arb_opps.append({"profit": profit, "src_token": src_token, "trade_instructions_dic": trade_instructions_dic})

        return {"combos": combos, "arb_opps": sorted(arb_opps, key=lambda arb_opp: arb_opp["profit"], reverse=True)}
