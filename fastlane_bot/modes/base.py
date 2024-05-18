"""
Defines the base class for all arbitrage finder modes

[DOC-TODO-OPTIONAL-longer description in rst format]

---
(c) Copyright Bprotocol foundation 2023-24.
All rights reserved.
Licensed under MIT.
"""
import abc
from typing import Any, Tuple, Dict, List, Union
from _decimal import Decimal
import pandas as pd

class ArbitrageFinderBase:
    """
    Base class for all arbitrage finder modes
    """

    AO_TOKENS = "tokens"
    AO_CANDIDATES = "candidates"

    def __init__(
        self,
        flashloan_tokens,
        CCm,
        mode="bothin",
        result=AO_CANDIDATES,
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
    def find_arbitrage() -> Union[List, Tuple]:
        """
        See subclasses for details

        Returns
        -------
        Union[List, Tuple]
            If self.result == self.AO_CANDIDATES, it returns a list of candidates.
        """
        pass

    def get_prices_simple(self, CCm, tkn0, tkn1):
        curve_prices = [(x.params['exchange'],x.descr,x.cid,x.p) for x in CCm.bytknx(tkn0).bytkny(tkn1)]
        curve_prices += [(x.params['exchange'],x.descr,x.cid,1/x.p) for x in CCm.bytknx(tkn1).bytkny(tkn0)]
        return curve_prices
    
    # Create a sort order mapping function
    def create_sort_order(self, sort_sequence):
        # Create a dictionary mapping from sort sequence to indices, except for Carbon Forks
        return {key: index for index, key in enumerate(sort_sequence) if key not in self.ConfigObj.CARBON_V1_FORKS}

    # Define the sort key function separately
    def sort_key(self, item, sort_order):
        return float('inf') if item[0] in self.ConfigObj.CARBON_V1_FORKS else sort_order.get(item[0], float('inf'))

    # Define the custom sort function
    def custom_sort(self, data, sort_sequence):
        sort_order = self.create_sort_order(sort_sequence)
        return sorted(data, key=lambda item: self.sort_key(item, sort_order))

    def update_results(
        self,
        src_token: str,
        r,
        trade_instructions_dic,
        trade_instructions_df,
        trade_instructions,
        candidates,
        best_ops,
    ):
        profit = self.calculate_profit(src_token, -r.result, self.CCm)
        if str(profit) != "nan" and is_net_change_small(trade_instructions_df):
            if profit > self.ConfigObj.DEFAULT_MIN_PROFIT_GAS_TOKEN:
                candidates.append(
                    (
                        profit,
                        trade_instructions_df,
                        trade_instructions_dic,
                        src_token,
                        trade_instructions,
                    )
                )
            if best_ops is None or profit > best_ops[0]:
                best_ops = (
                    profit,
                    trade_instructions_df,
                    trade_instructions_dic,
                    src_token,
                    trade_instructions,
                )
        return best_ops

    def calculate_profit(
        self,
        src_token: str,
        profit_src: float,
        CCm: Any,
    ) -> float:
        """
        Calculate profit based on the source token.
        """

        best_profit_fl_token = profit_src
        if src_token not in [
            self.ConfigObj.NATIVE_GAS_TOKEN_ADDRESS,
            self.ConfigObj.WRAPPED_GAS_TOKEN_ADDRESS,
        ]:
            if src_token == self.ConfigObj.NATIVE_GAS_TOKEN_ADDRESS:
                fl_token_with_weth = self.ConfigObj.WRAPPED_GAS_TOKEN_ADDRESS
            else:
                fl_token_with_weth = src_token

            sort_sequence = ['bancor_v2','bancor_v3','uniswap_v2','uniswap_v3']
            price_curves = self.get_prices_simple(CCm, self.ConfigObj.WRAPPED_GAS_TOKEN_ADDRESS, fl_token_with_weth)
            sorted_price_curves = self.custom_sort(price_curves, sort_sequence)
            self.ConfigObj.logger.debug(f"[modes.base.calculate_profit sort_sequence] {sort_sequence}")
            self.ConfigObj.logger.debug(f"[modes.base.calculate_profit price_curves] {price_curves}")
            self.ConfigObj.logger.debug(f"[modes.base.calculate_profit sorted_price_curves] {sorted_price_curves}")
            if len(sorted_price_curves)>0:
                fltkn_eth_conversion_rate = sorted_price_curves[0][-1]
                best_profit_eth = Decimal(str(best_profit_fl_token)) / Decimal(str(fltkn_eth_conversion_rate))
                self.ConfigObj.logger.debug(f"[modes.base.calculate_profit] {src_token, best_profit_fl_token, fltkn_eth_conversion_rate, best_profit_eth}")
            else:
                self.ConfigObj.logger.error(
                    f"[modes.base.calculate_profit] Failed to get conversion rate for {fl_token_with_weth} and {self.ConfigObj.WRAPPED_GAS_TOKEN_ADDRESS}. Raise"
                )
                raise
        else:
            best_profit_eth = best_profit_fl_token
        return best_profit_eth

def is_net_change_small(trade_instructions_df: pd.DataFrame) -> bool:
    """
    Check if the net change from the trade instructions is sufficiently small.
    """
    try:
        return max(trade_instructions_df.iloc[-1]) < 1e-4
    except Exception:
        return False
