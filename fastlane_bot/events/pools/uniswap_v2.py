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

from web3 import Web3
from web3.contract import Contract

from fastlane_bot.events.pools.base import Pool
from ..interfaces.event import Event


@dataclass
class UniswapV2Pool(Pool):
    """
    Class representing a Uniswap v2 pool.
    """

    base_exchange_name: str = "uniswap_v2"
    exchange_name: str = "uniswap_v2"
    fee: str = None
    router_address: str = None

    @property
    def fee_float(self):
        return float(self.fee)

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
        Check if an event matches the format of a Uniswap v2 event.
        """
        event_args = event.args
        return (
            "reserve0" in event_args
            and event.address in static_pools[f"{exchange_name}_pools"]
        )

    def update_from_event(
        self, event: Event, data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        See base class.
        """
        data["tkn0_balance"] = event.args["reserve0"]
        data["tkn1_balance"] = event.args["reserve1"]
        for key, value in data.items():
            self.state[key] = value

        data["cid"] = self.state["cid"]
        data["strategy_id"] = 0
        data["fee"] = self.state["fee"]
        data["fee_float"] = self.state["fee_float"]
        data["exchange_name"] = self.state["exchange_name"]
        return data

    def update_from_contract(
        self,
        contract: Contract,
        tenderly_fork_id: str = None,
        w3_tenderly: Web3 = None,
        w3: Web3 = None,
        tenderly_exchanges: List[str] = None,
    ) -> Dict[str, Any]:
        """
        See base class.
        """
        reserve_balance = contract.caller.getReserves()
        params = {
            "fee": self.fee,
            "fee_float": self.fee_float,
            "tkn0_balance": reserve_balance[0],
            "tkn1_balance": reserve_balance[1],
            "exchange_name": self.exchange_name,
            "router": self.router_address,
        }
        for key, value in params.items():
            self.state[key] = value
        return params

    async def async_update_from_contract(self,
        contract: Contract,
        tenderly_fork_id: str = None,
        w3_tenderly: Web3 = None,
        w3: Web3 = None,
        tenderly_exchanges: List[str] = None
         ) -> Dict[str, Any]:
        """
        See base class.
        """
        reserve_balance = await contract.caller.getReserves()
        params = {
            "fee": self.fee,
            "fee_float": self.fee_float,
            "tkn0_balance": reserve_balance[0],
            "tkn1_balance": reserve_balance[1],
            "exchange_name": self.exchange_name,
            "router": self.router_address,
        }
        for key, value in params.items():
            self.state[key] = value
        return params