# coding=utf-8
"""
Contains the exchange class for UniswapV2. This class is responsible for handling UniswapV2 exchanges and updating the state of the pools.

(c) Copyright Bprotocol foundation 2023.
Licensed under MIT
"""
from dataclasses import dataclass
from typing import List, Type, Tuple, Any

from web3.contract import Contract

from fastlane_bot.data.abi import SOLIDLY_V2_POOL_ABI, VELOCIMETER_V2_FACTORY_ABI, SOLIDLY_V2_FACTORY_ABI, \
    VELOCIMETER_V2_POOL_ABI
from fastlane_bot.events.exchanges.base import Exchange
from fastlane_bot.events.pools.base import Pool


@dataclass
class SolidlyV2(Exchange):
    """
    SolidlyV2 exchange class
    """

    base_exchange_name: str = "solidly_v2"
    exchange_name: str = None
    fee: str = None
    router_address: str = None
    exchange_initialized: bool = False

    stable_fee: float = None
    volatile_fee: float = None
    factory_address: str = None
    factory_contract: Contract = None

    @property
    def fee_float(self):
        return float(self.fee)

    def add_pool(self, pool: Pool):
        self.pools[pool.state["address"]] = pool

    def get_abi(self):
        return VELOCIMETER_V2_POOL_ABI if "velocimeter" in self.exchange_name else SOLIDLY_V2_POOL_ABI

    @property
    def get_factory_abi(self):
        return VELOCIMETER_V2_FACTORY_ABI if "velocimeter" in self.exchange_name else SOLIDLY_V2_FACTORY_ABI

    def get_events(self, contract: Contract) -> List[Type[Contract]]:
        return [contract.events.Sync] if self.exchange_initialized else []

    async def get_fee(self, address: str, contract: Contract) -> Tuple[str, float]:
        if "velocimeter" in self.exchange_name:
            default_fee = await self.factory_contract.caller.getFee(address)
            default_fee = float(default_fee) / 10000

        elif "scale" in self.exchange_name:
            default_fee = await self.factory_contract.caller.getRealFee(address)
            default_fee = float(default_fee) / 10 ** 18
        else:
            is_stable = await contract.caller.stable()
            default_fee = await self.factory_contract.caller.getFee(address, is_stable)
            default_fee = float(default_fee) / 10000
        return str(default_fee), default_fee

    async def get_tkn0(self, address: str, contract: Contract, event: Any) -> str:
        return await contract.functions.token0().call()

    async def get_tkn1(self, address: str, contract: Contract, event: Any) -> str:
        return await contract.functions.token1().call()
