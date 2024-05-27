"""
Contains the exchange class for CarbonV1. 

This class is responsible for handling CarbonV1 events and updating the state of the pools.


[DOC-TODO-OPTIONAL-longer description in rst format]

---
(c) Copyright Bprotocol foundation 2023-24.
All rights reserved.
Licensed under MIT.
"""
from dataclasses import dataclass
from typing import List, Type, Tuple, Any, Dict, Callable, Union

from fastlane_bot import Config
from web3 import Web3, AsyncWeb3
from web3.contract import Contract

from fastlane_bot.data.abi import CARBON_CONTROLLER_ABI
from ..exchanges.base import Exchange
from ..pools.base import Pool
from ..interfaces.event import Event
from ..interfaces.subscription import Subscription
from ..pools.utils import get_pool_cid


STRATEGY_CREATED_TOPIC = "0xff24554f8ccfe540435cfc8854831f8dcf1cf2068708cfaf46e8b52a4ccc4c8d"
STRATEGY_UPDATED_TOPIC = "0x720da23a5c920b1d8827ec83c4d3c4d90d9419eadb0036b88cb4c2ffa91aef7d"
STRATEGY_DELETED_TOPIC = "0x4d5b6e0627ea711d8e9312b6ba56f50e0b51d41816fd6fd38643495ac81d38b6"


@dataclass
class CarbonV1(Exchange):
    """
    Carbon exchange class
    """
    base_exchange_name: str = "carbon_v1"
    exchange_name: str = None
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
    def factory_abi(self):
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

    def get_subscriptions(self, w3: Union[Web3, AsyncWeb3]) -> List[Subscription]:
        contract = self.get_event_contract(w3)
        return [
            Subscription(contract.events.StrategyCreated, STRATEGY_CREATED_TOPIC),
            Subscription(contract.events.StrategyUpdated, STRATEGY_UPDATED_TOPIC),
            Subscription(contract.events.StrategyDeleted, STRATEGY_DELETED_TOPIC),
            Subscription(contract.events.PairTradingFeePPMUpdated),
            Subscription(contract.events.TradingFeePPMUpdated),
            Subscription(contract.events.PairCreated),
        ]

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
            fee = await contract.caller.tradingFeePPM()
        except AttributeError:
            fee = await contract.tradingFeePPM()
        return f"{fee}", fee / 1e6

    async def get_tkn0(self, address: str, contract: Contract, event: Event) -> str:
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
            return await contract.caller.token0()
        else:
            return event.args["token0"]

    async def get_tkn1(self, address: str, contract: Contract, event: Event) -> str:
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
            return await contract.caller.token1()
        else:
            return event.args["token1"]

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

        strategy_id = strategy[0]
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

        pool_info_temp = {"exchange_name": self.exchange_name, "fee": f"{fee}",
                          'pair_name': f"{tkn0_address}/{tkn1_address}", 'strategy_id': strategy_id}
        cid = get_pool_cid(pool_info_temp, cfg.CARBON_V1_FORKS)

        return func(
            address=cfg.CARBON_CONTROLLER_MAPPING[self.exchange_name],
            exchange_name=self.exchange_name,
            fee=f"{fee}",
            fee_float=fee_float,
            tkn0_address=tkn0_address,
            tkn1_address=tkn1_address,
            cid=cid,
            strategy_id=strategy_id,
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

    def get_pool_func_call(self, addr1, addr2):
        raise NotImplementedError
