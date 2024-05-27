"""
Contains the exchange class for SolidlyV2. 

This class is responsible for handling SolidlyV2 events and updating the state of the pools.


[DOC-TODO-OPTIONAL-longer description in rst format]

---
(c) Copyright Bprotocol foundation 2023-24.
All rights reserved.
Licensed under MIT.
"""
from abc import abstractmethod
from dataclasses import dataclass
from typing import List, Type, Any, Union

from web3 import Web3, AsyncWeb3
from web3.contract import Contract, AsyncContract

from fastlane_bot.data.abi import SOLIDLY_V2_POOL_ABI
from fastlane_bot.events.exchanges.base import Exchange
from ...exchanges.base import Exchange
from ...pools.base import Pool
from ...interfaces.subscription import Subscription


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
    factory_contract: AsyncContract = None

    @property
    def fee_float(self):  # TODO: why is this here?
        return float(self.fee)

    def add_pool(self, pool: Pool):
        self.pools[pool.state["address"]] = pool

    def get_events(self, contract: Contract) -> List[Type[Contract]]:
        return [contract.events.Sync] if self.exchange_initialized else []

    def get_subscriptions(self, w3: Union[Web3, AsyncWeb3]) -> List[Subscription]:
        contract = self.get_event_contract(w3)
        return [Subscription(contract.events.Sync)]

    def get_abi(self):
        return SOLIDLY_V2_POOL_ABI

    async def get_tkn0(self, address: str, contract: Contract, event: Any) -> str:
        return await contract.caller.token0()

    async def get_tkn1(self, address: str, contract: Contract, event: Any) -> str:
        return await contract.caller.token1()

    def get_pool_func_call(self, addr1, addr2):
        return self.factory_contract.functions.getPair(addr1, addr2, False)

    @property
    @abstractmethod
    def factory_abi(self):
        ...
    
    @abstractmethod
    async def get_fee(self, address: str, contract: Contract, factory_contract: Contract):
        ...
