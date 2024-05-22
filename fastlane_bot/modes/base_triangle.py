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
                pstart = build_pstart(self.CCm, CC_cc, src_token)
                r = O.optimize(src_token, params=dict(pstart=pstart))
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

def build_pstart(CCm, CC_cc, tkn1):
    pstart = {tkn1: 1}
    for tkn0 in [tkn for tkn in CC_cc.tokens() if tkn != tkn1]:
        for s in [+1, -1]:
            tknx, tkny = [tkn0, tkn1][::s]
            res = CCm.bytknx(tknx).bytkny(tkny)
            if res:
                pstart[tkn0] = res[0].p ** s
                break
    return pstart
