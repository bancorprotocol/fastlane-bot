# coding=utf-8
"""
Contains the base class for pools. This class is responsible for handling pools and updating the state of the pools.

(c) Copyright Bprotocol foundation 2023.
Licensed under MIT
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Any

from web3.contract import Contract


@dataclass
class Pool(ABC):
    """
    Abstract base class representing a pool.

    Attributes
    ----------
    state : Dict[str, Any]
        The pool state.
    """

    __VERSION__ = "0.0.1"
    __DATE__ = "2023-07-03"

    state: Dict[str, Any] = field(default_factory=dict)

    @staticmethod
    def get_common_data(
        event: Dict[str, Any], pool_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Get common (common to all Pool child classes) data from an event and pool info.

        Args:
            event (Dict[str, Any]): The event data.
            pool_info (Dict[str, Any]): The pool information.

        Returns:
            Dict[str, Any]: A dictionary containing common data extracted from the event and pool info.
        """
        return {
            "last_updated_block": event["blockNumber"],
            "timestamp": datetime.now().strftime("%H:%M:%S"),
            "pair_name": pool_info["pair_name"],
            "descr": pool_info["descr"],
            "address": event["address"],
        }

    @staticmethod
    @abstractmethod
    def update_from_event(
        event_args: Dict[str, Any], data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Update the pool state from an event.

        Parameters
        ----------
        event_args : Dict[str, Any]
            The event arguments.
        data : Dict[str, Any]
            The pool data.

        Returns
        -------
        Dict[str, Any]
            The updated pool data.
        """
        pass

    @abstractmethod
    def update_from_contract(self, contract: Contract) -> Dict[str, Any]:
        """
        Update the pool state from a contract.

        Parameters
        ----------
        contract : Contract
            The contract.

        Returns
        -------
        Dict[str, Any]
            The updated pool data.
        """
        pass

    @staticmethod
    @abstractmethod
    def unique_key() -> str:
        """
        Returns the unique key for the pool.
        """
        pass
