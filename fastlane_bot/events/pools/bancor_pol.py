# coding=utf-8
"""
Contains the exchange class for BancorV3. This class is responsible for handling BancorV3 events and updating the state of the pools.

(c) Copyright Bprotocol foundation 2023.
Licensed under MIT
"""
from dataclasses import dataclass
from typing import Dict, Any, List

import web3
from web3 import Web3
from web3.contract import Contract
import web3.exceptions

from fastlane_bot.data.abi import ERC20_ABI, BANCOR_POL_ABI
from fastlane_bot.events.pools.base import Pool
from _decimal import Decimal


@dataclass
class BancorPolPool(Pool):
    """
    Class representing a Bancor protocol-owned liquidity pool.
    """

    exchange_name: str = "bancor_pol"
    ONE = 2**48
    contract: Contract = None
    BANCOR_POL_ADDRESS = "0xD06146D292F9651C1D7cf54A3162791DFc2bEf46"
    ARB_CONTRACT_VERSION = None

    @staticmethod
    def unique_key() -> str:
        """
        see base class.
        """
        return "token"

    @classmethod
    def event_matches_format(
        cls, event: Dict[str, Any], static_pools: Dict[str, Any]
    ) -> bool:
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
            data["tkn1_address"] = "0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE" if event_args["args"]["token"] not in "0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE" else "0x1F573D6Fb3F13d689FF844B4cE37794d79a7FF1C"

        if event_args["args"]["token"] == self.state["tkn0_address"] and event_type in [
            "TokenTraded"
        ]:
            # *** Balance now updated from multicall ***
            pass
            # if self.state['last_updated_block'] < event_args['blockNumber']:
            #     data["y_0"] = (
            #         self.state["y_0"] - event_args["args"]["amount"]
            #     )

        for key, value in data.items():
            self.state[key] = value

        data["cid"] = self.state["cid"]
        data["fee"] = 0
        data["fee_float"] = 0
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

        This only updates the current price, not the balance.
        """
        tkn0 = self.state["tkn0_address"]

        # Use ERC20 token contract to get balance of POL contract
        p0 = 0
        p1 = 0

        tkn_balance = self.get_erc20_tkn_balance(contract, tkn0, w3_tenderly, w3)

        if tenderly_fork_id and "bancor_pol" in tenderly_exchanges:
            contract = w3_tenderly.eth.contract(
                abi=BANCOR_POL_ABI, address=contract.address
            )

        try:
            p0, p1 = contract.functions.tokenPrice(tkn0).call()
        except web3.exceptions.BadFunctionCallOutput:
            print(f"BadFunctionCallOutput: {tkn0}")

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
        contract: Contract, tkn0: str, w3_tenderly: Web3 = None, w3: Web3 = None
    ) -> int:
        """
        Get the ERC20 token balance of the POL contract

        Parameters
        ----------
        contract: Contract
            The contract object
        tkn0: str
            The token address
        w3_tenderly: Web3
            The tenderly web3 object
        w3: Web3
            The web3 object

        Returns
        -------
        int
            The token balance

        """
        if w3_tenderly:
            contract = w3_tenderly.eth.contract(abi=BANCOR_POL_ABI, address=contract.address)
        try:
            return contract.caller.amountAvailableForTrading(tkn0)
        except web3.exceptions.ContractLogicError:
            if w3_tenderly:
                erc20_contract = w3_tenderly.eth.contract(abi=ERC20_ABI, address=tkn0)
            else:
                erc20_contract = w3.eth.contract(abi=ERC20_ABI,address=tkn0)
            return erc20_contract.functions.balanceOf(contract.address).call()


    @staticmethod
    def bitLength(value):
        return len(bin(value).lstrip("0b")) if value > 0 else 0

    def encodeFloat(self, value):
        exponent = self.bitLength(value // self.ONE)
        mantissa = value >> exponent
        return mantissa | (exponent * self.ONE)

    def encodeRate(self, value):
        data = int(value.sqrt() * self.ONE)
        length = self.bitLength(data // self.ONE)
        return (data >> length) << length

    def encode_token_price(self, price):
        return self.encodeFloat(self.encodeRate((price)))

    def update_erc20_balance(self, token_contract, address) -> dict:
        """
        returns: the current balance held by the POL contract
        Uses ERC20 contracts to get the number of tokens held by the POL contract
        """

        balance = token_contract.caller.balanceOf(address)
        params = {
            "y_0": balance,
            "z_0": balance,
        }

        return params

