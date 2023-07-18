# coding=utf-8
"""
Contains the events manager module for handling event related functionality of data fetching.

(c) Copyright Bprotocol foundation 2023.
Licensed under MIT
"""
from typing import Dict, Any, List, Type

from web3.contract import Contract

from fastlane_bot.events.managers.base import BaseManager


class EventManager(BaseManager):
    @property
    def events(self) -> List[Type[Contract]]:
        """
        Get the events from the exchanges.

        Returns
        -------
        List[Type[Contract]]
            The events.
        """
        return [
            event
            for exchange in self.exchanges.values()
            for event in exchange.get_events(
                self.event_contracts[exchange.exchange_name]
            )
        ]

    def add_pool_info_from_event(
        self, strategy: List[Any], block_number: int = None
    ) -> Dict[str, Any]:
        """
        Add the pool info from the strategy.

        Parameters
        ----------
        strategy : List[Any]
            The strategy.
        block_number (optional) : int
            The block number the data was gathered.

        Returns
        -------
        Dict[str, Any]
            The pool info.

        """
        cid = strategy[0]
        order0, order1 = strategy[3][0], strategy[3][1]
        tkn0_address, tkn1_address = self.web3.toChecksumAddress(
            strategy[2][0]
        ), self.web3.toChecksumAddress(strategy[2][1])

        return self.add_pool_info(
            address=self.cfg.CARBON_CONTROLLER_ADDRESS,
            exchange_name="carbon_v1",
            fee="0.002",
            fee_float=0.002,
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
