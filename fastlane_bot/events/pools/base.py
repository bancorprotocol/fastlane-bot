"""
Contains the base class for pools. 

This class is responsible for handling pools and updating the state of the pools.

[DOC-TODO-OPTIONAL-longer description in rst format]

---
(c) Copyright Bprotocol foundation 2023-24.
All rights reserved.
Licensed under MIT.
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Any, List

from web3 import Web3
from web3.contract import Contract

from ..interfaces.event import Event


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
    factory_contract = None
    @classmethod
    @abstractmethod
    def event_matches_format(
        cls, event: Dict[str, Any], static_pools: Dict[str, Any], exchange_name: str = None
    ) -> bool:
        """
        Check if an event matches the format for a given pool type.

        Parameters
        ----------
        event : Dict[str, Any]
            The event arguments.
        static_pools : Dict[str, Any]
            The static pools.
        exchange_name : str
            The name of the exchange in order to match forks
        Returns
        -------
        bool
            True if the event matches the format of a Bancor v3 event, False otherwise.

        """
        pass

    @staticmethod
    def get_common_data(
        event: Event, pool_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Get common (common to all Pool child classes) data from an event and pool info.

        Args:
            event (Event): The event data.
            pool_info (Dict[str, Any]): The pool information.

        Returns:
            Dict[str, Any]: A dictionary containing common data extracted from the event and pool info.
        """
        return {
            "last_updated_block": event.block_number,
            "timestamp": datetime.now().strftime("%H:%M:%S"),
            "pair_name": pool_info["pair_name"],
            "descr": pool_info["descr"],
            "address": event.address,
        }

    @staticmethod
    @abstractmethod
    def update_from_event(
        event: Event, data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Update the pool state from an event.

        Parameters
        ----------
        event : Event
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
    def update_from_contract(
        self,
        contract: Contract,
        tenderly_fork_id: str = None,
        w3_tenderly: Web3 = None,
        w3: Web3 = None,
        tenderly_exchanges: List[str] = None,
    ) -> Dict[str, Any]:
        """
        Update the pool state from a contract.

        Parameters
        ----------
        contract : Contract
            The contract.
        tenderly_fork_id : str, optional
            The tenderly fork id, by default None
        w3_tenderly : Web3, optional
            The tenderly web3 instance, by default None
        w3 : Web3, optional
            The web3 instance, by default None
        tenderly_exchanges : List[str], optional
            The tenderly exchanges, by default None

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
