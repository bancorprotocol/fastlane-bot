# coding=utf-8
"""
Contains the exchange class for BancorV3. This class is responsible for handling BancorV3 events and updating the state of the pools.

(c) Copyright Bprotocol foundation 2023.
Licensed under MIT
"""
from dataclasses import dataclass
from typing import List, Type, Tuple, Any

from web3.contract import Contract

from fastlane_bot.data.abi import BANCOR_V3_POOL_COLLECTION_ABI
from fastlane_bot.events.exchanges.base import Exchange
from fastlane_bot.events.pools.base import Pool


@dataclass
class BancorV3(Exchange):
    """
    BancorV3 exchange class
    """

    exchange_name: str = "bancor_v3"
    BNT_ADDRESS: str = "0x1F573D6Fb3F13d689FF844B4cE37794d79a7FF1C"

    def add_pool(self, pool: Pool):
        self.pools[pool.state["tkn1_address"]] = pool

    def get_abi(self):
        return BANCOR_V3_POOL_COLLECTION_ABI

    def get_events(self, contract: Contract) -> List[Type[Contract]]:
        return [contract.events.TradingLiquidityUpdated]

    def get_fee(self, address: str, contract: Contract) -> Tuple[str, float]:
        return "0.000", 0.000

    def get_tkn0(self, address: str, contract: Contract, event: Any) -> str:
        return self.BNT_ADDRESS

    def get_tkn1(self, address: str, contract: Contract, event: Any) -> str:
        return (
            event["args"]["pool"]
            if event["args"]["pool"] != self.BNT_ADDRESS
            else event["args"]["tkn_address"]
        )
