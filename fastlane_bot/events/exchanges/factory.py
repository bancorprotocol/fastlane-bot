# coding=utf-8
"""
Contains the factory class for exchanges. This class is responsible for creating exchanges.

(c) Copyright Bprotocol foundation 2023.
Licensed under MIT
"""


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

    def get_exchange(self, key):
        """
        Get an exchange from the factory

        Parameters
        ----------
        key : str
            The key to use for the exchange

        Returns
        -------
        Exchange
            The exchange class
        """
        creator = self._creators.get(key)
        if not creator:
            raise ValueError(key)
        return creator()
