"""
Contains the exchange class for SolidlyV2. 

This class is responsible for handling SolidlyV2 events and updating the state of the pools.


[DOC-TODO-OPTIONAL-longer description in rst format]

---
(c) Copyright Bprotocol foundation 2023-24.
All rights reserved.
Licensed under MIT.
"""
from dataclasses import dataclass
from typing import List, Type, Tuple, Any

from web3.contract import Contract, AsyncContract

from fastlane_bot.data.abi import SOLIDLY_V2_POOL_ABI, VELOCIMETER_V2_FACTORY_ABI, SOLIDLY_V2_FACTORY_ABI, \
    SCALE_V2_FACTORY_ABI, CLEOPATRA_V2_FACTORY_ABI, LYNEX_V2_FACTORY_ABI, NILE_V2_FACTORY_ABI, \
    XFAI_V0_FACTORY_ABI, XFAI_V0_CORE_ABI, XFAI_V0_POOL_ABI
from fastlane_bot.events.exchanges.base import Exchange
from fastlane_bot.events.pools.base import Pool

async def _get_fee_1(address: str, contract: Contract, factory_contract: Contract) -> int:
    return await factory_contract.caller.getFee(address)

async def _get_fee_2(address: str, contract: Contract, factory_contract: Contract) -> int:
    return await factory_contract.caller.getRealFee(address)

async def _get_fee_3(address: str, contract: Contract, factory_contract: Contract) -> int:
    return await factory_contract.caller.getFee(address, await contract.caller.stable())

async def _get_fee_4(address: str, contract: Contract, factory_contract: Contract) -> int:
    return await factory_contract.caller.getPairFee(address, await contract.caller.stable())

async def _get_fee_5(address: str, contract: Contract, factory_contract: Contract) -> int:
    return await factory_contract.caller.getFee(await contract.caller.stable())

async def _get_fee_6(address: str, contract: Contract, factory_contract: Contract) -> int:
    return await factory_contract.caller.pairFee(address)

async def _get_fee_7(address: str, contract: Contract, factory_contract: Contract) -> int:
    core_address = factory_contract.w3.to_checksum_address(await factory_contract.caller.getXfaiCore())
    core_contract = factory_contract.w3.eth.contract(address=core_address, abi=XFAI_V0_CORE_ABI)
    return await core_contract.caller.getTotalFee()

async def _get_tkn0_A(contract: Contract) -> str:
    return await contract.caller.token0()

async def _get_tkn1_A(contract: Contract) -> str:
    return await contract.caller.token1()

async def _get_tkn0_B(contract: Contract) -> str:
    return await contract.caller.poolToken()

async def _get_tkn1_B(contract: Contract) -> str:
    return "0xe5D7C2a44FfDDf6b295A15c148167daaAf5Cf34f" # TODO Use the constant WRAPPED_GAS_TOKEN_ADDRESS for this network

EXCHANGE_INFO = {
    "velocimeter_v2": {"decimals":  4, "factory_abi": VELOCIMETER_V2_FACTORY_ABI, "pool_abi": SOLIDLY_V2_POOL_ABI, "get_fee": _get_fee_1, "get_tkn0": _get_tkn0_A, "get_tkn1": _get_tkn1_A},
    "equalizer_v2"  : {"decimals":  4, "factory_abi": SCALE_V2_FACTORY_ABI      , "pool_abi": SOLIDLY_V2_POOL_ABI, "get_fee": _get_fee_2, "get_tkn0": _get_tkn0_A, "get_tkn1": _get_tkn1_A},
    "aerodrome_v2"  : {"decimals":  4, "factory_abi": SOLIDLY_V2_FACTORY_ABI    , "pool_abi": SOLIDLY_V2_POOL_ABI, "get_fee": _get_fee_3, "get_tkn0": _get_tkn0_A, "get_tkn1": _get_tkn1_A},
    "velodrome_v2"  : {"decimals":  4, "factory_abi": SOLIDLY_V2_FACTORY_ABI    , "pool_abi": SOLIDLY_V2_POOL_ABI, "get_fee": _get_fee_3, "get_tkn0": _get_tkn0_A, "get_tkn1": _get_tkn1_A},
    "scale_v2"      : {"decimals": 18, "factory_abi": SCALE_V2_FACTORY_ABI      , "pool_abi": SOLIDLY_V2_POOL_ABI, "get_fee": _get_fee_2, "get_tkn0": _get_tkn0_A, "get_tkn1": _get_tkn1_A},
    "cleopatra_v2"  : {"decimals":  4, "factory_abi": CLEOPATRA_V2_FACTORY_ABI  , "pool_abi": SOLIDLY_V2_POOL_ABI, "get_fee": _get_fee_4, "get_tkn0": _get_tkn0_A, "get_tkn1": _get_tkn1_A},
    "stratum_v2"    : {"decimals":  4, "factory_abi": VELOCIMETER_V2_FACTORY_ABI, "pool_abi": SOLIDLY_V2_POOL_ABI, "get_fee": _get_fee_1, "get_tkn0": _get_tkn0_A, "get_tkn1": _get_tkn1_A},
    "lynex_v2"      : {"decimals":  4, "factory_abi": LYNEX_V2_FACTORY_ABI      , "pool_abi": SOLIDLY_V2_POOL_ABI, "get_fee": _get_fee_5, "get_tkn0": _get_tkn0_A, "get_tkn1": _get_tkn1_A},
    "nile_v2"       : {"decimals":  4, "factory_abi": NILE_V2_FACTORY_ABI       , "pool_abi": SOLIDLY_V2_POOL_ABI, "get_fee": _get_fee_6, "get_tkn0": _get_tkn0_A, "get_tkn1": _get_tkn1_A},
    "xfai_v0"       : {"decimals":  4, "factory_abi": XFAI_V0_FACTORY_ABI       , "pool_abi": XFAI_V0_POOL_ABI   , "get_fee": _get_fee_7, "get_tkn0": _get_tkn0_B, "get_tkn1": _get_tkn1_B},
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
    factory_contract: AsyncContract = None

    @property
    def fee_float(self):
        return float(self.fee)

    def add_pool(self, pool: Pool):
        self.pools[pool.state["address"]] = pool

    def get_abi(self):
        return EXCHANGE_INFO[self.exchange_name]["pool_abi"]

    @property
    def get_factory_abi(self):
        return EXCHANGE_INFO[self.exchange_name]["factory_abi"]

    def get_events(self, contract: Contract) -> List[Type[Contract]]:
        return [contract.events.Sync] if self.exchange_initialized else []

    async def get_fee(self, address: str, contract: AsyncContract) -> Tuple[str, float]:
        exchange_info = EXCHANGE_INFO[self.exchange_name]
        fee = await exchange_info["get_fee"](address, contract, self.factory_contract)
        fee_float = float(fee) / 10 ** exchange_info["decimals"]
        return str(fee_float), fee_float

    async def get_tkn0(self, address: str, contract: Contract, event: Any) -> str:
        return await EXCHANGE_INFO[self.exchange_name]["get_tkn0"](contract)

    async def get_tkn1(self, address: str, contract: Contract, event: Any) -> str:
        return await EXCHANGE_INFO[self.exchange_name]["get_tkn1"](contract)
