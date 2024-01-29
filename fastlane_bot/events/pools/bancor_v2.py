# coding=utf-8
"""
Contains the pool class for bancor v2. This class is responsible for handling bancor v2 pools and updating the state of the pools.

(c) Copyright Bprotocol foundation 2023.
Licensed under MIT
"""
from dataclasses import dataclass
from typing import Dict, Any, List

from web3 import Web3
from web3.contract import Contract

from fastlane_bot.events.pools.base import Pool


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
        cls, event: Dict[str, Any], static_pools: Dict[str, Any], exchange_name: str = None
    ) -> bool:
        """
        Check if an event matches the format of a Bancor v2 event.

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
        return "_rateN" in event_args

    def update_from_event(
        self, event_args: Dict[str, Any], data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        **** IMPORTANT ****
        Bancor V2 pools emit 3 events per trade. Only one of them contains the new token balances we want.
        The one we want is the one where _token1 and _token2 match the token addresses of the pool.
        """
        data["tkn0_address"] = event_args["args"]["_token1"]
        data["tkn1_address"] = event_args["args"]["_token2"]
        data["tkn0_balance"] = event_args["args"]["_rateD"]
        data["tkn1_balance"] = event_args["args"]["_rateN"]

        # if (
        #     self.state["tkn0_address"] == event_args["args"]["_token1"]
        #     and self.state["tkn1_address"] == event_args["args"]["_token2"]
        # ):
        #     data["tkn0_balance"] = event_args["args"]["_rateD"]
        #     data["tkn1_balance"] = event_args["args"]["_rateN"]
        #     case = 1
        # elif (
        #     self.state["tkn0_address"] == event_args["args"]["_token2"]
        #     and self.state["tkn1_address"] == event_args["args"]["_token1"]
        # ):
        #     data["tkn0_balance"] = event_args["args"]["_rateN"]
        #     data["tkn1_balance"] = event_args["args"]["_rateD"]
        #     case = 2
        # else:
        #     data["tkn0_balance"] = self.state["tkn0_balance"]
        #     data["tkn1_balance"] = self.state["tkn1_balance"]
        #     case = 3

        # print(f"case: {case}, address: {self.state['address']}, event: {event_args}")

        for key, value in data.items():
            self.state[key] = value

        data["anchor"] = self.state["anchor"]
        data["cid"] = self.state["cid"]
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

        # for i in [0, 1]:
        #     conv_token = await contract.functions.connectorTokens(i).call()
        #     if conv_token != '0x1F573D6Fb3F13d689FF844B4cE37794d79a7FF1C':
        #

        # if tkn0_address != self.state["tkn0_address"]:
        #     print(f"balance is flipped...")
        #     reserve0c, reserve1c = reserve0, reserve1
        #     reserve1, reserve0 = reserve0c, reserve1c

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
