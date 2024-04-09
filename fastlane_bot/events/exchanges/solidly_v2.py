# coding=utf-8
"""
Contains the exchange class for UniswapV2. This class is responsible for handling UniswapV2 exchanges and updating the state of the pools.

(c) Copyright Bprotocol foundation 2023.
Licensed under MIT
"""
from dataclasses import dataclass
from typing import List, Type, Tuple, Any

from web3.contract import Contract, AsyncContract

from fastlane_bot.data.abi import SOLIDLY_V2_POOL_ABI, VELOCIMETER_V2_FACTORY_ABI, SOLIDLY_V2_FACTORY_ABI, \
    VELOCIMETER_V2_POOL_ABI, SCALE_V2_FACTORY_ABI, EQUALIZER_V2_POOL_ABI, CLEOPATRA_V2_POOL_ABI, LYNEX_V2_FACTORY_ABI, NILE_V2_FACTORY_ABI
from fastlane_bot.events.exchanges.base import Exchange
from fastlane_bot.events.pools.base import Pool


async def _get_fee_1(address: str, contract: Contract, factory_contract: Contract) -> int:
    """ Function to get fee for a Solidly pool.

    This async function fetches the fee for a Solidly pool.
    Known uses of this function: velocimeter_v2, stratum_v2

    Args:
        address: The pool address.
        contract: The pool contract.
        factory_contract: The factory contract.

    Returns:
        The pool fee.
    """
    return await factory_contract.caller.getFee(address)


async def _get_fee_2(address: str, contract: Contract, factory_contract: Contract) -> int:
    """ Function to get fee for a Solidly pool.

    This async function fetches the fee for a Solidly pool.
    Known uses of this function: equalizer_v2, scale_v2

    Args:
        address: The pool address.
        contract: The pool contract.
        factory_contract: The factory contract.

    Returns:
        The pool fee.
    """
    return await factory_contract.caller.getRealFee(address)


async def _get_fee_3(address: str, contract: Contract, factory_contract: Contract) -> int:
    """ Function to get fee for a Solidly pool.

    This async function fetches the fee for a Solidly pool.
    Known uses of this function: aerodrome_v2, velodrome_v2

    Args:
        address: The pool address.
        contract: The pool contract.
        factory_contract: The factory contract.

    Returns:
        The pool fee.
    """
    return await factory_contract.caller.getFee(address, await contract.caller.stable())


async def _get_fee_4(address: str, contract: Contract, factory_contract: Contract) -> int:
    """ Function to get fee for a Solidly pool.

    This async function fetches the fee for a Solidly pool.
    Known uses of this function: cleopatra_v2

    Args:
        address: The pool address.
        contract: The pool contract.
        factory_contract: The factory contract.

    Returns:
        The pool fee.
    """
    return await factory_contract.caller.getPairFee(address, await contract.caller.stable())

async def _get_fee_5(address: str, contract: Contract, factory_contract: Contract) -> int:
    """ Function to get fee for a Solidly pool.

    This async function fetches the fee for a Solidly pool.
    Known uses of this function: lynex_v2

    Args:
        address: The pool address.
        contract: The pool contract.
        factory_contract: The factory contract.

    Returns:
        The pool fee.
    """
    return await factory_contract.caller.getFee(await contract.caller.stable())

async def _get_fee_6(address: str, contract: Contract, factory_contract: Contract) -> int:
    """ Function to get fee for a Solidly pool.

    This async function fetches the fee for a Solidly pool.
    Known uses of this function: nile_v2

    Args:
        address: The pool address.
        contract: The pool contract.
        factory_contract: The factory contract.

    Returns:
        The pool fee.
    """
    return await factory_contract.caller.pairFee(address)

EXCHANGE_INFO = {
    "velocimeter_v2": {"decimals": 4, "factory_abi": VELOCIMETER_V2_FACTORY_ABI, "pool_abi": VELOCIMETER_V2_POOL_ABI, "fee_function": _get_fee_1},
    "equalizer_v2": {"decimals": 4, "factory_abi": SCALE_V2_FACTORY_ABI, "pool_abi": EQUALIZER_V2_POOL_ABI, "fee_function": _get_fee_2},
    "aerodrome_v2": {"decimals": 4, "factory_abi": SOLIDLY_V2_FACTORY_ABI, "pool_abi": SOLIDLY_V2_POOL_ABI, "fee_function": _get_fee_3},
    "velodrome_v2": {"decimals": 4, "factory_abi": SOLIDLY_V2_FACTORY_ABI, "pool_abi": SOLIDLY_V2_POOL_ABI, "fee_function": _get_fee_3},
    "scale_v2": {"decimals": 18, "factory_abi": SCALE_V2_FACTORY_ABI, "pool_abi": SOLIDLY_V2_POOL_ABI, "fee_function": _get_fee_2},
    "cleopatra_v2": {"decimals": 4, "factory_abi": CLEOPATRA_V2_POOL_ABI, "pool_abi": EQUALIZER_V2_POOL_ABI, "fee_function": _get_fee_4},
    "stratum_v2": {"decimals": 4, "factory_abi": VELOCIMETER_V2_FACTORY_ABI, "pool_abi": VELOCIMETER_V2_POOL_ABI, "fee_function": _get_fee_1},
    "lynex_v2": {"decimals": 4, "factory_abi": LYNEX_V2_FACTORY_ABI, "pool_abi": SOLIDLY_V2_POOL_ABI, "fee_function": _get_fee_5},
    "nile_v2": {"decimals": 4, "factory_abi": NILE_V2_FACTORY_ABI, "pool_abi": SOLIDLY_V2_POOL_ABI, "fee_function": _get_fee_6},
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
        fee = await exchange_info["fee_function"](address, contract, self.factory_contract)
        fee_float = float(fee) / 10 ** exchange_info["decimals"]
        return str(fee_float), fee_float

    async def get_tkn0(self, address: str, contract: Contract, event: Any) -> str:
        return await contract.functions.token0().call()

    async def get_tkn1(self, address: str, contract: Contract, event: Any) -> str:
        return await contract.functions.token1().call()

