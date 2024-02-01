"""
Networks module for fastlane - used to interact with the blockchain.

(c) Copyright Bprotocol foundation 2024.
Licensed under MIT
"""

import logging
import os
from abc import ABCMeta, ABC

from dotenv import load_dotenv
from eth_typing import HexStr
from hexbytes import HexBytes
from web3 import Web3, AsyncWeb3
from web3.types import TxReceipt

load_dotenv()

logger = logging.getLogger(__name__)


class Singleton(ABCMeta):
    """
    Metaclass for implementing the Singleton design pattern.

    Explanation:
        This metaclass ensures that only one instance of a class is created and returned upon subsequent calls to the class constructor.

    Args:
        *args: Positional arguments to be passed to the class constructor.
        **kwargs: Keyword arguments to be passed to the class constructor.

    Returns:
        EthereumNetwork: The instance of the class.

    Examples:
        # Create a singleton class
        class MySingleton(metaclass=Singleton):
            pass

        instance1 = MySingleton()
        instance2 = MySingleton()

        assert instance1 is instance2  # Only one instance is created
    """

    _instances = {}

    def __call__(self, *args, **kwargs) -> "EthereumNetwork":
        """
        Creates and returns an instance of the class.

        Args:
            *args: Positional arguments to be passed to the class constructor.
            **kwargs: Keyword arguments to be passed to the class constructor.

        Returns:
            EthereumNetwork: The instance of the class.
        """

        if self not in self._instances:
            self._instances[self] = super(Singleton, self).__call__(*args, **kwargs)
        return self._instances[self]


class NetworkBase(ABC, metaclass=Singleton):
    """
    Base class for network configurations.

    Explanation:
        This class serves as the base class for network configurations. It provides common attributes and initialization logic.

    Args:
        network_id: The ID of the network.
        network_name: The name of the network.
        provider_url: The RPC URL to connect to.
        provider_name: The name of the provider.
        nonce: The nonce value.

    Returns:
        None
    """

    web3: Web3
    w3_async: AsyncWeb3

    def __init__(
        self,
        network_id: str,
        network_name: str,
        provider_url: str,
        provider_name: str,
        nonce: int,
    ) -> None:
        """
        Initializes a network configuration.

        Args:
            network_id: The ID of the network.
            network_name: The name of the network.
            provider_url: The RPC URL to connect to.
            provider_name: The name of the provider.
            nonce: The nonce value.

        Returns:
            None
        """

        self.network_id = network_id.lower()
        self.network_name = network_name
        self.provider_url = provider_url
        self.provider_name = provider_name
        self.nonce = nonce


class EthereumNetwork(NetworkBase):
    """
    Ethereum network configuration class.

    Explanation:
        This class represents the configuration for an Ethereum network. It inherits from the NetworkBase class and provides additional attributes and methods specific to Ethereum.

    Attributes:
        chain_id: The ID of the Ethereum chain. Defaults to 1.
        block_time: The average block time of the Ethereum network. Defaults to 0.
        gas_price: The gas price for transactions on the Ethereum network. Defaults to 0.
        gas_limit: The gas limit for transactions on the Ethereum network. Defaults to 0.
        _is_connected: A flag indicating whether the network is connected.

    Args:
        network_id: The ID of the network to connect to. Defaults to None.
        network_name: The name of the network to connect to. Defaults to None.
        provider_url: The URL of the provider. Defaults to None.
        provider_name: The name of the provider. Defaults to None.
        nonce: The nonce to use for transactions. Defaults to 0.

    Returns:
        None

    Properties:
        is_connected: A property indicating whether the network is connected.

    Methods:
        tx_to_hex: Convert a transaction receipt to a hex string.
        sign_transaction: Sign a transaction.
        increment_nonce: Increment the nonce counter before submitting a transaction.
        connect_network: Connect to the network.
    """

    chain_id: int = 1
    block_time: int = 0
    gas_price: int = 0
    gas_limit: int = 0
    _is_connected: bool = False

    def __init__(
        self,
        network_id: str = None,
        network_name: str = None,
        provider_url: str = None,
        provider_name: str = None,
        nonce: int = 0,
    ) -> None:
        """
        Initializes the Ethereum network configuration.

        Args:
            network_id: The ID of the network to connect to. Defaults to None.
            network_name: The name of the network to connect to. Defaults to None.
            provider_url: The URL of the provider. Defaults to None.
            provider_name: The name of the provider. Defaults to None.
            nonce: The nonce to use for transactions. Defaults to 0.

        Returns:
            None
        """

        super().__init__(
            network_id,
            network_name,
            provider_url,
            provider_name,
            nonce,
        )

    @property
    def is_connected(self) -> bool:
        """
        Property indicating whether the network is connected.

        Returns:
            bool: True if the network is connected, False otherwise.
        """

        return self._is_connected

    @is_connected.setter
    def is_connected(self, value: bool):
        """
        Setter for the property indicating whether the network is connected.

        Args:
            value: The value to set for the property.

        Returns:
            None
        """

        self._is_connected = value

    def tx_to_hex(self, tx_receipt: TxReceipt) -> HexStr:
        """
        Converts a transaction receipt to a hexadecimal string.

        Args:
            tx_receipt: The transaction receipt.

        Returns:
            HexStr: The hexadecimal string representing the transaction hash.
        """

        return self.web3.to_hex(dict(tx_receipt)["transactionHash"])

    def sign_transaction(self, transaction: HexBytes) -> HexBytes:
        """
        Signs a transaction.

        Args:
            transaction: The transaction to sign.

        Returns:
            HexBytes: The signed transaction.
        """

        return self.web3.eth.account.sign_transaction(
            transaction, os.getenv("ETHERSCAN_TOKEN")
        )

    def increment_nonce(self) -> None:
        """
        Increments the nonce counter before submitting a transaction.

        Returns:
            None
        """

        self.nonce += 1

    def connect_network(self) -> None:
        """
        Connects to the network.

        Explanation:
            This method establishes a connection to the specified network using the provided provider URL.

        Returns:
            None
        """

        logger.info(f"Connecting to {self.network_name} network")

        if self.is_connected:
            return

        self.web3 = Web3(
            Web3.HTTPProvider(self.provider_url, request_kwargs={"timeout": 60})
        )
        self.w3_async = AsyncWeb3(AsyncWeb3.AsyncHTTPProvider(self.provider_url))
        logger.info(f"Connected to {self.network_id} network")
        logger.info(f"Connected to {self.web3.provider.endpoint_uri} network")
