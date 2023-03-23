"""
Networks module for fastlane_bot - used to interact with the blockchain.

(c) Copyright Bprotocol foundation 2023.
Licensed under MIT
"""
import subprocess
from abc import ABCMeta, ABC

from brownie import network, Contract, accounts  # type: ignore
from eth_typing import HexStr
from hexbytes import HexBytes
from web3 import Web3
from web3.types import TxReceipt

from fastlane_bot.constants import ec

logger = ec.DEFAULT_LOGGER


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


class NetworkBase(metaclass=Singleton):
    """
    Base class for all networks - this is a singleton class that is used to interact with the blockchain
    """

    web3: Web3

    def __init__(
        self,
        network_id: str,
        network_name: str,
        provider_url: str,
        fastlane_contract_address: str,
    ):
        """
        :param provider_url: the RPC URL to connect to
        :param fastlane_contract_address: the address of the FastLane contract
        """
        # Validate parameters - network id
        try:
            assert len(str(network_id)) != 0
        except AssertionError as e:
            raise ValueError("Network ID cannot be empty") from e
        self.network_id = network_id.lower()

        # Validate parameters - network name
        try:
            assert len(str(network_name)) != 0
        except AssertionError as e:
            raise ValueError("Network name cannot be empty") from e
        self.network_name = network_name

        # Validate parameters - provider url
        try:
            assert len(str(provider_url)) != 0
        except AssertionError as e:
            raise ValueError("Provider URL cannot be empty") from e
        self.provider_url = provider_url

        # Validate parameters - fastlane_bot contract address
        try:
            assert len(str(fastlane_contract_address)) != 0
        except AssertionError as e:
            raise ValueError("FastLane contract address cannot be empty")
        self.fastlane_contract_address = fastlane_contract_address

        # Connect to the network
        self.web3 = Web3(Web3.HTTPProvider(provider_url))


# *******************************************************************************************
# Network - Ethereum
# *******************************************************************************************


class EthereumNetwork(NetworkBase):
    """
    Ethereum network class
    """

    chain_id: int = ec.CHAIN_ID
    block_time: int = 0
    gas_price: int = ec.DEFAULT_GAS_PRICE
    gas_limit: int = ec.DEFAULT_GAS
    _is_connected: bool = False

    def __init__(
        self,
        network_id: str = None,
        network_name: str = None,
        provider_url: str = None,
        fastlane_contract_address: str = None,
    ):
        """
        Note that Tenderly here must be configured in brownie - you can do this in the Terminal using the following command:
        brownie networks add [environment] [id] host=[host] [KEY=VALUE, ...]. For example:
        brownie networks add "Ethereum" "tenderly" host=https://rpc.tenderly.co/fork/7fd3f956-5409-4496-be95 chainid=1

        :param network_id: the name of the network to connect to
        :param provider_url: the url of the provider
        :param fastlane_contract_address: the address of the fastlane_bot contract
        :param logger: the logger!
        :param max_slippage: the maximum slippage allowed
        """

        super().__init__(
            network_id,
            network_name,
            provider_url,
            fastlane_contract_address,
        )
        self.network = network

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
        return self.web3.eth.account.sign_transaction(transaction, ec.ETHERSCAN_TOKEN)

    def connect_network(self):
        """
        Connect to the network
        """
        logger.info(f"Connecting to {self.network_name} network")

        if self.is_connected:
            return
        add_tenderly = f'brownie networks add "Ethereum" "{self.network_id}" host="{self.provider_url}" name="{self.network_name}" chainid={ec.CHAIN_ID}'
        mod_tenderly = f'brownie networks modify "{self.network_id}" host="{self.provider_url}" name="{self.network_name}" chainid={ec.CHAIN_ID}'
        set_tenderly = f'brownie networks set_provider "{self.network_id}" host="{self.provider_url}" name="{self.network_name}" chainid={ec.CHAIN_ID}'

        cmds = [add_tenderly, mod_tenderly, set_tenderly]
        for cmd in cmds:
            p = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                stdin=subprocess.PIPE,
                shell=True,
            )

            stdout, stderr = p.communicate()
            if "already exists" in stderr.decode("utf-8"):
                logger.debug(f"network {self.network_id} already exists")

        self.network.connect(self.network_id)
        self._is_connected = True
        self.web3 = Web3(Web3.HTTPProvider(self.provider_url))
        logger.info(f"Connected to {self.network_id} network")
        logger.info(f"Connected to {self.web3.provider.endpoint_uri}")
