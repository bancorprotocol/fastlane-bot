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
                pstart = build_pstart(self.CCm, CC_cc, src_token, self.ConfigObj)
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

def build_pstart(CCm, CC_cc, tkn1, cfg):
    pstart = {tkn1: 1}
    for tkn0 in [x for x in CC_cc.tokens() if x != tkn1]:
        try:
            pstart[tkn0] = CCm.bytknx(tkn0).bytkny(tkn1)[0].p
        except Exception as e:
            cfg.logger.info(f"[build_pstart] attempt 1: {tkn0}/{tkn1} price error {e}")
            try:
                pstart[tkn0] = 1/CCm.bytknx(tkn1).bytkny(tkn0)[0].p
            except Exception as e:
                cfg.logger.info(f"[build_pstart] attempt 2: {tkn0}/{tkn1} price error {e}")
    return pstart
