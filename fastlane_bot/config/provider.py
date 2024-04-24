"""
Provider configuration (provides the ``ConfigProvider`` class)

[DOC-TODO-OPTIONAL-longer description in rst format]

---
(c) Copyright Bprotocol foundation 2023-24.
All rights reserved.
Licensed under MIT.
"""

__VERSION__ = "0.9.1"
__DATE__ = "30/Apr 2023"

from .base import ConfigBase
from . import selectors as S
from .network import ConfigNetwork
from .connect import EthereumNetwork
import os
from dotenv import load_dotenv

load_dotenv()

from ..data.abi import (
    BANCOR_V3_NETWORK_INFO_ABI,
    CARBON_CONTROLLER_ABI,
    FAST_LANE_CONTRACT_ABI,
    GAS_ORACLE_ABI,
)

ETH_PRIVATE_KEY_BE_CAREFUL = os.environ.get("ETH_PRIVATE_KEY_BE_CAREFUL")
# WEB3_ALCHEMY_PROJECT_ID = os.environ.get("WEB3_ALCHEMY_PROJECT_ID")


class ConfigProvider(ConfigBase):
    """
    Fastlane bot config -- provider
    """

    __VERSION__ = __VERSION__
    __DATE__ = __DATE__

    RPC_URL = None  # set in derived class init

    PROVIDER_DEFAULT = S.PROVIDER_DEFAULT
    PROVIDER_INFURA = S.PROVIDER_INFURA
    PROVIDER_ALCHEMY = S.PROVIDER_ALCHEMY
    PROVIDER_TENDERLY = S.PROVIDER_TENDERLY
    PROVIDER_UNITTEST = S.PROVIDER_UNITTEST
    ETH_PRIVATE_KEY_BE_CAREFUL = ETH_PRIVATE_KEY_BE_CAREFUL
    # WEB3_ALCHEMY_PROJECT_ID = WEB3_ALCHEMY_PROJECT_ID

    @classmethod
    def new(cls, network: ConfigNetwork, provider=None, **kwargs):
        """
        Return a new ConfigProvider.
        """
        if not issubclass(type(network), ConfigNetwork):
            raise TypeError(f"Invalid network type: {type(network)}")

        if provider is None:
            provider = cls.PROVIDER_DEFAULT

        if provider == S.PROVIDER_DEFAULT:
            provider = network.DEFAULT_PROVIDER

        if provider == S.PROVIDER_ALCHEMY:
            return _ConfigProviderAlchemy(network, _direct=False, **kwargs)
        elif provider == S.PROVIDER_TENDERLY:
            return _ConfigProviderTenderly(network, _direct=False, **kwargs)
        elif provider == S.PROVIDER_INFURA:
            return _ConfigProviderInfura(network, _direct=False, **kwargs)
        elif provider == S.PROVIDER_UNITTEST:
            return _ConfigProviderUnitTest(network, _direct=False, **kwargs)
        else:
            raise ValueError(f"Unknown provider: {provider}")

    def __init__(self, network: ConfigNetwork, **kwargs):
        super().__init__(**kwargs)
        self.BANCOR_ARBITRAGE_CONTRACT = None
        self.network = network

class _ConfigProviderAlchemy(ConfigProvider):
    """
    Fastlane bot config -- provider [Alchemy]
    """

    PROVIDER = S.PROVIDER_ALCHEMY
    # WEB3_ALCHEMY_PROJECT_ID = WEB3_ALCHEMY_PROJECT_ID

    def __init__(self, network: ConfigNetwork, **kwargs):
        super().__init__(network, **kwargs)
        # assert self.network.NETWORK == ConfigNetwork.NETWORK_ETHEREUM, f"Alchemy only supports Ethereum {self.network}"
        self.WEB3_ALCHEMY_PROJECT_ID = network.WEB3_ALCHEMY_PROJECT_ID
        self.RPC_URL = f"{network.RPC_ENDPOINT}{self.WEB3_ALCHEMY_PROJECT_ID}"
        N = self.network
        self.connection = EthereumNetwork(
            network_id=N.NETWORK_ID,
            network_name=N.NETWORK_NAME,
            provider_url=self.RPC_URL,
            provider_name="alchemy",
        )
        self.connection.connect_network(network.IS_INJECT_POA_MIDDLEWARE)
        self.w3 = self.connection.web3
        self.w3_async = self.connection.w3_async

        self.BANCOR_ARBITRAGE_CONTRACT = self.w3.eth.contract(
            address=self.w3.to_checksum_address(N.FASTLANE_CONTRACT_ADDRESS),
            abi=FAST_LANE_CONTRACT_ABI,
        )

        if N.GAS_ORACLE_ADDRESS:
            self.GAS_ORACLE_CONTRACT = self.w3.eth.contract(
                address=N.GAS_ORACLE_ADDRESS,
                abi=GAS_ORACLE_ABI,
            )

        self.ARB_REWARDS_PPM = self.BANCOR_ARBITRAGE_CONTRACT.caller.rewards()[0]


class _ConfigProviderTenderly(ConfigProvider):
    """
    Fastlane bot config -- provider [Tenderly]
    """

    PROVIDER = S.PROVIDER_TENDERLY

    def __init__(self, network: ConfigNetwork, **kwargs):
        super().__init__(network, **kwargs)
        assert (
            self.network.NETWORK == ConfigNetwork.NETWORK_TENDERLY
        ), f"Tenderly only supports Tenderly {self.network}"
        self.RPC_URL = f"https://rpc.tenderly.co/fork/{self.network.TENDERLY_FORK}"

        N = self.network
        self.connection = EthereumNetwork(
            network_id=N.NETWORK_ID,
            network_name=f"{N.NETWORK_NAME}",
            provider_url=self.RPC_URL,
            provider_name="tenderly",
        )
        self.connection.connect_network()
        self.w3 = self.connection.web3

        self.BANCOR_ARBITRAGE_CONTRACT = self.w3.eth.contract(
            address=self.w3.to_checksum_address(N.FASTLANE_CONTRACT_ADDRESS),
            abi=FAST_LANE_CONTRACT_ABI,
        )

        if N.GAS_ORACLE_ADDRESS:
            self.GAS_ORACLE_CONTRACT = self.w3.eth.contract(
                address=N.GAS_ORACLE_ADDRESS,
                abi=GAS_ORACLE_ABI,
            )

        self.ARB_REWARDS_PPM = self.BANCOR_ARBITRAGE_CONTRACT.caller.rewards()[0]


class _ConfigProviderInfura(ConfigProvider):
    """
    Fastlane bot config -- provider [Infura]
    """

    PROVIDER = S.PROVIDER_INFURA

    def __init__(self, network: ConfigNetwork, **kwargs):
        super().__init__(network, **kwargs)
        assert (
            self.network.NETWORK == ConfigNetwork.NETWORK_ETHEREUM
        ), f"Alchemy only supports Ethereum {self.network}"
        raise NotImplementedError("Infura not implemented")


class _ConfigProviderUnitTest(ConfigProvider):
    """
    Fastlane bot config -- provider [UnitTest]
    """

    PROVIDER = S.PROVIDER_UNITTEST

    def __init__(self, network: ConfigNetwork, **kwargs):
        super().__init__(network, **kwargs)
        # assert self.network.NETWORK == ConfigNetwork.NETWORK_ETHEREUM, f"Alchemy only supports Ethereum {self.network}"
        # raise NotImplementedError("Infura not implemented")
        self.connection = None
        self.w3 = None
        self.BANCOR_ARBITRAGE_CONTRACT = None
