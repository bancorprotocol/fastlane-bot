"""
Contains the base class for exchanges. 

This class is responsible for handling exchanges and updating the state of the pools.

[DOC-TODO-OPTIONAL-longer description in rst format]

---
(c) Copyright Bprotocol foundation 2023-24.
All rights reserved.
Licensed under MIT.
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, List, Type, Any, Union

from web3 import Web3, AsyncWeb3
from web3.contract import Contract, AsyncContract

from fastlane_bot.config.constants import CARBON_V1_NAME
from ..pools.base import Pool
from ..interfaces.subscription import Subscription


@dataclass
class Exchange(ABC):
    """
    Base class for exchanges
    """

    exchange_name: str
    base_exchange_name: str = ''
    pools: Dict[str, Pool] = field(default_factory=dict)
    factory_contract: Contract = None

    __VERSION__ = "0.0.3"
    __DATE__ = "2024-03-20"

    @property
    def is_carbon_v1_fork(self) -> bool:
        return self.base_exchange_name == CARBON_V1_NAME

    def get_pools(self) -> List[Pool]:
        """
        Get the pools of the exchange.

        Returns
        -------
        List[Pool]
            The pools of the exchange

        """
        return list(self.pools.values())

    def get_event_contract(self, w3: Union[Web3, AsyncWeb3]) -> Union[Contract, AsyncContract]:
        return w3.eth.contract(abi=self.get_abi())

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
    def get_subscriptions(self, w3: Union[Web3, AsyncWeb3]) -> List[Subscription]:
        ...

    @staticmethod
    @abstractmethod
    async def get_fee(address: str, contract: AsyncContract) -> float:
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
    def get_pool_func_call(self, addr1, addr2, *args, **kwargs):
        ...

    @staticmethod
    @abstractmethod
    async def get_tkn0(address: str, contract: AsyncContract, event: Any) -> str:
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

    @staticmethod
    @abstractmethod
    async def get_tkn1(address: str, contract: AsyncContract, event: Any) -> str:
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

    @abstractmethod
    def factory_abi(self):
        """
                Get the ABI of the exchange's Factory contract

                Returns
                -------
                ABI
                    The ABI of the exchange Factory

                """
        pass
