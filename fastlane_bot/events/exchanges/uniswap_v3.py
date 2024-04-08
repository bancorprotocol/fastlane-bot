# coding=utf-8
"""
Contains the exchange class for BancorV3. This class is responsible for handling BancorV3 events and updating the state of the pools.

(c) Copyright Bprotocol foundation 2023.
Licensed under MIT
"""
from dataclasses import dataclass
from typing import List, Type, Tuple, Any

from web3.contract import Contract

from fastlane_bot.config.constants import AGNI_V3_NAME, PANCAKESWAP_V3_NAME, FUSIONX_V3_NAME, ECHODEX_V3_NAME, \
    SECTA_V3_NAME, SUSHISWAP_V3_NAME, UNISWAP_V3_NAME, BASESWAP_V3_NAME, HORIZON_V3_NAME, METAVAULT_V3_NAME, \
    BUTTER_V3_NAME, CLEOPATRA_V3_NAME, NILE_V3_NAME
from fastlane_bot.data.abi import UNISWAP_V3_POOL_ABI, UNISWAP_V3_FACTORY_ABI, PANCAKESWAP_V3_POOL_ABI, NILE_V3_POOL_ABI
from fastlane_bot.events.exchanges.base import Exchange
from fastlane_bot.events.pools.base import Pool


async def _get_fee_1(contract: Contract) -> int:
    return await contract.functions.fee().call()


async def _get_fee_2(contract: Contract) -> int:
    return await contract.functions.currentFee().call()


EXCHANGE_INFO = {
    SUSHISWAP_V3_NAME: {"pool_abi": UNISWAP_V3_POOL_ABI, "fee_function": _get_fee_1},
    UNISWAP_V3_NAME: {"pool_abi": UNISWAP_V3_POOL_ABI, "fee_function": _get_fee_1},
    BASESWAP_V3_NAME: {"pool_abi": UNISWAP_V3_POOL_ABI, "fee_function": _get_fee_1},
    HORIZON_V3_NAME: {"pool_abi": UNISWAP_V3_POOL_ABI, "fee_function": _get_fee_1},
    METAVAULT_V3_NAME: {"pool_abi": UNISWAP_V3_POOL_ABI, "fee_function": _get_fee_1},
    BUTTER_V3_NAME: {"pool_abi": UNISWAP_V3_POOL_ABI, "fee_function": _get_fee_1},
    CLEOPATRA_V3_NAME: {"pool_abi": UNISWAP_V3_POOL_ABI, "fee_function": _get_fee_1},
    PANCAKESWAP_V3_NAME: {"pool_abi": PANCAKESWAP_V3_POOL_ABI, "fee_function": _get_fee_1},
    AGNI_V3_NAME: {"pool_abi": PANCAKESWAP_V3_POOL_ABI, "fee_function": _get_fee_1},
    FUSIONX_V3_NAME: {"pool_abi": PANCAKESWAP_V3_POOL_ABI, "fee_function": _get_fee_1},
    ECHODEX_V3_NAME: {"pool_abi": PANCAKESWAP_V3_POOL_ABI, "fee_function": _get_fee_1},
    SECTA_V3_NAME: {"pool_abi": PANCAKESWAP_V3_POOL_ABI, "fee_function": _get_fee_1},
    NILE_V3_NAME: {"pool_abi": NILE_V3_POOL_ABI, "fee_function": _get_fee_2},
}


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
        return EXCHANGE_INFO[self.exchange_name]["pool_abi"]

    @property
    def get_factory_abi(self):
        return UNISWAP_V3_FACTORY_ABI

    def get_events(self, contract: Contract) -> List[Type[Contract]]:
        return [contract.events.Swap] if self.exchange_initialized else []

    async def get_fee(self, address: str, contract: Contract) -> Tuple[str, float]:
        fee = await EXCHANGE_INFO[self.exchange_name]["fee_function"](contract)
        fee_float = float(fee) / 1e6
        return fee, fee_float

    async def get_tkn0(self, address: str, contract: Contract, event: Any) -> str:
        return await contract.functions.token0().call()

    async def get_tkn1(self, address: str, contract: Contract, event: Any) -> str:
        return await contract.functions.token1().call()
