import abc
from typing import Any


class ArbitrageFinderBase:
    """
    Base class for all arbitrage finder modes
    """

    XS_ARBOPPS = "arbopps"
    XS_TI = "ti"
    XS_EXACT = "exact"
    XS_ORDSCAL = "ordscal"
    XS_AGGTI = "aggti"
    XS_ORDINFO = "ordinfo"
    XS_ENCTI = "encti"
    XS_ROUTE = "route"

    AM_REGULAR = "regular"
    AM_SINGLE = "single"
    AM_TRIANGLE = "triangle"
    AM_MULTI = "multi"
    AM_MULTI_TRIANGLE = "multi_triangle"
    AM_BANCOR_V3 = "bancor_v3"

    AO_TOKENS = "tokens"
    AO_CANDIDATES = "candidates"

    def __init__(
        self,
        flashloan_tokens,
        CCm,
        mode="bothin",
        result=None,
        ConfigObj: Any = None,
        arb_mode: str = None,
    ):
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
        self.base_exchange = "bancor_v3" if arb_mode == "bancor_v3" else "carbon_v1"

    @abc.abstractmethod
    def get_trade_instructions(
        self, arb_mode, trade_instructions_df, curve_combo, tkn0, tkn1, src_token, r, O
    ):
        pass

    @abc.abstractmethod
    def find_arbitrage(self, arb_mode: str):
        pass

    @abc.abstractmethod
    def optimize(self, arb_mode, src_token, curve_combo, tkn0, tkn1, O, CC_cc):
        pass

    def calculate_profit(self, CCm, src_token, result):
        profit_src = -result
        if src_token == "BNT-FF1C":
            profit = profit_src
        else:
            try:
                price_src_per_bnt = (
                    CCm.bypair(pair=f"BNT-FF1C/{src_token}")
                    .byparams(exchange="bancor_v3")[0]
                    .p
                )
                profit = profit_src / price_src_per_bnt
            except Exception as e:
                self.ConfigObj.logger.error(f"{e}")
        return profit

    def get_netchange(self, trade_instructions_df):
        try:
            return trade_instructions_df.iloc[-1]
        except Exception as e:
            return [500]

    def get_conditions(self, profit, netchange, ConfigObj, best_profit):
        condition_better_profit = profit > best_profit
        ConfigObj.logger.debug(f"profit > best_profit: {condition_better_profit}")
        condition_zeros_one_token = max(netchange) < 1e-4
        ConfigObj.logger.debug(f"max(netchange)<1e-4: {condition_zeros_one_token}")
        return condition_better_profit, condition_zeros_one_token

    def add_mandatory_candidates(
            self,
            profit,
            ConfigObj,
            src_token,
            trade_instructions_df,
            trade_instructions_dic,
            trade_instructions,
            candidates,
            condition_zeros_one_token,
    ):
        if (
                condition_zeros_one_token and profit > ConfigObj.DEFAULT_MIN_PROFIT
        ):  # candidate regardless if profitable
            candidates += [
                (
                    profit,
                    trade_instructions_df,
                    trade_instructions_dic,
                    src_token,
                    trade_instructions,
                )
            ]

        return candidates

    def is_new_best(self, profit, best_profit, netchange):
        condition_better_profit = profit > best_profit
        condition_zeros_one_token = max(netchange) < 1e-4
        return condition_better_profit and condition_zeros_one_token
