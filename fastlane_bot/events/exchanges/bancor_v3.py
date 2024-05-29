"""
Contains the exchange class for BancorV3. 

This class is responsible for handling BancorV3 events and updating the state of the pools.


[DOC-TODO-OPTIONAL-longer description in rst format]

---
(c) Copyright Bprotocol foundation 2023-24.
All rights reserved.
Licensed under MIT.
"""
from dataclasses import dataclass
from typing import List, Type, Tuple, Union

from web3 import Web3, AsyncWeb3
from web3.contract import Contract

from fastlane_bot.data.abi import BANCOR_V3_POOL_COLLECTION_ABI
from ..exchanges.base import Exchange
from ..pools.base import Pool
from ..interfaces.event import Event
from ..interfaces.subscription import Subscription


TRADING_LIQUIDITY_UPDATED_TOPIC = "0x6e96dc5343d067ec486a9920e0304c3610ed05c65e45cc029d9b9fe7ecfa7620"
TOTAL_LIQUIDITY_UPDATED_TOPIC = "0x85a03952f50b8c00b32a521c32094023b64ef0b6d4511f423d44c480a62cb145"


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

    @property
    def factory_abi(self):
        # Not used for Bancor V3
        return BANCOR_V3_POOL_COLLECTION_ABI

    def get_events(self, contract: Contract) -> List[Type[Contract]]:
        return [contract.events.TradingLiquidityUpdated]

    def get_subscriptions(self, w3: Union[Web3, AsyncWeb3]) -> List[Subscription]:
        contract = self.get_event_contract(w3)
        return [
            Subscription(contract.events.TradingLiquidityUpdated, TRADING_LIQUIDITY_UPDATED_TOPIC),
            # Subscription(contract.events.TotalLiquidityUpdated, TOTAL_LIQUIDITY_UPDATED_TOPIC),  # Unused
        ]

    async def get_fee(self, address: str, contract: Contract) -> Tuple[str, float]:
        return "0.000", 0.000

    async def get_tkn0(self, address: str, contract: Contract, event: Event) -> str:
        return self.BNT_ADDRESS

    async def get_tkn1(self, address: str, contract: Contract, event: Event) -> str:
        return (
            event.args["pool"]
            if event.args["pool"] != self.BNT_ADDRESS
            else event.args["tkn_address"]
        )

    def get_pool_func_call(self, addr1, addr2):
        raise NotImplementedError
