"""
Defines the base class for triangular arbitrage finder modes

[DOC-TODO-OPTIONAL-longer description in rst format]

---
(c) Copyright Bprotocol foundation 2023-24.
All rights reserved.
Licensed under MIT.
"""
import random
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
                container = CPCContainer(miniverse)
                optimizer = MargPOptimizer(container)
                params = get_params(self, container, container.tokens(), src_token)
                optimization = optimizer.optimize(src_token, params=params)
                trade_instructions_dic = optimization.trade_instructions(optimizer.TIF_DICTS)
                trade_instructions_df = optimization.trade_instructions(optimizer.TIF_DFAGGR)
            except Exception as e:
                self.ConfigObj.logger.debug(f"[base_triangle] {e}")
                continue
            if trade_instructions_dic is None or len(trade_instructions_dic) < 3:
                # Failed to converge
                continue

            profit = self.get_profit(src_token, optimization, trade_instructions_df)
            if profit is not None:
                arb_opps.append(
                    {
                        "profit": profit,
                        "src_token": src_token,
                        'trade_instructions_dic': trade_instructions_dic,
                    }
                )

        return {"combos": combos, "arb_opps": sorted(arb_opps, key=lambda arb_opp: arb_opp["profit"], reverse=True)}

def get_params(self, CCm, dst_tokens, src_token):
    # For a triangle, the pstart of each dst_token is derived from its rate vs the src_token.
    # Since Carbon orders can contain diverse prices independent of external market prices, and
    # we require that the pstart be on the Carbon curve to get successful optimizer runs,
    # then for Carbon orders only we must randomize the pstart from the list of available Carbon curves.
    # Random selection chosen as opposed to iterating over all possible combinations.

    # ASSUMPTIONS: There must be a complete triangle arb available i.e. src_token->dst_token1->dst_token2->src_token
    sort_sequence = ['bancor_v2','bancor_v3'] + self.ConfigObj.UNI_V2_FORKS + self.ConfigObj.UNI_V3_FORKS
    pstart = {src_token: 1}
    for dst_token in [token for token in dst_tokens if token != src_token]:
        curves = list(CCm.bytknx(dst_token).bytkny(src_token))
        CC = CPCContainer(custom_sort(curves, sort_sequence, self.ConfigObj.CARBON_V1_FORKS))
        if CC:
            if CC[0].params['exchange'] in self.ConfigObj.CARBON_V1_FORKS: #only carbon curve options left
                pstart[dst_token] = random.choice(CC).p
            else:
                pstart[dst_token] = CC[0].p
        else:
            curves = list(CCm.bytknx(src_token).bytkny(dst_token))
            CC = CPCContainer(custom_sort(curves, sort_sequence, self.ConfigObj.CARBON_V1_FORKS))
            if CC:
                if CC[0].params['exchange'] in self.ConfigObj.CARBON_V1_FORKS: #only carbon curve options left
                    pstart[dst_token] = 1/(random.choice(CC).p)
                else:
                    pstart[dst_token] = 1 / CC[0].p
            else:
                return None
    return {"pstart": pstart}

def custom_sort(data, sort_sequence, carbon_v1_forks):
    sort_order = {key: index for index, key in enumerate(sort_sequence) if key not in carbon_v1_forks}
    return sorted(data, key=lambda item: float('inf') if item.params['exchange'] in carbon_v1_forks else sort_order.get(item.params['exchange'], float('inf')))
