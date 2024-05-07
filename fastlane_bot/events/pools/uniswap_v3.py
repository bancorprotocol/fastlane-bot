"""
[DOC-TODO-short description of what the file does, max 80 chars]

[DOC-TODO-OPTIONAL-longer description in rst format]

---
(c) Copyright Bprotocol foundation 2023-24.
All rights reserved.
Licensed under MIT.
"""
from dataclasses import dataclass
from typing import Dict, Any, List

from web3.contract import Contract

from fastlane_bot.events.pools.base import Pool
from ..interfaces.event import Event


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
        cls, event: Event, static_pools: Dict[str, Any], exchange_name: str = None
    ) -> bool:
        """
        Check if an event matches the format of a Uniswap v3 event.
        """
        event_args = event.args
        return (
            "sqrtPriceX96" in event_args
            and event.address in static_pools[f"{exchange_name}_pools"]
        )

    def update_from_event(
        self, event: Event, data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        See base class.
        """
        data["liquidity"] = event.args["liquidity"]
        data["sqrt_price_q96"] = event.args["sqrtPriceX96"]
        data["tick"] = event.args["tick"]

        for key, value in data.items():
            self.state[key] = value

        try:
            data["cid"] = self.state["cid"]
            data["strategy_id"] = 0
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
        }
        for key, value in params.items():
            self.state[key] = value
        return params