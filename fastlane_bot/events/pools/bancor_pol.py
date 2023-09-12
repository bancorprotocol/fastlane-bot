# coding=utf-8
"""
Contains the exchange class for BancorV3. This class is responsible for handling BancorV3 events and updating the state of the pools.

(c) Copyright Bprotocol foundation 2023.
Licensed under MIT
"""
from dataclasses import dataclass
from typing import Dict, Any

import web3
from web3 import Web3
from web3.contract import Contract

from fastlane_bot import Config
from fastlane_bot.data.abi import ERC20_ABI
from fastlane_bot.events.pools.base import Pool
from _decimal import Decimal


@dataclass
class BancorPolPool(Pool):
    """
    Class representing a Bancor protocol-owned liquidity pool.
    """

    exchange_name: str = "bancor_pol"
    ONE = 2**48

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
        event_args = event["args"]
        return "token" in event_args and "token0" not in event_args

    def update_from_event(
        self, event_args: Dict[str, Any], data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        This updates the pool balance from TokenTraded events.

        See base class.
        """

        event_type = event_args["event"]
        if event_type in "TradingEnabled":
            data["tkn0_address"] = event_args["args"]["token"]
            data["tkn1_address"] = Config.ETH_ADDRESS

        if event_args["args"]["token"] == self.state["tkn0_address"] and event_type in [
            "TokenTraded"
        ]:
            # TODO: check if this is correct (if tkn0_balance - amount, can be negative if amount > tkn0_balance)
            data["tkn0_balance"] = (
                self.state["tkn0_balance"] - event_args["args"]["amount"]
            )

        for key, value in data.items():
            self.state[key] = value

        data["cid"] = self.state["cid"]
        data["fee"] = 0
        data["fee_float"] = 0
        data["exchange_name"] = self.state["exchange_name"]
        return data

    def update_from_contract(
        self, contract: Contract, tenderly_fork_id: str = None, cfg: Config = None
    ) -> Dict[str, Any]:
        """
        See base class.
        """
        tkn0 = self.state["tkn0_address"]

        # Use ERC20 token contract to get balance of POL contract
        p0 = p1 = 0
        tkn_balance = self.get_erc20_tkn_balance(contract, tenderly_fork_id, tkn0)

        try:
            p0, p1 = contract.functions.tokenPrice(tkn0).call()
        except web3.exceptions.BadFunctionCallOutput:
            cfg.logger.warning(f"BadFunctionCallOutput: {tkn0}")

        token_price = Decimal(p1) / Decimal(p0)

        params = {
            "fee": "0.000",
            "fee_float": 0.000,
            "tkn0_balance": 0,
            "tkn1_balance": 0,
            "exchange_name": self.state["exchange_name"],
            "address": self.state["address"],
            "y_0": tkn_balance,
            "z_0": tkn_balance,
            "A_0": 0,
            "B_0": int(str(self.encode_token_price(token_price))),
        }
        for key, value in params.items():
            self.state[key] = value
        return params

    @staticmethod
    def get_erc20_tkn_balance(
        contract: Contract, tenderly_fork_id: str, tkn0: str, cfg: Config = None
    ) -> int:
        """
        Get the ERC20 token balance of the POL contract

        Parameters
        ----------
        contract: Contract
            The contract object
        tenderly_fork_id: str
            The tenderly fork id
        tkn0: str
            The token address
        cfg: Config
            The config object

        Returns
        -------
        int
            The token balance

        """
        if tenderly_fork_id:
            w3 = Web3(
                Web3.HTTPProvider(f"https://rpc.tenderly.co/fork/{tenderly_fork_id}")
            )
            erc20_contract = w3.eth.contract(abi=ERC20_ABI, address=tkn0)
        else:
            erc20_contract = cfg.w3.eth.contract(abi=ERC20_ABI, address=tkn0)
        return erc20_contract.functions.balanceOf(contract.address).call()

    @staticmethod
    def bit_length(value: int) -> int:
        """
        Get the bit length of a value

        Parameters
        ----------
        value: int
            The value

        Returns
        -------
        int
            The bit length

        """
        return len(bin(value).lstrip("0b")) if value > 0 else 0

    def encode_float(self, value: int) -> int:
        """
        Encode the float value

        Parameters
        ----------
        value: int
            The float value

        Returns
        -------
        int
            The encoded float value

        """
        exponent = self.bit_length(value // self.ONE)
        mantissa = value >> exponent
        return mantissa | (exponent * self.ONE)

    def encode_rate(self, value: Decimal) -> int:
        """
        Encode the rate

        Parameters
        ----------
        value: Decimal
            The rate

        Returns
        -------
        int
            The encoded rate

        """
        data = int(value.sqrt() * self.ONE)
        length = self.bit_length(data // self.ONE)
        return (data >> length) << length

    def encode_token_price(self, price: Decimal) -> int:
        """
        Encode the token price

        Parameters
        ----------
        price: Decimal
            The token price

        Returns
        -------
        int
            The encoded token price

        """
        return self.encode_float(self.encode_rate(price))

    @staticmethod
    def update_erc20_balance(token_contract: Contract, address: str) -> Dict[str, Any]:
        """
        Update the ERC20 token balance of the POL contract

        Parameters
        ----------
        token_contract: Contract
            The contract object
        address: str
            The token address

        Returns
        -------
        Dict[str, Any]
            The updated pool data.
        """

        balance = token_contract.caller.balanceOf(address)
        return {
            "y_0": balance,
            "z_0": balance,
        }
