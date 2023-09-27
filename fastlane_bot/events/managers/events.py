# coding=utf-8
"""
Contains the events manager module for handling event related functionality of data fetching.

(c) Copyright Bprotocol foundation 2023.
Licensed under MIT
"""
from typing import Dict, Any, List, Type, Tuple

from web3.contract import Contract

from fastlane_bot.events.managers.base import BaseManager


class EventManager(BaseManager):
    @property
    def events(self) -> List[Contract]:
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
