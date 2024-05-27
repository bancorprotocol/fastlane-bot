"""
Contains the exchange class for Bancor POL. 

This class is responsible for handling Bancor POL events and updating the state of the pools.


[DOC-TODO-OPTIONAL-longer description in rst format]

---
(c) Copyright Bprotocol foundation 2023-24.
All rights reserved.
Licensed under MIT.
"""
from dataclasses import dataclass
from typing import List, Type, Tuple, Any, Dict, Callable, Union

from web3 import Web3, AsyncWeb3
from web3.contract import Contract

from fastlane_bot.data.abi import BANCOR_POL_ABI
from fastlane_bot import Config
from ..exchanges.base import Exchange
from ..pools.base import Pool
from ..interfaces.event import Event
from ..interfaces.subscription import Subscription


@dataclass
class BancorPol(Exchange):
    """
    Bancor protocol-owned liquidity exchange class
    """

    exchange_name: str = "bancor_pol"
    BNT_ADDRESS: str = "0x1F573D6Fb3F13d689FF844B4cE37794d79a7FF1C"
    ETH_ADDRESS = "0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE"

    def add_pool(self, pool: Pool):
        self.pools[pool.state["tkn0_address"]] = pool

    def get_abi(self):
        return BANCOR_POL_ABI

    @property
    def factory_abi(self):
        # Not used for Bancor POL
        return BANCOR_POL_ABI

    def get_events(self, contract: Contract) -> List[Type[Contract]]:
        return [contract.events.TokenTraded, contract.events.TradingEnabled]

    def get_subscriptions(self, w3: Union[Web3, AsyncWeb3]) -> List[Subscription]:
        contract = self.get_event_contract(w3)
        return [
            Subscription(contract.events.TokenTraded, collect_all=True),
            Subscription(contract.events.TradingEnabled, "0xae3f48c001771f8e9868e24d47b9e4295b06b1d78072acf96f167074aa3fab64", collect_all=True),
        ]

    async def get_fee(self, address: str, contract: Contract) -> Tuple[str, float]:
        return "0.000", 0.000

    async def get_tkn0(self, address: str, contract: Contract, event: Event) -> str:
        return event.args["token"]

    async def get_tkn1(self, address: str, contract: Contract, event: Event) -> str:
        return self.ETH_ADDRESS if event.args["token"] not in self.ETH_ADDRESS else self.BNT_ADDRESS

    def save_strategy(
        self,
        token: str,
        block_number: int,
        cfg: Config,
        func: Callable,
    ) -> Dict[str, Any]:
        """
        Add the pool info from the strategy.

        Parameters
        ----------
        token : str
            The token address for POL
        block_number : int
            The block number.
        cfg : Config
            The config.
        func : Callable
            The function to call.

        Returns
        -------
        Dict[str, Any]
            The pool info.

        """
        # TODO: This needs to be changed so that it is handled in the same way, and place, as the other exchanges.
        cid = f"{self.exchange_name}_{token}"
        tkn0_address = cfg.w3.to_checksum_address(token)
        tkn1_address = cfg.w3.to_checksum_address(cfg.ETH_ADDRESS) if token not in cfg.ETH_ADDRESS else cfg.BNT_ADDRESS

        return func(
            address=cfg.BANCOR_POL_ADDRESS,
            exchange_name="bancor_pol",
            fee="0",
            fee_float=0,
            tkn0_address=tkn0_address,
            tkn1_address=tkn1_address,
            cid=cid,
            block_number=block_number,
        )

    def get_pool_func_call(self, addr1, addr2):
        raise NotImplementedError
