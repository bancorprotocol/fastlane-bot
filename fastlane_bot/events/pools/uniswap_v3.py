# coding=utf-8
"""
Contains the pool class for Uniswap v3. This class is responsible for handling Uniswap v3 pools and updating the state of the pools.

(c) Copyright Bprotocol foundation 2023.
Licensed under MIT
"""
from dataclasses import dataclass
from typing import Dict, Any

from web3.contract import Contract

from fastlane_bot.data.pools import uniswap_v3_pools
from fastlane_bot.events.pools.base import Pool


@dataclass
class UniswapV3Pool(Pool):
    """
    Class representing a Uniswap v3 pool.
    """

    exchange_name: str = "uniswap_v3"

    @staticmethod
    def unique_key() -> str:
        """
        see base class.
        """
        return "address"

    @classmethod
    def event_matches_format(cls, event: Dict[str, Any]) -> bool:
        """
        Check if an event matches the format of a Uniswap v3 event.
        """
        event_args = event["args"]
        return "sqrtPriceX96" in event_args and event["address"] in uniswap_v3_pools

    def update_from_event(
        self, event_args: Dict[str, Any], data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        See base class.
        """
        event_args = event_args["args"]
        data["liquidity"] = event_args["liquidity"]
        data["sqrt_price_q96"] = event_args["sqrtPriceX96"]
        data["tick"] = event_args["tick"]

        for key, value in data.items():
            self.state[key] = value

        try:
            data["cid"] = self.state["cid"]
            data["exchange_name"] = self.state["exchange_name"]
            data["fee"] = self.state["fee"]
            data["fee_float"] = self.state["fee_float"]
            data["tick_spacing"] = self.state["tick_spacing"]
        except KeyError as e:
            pass
        except Exception as e:
            print(f"[pools.update_from_event] Exception: {e}")
        return data

    def update_from_contract(self, contract: Contract) -> Dict[str, Any]:
        """
        See base class.
        """
        slot0 = contract.caller.slot0()
        fee = contract.caller.fee()
        params = {
            "tick": slot0[1],
            "sqrt_price_q96": slot0[0],
            "liquidity": contract.caller.liquidity(),
            "fee": fee,
            "fee_float": fee / 1e6,
            "tick_spacing": contract.caller.tickSpacing(),
            "exchange_name": self.state["exchange_name"],
            "address": self.state["address"],
        }
        for key, value in params.items():
            self.state[key] = value
        return params
