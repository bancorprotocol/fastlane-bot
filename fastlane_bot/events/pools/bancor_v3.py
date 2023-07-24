# coding=utf-8
"""
Contains the exchange class for BancorV3. This class is responsible for handling BancorV3 events and updating the state of the pools.

(c) Copyright Bprotocol foundation 2023.
Licensed under MIT
"""
from dataclasses import dataclass
from typing import Dict, Any

from web3.contract import Contract

from .base import Pool


@dataclass
class BancorV3Pool(Pool):
    """
    Class representing a Bancor v3 pool.
    """

    exchange_name: str = "bancor_v3"

    @staticmethod
    def unique_key() -> str:
        """
        see base class.
        """
        return "tkn1_address"

    @classmethod
    def event_matches_format(cls, event: Dict[str, Any]) -> bool:
        """
        Check if an event matches the format of a Bancor v3 event.

        Parameters
        ----------
        event : Dict[str, Any]
            The event arguments.

        Returns
        -------
        bool
            True if the event matches the format of a Bancor v3 event, False otherwise.

        """
        event_args = event["args"]
        return "pool" in event_args

    def update_from_event(
        self, event_args: Dict[str, Any], data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        See base class.
        """
        event_args = event_args["args"]
        if event_args["tkn_address"] == "0x1F573D6Fb3F13d689FF844B4cE37794d79a7FF1C":
            data["tkn0_balance"] = event_args["newLiquidity"]
        else:
            data["tkn1_balance"] = event_args["newLiquidity"]

        for key, value in data.items():
            self.state[key] = value

        data["cid"] = self.state["cid"]
        data["fee"] = self.state["fee"]
        data["fee_float"] = self.state["fee_float"]
        data["exchange_name"] = self.state["exchange_name"]
        return data

    def update_from_contract(self, contract: Contract) -> Dict[str, Any]:
        """
        See base class.
        """
        pool_balances = contract.tradingLiquidity(self.state["tkn1_address"])
        params = {
            "fee": "0.000",
            "fee_float": 0.000,
            "tkn0_balance": pool_balances[0],
            "tkn1_balance": pool_balances[1],
            "exchange_name": self.state["exchange_name"],
            "address": self.state["address"],
        }
        for key, value in params.items():
            self.state[key] = value
        return params
