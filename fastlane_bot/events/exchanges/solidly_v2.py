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
    VELOCIMETER_V2_POOL_ABI, SCALE_V2_FACTORY_ABI, EQUALIZER_V2_POOL_ABI
from fastlane_bot.events.exchanges.base import Exchange
from fastlane_bot.events.pools.base import Pool

FEE_RESOLUTION_MAP = {
    "velocimeter_v2": 10000,
    "equalizer_v2": 10000,
    "aerodrome_v2": 10000,
    "velodrome_v2": 10000,
    "scale_v2": 1000000000000000000,
    "solidly_v2": 10000,
}

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
        if self.exchange_name == "velocimeter_v2":
            return VELOCIMETER_V2_POOL_ABI
        elif self.exchange_name == "equalizer_v2":
            return EQUALIZER_V2_POOL_ABI
        elif self.exchange_name == "scale_v2":
            return SOLIDLY_V2_POOL_ABI
        elif self.exchange_name == "aerodrome_v2":
            return SOLIDLY_V2_POOL_ABI
        elif self.exchange_name == "velodrome_v2":
            return SOLIDLY_V2_POOL_ABI
        elif self.exchange_name == "solidly_v2":
            return SOLIDLY_V2_POOL_ABI
        else:
            raise self.WrongExchangeException(f"[exchanges/solidly_v2 get_Abi] Exchange {self.exchange_name} not in supported exchanges.")


    @property
    def get_factory_abi(self):
        if self.exchange_name == "velocimeter_v2":
            return VELOCIMETER_V2_FACTORY_ABI
        elif self.exchange_name == "equalizer_v2":
            return SCALE_V2_FACTORY_ABI
        elif self.exchange_name == "scale_v2":
            return SCALE_V2_FACTORY_ABI
        elif self.exchange_name == "aerodrome_v2":
            return SOLIDLY_V2_FACTORY_ABI
        elif self.exchange_name == "velodrome_v2":
            return SOLIDLY_V2_FACTORY_ABI
        elif self.exchange_name == "solidly_v2":
            return SOLIDLY_V2_FACTORY_ABI
        else:
            raise self.WrongExchangeException(f"[exchanges/solidly_v2 get_Abi] Exchange {self.exchange_name} not in supported exchanges.")

    def get_events(self, contract: Contract) -> List[Type[Contract]]:
        return [contract.events.Sync] if self.exchange_initialized else []

    async def get_fee(self, address: str, contract: Contract) -> Tuple[str, float]:
        if self.exchange_name == "velocimeter_v2":
            default_fee = await self.factory_contract.caller.getFee(address)
        elif self.exchange_name == "equalizer_v2":
            default_fee = await self.factory_contract.caller.getRealFee(address)
        elif self.exchange_name == "scale_v2":
            default_fee = await self.factory_contract.caller.getRealFee(address)
        elif self.exchange_name == "aerodrome_v2":
            is_stable = await contract.caller.stable()
            default_fee = await self.factory_contract.caller.getFee(address, is_stable)
        elif self.exchange_name == "velodrome_v2":
            is_stable = await contract.caller.stable()
            default_fee = await self.factory_contract.caller.getFee(address, is_stable)
        elif self.exchange_name == "solidly_v2":
            is_stable = await contract.caller.stable()
            default_fee = await self.factory_contract.caller.getFee(address, is_stable)
        else:
            raise self.WrongExchangeException(f"[exchanges/solidly_v2 get_Abi] Exchange {self.exchange_name} not in supported exchanges.")

        fee_float = float(default_fee) / FEE_RESOLUTION_MAP.get(self.exchange_name)

        return str(fee_float), fee_float

    async def get_tkn0(self, address: str, contract: Contract, event: Any) -> str:
        return await contract.functions.token0().call()

    async def get_tkn1(self, address: str, contract: Contract, event: Any) -> str:
        return await contract.functions.token1().call()

    class WrongExchangeException(Exception):
        pass
