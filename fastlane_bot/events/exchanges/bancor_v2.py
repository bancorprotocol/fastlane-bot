# coding=utf-8
"""
Contains the exchange class for bancorV2. This class is responsible for handling bancorV2 exchanges and updating the state of the pools.

(c) Copyright Bprotocol foundation 2023.
Licensed under MIT
"""
from dataclasses import dataclass
from typing import List, Type, Tuple, Any

from web3.contract import Contract

from fastlane_bot.data.abi import BANCOR_V2_CONVERTER_ABI
from fastlane_bot.events.exchanges.base import Exchange
from fastlane_bot.events.pools.base import Pool


@dataclass
class BancorV2(Exchange):
    """
    bancorV2 exchange class
    """

    exchange_name: str = "bancor_v2"
    _tokens: List[str] = None

    def add_pool(self, pool: Pool):
        self.pools[pool.state["address"]] = pool

    def get_abi(self):
        return BANCOR_V2_CONVERTER_ABI

    def get_events(self, contract: Contract) -> List[Type[Contract]]:
        return [contract.events.TokenRateUpdate]

    def get_fee(self, address: str, contract: Contract) -> Tuple[str, float]:
        pool = self.get_pool(address)
        fee, fee_float = (
            (pool.state["fee"], pool.state["fee_float"])
            if pool
            else (
                contract.functions.conversionFee().call(),
                float(contract.functions.conversionFee().call()) / 1e6,
            )
        )
        return fee, fee_float

    def get_tkn0(self, address: str, contract: Contract, event: Any) -> str:
        return (
            event["args"]["_token1"]
            if event
            else contract.functions.reserveTokens().call()[0]
        )

    def get_tkn1(self, address: str, contract: Contract, event: Any) -> str:
        return (
            event["args"]["_token2"]
            if event
            else contract.functions.reserveTokens().call()[1]
        )
