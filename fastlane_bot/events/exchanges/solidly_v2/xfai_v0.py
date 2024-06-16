from dataclasses import dataclass
from typing import Any, Tuple

from web3.contract import Contract, AsyncContract

from fastlane_bot.data.abi import XFAI_V0_POOL_ABI, XFAI_V0_FACTORY_ABI, XFAI_V0_CORE_ABI
from .base import SolidlyV2


@dataclass
class XFaiV2(SolidlyV2):
    def get_abi(self):
        return XFAI_V0_POOL_ABI

    def get_core_abi(self):
        return XFAI_V0_CORE_ABI

    async def get_tkn0(self, address: str, contract: Contract, event: Any) -> str:
        return await contract.caller.poolToken()

    async def get_tkn1(self, address: str, contract: Contract, event: Any) -> str:
        return "0xe5D7C2a44FfDDf6b295A15c148167daaAf5Cf34f" # TODO Use the constant WRAPPED_GAS_TOKEN_ADDRESS for this network

    @property
    def factory_abi(self):  # TODO: change to staticmethod
        return XFAI_V0_FACTORY_ABI

    async def get_fee(self, address: str, contract: AsyncContract) -> Tuple[str, float]:
        core_address = self.factory_contract.w3.to_checksum_address(await self.factory_contract.caller.getXfaiCore())
        core_contract = self.factory_contract.w3.eth.contract(address=core_address, abi=self.get_core_abi())
        fee = await core_contract.caller.getTotalFee()
        fee_float = float(fee) / 10 ** 4
        return str(fee_float), fee_float

    def get_pool_func_call(self, addr1, addr2):
        return self.factory_contract.functions.getPool(addr1)
