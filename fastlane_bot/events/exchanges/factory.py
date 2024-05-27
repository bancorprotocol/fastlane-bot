"""
Contains the factory class for exchanges. 

This class is responsible for creating exchanges.

[DOC-TODO-OPTIONAL-longer description in rst format]

---
(c) Copyright Bprotocol foundation 2023-24.
All rights reserved.
Licensed under MIT.
"""
from typing import Dict, Any

from fastlane_bot.config.constants import SOLIDLY_V2_NAME, UNISWAP_V2_NAME, UNISWAP_V3_NAME


class ExchangeFactory:
    """
    Factory class for exchanges
    """

    def __init__(self):
        self._creators = {}

    def register_exchange(self, key, creator):
        """
        Register an exchange with the factory

        Parameters
        ----------
        key : str
            The key to use for the exchange
        creator : Exchange
            The exchange class to register
        """
        self._creators[key] = creator

    def get_exchange(self, key, cfg: Any, exchange_initialized: bool = None):
        """
        Get an exchange from the factory

        Parameters
        ----------
        key : str
            The key to use for the exchange
        cfg : Any
            The Config object
        exchange_initialized : bool
            If the exchange has been initialized - this flag signals if an exchange that has data updated through events has already been initialized in order to avoid duplicate event filters.
        Returns
        -------
        Exchange
            The exchange class
        """
        creator = self._creators.get(key)
        if not creator:
            fork_name = cfg.network.exchange_name_base_from_fork(exchange_name=key)
            if fork_name in key:
                raise ValueError(key)
            else:
                creator = self._creators.get(fork_name)

        args = self.get_fork_extras(exchange_name=key, cfg=cfg, exchange_initialized=exchange_initialized)
        exchange = creator(**args)

        base_exchange_name = cfg.network.exchange_name_base_from_fork(exchange_name=key)
        if base_exchange_name in [SOLIDLY_V2_NAME, UNISWAP_V2_NAME, UNISWAP_V3_NAME]:
            exchange.factory_contract = cfg.w3_async.eth.contract(
                address=cfg.FACTORY_MAPPING[key],
                abi=exchange.factory_abi,
            )

        return exchange

    def get_fork_extras(self, exchange_name: str, cfg: Any, exchange_initialized: bool) -> Dict[str, str]:
        """
        Gets extra information necessary for forked exchanges

        """

        exchange_initialized = False if exchange_initialized is None else exchange_initialized

        # Logic to handle assigning the correct router address and fee
        extras = {'exchange_name': exchange_name}
        if exchange_name in cfg.UNI_V2_FORKS:
            extras['router_address'] = cfg.UNI_V2_ROUTER_MAPPING[exchange_name]
            extras['fee'] = cfg.UNI_V2_FEE_MAPPING[exchange_name]
            extras['exchange_initialized'] = exchange_initialized
        elif exchange_name in cfg.UNI_V3_FORKS:
            extras['router_address'] = cfg.UNI_V3_ROUTER_MAPPING[exchange_name]
            extras['exchange_initialized'] = exchange_initialized
        elif exchange_name in cfg.SOLIDLY_V2_FORKS:
            extras['router_address'] = cfg.SOLIDLY_V2_ROUTER_MAPPING[exchange_name]
            extras['factory_address'] = cfg.FACTORY_MAPPING[exchange_name]
            extras['exchange_initialized'] = exchange_initialized
        elif exchange_name in cfg.CARBON_V1_FORKS:
            extras['router_address'] = cfg.CARBON_CONTROLLER_MAPPING[exchange_name]
            extras['exchange_initialized'] = exchange_initialized
        return extras
