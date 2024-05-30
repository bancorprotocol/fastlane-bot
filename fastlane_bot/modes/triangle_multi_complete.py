"""
Defines the Triangular arbitrage finder class

[DOC-TODO-OPTIONAL-longer description in rst format]

---
(c) Copyright Bprotocol foundation 2023-24.
All rights reserved.
Licensed under MIT.
"""
from typing import List, Any, Tuple, Union
import random

from fastlane_bot.modes.base_triangle import ArbitrageFinderTriangleBase
from fastlane_bot.tools.cpc import CPCContainer
from fastlane_bot.tools.optimizer import MargPOptimizer


class ArbitrageFinderTriangleMultiComplete(ArbitrageFinderTriangleBase):
    """
    Triangular arbitrage finder mode
    """

    arb_mode = "multi_triangle_complete"

    def find_arbitrage(self, candidates: List[Any] = None, ops: Tuple = None, best_profit: float = 0, profit_src: float = 0) -> Union[List, Tuple]:
        """
        see base.py
        """

        if candidates is None:
            candidates = []

        combos = self.get_comprehensive_triangles(self.flashloan_tokens, self.CCm)

        for src_token, miniverse in combos:
            try:
                CC_cc = CPCContainer(miniverse)
                O = MargPOptimizer(CC_cc)
                pstart = get_params(self, CC_cc, CC_cc.tokens(), src_token)
                r = O.optimize(src_token, params=dict(pstart=pstart))
                trade_instructions_dic = r.trade_instructions(O.TIF_DICTS)
                if trade_instructions_dic is None or len(trade_instructions_dic) < 3:
                    # Failed to converge
                    continue
                trade_instructions_df = r.trade_instructions(O.TIF_DFAGGR)
                trade_instructions = r.trade_instructions()

            except Exception as e:
                self.ConfigObj.logger.info(f"[triangle multi] {e}")
                continue
            profit_src = -r.result

            # Get the cids
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
    return pstart

def custom_sort(data, sort_sequence, carbon_v1_forks):
    sort_order = {key: index for index, key in enumerate(sort_sequence) if key not in carbon_v1_forks}
    return sorted(data, key=lambda item: float('inf') if item.params['exchange'] in carbon_v1_forks else sort_order.get(item.params['exchange'], float('inf')))
