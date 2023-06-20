import abc
import contextlib
from typing import Any, List

from fastlane_bot import Config
from fastlane_bot.tools.cpc import CPCContainer
from fastlane_bot.tools.optimizer import CPCArbOptimizer


class ArbitrageFinderBase:
    def __init__(self, flashloan_tokens, CCm, mode="bothin", result=None, ConfigObj: Config = None):
        self.flashloan_tokens = flashloan_tokens
        self.CCm = CCm
        self.mode = mode
        self.result = result
        self.best_profit = 0
        self.best_src_token = None
        self.best_trade_instructions = None
        self.best_trade_instructions_df = None
        self.best_trade_instructions_dic = None
        self.ConfigObj = ConfigObj

    AO_CANDIDATES = "candidates"
    AO_TOKENS = "tokens"

    def optimize(self, curve_combo, tkn0, tkn1):
        r = None
        CC_cc = CPCContainer(curve_combo)
        O = CPCArbOptimizer(CC_cc)
        with contextlib.suppress(Exception):
            pstart = ({tkn0: CC_cc.bypairs(f"{tkn0}/{tkn1}")[0].p})
            r = O.margp_optimizer(tkn1, params=dict(pstart=pstart))
            trade_instructions_df = r.trade_instructions(O.TIF_DFAGGR)
            wrong_direction_cids = self.get_wrong_direction_cids(trade_instructions_df, curve_combo)

            if wrong_direction_cids:
                new_curves = [curve for curve in curve_combo if curve.cid not in wrong_direction_cids]
                CC_cc = CPCContainer(new_curves)
                O = CPCArbOptimizer(CC_cc)
                pstart = ({tkn0: CC_cc.bypairs(f"{tkn0}/{tkn1}")[0].p})
                r = O.margp_optimizer(tkn1, params=dict(pstart=pstart))
                trade_instructions_df = r.trade_instructions(O.TIF_DFAGGR)
        return O, r, trade_instructions_df

    def get_trade_instructions(self, r, O):
        trade_instructions_df = r.trade_instructions(O.TIF_DFAGGR)
        trade_instructions_dic = r.trade_instructions(O.TIF_DICTS)
        trade_instructions = r.trade_instructions()
        return trade_instructions_df, trade_instructions_dic, trade_instructions

    def calculate_profit(self, CCm, src_token, result):
        profit_src = -result
        if src_token == 'BNT-FF1C':
            profit = profit_src
        else:
            try:
                price_src_per_bnt = CCm.bypair(pair=f"BNT-FF1C/{src_token}").byparams(exchange='bancor_v3')[0].p
                profit = profit_src/price_src_per_bnt
            except Exception as e:
                self.ConfigObj.logger.error(f"[TODO CLEAN UP]{e}")
        return profit

    get_profit = calculate_profit

    def get_netchange(self, trade_instructions_df):
        try:
            return trade_instructions_df.iloc[-1]
        except Exception as e:
            return [500]

    def is_candidate(self, profit, netchange):
        condition_zeros_one_token = max(netchange) < 1e-4
        return condition_zeros_one_token and profit > self.ConfigObj.DEFAULT_MIN_PROFIT

    def check_candidate(self, profit, src_token, trade_instructions_df, trade_instructions_dic, trade_instructions, candidates, best_profit, best_src_token, best_trade_instructions_df, best_trade_instructions_dic, best_trade_instructions, netchange):
        if self.is_candidate(profit, best_profit, netchange):
            candidates.append((profit, trade_instructions_df, trade_instructions_dic, src_token, trade_instructions))
        if self.is_new_best(profit, best_profit, netchange):
            best_profit, best_src_token, best_trade_instructions_df, best_trade_instructions_dic, best_trade_instructions = profit, src_token, trade_instructions_df, trade_instructions_dic, trade_instructions
        return candidates, best_profit, best_src_token, best_trade_instructions_df, best_trade_instructions_dic, best_trade_instructions

    def is_new_best(self, profit, best_profit, netchange):
        condition_better_profit = (profit > best_profit)
        condition_zeros_one_token = max(netchange) < 1e-4
        return condition_better_profit and condition_zeros_one_token

    def get_wrong_direction_cids(self, trade_instructions_df, curve_combo):
        non_carbon_cids = [curve.cid for curve in curve_combo if curve.params.get('exchange') != "carbon_v1"]
        non_carbon_row = trade_instructions_df.loc[non_carbon_cids[0]]
        tkn0_into_carbon = non_carbon_row[0] < 0

        return [
            idx
            for idx, row in trade_instructions_df.iterrows()
            if ("-0" in idx or "-1" in idx)
            and (
                (tkn0_into_carbon and row[0] < 0)
                or (not tkn0_into_carbon and row[0] > 0)
            )
        ]

    @abc.abstractmethod
    def find_arbitrage(self, flashloan_tokens: List[str], CCm: CPCContainer, mode: str = "bothin", result: str = None, ConfigObj: Config = None):
        pass




