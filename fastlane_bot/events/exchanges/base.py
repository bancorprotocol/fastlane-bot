# coding=utf-8
"""
Contains the base class for exchanges. This class is responsible for handling exchanges and updating the state of the pools.

(c) Copyright Bprotocol foundation 2023.
Licensed under MIT
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, List, Type, Any

from web3.contract import Contract

from fastlane_bot.events.pools.base import Pool


@dataclass
class Exchange(ABC):
    """
    Base class for exchanges
    """

    __VERSION__ = "0.0.1"
    __DATE__ = "2023-07-03"

    pools: Dict[str, Pool] = field(default_factory=dict)

    def get_pools(self) -> List[Pool]:
        """
        Get the pools of the exchange.

        Returns
        -------
        List[Pool]
            The pools of the exchange

        """
        return list(self.pools.values())

    @abstractmethod
    def add_pool(self, pool: Pool):
        """
        Add a pool to the exchange.

        Parameters
        ----------
        pool : Pool
            The pool object

        Returns
        -------
        None
        """
        pass

    @abstractmethod
    def get_abi(self):
        """
        Get the ABI of the exchange

        Returns
        -------
        ABI
            The ABI of the exchange

        """
        pass

    @abstractmethod
    def get_events(self, contract: Contract) -> List[Type[Contract]]:
        """
        Get the events of the exchange

        Parameters
        ----------
        contract : Contract
            The contract object

        Returns
        -------
        List[Type[Contract]]
            The events of the exchange

        """
        pass

    @abstractmethod
    def get_fee(self, address: str, contract: Contract) -> float:
        """
        Get the fee of the exchange

        Parameters
        ----------
        address : str
            The address of the exchange
        contract : Contract
            The contract object

        Returns
        -------
        float
            The fee of the exchange

        """
        pass

    @abstractmethod
    def get_tkn0(self, address: str, contract: Contract, event: Any) -> str:
        """
        Get the tkn0 of the exchange

        Parameters
        ----------
        address : str
            The address of the exchange
        contract : Contract
            The contract object
        event : Any
            The event object

        Returns
        -------
        str
            The tkn0 of the exchange
        """
        pass

    @abstractmethod
    def get_tkn1(self, address: str, contract: Contract, event: Any) -> str:
        """
        Get the tkn1 of the exchange

        Parameters
        ----------
        address : str
            The address of the exchange
        contract : Contract
            The contract object
        event : Any
            The event object

        Returns
        -------
        str
            The tkn1 of the exchange

        """
        pass

    def get_pool(self, key: str) -> Pool:
        """

        Parameters
        ----------
        key: str
            pool_address if UniswapV2 or SushiswapV2 or UniswapV3
            else tkn1_address if BancorV3
            else cid if Carbon

        Returns
        -------
        Pool
            The pool object

        """
        return self.pools[key] if key in self.pools else None
