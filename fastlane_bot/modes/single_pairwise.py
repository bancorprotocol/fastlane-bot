import itertools
from typing import List

from fastlane_bot import Config
from fastlane_bot.modes.base import ArbitrageFinderBase
from fastlane_bot.tools.cpc import CPCContainer


class ArbitrageFinderSinglePairwise(ArbitrageFinderBase):
    def find_arbitrage(self, flashloan_tokens: List[str], CCm: CPCContainer, mode: str = "bothin", result: str = None, ConfigObj: Config = None):
        assert mode == "bothin", "parameter not used"

        best_profit, best_src_token, best_trade_instructions, best_trade_instructions_df, best_trade_instructions_dic = self.initialize_best_ops()
        all_tokens, combos = self.get_tokens_combos(flashloan_tokens, CCm, result)

        if result == self.AO_TOKENS: return all_tokens, combos

        candidates = self.find_candidates(combos, CCm, best_profit, best_src_token, best_trade_instructions_df, best_trade_instructions_dic, best_trade_instructions)
        return candidates if result == self.AO_CANDIDATES else (best_profit, best_trade_instructions_df, best_trade_instructions_dic, best_src_token, best_trade_instructions)

    def initialize_best_ops(self):
        return 0, None, None, None, None

    def get_tokens_combos(self, flashloan_tokens, CCm):
        all_tokens = CCm.tokens()
        flashloan_tokens_intersect = all_tokens.intersection(set(flashloan_tokens))
        combos = [(tkn0, tkn1) for tkn0, tkn1 in itertools.product(all_tokens, flashloan_tokens_intersect) if tkn0 != tkn1]
        return all_tokens, combos

    def find_candidates(self, combos, CCm, best_profit):
        candidates = []
        for tkn0, tkn1 in combos:
            self.C.logger.debug(f"Checking flashloan token = {tkn1}, other token = {tkn0}")
            CC = CCm.bypairs(f"{tkn0}/{tkn1}")
            if len(CC) < 2: continue

            carbon_curves = [x for x in CC.curves if x.params.exchange == 'carbon_v1']
            not_carbon_curves = [x for x in CC.curves if x.params.exchange != 'carbon_v1']
            curve_combos = list(itertools.product(not_carbon_curves, carbon_curves))

            for curve_combo in curve_combos:
                O, r, trade_instructions_df = self.optimize(curve_combo, tkn0, tkn1)
                src_token = tkn1

                if r:
                    cids = [ti['cid'] for ti in r.trade_instructions(O.TIF_DICTS)]
                    profit_src = -r.result
                    profit = self.get_profit(src_token, profit_src, CCm)
                    netchange = self.get_netchange(trade_instructions_df)

                    if self.is_candidate(profit, best_profit, netchange):
                        candidates.append((profit, trade_instructions_df, r.trade_instructions(O.TIF_DICTS), tkn1, r.trade_instructions()))

                    if self.is_new_best(profit, best_profit, netchange):
                        best_profit, best_src_token, best_trade_instructions_df, best_trade_instructions_dic, best_trade_instructions = profit, tkn1, trade_instructions_df, r.trade_instructions(O.TIF_DICTS), r.trade_instructions()
                        self.ConfigObj.logger.debug(f"best_trade_instructions_df: {best_trade_instructions_df}")
        return candidates

