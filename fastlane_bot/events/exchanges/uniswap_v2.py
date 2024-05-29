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
from typing import List, Type, Tuple, Any, Union

from web3 import Web3, AsyncWeb3
from web3.contract import Contract, AsyncContract

from fastlane_bot.data.abi import UNISWAP_V2_POOL_ABI, UNISWAP_V2_FACTORY_ABI
from ..exchanges.base import Exchange
from ..pools.base import Pool
from ..interfaces.subscription import Subscription


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
    def factory_abi(self):
        return UNISWAP_V2_FACTORY_ABI

    def add_pool(self, pool: Pool):
        self.pools[pool.state["address"]] = pool

    def get_abi(self):
        return UNISWAP_V2_POOL_ABI

    def get_events(self, contract: Contract) -> List[Type[Contract]]:
        return [contract.events.Sync] if self.exchange_initialized else []

    def get_subscriptions(self, w3: Union[Web3, AsyncWeb3]) -> List[Subscription]:
        contract = self.get_event_contract(w3)
        return [Subscription(contract.events.Sync)]

    async def get_fee(self, address: str, contract: AsyncContract) -> Tuple[str, float]:
        return self.fee, self.fee_float

    @staticmethod
    async def get_tkn0(address: str, contract: AsyncContract, event: Any) -> str:
        return await contract.caller.token0()

    @staticmethod
    async def get_tkn1(address: str, contract: AsyncContract, event: Any) -> str:
        return await contract.caller.token1()

    def get_pool_func_call(self, addr1, addr2):
        return self.factory_contract.functions.getPair(addr1, addr2)
