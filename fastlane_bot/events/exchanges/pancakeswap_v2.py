# coding=utf-8
"""
Contains the exchange class for PancakeswapV2. This class is responsible for handling SushiswapV2 exchanges and updating the state of the pools.

(c) Copyright Bprotocol foundation 2023.
Licensed under MIT
"""
from dataclasses import dataclass
from typing import List, Type, Tuple, Any

from web3.contract import Contract

from fastlane_bot.data.abi import PANCAKESWAP_V2_POOL_ABI
from fastlane_bot.events.exchanges.base import Exchange
from fastlane_bot.events.pools.base import Pool


@dataclass
class PancakeswapV2(Exchange):
    """
    PancakeswapV2 exchange class
    """

    exchange_name: str = "pancakeswap_v2"

    def add_pool(self, pool: Pool):
        self.pools[pool.state["address"]] = pool

    def get_abi(self):
        return PANCAKESWAP_V2_POOL_ABI

    def get_events(self, contract: Contract) -> List[Type[Contract]]:
        return [contract.events.Sync]

    def get_fee(self, address: str, contract: Contract) -> Tuple[str, float]:
        return "0.0025", 0.0025

    def get_tkn0(self, address: str, contract: Contract, event: Any) -> str:
        return contract.functions.token0().call()

    def get_tkn1(self, address: str, contract: Contract, event: Any) -> str:
        return contract.functions.token1().call()
