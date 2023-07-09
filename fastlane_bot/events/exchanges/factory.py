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
