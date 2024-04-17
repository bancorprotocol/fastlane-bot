"""
Contains the exchange class for VelocoreV2. 

This class is responsible for handling VelocoreV2 events and updating the state of the pools.


[DOC-TODO-OPTIONAL-longer description in rst format]

---
(c) Copyright Bprotocol foundation 2023-24.
All rights reserved.
Licensed under MIT.
"""
from dataclasses import dataclass
from typing import List, Type, Tuple, Any

from web3.contract import Contract, AsyncContract

from fastlane_bot.data.abi import VELOCORE_V2_FACTORY_ABI, VELOCORE_V2_LENS_ABI, VELOCORE_V2_VAULT_ABI
from fastlane_bot.events.exchanges.base import Exchange
from fastlane_bot.events.pools.base import Pool


async def _get_pool_fee(address: str, contract: Contract, lens_contract: Contract) -> int:
    """ Function to get fee for a Velocore_v2 pool

    This async function fetches the fee for a Velocore_v2 pool.
    Known uses of this function: velocore_v2

    Args:
        address: The pool address.
        contract: The lens contract.
        lens_contract: The lens contract.

    Returns:
        The pool fee. (in wei resolution)
    """

    pool_data = await lens_contract.caller.queryPool(contract.address)  # TODO this is the process to get the fee but it comes from the LENS contract not the factory
    pool_params = pool_data[-1].hex()
    fee = int('0x'+pool_params[:64],16)
    return fee


EXCHANGE_INFO = {
    "velocore_v2": {"decimals": 18, 
                    "factory_abi": VELOCORE_V2_FACTORY_ABI, 
                    "lens_abi": VELOCORE_V2_LENS_ABI, 
                    "vault_abi": VELOCORE_V2_VAULT_ABI, 
                    "fee_function": _get_pool_fee
                    },
}

@dataclass
class VelocoreV2(Exchange):
    """
    Velocore V2 exchange class
    """

    base_exchange_name: str = "velocore_v2"
    exchange_name: str = None
    fee: str = None
    router_address: str = None
    exchange_initialized: bool = False

    stable_fee: float = None
    volatile_fee: float = None
    factory_address: str = None
    factory_contract: AsyncContract = None
    lens_address: AsyncContract = None
    lens_contract: AsyncContract = None

    @property
    def fee_float(self):
        return float(self.fee)

    def add_pool(self, pool: Pool):
        self.pools[pool.state["address"]] = pool

    def get_abi(self):
        return VELOCORE_V2_FACTORY_ABI
    
    @property
    def get_factory_abi(self):
        return EXCHANGE_INFO[self.exchange_name]["factory_abi"]
    
    @property
    def get_lens_abi(self):
        return EXCHANGE_INFO[self.exchange_name]["lens_abi"]

    def get_events(self, contract: Contract) -> List[Type[Contract]]:
        return [contract.events.Swap] if self.exchange_initialized else []

    async def get_fee(self, address: str, contract: AsyncContract) -> Tuple[str, float]:
        exchange_info = EXCHANGE_INFO[self.exchange_name]
        fee = await exchange_info["fee_function"](address, contract, self.lens_contract)
        fee_float = float(fee) / 10 ** exchange_info["decimals"]
        return str(fee_float), fee_float

    async def get_tkn0(self, address: str, contract: Contract, event: Any) -> str:
        return await contract.functions.token0().call()

    async def get_tkn1(self, address: str, contract: Contract, event: Any) -> str:
        return await contract.functions.token1().call()

