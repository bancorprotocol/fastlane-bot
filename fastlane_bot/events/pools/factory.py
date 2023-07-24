# coding=utf-8
"""
Contains the factory class for pools. This class is responsible for creating pools.

(c) Copyright Bprotocol foundation 2023.
Licensed under MIT
"""
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

    def get_pool(self, format_name: str) -> Pool:
        """
        Get a pool.

        Parameters
        ----------
        format_name : str
            The name of the pool type.
        """
        creator = self._creators.get(format_name)
        if not creator:
            if format_name:
                raise ValueError(format_name)
            else:
                # raise ValueError("format_name")
                pass
        return creator


# create an instance of the factory
pool_factory = PoolFactory()
