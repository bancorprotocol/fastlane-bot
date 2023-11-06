# coding=utf-8
"""
Contains the exchange class for UniswapV2. This class is responsible for handling UniswapV2 exchanges and updating the state of the pools.

(c) Copyright Bprotocol foundation 2023.
Licensed under MIT
"""
from dataclasses import dataclass
from typing import List, Type, Tuple, Any

from web3.contract import Contract, AsyncContract

from fastlane_bot.data.abi import UNISWAP_V2_POOL_ABI
from fastlane_bot.events.exchanges.base import Exchange
from fastlane_bot.events.pools.base import Pool


@dataclass
class UniswapV2(Exchange):
    """
    UniswapV2 exchange class
    """

    exchange_name: str = "uniswap_v2"

    def add_pool(self, pool: Pool):
        self.pools[pool.state["address"]] = pool

    def get_abi(self):
        return UNISWAP_V2_POOL_ABI

    def get_events(self, contract: Contract) -> List[Type[Contract]]:
        return [contract.events.Sync]

    @staticmethod
    async def get_fee(address: str, contract: AsyncContract) -> Tuple[str, float]:
        return "0.003", 0.003

    @staticmethod
    async def get_tkn0(address: str, contract: AsyncContract, event: Any) -> str:
        return await contract.functions.token0().call()

    @staticmethod
    async def get_tkn1(address: str, contract: AsyncContract, event: Any) -> str:
        return await contract.functions.token1().call()
