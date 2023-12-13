"""
Networks module for fastlane - used to interact with the blockchain.

(c) Copyright Bprotocol foundation 2023.
Licensed under MIT
"""


import subprocess
from abc import ABCMeta, ABC

from eth_typing import HexStr
from hexbytes import HexBytes
from web3 import Web3
from web3.types import TxReceipt

import os
from dotenv import load_dotenv

from fastlane_bot.config import network

load_dotenv()

import logging
logger = logging.getLogger(__name__)


# *******************************************************************************************
# Singleton
# *******************************************************************************************


class Singleton(ABCMeta):
    """
    Singleton metaclass that enables the creation of a singleton object, as seen in this post:
    """

    _instances = {}

    def __call__(self, *args, **kwargs):
        if self not in self._instances:
            self._instances[self] = super(Singleton, self).__call__(*args, **kwargs)
        return self._instances[self]


# *******************************************************************************************
# Base Network
# *******************************************************************************************


class NetworkBase(ABC, metaclass=Singleton):
    """
    Base class for all networks - this is a singleton class that is used to interact with the blockchain

    :param network_id: the name of the network to connect to
    :param network_name: the name of the network to connect to
    :param provider_url: the url of the provider
    :param nonce: the nonce to use for transactions
    """

    web3: Web3

    def __init__(
        self,
        network_id: str,
        network_name: str,
        provider_url: str,
        provider_name: str,
        nonce: int,
    ):
        """
        :param provider_url: the RPC URL to connect to
        :param fastlane_contract_address: the address of the FastLane contract
        """
        self.network_id = network_id.lower()
        self.network_name = network_name
        self.provider_url = provider_url
        self.provider_name = provider_name
        self.web3 = Web3(Web3.HTTPProvider(provider_url, request_kwargs={'timeout': 60}))
        self.nonce = nonce


class EthereumNetwork(NetworkBase):
    """
    Ethereum network class

    :param network_id: the name of the network to connect to
    :param network_name: the name of the network to connect to
    :param provider_url: the url of the provider
    :param nonce: the nonce to use for transactions

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
    ):
        """

        :param network_id: the name of the network to connect to
        :param network_name: the name of the network to connect to
        :param provider_url: the url of the provider
        :param provider_name: the name of the provider
        :param nonce: the nonce to use for transactions

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
        :return: True if the network is connected, False otherwise
        """
        return self._is_connected

    @is_connected.setter
    def is_connected(self, value: bool):
        self._is_connected = value

    def tx_to_hex(self, tx_receipt: TxReceipt) -> HexStr:
        """
        Convert a transaction receipt to a hex string
        :param tx_receipt:
        :return: the hex string
        """
        return self.web3.toHex(dict(tx_receipt)["transactionHash"])

    def sign_transaction(self, transaction: HexBytes) -> HexBytes:
        """
        Sign a transaction
        :param transaction:
        :return: the signed transaction
        """
        return self.web3.eth.account.sign_transaction(
            transaction, os.getenv("ETHERSCAN_TOKEN")
        )

    def increment_nonce(self) -> None:
        """
        increments nonce counter before submitting a transaction
        """
        self.nonce += 1

    def connect_network(self):
        """
        Connect to the network
        """
        logger.info(f"Connecting to {self.network_name} network")

        if self.is_connected:
            return

        self.web3 = Web3(Web3.HTTPProvider(self.provider_url, request_kwargs={'timeout': 60}))
        logger.info(f"Connected to {self.network_id} network")
        logger.info(f"Connected to {self.web3.provider.endpoint_uri} network")
