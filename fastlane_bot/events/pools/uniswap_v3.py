# coding=utf-8
"""
Contains the pool class for Uniswap v3. This class is responsible for handling Uniswap v3 pools and updating the state of the pools.

(c) Copyright Bprotocol foundation 2023.
Licensed under MIT
"""
from dataclasses import dataclass
from typing import Dict, Any, List

from web3.contract import Contract

from fastlane_bot.events.pools.base import Pool


@dataclass
class UniswapV3Pool(Pool):
    """
    Class representing a Uniswap v3 pool.
    """
    base_exchange_name: str = "uniswap_v3"
    exchange_name: str = "uniswap_v3"
    router_address: str = None

    @staticmethod
    def unique_key() -> str:
        """
        see base class.
        """
        return "address"

    @classmethod
    def event_matches_format(
        cls, event: Dict[str, Any], static_pools: Dict[str, Any], exchange_name: str = None
    ) -> bool:
        """
        Check if an event matches the format of a Uniswap v3 event.
        """
        event_args = event["args"]
        return (
            "sqrtPriceX96" in event_args
            and event["address"] in static_pools[f"{exchange_name}_pools"]
        )

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

    def update_from_contract(
        self,
        contract: Contract,
        tenderly_fork_id: str = None,
        w3_tenderly: Any = None,
        w3: Any = None,
        tenderly_exchanges: List[str] = None,
    ) -> Dict[str, Any]:
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
            "router": self.router_address,
        }
        for key, value in params.items():
            self.state[key] = value
        return params

    async def async_update_from_contract(
        self,
        contract: Contract,
        tenderly_fork_id: str = None,
        w3_tenderly: Any = None,
        w3: Any = None,
        tenderly_exchanges: List[str] = None,
    ) -> Dict[str, Any]:
        """
        See base class.
        """
        fee = await contract.caller.fee()
        factory_address = await contract.caller.factory()
        slot0 = await contract.caller.slot0()

        params = {
            "tick": slot0[1],
            "sqrt_price_q96": slot0[0],
            "liquidity": await contract.caller.liquidity(),
            "fee": fee,
            "fee_float": fee / 1e6,
            "tick_spacing": await contract.caller.tickSpacing(),
            "exchange_name": self.state["exchange_name"],
            "address": self.state["address"],
            "router": self.router_address,
            "factory": factory_address,
        }
        for key, value in params.items():
            self.state[key] = value
        return params