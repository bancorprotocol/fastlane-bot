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

        for dst_token, src_token in combos:
            CC = self.CCm.bypairs(f"{dst_token}/{src_token}")
            if len(CC) < 2:
                continue

            for curve_combo in self.get_curve_combos(CC):
                if len(curve_combo) < 2:
                    continue
                try:
                    CC_cc = CPCContainer(curve_combo)
                    O = PairOptimizer(CC_cc)
                    params = get_params(CC_cc, dst_token, src_token)
                    r = O.optimize(src_token, params=params)
                    trade_instructions_dic = r.trade_instructions(O.TIF_DICTS)
                    trade_instructions_df = r.trade_instructions(O.TIF_DFAGGR)
                except Exception as e:
                    self.ConfigObj.logger.debug(f"[base_pairwise] {e}")
                    continue
                if trade_instructions_dic is None or len(trade_instructions_dic) < 2:
                    # Failed to converge
                    continue

                profit = self.get_profit(src_token, r, trade_instructions_df)
                if profit is not None:
                    arb_opps.append(
                        {
                            "profit": profit,
                            "src_token": src_token,
                            'trade_instructions_dic': trade_instructions_dic,
                        }
                    )

        return {"combos": combos, "arb_opps": sorted(arb_opps, key=lambda x: x["profit"], reverse=True)}

def get_params(CC_cc, dst_token, src_token):
    pstart = {dst_token: CC_cc.bypairs(f"{dst_token}/{src_token}")[0].p}
    return {"pstart": pstart}
