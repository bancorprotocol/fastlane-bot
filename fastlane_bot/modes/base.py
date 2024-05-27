"""
Defines the base class for all arbitrage finder modes

[DOC-TODO-OPTIONAL-longer description in rst format]

---
(c) Copyright Bprotocol foundation 2023-24.
All rights reserved.
Licensed under MIT.
"""
import abc
from _decimal import Decimal
from typing import Any, List, Dict

class ArbitrageFinderBase:
    """
    Base class for all arbitrage finder modes
    """

    def __init__(self, flashloan_tokens, CCm, ConfigObj):
        self.flashloan_tokens = flashloan_tokens
        self.CCm = CCm
        self.ConfigObj = ConfigObj
        self.sort_order = {key: index for index, key in enumerate(['bancor_v2', 'bancor_v3'] + ConfigObj.UNI_V2_FORKS + ConfigObj.UNI_V3_FORKS)}

    def find_combos(self) -> List[Any]:
        return self.find_arbitrage()["combos"]

    def find_arb_opps(self) -> List[Any]:
        return self.find_arbitrage()["arb_opps"]

    @abc.abstractmethod
    def find_arbitrage(self) -> Dict[List[Any], List[Any]]:
        """
        See subclasses for details

        Returns
        -------
        A dictionary with:
        - A list of combinations
        - A list of arbitrage opportunities
        """
        ...

    def get_profit(self, src_token: str, optimization, trade_instructions_df):
        if is_net_change_small(trade_instructions_df):
            profit = self.calculate_profit(src_token, -optimization.result)
            if profit.is_finite() and profit > self.ConfigObj.DEFAULT_MIN_PROFIT_GAS_TOKEN:
                return profit
        return None

    def calculate_profit(self, src_token: str, src_profit: float) -> Decimal:
        """
        Calculate profit based on the source token.
        """
        if src_token not in [self.ConfigObj.NATIVE_GAS_TOKEN_ADDRESS, self.ConfigObj.WRAPPED_GAS_TOKEN_ADDRESS]:
            source_prices = get_source_prices(self.CCm, self.ConfigObj.WRAPPED_GAS_TOKEN_ADDRESS, src_token)
            sorted_prices = get_sorted_prices(self.sort_order, self.ConfigObj.CARBON_V1_FORKS, source_prices)
            assert len(sorted_prices) > 0, f"Failed to get conversion rate for {src_token} and {self.ConfigObj.WRAPPED_GAS_TOKEN_ADDRESS}"
            return Decimal(str(src_profit)) / Decimal(str(sorted_prices[0]))
        return Decimal(str(src_profit))

def is_net_change_small(trade_instructions_df) -> bool:
    try:
        return max(trade_instructions_df.iloc[-1]) < 1e-4
    except Exception:
        return False

def get_source_prices(CCm, dst_token, src_token):
    prices_1 = [curve.p / 1 for curve in CCm.bytknx(dst_token).bytkny(src_token).curves]
    prices_2 = [1 / curve.p for curve in CCm.bytknx(src_token).bytkny(dst_token).curves]
    return prices_1 + prices_2

def get_sorted_prices(sort_order, carbon_v1_forks, prices):
    return sorted(prices, key=lambda item: float('inf') if item[0] in carbon_v1_forks else sort_order.get(item[0], float('inf')))
