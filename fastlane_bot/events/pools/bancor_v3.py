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

from .base import Pool
from ..interfaces.event import Event


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
    def event_matches_format(
        cls, event: Event, static_pools: Dict[str, Any], exchange_name: str = None
    ) -> bool:
        """
        Check if an event matches the format of a Bancor v3 event.

        Parameters
        ----------
        event : Event
            The event arguments.

        Returns
        -------
        bool
            True if the event matches the format of a Bancor v3 event, False otherwise.

        """
        event_args = event.args
        return "pool" in event_args

    def update_from_event(
        self, event: Event, data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        See base class.
        """
        if event.args["tkn_address"] == "0x1F573D6Fb3F13d689FF844B4cE37794d79a7FF1C":
            data["tkn0_balance"] = event.args["newLiquidity"]
        else:
            data["tkn1_balance"] = event.args["newLiquidity"]

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
        pool_balances = contract.caller.tradingLiquidity(self.state["tkn1_address"])

        params = {
            "fee": self.state["fee"],
            "fee_float": self.state["fee_float"],
            "tkn0_balance": pool_balances[0],
            "tkn1_balance": pool_balances[1],
            "exchange_name": self.state["exchange_name"],
            "address": self.state["address"],
        }
        for key, value in params.items():
            self.state[key] = value
        return params
