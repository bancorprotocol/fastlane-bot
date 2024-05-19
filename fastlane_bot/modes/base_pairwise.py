"""
Defines the base class for pairwise arbitrage finder modes

[DOC-TODO-OPTIONAL-longer description in rst format]

---
(c) Copyright Bprotocol foundation 2023-24.
All rights reserved.
Licensed under MIT.
"""
from typing import Any, List, Dict
from fastlane_bot.tools.cpc import CPCContainer
from fastlane_bot.tools.optimizer import PairOptimizer
from fastlane_bot.modes.base import ArbitrageFinderBase

class ArbitrageFinderPairwiseBase(ArbitrageFinderBase):
    def find_arbitrage(self) -> Dict[List[Any], List[Any]]:
        arb_opps = []
        combos = self.get_combos()

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
                    trade_instructions = r.trade_instructions(O.TIF_OBJECTS)
                except Exception as e:
                    self.ConfigObj.logger.debug(f"[base_pairwise] {e}")
                    continue
                if trade_instructions_dic is None or len(trade_instructions_dic) < 2:
                    # Failed to converge
                    continue

                profit = self.get_profit(src_token, r, trade_instructions_df)
                if profit is not None:
                    arb_opps.append(
                        (
                            profit,
                            trade_instructions_df,
                            trade_instructions_dic,
                            src_token,
                            trade_instructions,
                        )
                    )

        arb_opps.sort(key=lambda x: x[0], reverse=True)
        return {"combos": combos, "arb_opps": arb_opps}
