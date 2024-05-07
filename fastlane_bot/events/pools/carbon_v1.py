"""
[DOC-TODO-short description of what the file does, max 80 chars]

[DOC-TODO-OPTIONAL-longer description in rst format]

---
(c) Copyright Bprotocol foundation 2023-24.
All rights reserved.
Licensed under MIT.
"""
from dataclasses import dataclass
from typing import Dict, Any, Tuple, List

from web3 import Web3
from web3.contract import Contract

from .base import Pool
from ..interfaces.event import Event
from fastlane_bot.events.pools.utils import get_pool_cid


@dataclass
class CarbonV1Pool(Pool):
    """
    Class representing a Carbon v1 pool.
    """
    base_exchange_name: str = "carbon_v1"
    exchange_name: str = None
    router_address: str = None

    @staticmethod
    def unique_key() -> str:
        """
        see base class.
        """
        return "cid"

    @classmethod
    def event_matches_format(
        cls, event: Event, static_pools: Dict[str, Any], exchange_name: str = None
    ) -> bool:
        """
        see base class.
        """
        event_args = event.args
        return "order0" in event_args

    def update_from_event(
        self, event: Event, data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        See base class.
        """
        assert event.event not in ["TradingFeePPMUpdated", "PairTradingFeePPMUpdated"], (
            "This event should not be " "handled by this class."
        )
        data = CarbonV1Pool.parse_event(data, event)
        data["router"] = self.router_address
        for key, value in data.items():
            self.state[key] = value
        return data

    @staticmethod
    def parse_event(data: Dict[str, Any], event: Event) -> Dict[str, Any]:
        """
        Parse the event args into a dict.

        Parameters
        ----------
        data : Dict[str, Any]
            The data to update.
        event_args : Event
            The event object.

        Returns
        -------
        Dict[str, Any]
            The updated data.
        """
        order0, order1 = CarbonV1Pool.parse_orders(event)
        data["strategy_id"] = event.args.get("id")
        if isinstance(order0, list) and isinstance(order1, list):
            data["y_0"] = order0[0]
            data["z_0"] = order0[1]
            data["A_0"] = order0[2]
            data["B_0"] = order0[3]
            data["y_1"] = order1[0]
            data["z_1"] = order1[1]
            data["A_1"] = order1[2]
            data["B_1"] = order1[3]
        else:
            data["y_0"] = order0["y"]
            data["z_0"] = order0["z"]
            data["A_0"] = order0["A"]
            data["B_0"] = order0["B"]
            data["y_1"] = order1["y"]
            data["z_1"] = order1["z"]
            data["A_1"] = order1["A"]
            data["B_1"] = order1["B"]

        return data

    @staticmethod
    def parse_orders(event: Event) -> Tuple[List[int], List[int]]:
        """
        Parse the orders from the event args. If the event type is StrategyDeleted, then the orders are set to 0.

        Parameters
        ----------
        event_args : Dict[str, Any]
            The event arguments.

        Returns
        -------
        Tuple[List[int], List[int]]
            The parsed orders.
        """
        if event.event not in ["StrategyDeleted"]:
            order0 = event.args.get("order0")
            order1 = event.args.get("order1")
        else:
            order0 = [0, 0, 0, 0]
            order1 = [0, 0, 0, 0]
        return order0, order1

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
        strategy = contract.caller.strategy(int(self.state["strategy_id"]))

        fake_event = {
            "args": {
                "id": strategy[0],
                "order0": strategy[3][0],
                "order1": strategy[3][1],
            }
        }
        params = self.parse_event(self.state, fake_event, "None")
        params["exchange_name"] = self.exchange_name
        params["router"] = self.router_address
        params["fee"] = self.state["fee"]
        carbon_v1_fork_list = [self.exchange_name]  # This is safe because we are in the CarbonV1Pool class
        params["cid"] = get_pool_cid(params, carbon_v1_fork_list)
        for key, value in params.items():
            self.state[key] = value

        return params


