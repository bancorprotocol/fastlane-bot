# coding=utf-8
"""
Contains the exchange class for BancorV3. This class is responsible for handling BancorV3 events and updating the state of the pools.

(c) Copyright Bprotocol foundation 2023.
Licensed under MIT
"""
from dataclasses import dataclass
from typing import Dict, Any

import web3
from web3.contract import Contract

from fastlane_bot.events.pools.base import Pool


@dataclass
class BancorPolPool(Pool):
    """
    Class representing a Bancor protocol-owned liquidity pool.
    """

    exchange_name: str = "bancor_pol"

    @staticmethod
    def unique_key() -> str:
        """
        see base class.
        """
        return "token"

    @classmethod
    def event_matches_format(cls, event: Dict[str, Any]) -> bool:
        """
        Check if an event matches the format of a Bancor pol event.

        Parameters
        ----------
        event : Dict[str, Any]
            The event arguments.

        Returns
        -------
        bool
            True if the event matches the format of a Bancor v3 event, False otherwise.

        """
        # TODO CHECK THIS WORKS
        event_args = event["args"]
        return "token" in event_args and "token0" not in event_args

    def update_from_event(
        self, event_args: Dict[str, Any], data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """

        # TODO

        See base class.
        """

        event_type = event_args["event"]
        if event_type in "TradingEnabled":
            print(f"TradingEnabled state: {self.state}")
            data["tkn0_address"] = event_args["args"]["token"]
            data["tkn1_address"] = "0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE"

        if event_args["args"]["token"] == self.state["tkn0_address"] and event_type in [
            "TokenTraded"
        ]:
            # TODO: check if this is correct (if tkn0_balance - amount, can be negative if amount > tkn0_balance)
            data["tkn0_balance"] = event_args["args"]["amount"]

        for key, value in data.items():
            self.state[key] = value

        data["cid"] = self.state["cid"]
        data["fee"] = 0
        data["fee_float"] = 0
        data["exchange_name"] = self.state["exchange_name"]
        return data

    def update_from_contract(self, contract: Contract) -> Dict[str, Any]:
        """
        See base class.

        This only updates the current price, not the balance.
        """
        print("UPDATE FROM CONTRACT FIRED")
        tkn0 = self.state["tkn0_address"]

        print(f"CONTRACT ADDRESS: {contract.address}, {type(contract)}")
        # Use ERC20 token contract to get balance of POL contract
        tkn0_balance = 0
        tkn1_balance = 0
        try:
            tkn0_balance, tkn1_balance = contract.functions.tokenPrice(
                self.state["tkn0_address"]
            ).call()
        except web3.exceptions.BadFunctionCallOutput:
            print(f"BadFunctionCallOutput: {self.state['tkn0_address']}")

        # TODO is this the correct direction?
        token_price = tkn0_balance / tkn1_balance

        # TODO is this necessary?
        token_price = self.encode_token_price(token_price)

        params = {
            "fee": "0.000",
            "fee_float": 0.000,
            "tkn0_balance": 0,
            "tkn1_balance": 0,
            "exchange_name": self.state["exchange_name"],
            "address": self.state["address"],
            "y_0": tkn0_balance,
            "z_0": tkn0_balance,
            "A_0": token_price,
            "B_0": token_price,
        }
        for key, value in params.items():
            self.state[key] = value
        return params

    def encode_token_price(self, Pa):
        # TODO encode this to the format of a Carbon Order
        return Pa
        pass

    def update_erc20_balance(self, token_contract, address) -> int:
        """
        :param cfg: the Config object

        returns: the current balance held by the POL contract
        Uses ERC20 contracts to get the number of tokens held by the POL contract
        """

        # TODO Initialize and save ERC20 contract in managers/base.py and pass it into this function: erc20_contracts: Dict[str, Contract or Type[Contract]] = field(default_factory=dict)

        balance = token_contract.caller.balanceOf(address)
        params = {
            "y_0": balance,
            "z_0": balance,
        }

        return params
