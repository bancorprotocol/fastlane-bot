import abc
import itertools
from abc import ABC
from typing import Any

from fastlane_bot.modes.base import ArbitrageFinderBase
from fastlane_bot.tools.cpc import CPCContainer
from fastlane_bot.tools.optimizer import CPCArbOptimizer
from fastlane_bot.utils import num_format


class ArbitrageFinderPairwiseBase(ArbitrageFinderBase):

    @abc.abstractmethod
    def get_trade_instructions(self, arb_mode, trade_instructions_df, curve_combo, tkn0, tkn1, src_token, r, O):
        pass





    def optimize(self, arb_mode, src_token, curve_combo, tkn0, tkn1, O, CC_cc):
        pstart = {tkn0: CC_cc.bypairs(f"{tkn0}/{tkn1}")[0].p}
        r = O.margp_optimizer(src_token, params=dict(pstart=pstart))
        profit_src = -r.result
        trade_instructions_df = r.trade_instructions(O.TIF_DFAGGR)
        (
            trade_instructions_df,
            trade_instructions_dic,
            trade_instructions,
        ) = self.get_trade_instructions(
            arb_mode, trade_instructions_df, curve_combo, tkn0, tkn1, src_token, r, O
        )
        return (
            profit_src,
            trade_instructions_df,
            trade_instructions_dic,
            trade_instructions,
            r,
        )

    def check_best_profit(
        self,
        ConfigObj,
        candidates,
        netchange,
        profit,
        src_token,
        trade_instructions,
        trade_instructions_df,
        trade_instructions_dic,
        best_profit,
    ):
        (
            best_src_token,
            best_trade_instructions,
            best_trade_instructions_df,
            best_trade_instructions_dic,
            ops,
        ) = (
            self.best_src_token,
            self.best_trade_instructions,
            self.best_trade_instructions_df,
            self.best_trade_instructions_dic,
            self.ops
        )
        condition_better_profit, condition_zeros_one_token = self.get_conditions(
            profit, netchange, ConfigObj, best_profit
        )
        candidates = self.add_mandatory_candidates(
            profit,
            ConfigObj,
            src_token,
            trade_instructions_df,
            trade_instructions_dic,
            trade_instructions,
            candidates,
            condition_zeros_one_token,
        )
        if self.is_new_best(profit, best_profit, netchange):
            (
                best_profit,
                best_src_token,
                best_trade_instructions,
                best_trade_instructions_df,
                best_trade_instructions_dic,
                ops,
            ) = self.get_ops(
                ConfigObj,
                profit,
                src_token,
                trade_instructions,
                trade_instructions_df,
                trade_instructions_dic,
            )
        return (
            best_src_token,
            best_trade_instructions,
            best_trade_instructions_df,
            best_trade_instructions_dic,
            candidates,
            ops,
        )

    def get_ops(
        self,
        ConfigObj,
        profit,
        src_token,
        trade_instructions,
        trade_instructions_df,
        trade_instructions_dic,
    ):
        ConfigObj.logger.debug("*************")
        ConfigObj.logger.debug(f"New best profit: {profit}")
        best_profit = profit
        best_src_token = src_token
        best_trade_instructions_df = trade_instructions_df
        best_trade_instructions_dic = trade_instructions_dic
        best_trade_instructions = trade_instructions
        ConfigObj.logger.debug(
            f"best_trade_instructions_df: {best_trade_instructions_df}"
        )
        ops = (
            best_profit,
            best_trade_instructions_df,
            best_trade_instructions_dic,
            best_src_token,
            best_trade_instructions,
        )
        ConfigObj.logger.debug("*************")
        return (
            best_profit,
            best_src_token,
            best_trade_instructions,
            best_trade_instructions_df,
            best_trade_instructions_dic,
            ops,
        )

    def get_combos(self, CCm, flashloan_tokens):
        all_tokens = CCm.tokens()
        flashloan_tokens_intersect = all_tokens.intersection(set(flashloan_tokens))
        combos = [
            (tkn0, tkn1)
            for tkn0, tkn1 in itertools.product(all_tokens, flashloan_tokens_intersect)
            # tkn1 is always the token being flash loaned
            # note that the pair is tkn0/tkn1, ie tkn1 is the quote token
            if tkn0 != tkn1
        ]
        return all_tokens, combos

    def find_arbitrage(self, arb_mode: str):

        all_tokens, combos = self.get_combos(self.CCm, self.flashloan_tokens)
        if self.result == self.AO_TOKENS:
            return all_tokens, combos

        candidates = self.process_combos(
            combos, arb_mode, self.base_exchange, self.CCm, self.ConfigObj
        )

        self.ConfigObj.logger.debug(
            f"\n\ntrade_instructions_df={self.best_trade_instructions_df}\ntrade_instructions_dic={self.best_trade_instructions_dic}\ntrade_instructions={self.best_trade_instructions}\nsrc={self.best_src_token}\n"
        )
        return (
            candidates
            if self.result == self.AO_CANDIDATES
            else (
                self.best_profit,
                self.best_trade_instructions_df,
                self.best_trade_instructions_dic,
                self.best_src_token,
                self.best_trade_instructions,
            )
        )

    def process_combos(self, combos, arb_mode, base_exchange, CCm, ConfigObj):
        candidates = []
        self.ConfigObj.logger.debug(f"\n ************ combos: {len(combos)} ************\n")
        for tkn0, tkn1 in combos:
            self.ConfigObj.logger.debug(
                f"Checking flashloan token = {tkn1}, other token = {tkn0}"
            )
            CC = CCm.bypairs(f"{tkn0}/{tkn1}")
            if len(CC) < 2:
                continue
            base_exchange_curves = [
                x for x in CC.curves if x.params.exchange == base_exchange
            ]
            not_base_exchange_curves = [
                x for x in CC.curves if x.params.exchange != base_exchange
            ]
            curve_combos = self.get_curve_combos(
                arb_mode, base_exchange_curves, not_base_exchange_curves
            )
            candidates += self.process_curve_combos(
                curve_combos, CCm, ConfigObj, tkn0, tkn1, arb_mode
            )
        return candidates

    def get_curve_combos(
        self, arb_mode, base_exchange_curves, not_base_exchange_curves
    ):
        if arb_mode == "multi":
            return [
                [curve] + base_exchange_curves for curve in not_base_exchange_curves
            ]
        elif arb_mode == "single":
            return list(
                itertools.product(not_base_exchange_curves, base_exchange_curves)
            )

    def process_curve_combos(self, curve_combos, CCm, ConfigObj, tkn0, tkn1, arb_mode):
        candidates = []
        for curve_combo in curve_combos:
            CC_cc = CPCContainer(curve_combo)
            O = CPCArbOptimizer(CC_cc)
            src_token = tkn1
            try:
                (
                    profit_src,
                    trade_instructions_df,
                    trade_instructions_dic,
                    trade_instructions,
                    r,
                ) = self.optimize(
                    arb_mode, src_token, curve_combo, tkn0, tkn1, O, CC_cc
                )
            except Exception as e:
                ConfigObj.logger.error(f"[process_curve_combos] {e}")
                continue

            cids = [ti["cid"] for ti in trade_instructions_dic]
            profit = self.calculate_profit(CCm, src_token, r.result)
            ConfigObj.logger.debug(f"Profit in bnt: {num_format(profit)} {cids}")
            netchange = self.get_netchange(trade_instructions_df)

            if len(trade_instructions_df) > 0:
                candidates += self.update_best_profit(
                    ConfigObj,
                    candidates,
                    netchange,
                    profit,
                    src_token,
                    trade_instructions,
                    trade_instructions_df,
                    trade_instructions_dic,
                )
        return candidates

    def update_best_profit(
        self,
        ConfigObj,
        candidates,
        netchange,
        profit,
        src_token,
        trade_instructions,
        trade_instructions_df,
        trade_instructions_dic,
    ):
        condition_better_profit, condition_zeros_one_token = self.get_conditions(
            profit, netchange, ConfigObj, self.best_profit
        )
        candidates = self.add_mandatory_candidates(
            profit,
            ConfigObj,
            src_token,
            trade_instructions_df,
            trade_instructions_dic,
            trade_instructions,
            candidates,
            condition_zeros_one_token,
        )
        if self.is_new_best(profit, self.best_profit, netchange):
            (
                self.best_profit,
                self.best_src_token,
                self.best_trade_instructions,
                self.best_trade_instructions_df,
                self.best_trade_instructions_dic,
                self.ops,
            ) = self.get_ops(
                ConfigObj,
                profit,
                src_token,
                trade_instructions,
                trade_instructions_df,
                trade_instructions_dic,
            )
        return candidates
