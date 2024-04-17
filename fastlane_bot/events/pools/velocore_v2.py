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
from fastlane_bot.data.abi import VELOCORE_V2_LENS_ABI


@dataclass
class VelocoreV2Pool(Pool):
    """
    Class representing a Velocore v2 pool.
    """
    base_exchange_name: str = "velocore_v2"
    exchange_name: str = "velocore_v2"
    fee: str = None
    router_address: str = None
    # If this is false, it's a Uni V2 style pool
    is_stable: bool = None


    @property
    def fee_float(self):
        return float(self.fee)

    @property
    def pool_type(self):
        return "stable" if self.is_stable else "volatile"

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
        Check if an event matches the format of a Velocore v2 event.
        """
        event_args = event["args"]
        # print(event_args)
        return (
            "delta" in event_args
            and event_args["pool"] in static_pools[f"{exchange_name}_pools"]
        )

    def update_from_event(
        self, event_args: Dict[str, Any], data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        See base class.
        """
        event_args = event_args["args"]
        data["tkn0_balance"] = event_args["reserve0"]
        data["tkn1_balance"] = event_args["reserve1"]
        for key, value in data.items():
            self.state[key] = value

        data["cid"] = self.state["cid"]
        data["strategy_id"] = 0
        data["fee"] = self.state["fee"]
        data["fee_float"] = self.state["fee_float"]
        data["exchange_name"] = self.state["exchange_name"]
        data["router"] = self.router_address
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
        lens_contract = w3.eth.contract(address="0xaA18cDb16a4DD88a59f4c2f45b5c91d009549e06", abi=VELOCORE_V2_LENS_ABI) #TODO import this properly
        reserve_balance = lens_contract.caller.queryPool(contract.address)
        self.is_stable = False   # stable pools currently out of scope for velocore
        
        params = {

            "tkn0_balance": reserve_balance[-2][0],
            "tkn1_balance": reserve_balance[-2][1],
            "exchange_name": self.exchange_name,
            "router": self.router_address,
            "pool_type": self.pool_type,
        }
        for key, value in params.items():
            self.state[key] = value
        return params
    async def async_update_from_contract(
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
        lens_contract = w3.eth.contract(address="0xaA18cDb16a4DD88a59f4c2f45b5c91d009549e06", abi=VELOCORE_V2_LENS_ABI)  #TODO import this properly
        reserve_balance = await lens_contract.caller.queryPool(contract.address)
        self.is_stable = False   # stable pools currently out of scope for velocore

        params = {

            "tkn0_balance": reserve_balance[-2][0],
            "tkn1_balance": reserve_balance[-2][1],
            "exchange_name": self.exchange_name,
            "router": self.router_address,
            "pool_type": self.pool_type,
        }
        for key, value in params.items():
            self.state[key] = value
        return params