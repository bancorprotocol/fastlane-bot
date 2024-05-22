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
        profit = self.calculate_profit(src_token, -optimization.result, self.CCm)
        return profit if profit.is_finite() and profit > self.ConfigObj.DEFAULT_MIN_PROFIT_GAS_TOKEN and is_net_change_small(trade_instructions_df) else None

    def calculate_profit(self, src_token: str, src_profit: float, CCm: Any) -> Decimal:
        """
        Calculate profit based on the source token.
        """
        if src_token not in [self.ConfigObj.NATIVE_GAS_TOKEN_ADDRESS, self.ConfigObj.WRAPPED_GAS_TOKEN_ADDRESS]:
            sort_sequence = ['bancor_v2', 'bancor_v3', 'uniswap_v2', 'uniswap_v3']
            price_curves = get_prices_simple(CCm, self.ConfigObj.WRAPPED_GAS_TOKEN_ADDRESS, src_token)
            sorted_price_curves = custom_sort(price_curves, sort_sequence, self.ConfigObj.CARBON_V1_FORKS)
            self.ConfigObj.logger.debug(f"[modes.base.calculate_profit sort_sequence] {sort_sequence}")
            self.ConfigObj.logger.debug(f"[modes.base.calculate_profit price_curves] {price_curves}")
            self.ConfigObj.logger.debug(f"[modes.base.calculate_profit sorted_price_curves] {sorted_price_curves}")
            assert len(sorted_price_curves) > 0, f"[modes.base.calculate_profit] Failed to get conversion rate for {src_token} and {self.ConfigObj.WRAPPED_GAS_TOKEN_ADDRESS}"
            return Decimal(str(src_profit)) / Decimal(str(sorted_price_curves[0][-1]))
        return Decimal(str(src_profit))

def is_net_change_small(trade_instructions_df) -> bool:
    try:
        return max(trade_instructions_df.iloc[-1]) < 1e-4
    except Exception:
        return False

def get_prices_simple(CCm, dst_token, src_token):
    curve_prices = [(CC.params['exchange'],CC.descr,CC.cid,CC.p) for CC in CCm.bytknx(dst_token).bytkny(src_token)]
    curve_prices += [(CC.params['exchange'],CC.descr,CC.cid,1/CC.p) for CC in CCm.bytknx(src_token).bytkny(dst_token)]
    return curve_prices

def custom_sort(data, sort_sequence, carbon_v1_forks):
    sort_order = {key: index for index, key in enumerate(sort_sequence) if key not in carbon_v1_forks}
    return sorted(data, key=lambda item: float('inf') if item[0] in carbon_v1_forks else sort_order.get(item[0], float('inf')))
