"""
Fastlane bot config -- network
"""
__VERSION__ = "1.0.3-RESTRICTED"
__DATE__ = "02/May 2023"

from .base import ConfigBase
from . import selectors as S

import os
from dotenv import load_dotenv

load_dotenv()

from decimal import Decimal

from dotenv import load_dotenv

load_dotenv()  # take environment variables from .env.

TENDERLY_FORK = os.environ.get("TENDERLY_FORK_ID")
mp = os.environ.get("DEFAULT_MIN_PROFIT_BNT")
DEFAULT_MIN_PROFIT_BNT = Decimal('1')


class ConfigNetwork(ConfigBase):
    """
    Fastlane bot config -- network
    """
    __VERSION__ = __VERSION__
    __DATE__ = __DATE__

    # COMMONLY USED TOKEN ADDRESSES SECTION
    #######################################################################################
    ZERO_ADDRESS = "0x0000000000000000000000000000000000000000"
    USDC_ADDRESS = "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48"
    MKR_ADDRESS = "0x9f8F72aA9304c8B593d555F12eF6589cC3A579A2"
    LINK_ADDRESS = "0x514910771AF9Ca656af840dff83E8264EcF986CA"
    WBTC_ADDRESS = "0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599"
    ETH_ADDRESS = "0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE"
    BNT_ADDRESS = "0x1F573D6Fb3F13d689FF844B4cE37794d79a7FF1C"
    WETH_ADDRESS = WETH9_ADDRESS = "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2"

    # ACCOUNTS SECTION
    #######################################################################################
    BINANCE8_WALLET_ADDRESS = "0xF977814e90dA44bFA03b6295A0616a897441aceC"
    BINANCE14_WALLET_ADDRESS = "0x28c6c06298d514db089934071355e5743bf21d60"

    # EXCHANGE IDENTIFIERS SECTION
    #######################################################################################
    BANCOR_V2_NAME = "bancor_v2"
    BANCOR_V3_NAME = "bancor_v3"
    UNISWAP_V2_NAME = "uniswap_v2"
    UNISWAP_V3_NAME = "uniswap_v3"
    SUSHISWAP_V2_NAME = "sushiswap_v2"
    CARBON_V1_NAME = "carbon_v1"
    EXCHANGE_IDS = {
        CARBON_V1_NAME: 6,
        UNISWAP_V2_NAME: 3,
        UNISWAP_V3_NAME: 4,
        BANCOR_V2_NAME: 1,
        BANCOR_V3_NAME: 2,
        SUSHISWAP_V2_NAME: 5,
    }
    UNIV2_FORKS = [UNISWAP_V2_NAME, SUSHISWAP_V2_NAME]
    SUPPORTED_EXCHANGES = list(EXCHANGE_IDS)

    # CARBON EVENTS
    #######################################################################################
    CARBON_POOL_CREATED = f"{CARBON_V1_NAME}_PoolCreated"
    CARBON_STRATEGY_CREATED = f"{CARBON_V1_NAME}_StrategyCreated"
    CARBON_STRATEGY_DELETED = f"{CARBON_V1_NAME}_StrategyDeleted"
    CARBON_STRATEGY_UPDATED = f"{CARBON_V1_NAME}_StrategyUpdated"
    CARBON_TOKENS_TRADED = f"{CARBON_V1_NAME}_TokensTraded"

    # DEFAULT VALUES SECTION
    #######################################################################################
    UNIV3_FEE_LIST = [100, 500, 3000, 10000]
    MIN_BNT_LIQUIDITY = 2_000_000_000_000_000_000
    DEFAULT_GAS = 950_000
    DEFAULT_GAS_PRICE = 0
    DEFAULT_GAS_PRICE_OFFSET = 1.09
    DEFAULT_GAS_SAFETY_OFFSET = 25_000
    DEFAULT_POLL_INTERVAL = 12
    DEFAULT_BLOCKTIME_DEVIATION = 13 * 500  # 10 block time deviation
    DEFAULT_MIN_PROFIT = DEFAULT_MIN_PROFIT_BNT
    DEFAULT_MIN_PROFIT_BNT = DEFAULT_MIN_PROFIT_BNT
    DEFAULT_MAX_SLIPPAGE = Decimal("1")  # 1%
    _PROJECT_PATH = os.path.normpath(f"{os.getcwd()}")  # TODO: FIX THIS
    DEFAULT_CURVES_DATAFILE = os.path.normpath(f"{_PROJECT_PATH}/carbon/data/curves.csv.gz")
    CARBON_STRATEGY_CHUNK_SIZE = 200
    Q96 = Decimal("2") ** Decimal("96")
    DEFAULT_TIMEOUT = 60
    CARBON_FEE = Decimal("0.002")
    BANCOR_V3_FEE = Decimal("0.0")
    DEFAULT_REWARD_PERCENT = Decimal("0.5")

    # SUNDRY SECTION
    #######################################################################################
    COINGECKO_URL = "https://tokens.coingecko.com/uniswap/all.json"

    NETWORK_ETHEREUM = S.NETWORK_ETHEREUM
    NETWORK_MAINNET = S.NETWORK_MAINNET
    NETWORK_TENDERLY = S.NETWORK_TENDERLY

    @classmethod
    def new(cls, network=None):
        """
        Return a new ConfigNetworkes object for the specified network.
        """
        if network is None:
            network = cls.NETWORK_ETHEREUM
        if network == cls.NETWORK_ETHEREUM:
            return _ConfigNetworkMainnet(_direct=False)
        elif network == cls.NETWORK_TENDERLY:
            return _ConfigNetworkTenderly(_direct=False)
        else:
            raise ValueError(f"Invalid network: {network}")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class _ConfigNetworkMainnet(ConfigNetwork):
    """
    Fastlane bot config -- network [Ethereum Mainnet]
    """

    NETWORK = S.NETWORK_ETHEREUM
    NETWORK_ID = "mainnet"
    NETWORK_NAME = "Ethereum Mainnet"
    DEFAULT_PROVIDER = S.PROVIDER_ALCHEMY

    # FACTORY, CONVERTER, AND CONTROLLER ADDRESSES
    #######################################################################################
    BANCOR_V3_NETWORK_INFO_ADDRESS = "0x8E303D296851B320e6a697bAcB979d13c9D6E760"
    UNISWAP_V2_FACTORY_ADDRESS = "0x5C69bEe701ef814a2B6a3EDD4B1652CB9cc5aA6f"
    UNISWAP_V2_ROUTER_ADDRESS = "0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D"
    SUSHISWAP_FACTORY_ADDRESS = "0xC0AEe478e3658e2610c5F7A4A2E1777cE9e4f2Ac"
    UNISWAP_V3_FACTORY_ADDRESS = "0x1F98431c8aD98523631AE4a59f267346ea31F984"
    BANCOR_V3_POOL_COLLECTOR_ADDRESS = "0xB67d563287D12B1F41579cB687b04988Ad564C6C"
    BANCOR_V2_CONVERTER_REGISTRY_ADDRESS = "0xC0205e203F423Bcd8B2a4d6f8C8A154b0Aa60F19"
    FASTLANE_CONTRACT_ADDRESS = "0x41Eeba3355d7D6FF628B7982F3F9D055c39488cB"
    CARBON_CONTROLLER_ADDRESS = "0xC537e898CD774e2dCBa3B14Ea6f34C93d5eA45e1"
    CARBON_CONTROLLER_VOUCHER = "0x3660F04B79751e31128f6378eAC70807e38f554E"
    MULTICALL_CONTRACT_ADDRESS = "0x5BA1e12693Dc8F9c48aAD8770482f4739bEeD696"


class _ConfigNetworkTenderly(ConfigNetwork):
    """
    Fastlane bot config -- network [Ethereum Tenderly]
    """

    NETWORK = S.NETWORK_TENDERLY
    DEFAULT_PROVIDER = S.PROVIDER_TENDERLY
    NETWORK_ID = S.NETWORK_TENDERLY
    NETWORK_NAME = "tenderly"
    TENDERLY_FORK = TENDERLY_FORK

    # FACTORY, CONVERTER, AND CONTROLLER ADDRESSES
    #######################################################################################
    BANCOR_V3_NETWORK_INFO_ADDRESS = "0x8E303D296851B320e6a697bAcB979d13c9D6E760"
    UNISWAP_V2_FACTORY_ADDRESS = "0x5C69bEe701ef814a2B6a3EDD4B1652CB9cc5aA6f"
    UNISWAP_V2_ROUTER_ADDRESS = "0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D"
    SUSHISWAP_FACTORY_ADDRESS = "0xC0AEe478e3658e2610c5F7A4A2E1777cE9e4f2Ac"
    UNISWAP_V3_FACTORY_ADDRESS = "0x1F98431c8aD98523631AE4a59f267346ea31F984"
    BANCOR_V3_POOL_COLLECTOR_ADDRESS = "0xB67d563287D12B1F41579cB687b04988Ad564C6C"
    BANCOR_V2_CONVERTER_REGISTRY_ADDRESS = "0xC0205e203F423Bcd8B2a4d6f8C8A154b0Aa60F19"
    FASTLANE_CONTRACT_ADDRESS = "0x41Eeba3355d7D6FF628B7982F3F9D055c39488cB"
    CARBON_CONTROLLER_ADDRESS = "0xC537e898CD774e2dCBa3B14Ea6f34C93d5eA45e1"
    CARBON_CONTROLLER_VOUCHER = "0x3660F04B79751e31128f6378eAC70807e38f554E"
    MULTICALL_CONTRACT_ADDRESS = "0x5BA1e12693Dc8F9c48aAD8770482f4739bEeD696"

    def shellcommand(self, chain_id=1):
        """
        the shell command to run to allow the bot to connect to tenderly
        """
        s = f'brownie networks delete {self.NETWORK_NAME}\n'
        s += f'brownie networks add "Ethereum" "{self.NETWORK_NAME}" '
        s += f'host=https://rpc.tenderly.co/fork/{self.TENDERLY_FORK} chainid={chain_id}'
        return s

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
