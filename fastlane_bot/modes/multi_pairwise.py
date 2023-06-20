import itertools
from typing import List

from fastlane_bot import Config
from fastlane_bot.modes.base import ArbitrageFinderBase
from fastlane_bot.tools.cpc import CPCContainer
from fastlane_bot.tools.optimizer import CPCArbOptimizer


class ArbitrageFinderMultiPairwise(ArbitrageFinderBase):
    def find_arbitrage(self, flashloan_tokens: List[str], CCm: CPCContainer, mode: str = "bothin", result: str = None, ConfigObj: Config = None):
        assert mode == "bothin", "parameter not used"

        best_profit, best_src_token, best_trade_instructions, best_trade_instructions_df, best_trade_instructions_dic = self.initialize_best_ops()
        all_tokens, combos = self.get_tokens_combos(flashloan_tokens, CCm, result)

        if result == self.AO_TOKENS: return all_tokens, combos

        candidates = self.find_candidates(combos, CCm, best_profit, best_src_token, best_trade_instructions_df, best_trade_instructions_dic, best_trade_instructions)
        return candidates if result == self.AO_CANDIDATES else (best_profit, best_trade_instructions_df, best_trade_instructions_dic, best_src_token, best_trade_instructions)

    def initialize_best_ops(self):
        return 0, None, None, None, None

    def get_tokens_combos(self, flashloan_tokens, CCm, result):
        all_tokens = CCm.tokens()
        flashloan_tokens_intersect = all_tokens.intersection(set(flashloan_tokens))
        combos = [(tkn0, tkn1) for tkn0, tkn1 in itertools.product(all_tokens, flashloan_tokens_intersect) if tkn0 != tkn1]
        return all_tokens, combos

    def find_candidates(self, combos, CCm, best_profit, best_src_token, best_trade_instructions_df, best_trade_instructions_dic, best_trade_instructions):
        candidates = []
        for tkn0, tkn1 in combos:
            r = None
            self.C.logger.debug(f"Checking flashloan token = {tkn1}, other token = {tkn0}")
            CC = CCm.bypairs(f"{tkn0}/{tkn1}")
            if len(CC) < 2: continue

            # Refactor this block of code into a separate function for improved readability and maintainability
            candidates, best_profit, best_src_token, best_trade_instructions_df, best_trade_instructions_dic, best_trade_instructions = self.process_curve_combos(CC, tkn0, tkn1, candidates, best_profit, best_src_token, best_trade_instructions_df, best_trade_instructions_dic, best_trade_instructions)
        return candidates

    def process_curve_combos(self, CC, tkn0, tkn1, candidates, best_profit, best_src_token, best_trade_instructions_df, best_trade_instructions_dic, best_trade_instructions):
        carbon_curves = [x for x in CC.curves if x.params.exchange == 'carbon_v1']
        not_carbon_curves = [x for x in CC.curves if x.params.exchange != 'carbon_v1']
        curve_combos = [[curve] + carbon_curves for curve in not_carbon_curves]

        for curve_combo in curve_combos:
            CC_cc = CPCContainer(curve_combo)
            O = CPCArbOptimizer(CC_cc)
            src_token = tkn1
            try:
                pstart = (
                    {tkn0: CC_cc.bypairs(f"{tkn0}/{tkn1}")[0].p})
                r = O.margp_optimizer(src_token, params=dict(pstart=pstart))
                trade_instructions_df, trade_instructions_dic, trade_instructions = self.get_trade_instructions(r, O)

                if self.is_valid_trade(trade_instructions_df, trade_instructions_dic):
                    profit = self.calculate_profit(CCm, src_token, r.result)
                    netchange = self.get_netchange(trade_instructions_df)
                    candidates, best_profit, best_src_token, best_trade_instructions_df, best_trade_instructions_dic, best_trade_instructions = self.check_candidate(profit, src_token, trade_instructions_df, trade_instructions_dic, trade_instructions, candidates, best_profit, best_src_token, best_trade_instructions_df, best_trade_instructions_dic, best_trade_instructions, netchange)
            except Exception as e:
                continue
        return candidates, best_profit, best_src_token, best_trade_instructions_df, best_trade_instructions_dic, best_trade_instructions


