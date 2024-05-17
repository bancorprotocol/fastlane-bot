"""
Defines the base class for pairwise arbitrage finder modes

[DOC-TODO-OPTIONAL-longer description in rst format]

---
(c) Copyright Bprotocol foundation 2023-24.
All rights reserved.
Licensed under MIT.
"""
from typing import List, Tuple, Union

from fastlane_bot.tools.cpc import CPCContainer
from fastlane_bot.tools.optimizer import PairOptimizer
from fastlane_bot.modes.base import ArbitrageFinderBase

class ArbitrageFinderPairwiseBase(ArbitrageFinderBase):
    def find_arbitrage(self) -> Union[List, Tuple]:
        all_tokens, combos = self.get_combos(self.flashloan_tokens, self.CCm)
        if self.result == self.AO_TOKENS:
            return all_tokens, combos

        candidates = []
        best_profit = 0
        ops = None

        for tkn0, tkn1 in combos:
            CC = self.CCm.bypairs(f"{tkn0}/{tkn1}")
            if len(CC) < 2:
                continue

            for curve_combo in self.get_curve_combos(CC):
                src_token = tkn1
                if len(curve_combo) < 2:
                    continue
                try:
                    CC_cc = CPCContainer(curve_combo)
                    O = PairOptimizer(CC_cc)
                    pstart = {tkn0: CC_cc.bypairs(f"{tkn0}/{tkn1}")[0].p}
                    r = O.optimize(src_token, params=dict(pstart=pstart))
                    trade_instructions_dic = r.trade_instructions(O.TIF_DICTS)
                    trade_instructions_df = r.trade_instructions(O.TIF_DFAGGR)
                    trade_instructions = r.trade_instructions()
                except Exception as e:
                    self.ConfigObj.logger.debug(f"[base_pairwise] {e}")
                    continue
                if trade_instructions_dic is None or len(trade_instructions_dic) < 2:
                    # Failed to converge
                    continue
                # Update the results
                best_profit, ops = self.update_results(
                    src_token,
                    r,
                    trade_instructions_dic,
                    trade_instructions_df,
                    trade_instructions,
                    candidates,
                    best_profit,
                    ops,
                )

        return candidates if self.result == self.AO_CANDIDATES else ops
