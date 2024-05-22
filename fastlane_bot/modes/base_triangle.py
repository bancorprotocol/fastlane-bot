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
            try:
                CC_cc = CPCContainer(miniverse)
                O = MargPOptimizer(CC_cc)
                params = get_params(self.CCm, CC_cc.tokens(), src_token)
                r = O.optimize(src_token, params=params)
                trade_instructions_dic = r.trade_instructions(O.TIF_DICTS)
                trade_instructions_df = r.trade_instructions(O.TIF_DFAGGR)
            except Exception as e:
                self.ConfigObj.logger.debug(f"[base_triangle] {e}")
                continue
            if trade_instructions_dic is None or len(trade_instructions_dic) < 3:
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

def get_params(CCm, dst_tokens, src_token):
    pstart = {src_token: 1}
    for dst_token in [token for token in dst_tokens if token != src_token]:
        res = CCm.bytknx(dst_token).bytkny(src_token)
        if res:
            pstart[dst_token] = res[0].p
        else:
            res = CCm.bytknx(src_token).bytkny(dst_token)
            if res:
                pstart[dst_token] = 1 / res[0].p
            else:
                return None
    return {"pstart": pstart}
