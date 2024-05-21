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
class BancorV2Pool(Pool):
    """
    Class representing a Bancor v2 pool.
    """

    exchange_name: str = "bancor_v2"

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
        Check if an event matches the format of a Bancor v2 event.

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
        return "_rateN" in event_args

    def update_from_event(
        self, event: Event, data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        **** IMPORTANT ****
        Bancor V2 pools emit 3 events per trade. Only one of them contains the new token balances we want.
        The one we want is the one where _token1 and _token2 match the token addresses of the pool.
        """
        data["tkn0_address"] = event.args["_token1"]
        data["tkn1_address"] = event.args["_token2"]
        data["tkn0_balance"] = event.args["_rateD"]
        data["tkn1_balance"] = event.args["_rateN"]

        for key, value in data.items():
            self.state[key] = value

        data["anchor"] = self.state["anchor"]
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
        reserve0, reserve1 = contract.caller.reserveBalances()
        tkn0_address, tkn1_address = contract.caller.reserveTokens()
        fee = contract.caller.conversionFee()

        params = {
            "fee": fee,
            "fee_float": fee / 1e6,
            "exchange_name": self.state["exchange_name"],
            "address": self.state["address"],
            "anchor": contract.caller.anchor(),
            "tkn0_balance": reserve0,
            "tkn1_balance": reserve1,
            "tkn0_address": tkn0_address,
            "tkn1_address": tkn1_address,
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
        reserve0, reserve1 = await contract.caller.reserveBalances()
        tkn0_address, tkn1_address = await contract.caller.reserveTokens()
        fee = await contract.caller.conversionFee()

        params = {
            "fee": fee,
            "fee_float": fee / 1e6,
            "exchange_name": self.state["exchange_name"],
            "address": self.state["address"],
            "anchor": await contract.caller.anchor(),
            "tkn0_balance": reserve0,
            "tkn1_balance": reserve1,
            "tkn0_address": tkn0_address,
            "tkn1_address": tkn1_address,
        }
        for key, value in params.items():
            self.state[key] = value
        return params
