from dataclasses import dataclass
from typing import Tuple

from web3.contract import AsyncContract

from fastlane_bot.data.abi import SCALE_V2_FACTORY_ABI
from .base import SolidlyV2


@dataclass
class ScaleV2(SolidlyV2):
    @property
    def factory_abi(self):
        return SCALE_V2_FACTORY_ABI

    async def get_fee(self, address: str, contract: AsyncContract) -> Tuple[str, float]:
        fee = await self.factory_contract.caller.getRealFee(address)
        fee_float = float(fee) / 10 ** 18
        return str(fee_float), fee_float
