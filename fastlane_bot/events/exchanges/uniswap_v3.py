# coding=utf-8
"""
Contains the exchange class for BancorV3. This class is responsible for handling BancorV3 events and updating the state of the pools.

(c) Copyright Bprotocol foundation 2023.
Licensed under MIT
"""
from dataclasses import dataclass
from typing import List, Type, Tuple, Any

from web3.contract import Contract

from fastlane_bot.data.abi import UNISWAP_V3_POOL_ABI, UNISWAP_V3_FACTORY_ABI, PANCAKESWAP_V3_FACTORY_ABI, PANCAKESWAP_V3_POOL_ABI
from fastlane_bot.events.exchanges.base import Exchange
from fastlane_bot.events.pools.base import Pool


@dataclass
class UniswapV3(Exchange):
    """
    UniswapV3 exchange class
    """
    base_exchange_name: str = "uniswap_v3"
    exchange_name: str = "uniswap_v3"
    router_address: str = None
    exchange_initialized: bool = False

    def add_pool(self, pool: Pool):
        self.pools[pool.state["address"]] = pool

    def get_abi(self):
        return UNISWAP_V3_POOL_ABI if self.exchange_name not in ["pancakeswap_v3"] else PANCAKESWAP_V3_POOL_ABI

    @property
    def get_factory_abi(self):
        return UNISWAP_V3_FACTORY_ABI if self.exchange_name not in ["pancakeswap_v3"] else PANCAKESWAP_V3_FACTORY_ABI

    def get_events(self, contract: Contract) -> List[Type[Contract]]:
        return [contract.events.Swap] if self.exchange_initialized else []

    async def get_fee(self, address: str, contract: Contract) -> Tuple[str, float]:
        fee = await contract.functions.fee().call()
        fee_float = float(fee) / 1e6
        return fee, fee_float

    async def get_tkn0(self, address: str, contract: Contract, event: Any) -> str:
        return await contract.functions.token0().call()

    async def get_tkn1(self, address: str, contract: Contract, event: Any) -> str:
        return await contract.functions.token1().call()
