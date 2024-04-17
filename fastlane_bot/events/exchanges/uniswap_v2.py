"""
Contains the exchange class for UniswapV2. 

This class is responsible for handling UniswapV2 events and updating the state of the pools.


[DOC-TODO-OPTIONAL-longer description in rst format]

---
(c) Copyright Bprotocol foundation 2023-24.
All rights reserved.
Licensed under MIT.
"""
from dataclasses import dataclass
from typing import List, Type, Tuple, Any

from web3.contract import Contract, AsyncContract

from fastlane_bot.data.abi import UNISWAP_V2_POOL_ABI, UNISWAP_V2_FACTORY_ABI
from ..exchanges.base import Exchange
from ..pools.base import Pool
from ..interfaces.subscription import Subscription


SYNC_TOPIC = "0x1c411e9a96e071241c2f21f7726b17ae89e3cab4c78be50e062b03a9fffbbad1"


@dataclass
class UniswapV2(Exchange):
    """
    UniswapV2 exchange class
    """
    base_exchange_name: str = "uniswap_v2"
    exchange_name: str = "uniswap_v2"
    fee: str = None
    router_address: str = None
    exchange_initialized: bool = False

    @property
    def fee_float(self):
        return float(self.fee)

    @property
    def get_factory_abi(self):
        return UNISWAP_V2_FACTORY_ABI

    def add_pool(self, pool: Pool):
        self.pools[pool.state["address"]] = pool

    def get_abi(self):
        return UNISWAP_V2_POOL_ABI

    def get_events(self, contract: Contract) -> List[Type[Contract]]:
        return [contract.events.Sync] if self.exchange_initialized else []

    def get_subscriptions(self, contract: Contract) -> List[Subscription]:
        return [Subscription(contract.events.Sync, SYNC_TOPIC)]

    async def get_fee(self, address: str, contract: AsyncContract) -> Tuple[str, float]:
        return self.fee, self.fee_float

    @staticmethod
    async def get_tkn0(address: str, contract: AsyncContract, event: Any) -> str:
        return await contract.caller.token0()

    @staticmethod
    async def get_tkn1(address: str, contract: AsyncContract, event: Any) -> str:
        return await contract.caller.token1()
