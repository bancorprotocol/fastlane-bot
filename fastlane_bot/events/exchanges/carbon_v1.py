# coding=utf-8
"""
Contains the exchange class for CarbonV1. This class is responsible for handling CarbonV1 events and updating the state of the pools.

(c) Copyright Bprotocol foundation 2023.
Licensed under MIT
"""
from dataclasses import dataclass
from typing import List, Type, Tuple, Any, Dict, Callable

import web3
from fastlane_bot import Config
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
    _fee_pairs: Dict[Tuple[str, str], int] = None
    router_address: str = None
    exchange_initialized: bool = False

    @property
    def fee_pairs(self) -> Dict[Tuple[str, str], int]:
        """
        Get the fee pairs.
        """
        return self._fee_pairs

    @fee_pairs.setter
    def fee_pairs(self, value: Dict[Tuple[str, str], int]):
        """
        Set the fee pairs.

        Parameters
        ----------
        value : List[Dict[Tuple[str, str], int]]

        """
        self._fee_pairs = value

    def add_pool(self, pool: Pool):
        self.pools[pool.state["cid"]] = pool

    def get_abi(self):
        return CARBON_CONTROLLER_ABI

    @property
    def get_factory_abi(self):
        return CARBON_CONTROLLER_ABI

    def get_events(self, contract: Contract) -> List[Type[Contract]]:
        return [
            contract.events.StrategyCreated,
            contract.events.StrategyUpdated,
            contract.events.StrategyDeleted,
            contract.events.PairTradingFeePPMUpdated,
            contract.events.TradingFeePPMUpdated,
            contract.events.PairCreated,
        ] if self.exchange_initialized else []

    async def get_fee(
        self, address: str, contract: Contract
    ) -> Tuple[str, float]:
        """
        Get the fee from the contract.

        Parameters
        ----------
        address
        contract

        Returns
        -------

        """
        try:
            fee = await contract.functions.tradingFeePPM().call()
        except AttributeError:
            fee = await contract.tradingFeePPM()
        return f"{fee}", fee / 1e6

    async def get_tkn0(self, address: str, contract: Contract, event: Any) -> str:
        """
        Get the token0 address from the contract or event.

        Parameters
        ----------
        address : str
            The address of the contract.
        contract : Contract
            The contract.
        event : Any
            The event.

        Returns
        -------
        str
            The token0 address.

        """
        if event is None:
            return await contract.functions.token0().call()
        else:
            return event["args"]["token0"]

    async def get_tkn1(self, address: str, contract: Contract, event: Any) -> str:
        """
        Get the token1 address from the contract or event.

        Parameters
        ----------
        address : str
            The address of the contract.
        contract : Contract
            The contract.
        event : Any
            The event.

        Returns
        -------
        str
            The token1 address.

        """
        if event is None:
            return await contract.functions.token1().call()
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
        if id in self.pools:
            self.pools.pop(id)

    def save_strategy(
        self,
        strategy: List[Any],
        block_number: int,
        cfg: Config,
        func: Callable,
        carbon_controller: Contract,
    ) -> Dict[str, Any]:
        """
        Add the pool info from the strategy.

        Parameters
        ----------
        strategy : List[Any]
            The strategy.
        block_number : int
            The block number.
        cfg : Config
            The config.
        func : Callable
            The function to call.
        carbon_controller : Contract
            The carbon controller contract.

        Returns
        -------
        Dict[str, Any]
            The pool info.

        """
        cid = strategy[0]
        order0, order1 = strategy[3][0], strategy[3][1]
        tkn0_address, tkn1_address = cfg.w3.to_checksum_address(
            strategy[2][0]
        ), cfg.w3.to_checksum_address(strategy[2][1])

        try:
            fee = self.fee_pairs[(tkn0_address, tkn1_address)]
            fee_float = fee / 1e6
        except KeyError:
            cfg.logger.warning(
                f"Fee pair not found for {tkn0_address} and {tkn1_address}... re-fetching from contract."
            )
            fee = carbon_controller.pairTradingFeePPM(tkn0_address, tkn1_address)
            fee_float = fee / 1e6
            self.fee_pairs[(tkn0_address, tkn1_address)] = fee

        return func(
            address=cfg.CARBON_CONTROLLER_ADDRESS,
            exchange_name="carbon_v1",
            fee=f"{fee}",
            fee_float=fee_float,
            tkn0_address=tkn0_address,
            tkn1_address=tkn1_address,
            cid=cid,
            other_args=dict(
                y_0=order0[0],
                y_1=order1[0],
                z_0=order0[1],
                z_1=order1[1],
                A_0=order0[2],
                A_1=order1[2],
                B_0=order0[3],
                B_1=order1[3],
            ),
            block_number=block_number,
        )
