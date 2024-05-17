"""
Defines the base class for triangular arbitrage finder modes

[DOC-TODO-OPTIONAL-longer description in rst format]

---
(c) Copyright Bprotocol foundation 2023-24.
All rights reserved.
Licensed under MIT.
"""
from typing import List, Tuple, Union

from fastlane_bot.tools.cpc import CPCContainer
from fastlane_bot.tools.optimizer import MargPOptimizer
from fastlane_bot.modes.base import ArbitrageFinderBase

class ArbitrageFinderTriangleBase(ArbitrageFinderBase):
    def find_arbitrage(self) -> Union[List, Tuple]:
        self.handle_exchange()
        combos = self.get_combos(self.flashloan_tokens, self.CCm)

        candidates = []
        best_profit = 0
        ops = None

        for src_token, miniverse in combos:
            try:
                CC_cc = CPCContainer(miniverse)
                O = MargPOptimizer(CC_cc)
                pstart = build_pstart(self.CCm, CC_cc, src_token, self.ConfigObj)
                r = O.optimize(src_token, params=dict(pstart=pstart))
                trade_instructions_dic = r.trade_instructions(O.TIF_DICTS)
                trade_instructions_df = r.trade_instructions(O.TIF_DFAGGR)
                trade_instructions = r.trade_instructions()
            except Exception as e:
                self.ConfigObj.logger.debug(f"[base_triangle] {e}")
                continue
            if trade_instructions_dic is None or len(trade_instructions_dic) < 3:
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

def build_pstart(CCm, CC_cc, tkn1, cfg):
    pstart = {tkn1: 1}
    for tkn0 in [x for x in CC_cc.tokens() if x != tkn1]:
        try:
            pstart[tkn0] = CCm.bytknx(tkn0).bytkny(tkn1)[0].p
        except:
            try:
                pstart[tkn0] = 1/CCm.bytknx(tkn1).bytkny(tkn0)[0].p
            except Exception as e:
                cfg.logger.info(f"[pstart build] {tkn0}/{tkn1} price error {e}")
    return pstart
