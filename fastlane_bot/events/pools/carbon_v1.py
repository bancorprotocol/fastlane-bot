# coding=utf-8
"""
Contains the pool class for Carbon v1. This class is responsible for handling Carbon v1 pools and updating the state of the pools.

(c) Copyright Bprotocol foundation 2023.
Licensed under MIT
"""
from dataclasses import dataclass
from typing import Dict, Any, Tuple, List

from web3 import Web3
from web3.contract import Contract

from .base import Pool


@dataclass
class CarbonV1Pool(Pool):
    """
    Class representing a Carbon v1 pool.
    """

    exchange_name: str = "carbon_v1"
    router_address: str = None

    @staticmethod
    def unique_key() -> str:
        """
        see base class.
        """
        return "cid"

    @classmethod
    def event_matches_format(
        cls, event: Dict[str, Any], static_pools: Dict[str, Any], exchange_name: str = None
    ) -> bool:
        """
        see base class.
        """
        event_args = event["args"]
        return "order0" in event_args

    def update_from_event(
        self, event_args: Dict[str, Any], data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        See base class.
        """
        event_type = event_args["event"]
        assert event_type not in ["TradingFeePPMUpdated", "PairTradingFeePPMUpdated"], (
            "This event should not be " "handled by this class."
        )
        data = CarbonV1Pool.parse_event(data, event_args, event_type)
        data["router"] = self.router_address,
        for key, value in data.items():
            self.state[key] = value
        return data

    @staticmethod
    def parse_event(
        data: Dict[str, Any], event_args: Dict[str, Any], event_type: str
    ) -> Dict[str, Any]:
        """
        Parse the event args into a dict.

        Parameters
        ----------
        data : Dict[str, Any]
            The data to update.
        event_args : Dict[str, Any]
            The event arguments.
        event_type : str
            The event type.

        Returns
        -------
        Dict[str, Any]
            The updated data.
        """
        if event_type not in ["StrategyDeleted"]:
            order0 = event_args["args"].get("order0")
            order1 = event_args["args"].get("order1")
        else:
            order0 = {"y_0": 0, "z_0": 0, "A_0": 0, "B_0": 0}
            order1 = {"y_1": 0, "z_1": 0, "A_1": 0, "B_1": 0}
        data["cid"] = event_args["args"].get("id")
        data["y_0"] = order0["y"]
        data["z_0"] = order0["z"]
        data["A_0"] = order0["A"]
        data["B_0"] = order0["B"]
        data["y_1"] = order1["y"]
        data["z_1"] = order1["z"]
        data["A_1"] = order1["A"]
        data["B_1"] = order1["B"]

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

        strategy = contract.caller.strategy(int(self.state["cid"]))

        y_0, z_0, A_0, B_0 = strategy[3][0]
        y_1, z_1, A_1, B_1 = strategy[3][1]

        params = {"cid": strategy[0],
                  "y_0": y_0, "z_0": z_0, "A_0": A_0, "B_0": B_0,
                  "y_1": y_1, "z_1": z_1, "A_1": A_1, "B_1": B_1,
                  "exchange_name": self.exchange_name,
                  "router": (self.router_address,)}

        for key, value in params.items():
            self.state[key] = value

        return params
