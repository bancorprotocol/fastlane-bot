# coding=utf-8
"""
Contains the exchange class for BancorV3. This class is responsible for handling BancorV3 events and updating the state of the pools.

(c) Copyright Bprotocol foundation 2023.
Licensed under MIT
"""
from dataclasses import dataclass
from typing import List, Type, Tuple, Any, Dict, Callable

from web3.contract import Contract

from fastlane_bot.data.abi import BANCOR_POL_ABI
from fastlane_bot.events.exchanges.base import Exchange
from fastlane_bot.events.pools.base import Pool
from fastlane_bot import Config


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

    def get_events(self, contract: Contract) -> List[Type[Contract]]:
        return [contract.events.TokenTraded, contract.events.TradingEnabled]

    def get_fee(self, address: str, contract: Contract) -> Tuple[str, float]:
        return "0.000", 0.000

    def get_tkn0(self, address: str, contract: Contract, event: Any) -> str:
        return event["args"]["token"]

    def get_tkn1(self, address: str, contract: Contract, event: Any) -> str:
        return self.ETH_ADDRESS if event["args"]["token"] not in self.ETH_ADDRESS else self.BNT_ADDRESS

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
        cid = f"{self.exchange_name}_{token}"
        tkn0_address = cfg.w3.toChecksumAddress(token)
        tkn1_address = cfg.w3.toChecksumAddress(cfg.ETH_ADDRESS) if token not in cfg.ETH_ADDRESS else cfg.BNT_ADDRESS

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
