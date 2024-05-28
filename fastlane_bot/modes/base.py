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
        self.sort_order = {
            key: index for index, key in enumerate(
                ["bancor_v2", "bancor_v3"]
                + ConfigObj.UNI_V2_FORKS
                + ConfigObj.UNI_V3_FORKS
            )
        }

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
        if src_token not in [self.ConfigObj.NATIVE_GAS_TOKEN_ADDRESS, self.ConfigObj.WRAPPED_GAS_TOKEN_ADDRESS]:
            price = self.find_reliable_price(self.CCm, self.ConfigObj.WRAPPED_GAS_TOKEN_ADDRESS, src_token)
            assert price is not None, f"No conversion rate for {self.ConfigObj.WRAPPED_GAS_TOKEN_ADDRESS} and {src_token}"
            return Decimal(str(src_profit)) / Decimal(str(price))
        return Decimal(str(src_profit))

    def get_params(self, cc, dst_tokens, src_token):
        pstart = {src_token: 1}
        for dst_token in dst_tokens:
            if dst_token != src_token:
                pstart[dst_token] = self.find_reliable_price(cc, dst_token, src_token)
                if pstart[dst_token] is None:
                    return None
        return {"pstart": pstart}

    def find_reliable_price(self, cc, dst_token, src_token):
        list1 = [{"exchange": curve.params.exchange, "price": curve.p / 1} for curve in cc.bytknx(dst_token).bytkny(src_token).curves]
        list2 = [{"exchange": curve.params.exchange, "price": 1 / curve.p} for curve in cc.bytknx(src_token).bytkny(dst_token).curves]
        items = sorted(list1 + list2, key = lambda item: self.sort_order.get(item["exchange"], float("inf")))
        return items[0]["price"] if len(items) > 0 else None

def is_net_change_small(trade_instructions_df) -> bool:
    try:
        return max(trade_instructions_df.iloc[-1]) < 1e-4
    except Exception:
        return False
