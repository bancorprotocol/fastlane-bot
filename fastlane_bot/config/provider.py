"""
Fastlane bot config -- provider
"""
__VERSION__ = "0.9.1"
__DATE__ = "30/Apr 2023"

from web3.contract import Contract

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
)

ETH_PRIVATE_KEY_BE_CAREFUL = os.environ.get("ETH_PRIVATE_KEY_BE_CAREFUL")
#WEB3_ALCHEMY_PROJECT_ID = os.environ.get("WEB3_ALCHEMY_PROJECT_ID")

class ConfigProvider(ConfigBase):
    """
    Fastlane bot config -- provider
    """
    __VERSION__=__VERSION__
    __DATE__=__DATE__
    
    RPC_URL = None # set in derived class init
    
    PROVIDER_DEFAULT = S.PROVIDER_DEFAULT
    PROVIDER_INFURA = S.PROVIDER_INFURA
    PROVIDER_ALCHEMY = S.PROVIDER_ALCHEMY
    PROVIDER_TENDERLY = S.PROVIDER_TENDERLY
    PROVIDER_UNITTEST = S.PROVIDER_UNITTEST
    ETH_PRIVATE_KEY_BE_CAREFUL = ETH_PRIVATE_KEY_BE_CAREFUL
    #WEB3_ALCHEMY_PROJECT_ID = WEB3_ALCHEMY_PROJECT_ID


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
        self.ARB_CONTRACT_VERSION = None
        self.BANCOR_ARBITRAGE_CONTRACT = None
        self.network = network

    def check_version_of_arb_contract(self):
        if self.BANCOR_ARBITRAGE_CONTRACT is not None:
            try:
                self.ARB_CONTRACT_VERSION = self.BANCOR_ARBITRAGE_CONTRACT.caller.version()
            except Exception as e:
                # Failed to get latest version of arbitrage contract
                print(f"Failed to get latest version of arbitrage contract due to exception: {e}")

class _ConfigProviderAlchemy(ConfigProvider):
    """
    Fastlane bot config -- provider [Alchemy]
    """
    PROVIDER = S.PROVIDER_ALCHEMY
    #WEB3_ALCHEMY_PROJECT_ID = WEB3_ALCHEMY_PROJECT_ID
    
    def __init__(self, network: ConfigNetwork, **kwargs):
        super().__init__(network, **kwargs)
        #assert self.network.NETWORK == ConfigNetwork.NETWORK_ETHEREUM, f"Alchemy only supports Ethereum {self.network}"
        self.WEB3_ALCHEMY_PROJECT_ID = network.WEB3_ALCHEMY_PROJECT_ID
        self.RPC_URL = f"{network.RPC_ENDPOINT}{self.WEB3_ALCHEMY_PROJECT_ID}"
        N = self.network
        self.connection = EthereumNetwork(
            network_id=N.NETWORK_ID,
            network_name=f"{N.NETWORK_NAME} (Alchemy)",
            provider_url=self.RPC_URL,
            provider_name="alchemy",
        )
        self.connection.connect_network()
        self.w3 = self.connection.web3
        self.LOCAL_ACCOUNT = self.w3.eth.account.from_key(ETH_PRIVATE_KEY_BE_CAREFUL)


        if network.NETWORK in [N.NETWORK_BASE, N.NETWORK_ETHEREUM]:
            self.CARBON_CONTROLLER_CONTRACT = self.w3.eth.contract(
                address=network.CARBON_CONTROLLER_ADDRESS,
                abi=CARBON_CONTROLLER_ABI,
            )
            self.BANCOR_ARBITRAGE_CONTRACT = self.w3.eth.contract(
                address=self.w3.toChecksumAddress(network.FASTLANE_CONTRACT_ADDRESS),
                abi=FAST_LANE_CONTRACT_ABI,
            )


        if network.NETWORK in N.NETWORK_ETHEREUM:
            self.BANCOR_NETWORK_INFO_CONTRACT = self.w3.eth.contract(
                address=network.BANCOR_V3_NETWORK_INFO_ADDRESS,
                abi=BANCOR_V3_NETWORK_INFO_ABI,
            )
            self.ARB_CONTRACT_VERSION = self.BANCOR_ARBITRAGE_CONTRACT.caller.version()

        else:
            self.CARBON_CONTROLLER_CONTRACT = None
            self.ARB_CONTRACT_VERSION = 10

        if self.BANCOR_ARBITRAGE_CONTRACT is not None:
            try:
                reward_percent, max_profit = self.BANCOR_ARBITRAGE_CONTRACT.caller.rewards()
                self.ARB_REWARD_PERCENTAGE = str(int(reward_percent) / 1000000)
                self.ARB_MAX_PROFIT = 1000000 # This is no longer used
            except:
                self.ARB_REWARD_PERCENTAGE = "0.5"
        else:
            self.ARB_REWARD_PERCENTAGE = "0.5"
            
        self.EXPECTED_GAS_MODIFIER = "0.85"
class _ConfigProviderTenderly(ConfigProvider):
    """
    Fastlane bot config -- provider [Tenderly]
    """
    PROVIDER = S.PROVIDER_TENDERLY
    
    def __init__(self, network: ConfigNetwork, **kwargs):
        super().__init__(network, **kwargs)
        assert self.network.NETWORK == ConfigNetwork.NETWORK_TENDERLY, f"Tenderly only supports Tenderly {self.network}"
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
        self.LOCAL_ACCOUNT = self.w3.eth.account.from_key(ETH_PRIVATE_KEY_BE_CAREFUL)

        self.BANCOR_NETWORK_INFO_CONTRACT = self.w3.eth.contract(
            address=N.BANCOR_V3_NETWORK_INFO_ADDRESS,
            abi=BANCOR_V3_NETWORK_INFO_ABI,
        )
        self.CARBON_CONTROLLER_CONTRACT = self.w3.eth.contract(
            address=N.CARBON_CONTROLLER_ADDRESS,
            abi=CARBON_CONTROLLER_ABI,
        )
        self.BANCOR_ARBITRAGE_CONTRACT = self.w3.eth.contract(
            address=self.w3.toChecksumAddress(N.FASTLANE_CONTRACT_ADDRESS),
            abi=FAST_LANE_CONTRACT_ABI,
        )
        self.ARB_CONTRACT_VERSION = self.BANCOR_ARBITRAGE_CONTRACT.caller.version()

        reward_percent, max_profit = self.BANCOR_ARBITRAGE_CONTRACT.caller.rewards()

        self.ARB_REWARD_PERCENTAGE = str(int(reward_percent) / 1000000)
        self.ARB_MAX_PROFIT = str(int(max_profit) / (10 ** 18))

    
class _ConfigProviderInfura(ConfigProvider):
    """
    Fastlane bot config -- provider [Infura]
    """
    PROVIDER = S.PROVIDER_INFURA
    
    def __init__(self, network: ConfigNetwork, **kwargs):
        super().__init__(network, **kwargs)
        assert self.network.NETWORK == ConfigNetwork.NETWORK_ETHEREUM, f"Alchemy only supports Ethereum {self.network}"
        raise NotImplementedError("Infura not implemented")

class _ConfigProviderUnitTest(ConfigProvider):
    """
    Fastlane bot config -- provider [UnitTest]
    """
    PROVIDER = S.PROVIDER_UNITTEST
    
    def __init__(self, network: ConfigNetwork, **kwargs):
        super().__init__(network, **kwargs)
        #assert self.network.NETWORK == ConfigNetwork.NETWORK_ETHEREUM, f"Alchemy only supports Ethereum {self.network}"
        #raise NotImplementedError("Infura not implemented")
        self.connection = None
        self.w3 = None
        self.BANCOR_NETWORK_INFO_CONTRACT = None
        self.CARBON_CONTROLLER_CONTRACT = None
        self.BANCOR_ARBITRAGE_CONTRACT = None
        

    
