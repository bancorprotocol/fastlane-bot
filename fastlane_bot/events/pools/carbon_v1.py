# coding=utf-8
"""
Contains the pool class for Carbon v1. This class is responsible for handling Carbon v1 pools and updating the state of the pools.

(c) Copyright Bprotocol foundation 2023.
Licensed under MIT
"""
from dataclasses import dataclass
from typing import Dict, Any, Tuple, List

from web3.contract import Contract

from .base import Pool


@dataclass
class CarbonV1Pool(Pool):
    """
    Class representing a Carbon v1 pool.
    """

    exchange_name: str = "carbon_v1"

    @staticmethod
    def unique_key() -> str:
        """
        see base class.
        """
        return "cid"

    @classmethod
    def event_matches_format(cls, event: Dict[str, Any]) -> bool:
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
        data = CarbonV1Pool.parse_event(data, event_args, event_type)
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
        order0, order1 = CarbonV1Pool.parse_orders(event_args, event_type)
        data["cid"] = event_args["args"].get("id")
        data["y_0"] = order0[0]
        data["z_0"] = order0[1]
        data["A_0"] = order0[2]
        data["B_0"] = order0[3]
        data["y_1"] = order1[0]
        data["z_1"] = order1[1]
        data["A_1"] = order1[2]
        data["B_1"] = order1[3]
        return data

    @staticmethod
    def parse_orders(
        event_args: Dict[str, Any], event_type: str
    ) -> Tuple[List[int], List[int]]:
        """
        Parse the orders from the event args. If the event type is StrategyDeleted, then the orders are set to 0.

        Parameters
        ----------
        event_args : Dict[str, Any]
            The event arguments.
        event_type : str
            The event type.

        Returns
        -------
        Tuple[List[int], List[int]]
            The parsed orders.
        """
        if event_type != "StrategyDeleted":
            order0 = event_args["args"].get("order0")
            order1 = event_args["args"].get("order1")
        else:
            order0 = [0, 0, 0, 0]
            order1 = [0, 0, 0, 0]
        return order0, order1

    def update_from_contract(self, contract: Contract) -> Dict[str, Any]:
        """
        See base class.
        """
        try:
            strategy = contract.strategy(self.state["cid"])
        except AttributeError:
            strategy = contract.caller.strategy(self.state["cid"])

        fake_event = {
            "args": {
                "id": strategy[0],
                "order0": strategy[3][0],
                "order1": strategy[3][1],
            }
        }
        params = self.parse_event(self.state, fake_event, "None")
        params["fee"] = "0.002"
        params["fee_float"] = 0.002
        params["exchange_name"] = "carbon_v1"
        for key, value in params.items():
            self.state[key] = value
        return params
