# coding=utf-8
"""
Contains the factory class for pools. This class is responsible for creating pools.

(c) Copyright Bprotocol foundation 2023.
Licensed under MIT
"""
from typing import Any, Dict

from fastlane_bot.events.pools.base import Pool


class PoolFactory:
    """
    Factory class for creating pools.
    """

    def __init__(self):
        self._creators = {}

    def register_format(self, format_name: str, creator: Pool) -> None:
        """
        Register a pool type.

        Parameters
        ----------
        format_name : str
            The name of the pool type.
        creator : Pool
            The pool class.
        """
        self._creators[format_name] = creator

    def get_pool(self, format_name: str, cfg: Any) -> Pool:
        """
        Get a pool.

        Parameters
        ----------
        format_name : str
            The name of the pool type.
        cfg : Any
            The config object
        """
        exchange_base = cfg.network.exchange_name_base_from_fork(exchange_name=format_name)
        creator = self._creators.get(exchange_base)

        if not creator:
            if format_name:
                raise ValueError(format_name)
            else:
                # raise ValueError("format_name")
                pass
        return creator

    def get_fork_extras(self, exchange_name: str, cfg: Any) -> Dict[str, str]:
        """
        Gets extra information necessary for forked exchanges

        """
        # Logic to handle assigning the correct router address and fee
        extras = {'exchange_name': exchange_name}
        if exchange_name in cfg.UNI_V2_FORKS:
            extras['router_address'] = cfg.UNI_V2_ROUTER_MAPPING[exchange_name]
            extras['fee'] = cfg.UNI_V2_FEE_MAPPING[exchange_name]
        elif exchange_name in cfg.UNI_V3_FORKS:
            extras['router_address'] = cfg.UNI_V3_ROUTER_MAPPING[exchange_name]
        elif exchange_name in cfg.SOLIDLY_V2_FORKS:
            extras['router_address'] = cfg.SOLIDLY_V2_ROUTER_MAPPING[exchange_name]
        elif exchange_name in cfg.CARBON_V1_FORKS:
            extras['router_address'] = cfg.CARBON_CONTROLLER_MAPPING[exchange_name]
        return extras

# create an instance of the factory
pool_factory = PoolFactory()
