# coding=utf-8
"""
Contains the pool class for bancor v2. This class is responsible for handling bancor v2 pools and updating the state of the pools.

(c) Copyright Bprotocol foundation 2023.
Licensed under MIT
"""
from dataclasses import dataclass
from typing import Dict, Any

import web3
from web3.contract import Contract

from fastlane_bot import Config
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
    def event_matches_format(cls, event: Dict[str, Any]) -> bool:
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

        if (
            self.state["tkn0_address"] == event_args["args"]["_token1"]
            and self.state["tkn1_address"] == event_args["args"]["_token2"]
        ):
            data["tkn0_balance"] = event_args["args"]["_rateN"]
            data["tkn1_balance"] = event_args["args"]["_rateD"]
        elif (
            self.state["tkn0_address"] == event_args["args"]["_token2"]
            and self.state["tkn1_address"] == event_args["args"]["_token1"]
        ):
            data["tkn0_balance"] = event_args["args"]["_rateD"]
            data["tkn1_balance"] = event_args["args"]["_rateN"]
        else:
            data["tkn0_balance"] = self.state["tkn0_balance"]
            data["tkn1_balance"] = self.state["tkn1_balance"]

        for key, value in data.items():
            self.state[key] = value

        data["cid"] = self.state["cid"]
        data["fee"] = self.state["fee"]
        data["fee_float"] = self.state["fee_float"]
        data["exchange_name"] = self.state["exchange_name"]
        return data

    def update_from_contract(
        self, contract: Contract, cfg: Config = None
    ) -> Dict[str, Any]:
        """
        See base class.
        """
        try:
            reserve0, reserve1 = contract.functions.reserveBalances().call()
            tkn0_address, tkn1_address = contract.functions.reserveTokens().call()
            fee = contract.functions.conversionFee().call()

            params = {
                "fee": fee,
                "fee_float": fee / 1e6,
                "exchange_name": self.state["exchange_name"],
                "address": self.state["address"],
                "anchor": contract.functions.anchor().call(),
                "tkn0_balance": reserve0,
                "tkn1_balance": reserve1,
                "tkn0_address": tkn0_address,
                "tkn1_address": tkn1_address,
            }
            for key, value in params.items():
                self.state[key] = value
            return params

        except web3.exceptions.ContractLogicError:
            cfg.logger.warning(
                "\n"
                "*****************"
                f"[events.pools.update_from_contract] \n"
                f"Bancor V2 ContractLogicError:\n"
                f"typically means that the contract address={contract.address} in the event is not valid. skipping..."
                "*****************"
                "\n"
            )
            return None
