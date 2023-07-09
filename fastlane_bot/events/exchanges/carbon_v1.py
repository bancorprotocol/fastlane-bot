# coding=utf-8
"""
Contains the exchange class for CarbonV1. This class is responsible for handling CarbonV1 events and updating the state of the pools.

(c) Copyright Bprotocol foundation 2023.
Licensed under MIT
"""
from dataclasses import dataclass
from typing import List, Type, Tuple, Any

from web3.contract import Contract

from fastlane_bot.data.abi import CARBON_CONTROLLER_ABI
from fastlane_bot.events.exchanges.base import Exchange
from fastlane_bot.events.pools.base import Pool


@dataclass
class CarbonV1(Exchange):
    """
    Carbon exchange class
    """

    exchange_name: str = "carbon_v1"

    def add_pool(self, pool: Pool):
        self.pools[pool.state["cid"]] = pool

    def get_abi(self):
        return CARBON_CONTROLLER_ABI

    def get_events(self, contract: Contract) -> List[Type[Contract]]:
        return [
            contract.events.StrategyCreated,
            contract.events.StrategyUpdated,
            contract.events.StrategyDeleted,
        ]

    def get_fee(self, address: str, contract: Contract) -> Tuple[str, float]:
        return "0.002", 0.002

    def get_tkn0(self, address: str, contract: Contract, event: Any) -> str:
        if event is None:
            return contract.functions.token0().call()
        else:
            return event["args"]["token0"]

    def get_tkn1(self, address: str, contract: Contract, event: Any) -> str:
        if event is None:
            return contract.functions.token1().call()
        else:
            return event["args"]["token1"]

    def delete_strategy(self, id: str):
        """
        Delete a strategy from the exchange

        Parameters
        ----------
        id : str (alias for cid)
            The id of the strategy to delete
        """
        self.pools.pop(id)
