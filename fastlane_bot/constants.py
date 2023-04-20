"""
Constants for fastlane_bot package.
Constants are organized as classes to support easier integration for other networks in the future.

(c) Copyright Bprotocol foundation 2023.
Licensed under MIT
"""
import logging
import os
from decimal import *

getcontext().prec = 150
from dataclasses import dataclass

import pandas as pd
from dotenv import load_dotenv

from fastlane_bot.data.abi import *

load_dotenv()

# @formatter:off
# fmt: off
PROJECT_PATH = os.path.normpath(f"{os.getcwd()}")
BASE_PATH = os.path.normpath(f"{PROJECT_PATH}/fastlane_bot")
DATA_PATH = os.path.normpath(f"{BASE_PATH}/data")
COLLECTION_PATH = os.path.normpath(f"{DATA_PATH}/collection")
ARCHIVE_PATH = os.path.normpath(f"{DATA_PATH}/archive")

@dataclass
class EthereumNetworkConstants:
    """Ethereum network Constants"""

    DECIMAL_PRECISION = 76

    # Define a mapping for exchange names and their corresponding IDs and versions
    EXCHANGE_IDS = {
        'bancor_v2': (1, 2),
        'bancor_v3': (2, 3),
        'uniswap_v2': (3, 2),
        'uniswap_v3': (4, 3),
        'sushiswap_v2': (5, 2),
        'carbon_v1': (6, 1),
    }

    # Paths and constants
    PROJECT_PATH: str = PROJECT_PATH
    BASE_PATH: str = BASE_PATH
    DATA_PATH: str = DATA_PATH
    TX_PATH: str = f"{DATA_PATH}/transactions"
    COLLECTION_PATH: str = f"{DATA_PATH}/collection"
    ARCHIVE_PATH: str = f"{DATA_PATH}/archive"
    REPORT_PATH: str = f"{DATA_PATH}/reports"
    TEST_PATH: str = f"{DATA_PATH}/tests"
    PROJECT_PATH: str = PROJECT_PATH
    FAST_LANE_CONTRACT_ABI = FAST_LANE_CONTRACT_ABI
    ERC20_ABI = ERC20_ABI

    # ******* ETHEREUM NETWORK INFO *******
    CHAIN_ID = 1
    MULTICALL_CONTRACT_ADDRESS = "0x5BA1e12693Dc8F9c48aAD8770482f4739bEeD696"
    FASTLANE_CONTRACT_ADDRESS = "0x41Eeba3355d7D6FF628B7982F3F9D055c39488cB"  # proxy

    # Settings
    VERBOSE = "INFO"
    TEST_NETWORK = "tenderly"
    TEST_NETWORK_NAME = "Mainnet (Tenderly)"
    PRODUCTION_NETWORK = "mainnet"
    PRODUCTION_NETWORK_NAME = "Mainnet (Alchemy)"
    DEFAULT_FILETYPE = "csv"
    DEFAULT_BLOCKTIME_DEVIATION = 13 * 35  # 10 block time deviation
    DEFAULT_EXECUTE_MODE = "search_and_execute"
    DEFAULT_RAISEONERROR = False  # TODO: Ensure all errors are caught and handled properly to respect this setting
    DEFAULT_MIN_PROFIT = Decimal("60")
    DEFAULT_MAX_SLIPPAGE = Decimal('1')  # 1%

    DEFAULT_N_JOBS = -1
    DEFAULT_BACKEND = "threading"
    DEFAULT_GAS_PRICE = 0
    DEFAULT_GAS = 950000
    DEFAULT_GAS_SAFETY_OFFSET = 25000
    DEFAULT_GAS_PRICE_OFFSET = 1.05
    DEFAULT_REWARD_PERCENT = Decimal("0.5")

    STAR_PRINT = "*" * 50
    MAX_ROUTE_LENGTH = 3
    TICK_BASE = Decimal("1.0001")
    Q96 = Decimal(str(2 ** 96))
    MAX_LIQUIDITY_CHECK_LOOPS = 1
    MAX_CROSS_TICK_CHECKS = 1
    DEFAULT_SEARCH_DELAY = 5
    DEFAULT_NUM_RETRIES = 3
    MINIMUM_REPORTING_PROFIT = 3

    # ******* CORE ETHEREUM NETWORK TOKENS *******
    ETH_SYMBOL = "ETH"
    BNT_SYMBOL = "BNT"
    WETH_SYMBOL = "WETH"
    ETH_ADDRESS = "0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE"
    BNT_ADDRESS = "0x1F573D6Fb3F13d689FF844B4cE37794d79a7FF1C"
    WETH_ADDRESS = WETH9_ADDRESS = "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2"
    ZERO_ADDRESS = "0x0000000000000000000000000000000000000000"
    ZERO_STRING = "000000000000000000000000"
    ZERO_INT = 000000000000000000000000

    BANCOR_V3_ROUTER_ABI = BANCOR_V3_NETWORK_INFO_ABI

    # SushiSwap
    SUSHISWAP_FACTORY_ABI = SUSHISWAP_FACTORY_ABI
    SUSHISWAP_ROUTER_ABI = SUSHISWAP_ROUTER_ABI
    SUSHISWAP_POOLS_ABI = SUSHISWAP_POOLS_ABI
    SUSHISWAP_FACTORY_ADDRESS = "0xC0AEe478e3658e2610c5F7A4A2E1777cE9e4f2Ac"
    SUSHISWAP_V2_ROUTER_ADDRESS = "0xd9e1cE17f2641f24aE83637ab66a2cca9C378B9F"
    SUSHISWAP_V2_ROUTER_ABI = SUSHISWAP_ROUTER_ABI
    SUSHISWAP_V2_NAME = "sushiswap_v2"
    SUSHISWAP_NAME = "sushiswap_v2"
    SUSHISWAP_VERSIONS = [2]
    SUSHISWAP_TYPES = ["CPMM"]

    # Uniswap
    UNISWAP_V2_FACTORY_ABI = UNISWAP_V2_FACTORY_ABI
    UNISWAP_V2_ROUTER_ABI = UNISWAP_V2_ROUTER_ABI
    UNISWAP_V2_POOL_ABI = UNISWAP_V2_POOL_ABI
    UNISWAP_V3_FACTORY_ABI = UNISWAP_V3_FACTORY_ABI
    UNISWAP_V3_POOL_ABI = UNISWAP_V3_POOL_ABI
    UNISWAP_V3_ROUTER_ABI = UNISWAP_V3_ROUTER_ABI
    UNISWAP_V3_ROUTER2_ABI = UNISWAP_V3_ROUTER2_ABI
    UNISWAP_V3_ROUTER_ADDRESS = "0x68b3465833fb72A70ecDF485E0e4C7bD8665Fc45"
    UNISWAP_V2_FACTORY_ADDRESS = "0x5C69bEe701ef814a2B6a3EDD4B1652CB9cc5aA6f"
    UNISWAP_V2_ROUTER_ADDRESS = "0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D"
    UNISWAP_NAME = "uniswap"
    UNISWAP_VERSIONS = [2, 3]
    UNISWAP_V2_NAME = "uniswap_v2"
    UNISWAP_V3_NAME = "uniswap_v3"

    # Bancor
    BANCOR_NETWORK_ABI = BANCOR_NETWORK_ABI
    BANCOR_V3_NETWORK_INFO_ABI = BANCOR_V3_NETWORK_INFO_ABI
    BANCOR_V2_ROUTER_ABI = BANCOR_V2_ROUTER_ABI
    BANCOR_V2_CONVERTER_ABI = BANCOR_V2_CONVERTER_ABI
    BANCOR_V2_CONTRACT_REGISTRY_ABI = BANCOR_V2_CONTRACT_REGISTRY_ABI
    BANCOR_V2_CONVERTER_REGISTRY_ABI = BANCOR_V2_CONVERTER_REGISTRY_ABI
    BANCOR_V2_POOL_TOKEN_ABI = BANCOR_V2_POOL_TOKEN_ABI
    BANCOR_NAME = "bancor"
    BANCOR_VERSIONS = [2, 3]
    BANCOR_TYPES = ["CPMM", "CPMM"]
    BANCOR_V3_NAME = "bancor_v3"
    BANCOR_V2_NAME = "bancor_v2"
    BANCOR_V3_NETWORK_ADDRESS = "0xeEF417e1D5CC832e619ae18D2F140De2999dD4fB"
    BANCOR_V3_NETWORK_INFO_ADDRESS = "0x8E303D296851B320e6a697bAcB979d13c9D6E760"
    BANCOR_V3_CONVERTER_REGISTRY_ADDRESS = "0x3f5CE5FBFe3E9af3971dD833D26bA9b5C936f0bE"
    BANCOR_V3_ROUTER_ADDRESS = "0x3f5CE5FBFe3E9af3971dD833D26bA9b5C936f0bE"
    BANCOR_V2_NETWORK_ADDRESS = "0x1F573D6Fb3F13d689FF844B4cE37794d79a7FF1C"
    BANCOR_V2_NETWORK_INFO_ADDRESS = "0x1F573D6Fb3F13d689FF844B4cE37794d79a7FF1C"
    BANCOR_V2_ROUTER_ADDRESS = "0x2F9EC37d6CcFFf1caB21733BdaDEdE11c823cCB0"
    BANCOR_V2_CONVERTER_REGISTRY_ADDRESS = "0x52Ae12ABe5D8BD778BD5397F99cA900624CfADD4"
    BANCOR_V2_CONTRACT_REGISTRY_ADDRESS = "0x52Ae12ABe5D8BD778BD5397F99cA900624CfADD4"

    # Carbon
    CARBON_V1_NAME = "carbon_v1"

    # # Environment Variables
    WEB3_ALCHEMY_PROJECT_ID = os.environ.get("WEB3_ALCHEMY_PROJECT_ID")
    ETH_PRIVATE_KEY = os.environ.get("ETH_PRIVATE_KEY_BE_CAREFUL")
    TENDERLY_FORK = os.environ.get("TENDERLY_FORK")
    # Providers
    TENDERLY_FORK_RPC = f"https://rpc.tenderly.co/fork/{TENDERLY_FORK}"
    ETHEREUM_MAINNET_PROVIDER = f"https://eth-mainnet.alchemyapi.io/v2/{WEB3_ALCHEMY_PROJECT_ID}"
    ALCHEMY_API_URL = f"https://eth-mainnet.g.alchemy.com/v2/{WEB3_ALCHEMY_PROJECT_ID}"

    VALID_TENDERLY_NETWORKS = ["tenderly", "tenderly_mainnet"]
    VALID_ETHEREUM_NETWORKS = ["mainnet", "ethereum"]

    def __post_init__(self):
        """
        Note that autopopulated attributes below are usually expected to be derrived from the pairs.parquet file.
        Thus, if you are using a custom pairs.parquet file, you may need to manually set these attributes in the file
        in order to use the library properly.
        """

        # ******* POOL DATA (replaces `lookup_table` dictionary in older code versions) *******
        df = self.DB = pd.read_parquet(f"{DATA_PATH}/pairs.parquet")

        # ******* AUTOMATICALLY DERRIVED FROM DATAFRAME *******
        self.SUPPORTED_EXCHANGES = list(df['exchange_name'].unique())
        self.SUPPORTED_EXCHANGE_VERSIONS = list(df['exchange'].unique())
        self.EXTERNAL_EXCHANGES = [exchange for exchange in self.SUPPORTED_EXCHANGE_VERSIONS if "bancor" not in exchange]
        self.SUPPORTED_TOKENS = list(set(list(df['symbol0'].unique()) + list(df['symbol1'].unique())))
        self.SUPPORTED_PAIRS = list(df['pair'].unique())
        self.SUPPORTED_CONSTANT_FUNCTION_EXCHANGES = list(df[df['exchange_type'] == 'Constant Function Pool']['exchange'].unique())
        self.SUPPORTED_CONSTANT_PRODUCT_EXCHANGES = list(df[df['exchange_type'] == 'Constant Product Pool']['exchange'].unique())
        self.SUPPORTED_EXCHANGE_TYPES = list(df['exchange_type'].unique())
        for exchange in self.SUPPORTED_EXCHANGE_VERSIONS:
            lst = list(set(list(df[df['exchange'] == exchange]['symbol0'].unique()) + list(df[df['exchange'] == exchange]['symbol1'].unique())))
            setattr(self, f'{exchange.upper()}_SUPPORTED_TOKENS', lst)
            setattr(self, f'{exchange.upper()}_SUPPORTED_PAIRS', list(df[df['exchange'] == exchange]['pair'].unique()))

        self.EXCHANGE_ID_MAP = {df['exchange'].values[i]: df['exchange_id'].values[i] for i in range(len(df))}
        self.EXCHANGE_ID_MAP[self.BANCOR_V3_NAME] = 0
        self.EXCHANGE_ID_MAP[self.CARBON_V1_NAME] = 5
        self.ADDRESS_FROM_SYMBOL = {
            df[f'symbol{j}'].values[i]: df[f'address{j}'].values[i]
            for i in range(len(df)) for j in range(2)
        }
        self.DECIMAL_FROM_SYMBOL = {
            df[f'symbol{j}'].values[i]: df[f'decimal{j}'].values[i]
            for i in range(len(df)) for j in range(2)
        }
        self.SYMBOL_FROM_ADDRESS = {
            df[f'address{j}'].values[i]: df[f'symbol{j}'].values[i]
            for i in range(len(df)) for j in range(2)
        }

        self.ROUTER_FROM_EXCHANGE_VERSIONS = {f'{exchange.upper()}_ROUTER_ADDRESS': self.__getattribute__(f'{exchange.upper()}_ROUTER_ADDRESS') for exchange in self.SUPPORTED_EXCHANGE_VERSIONS if f'{exchange.upper()}_ROUTER_ADDRESS' in self.__dict__}
        self.ROUTER_ABI_FROM_EXCHANGE_VERSIONS = {f'{exchange.upper()}_ROUTER_ABI': self.__getattribute__(f'{exchange.upper()}_ROUTER_ABI') for exchange in self.SUPPORTED_EXCHANGE_VERSIONS if f'{exchange.upper()}_ROUTER_ABI' in self.__dict__}
        self.BANCOR_BASE = self.BANCOR_V3_NAME
        self.DEFAULT_LOGGER = get_logger(self.VERBOSE)


def get_logger(verbose: str = "INFO") -> logging.Logger:
    """
    Returns a logger with the specified logging level
    """
    LOGGING_MAP = {
        "INFO": logging.INFO,
        "DEBUG": logging.DEBUG,
        "WARNING": logging.WARNING,
        "ERROR": logging.ERROR,
    }
    LOGGING_LEVEL = LOGGING_MAP[verbose.upper()]
    logger = logging.getLogger("fastlane_bot")
    logger.setLevel(LOGGING_LEVEL)
    handler = logging.StreamHandler()
    handler.setLevel(LOGGING_LEVEL)
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger


ec = EthereumNetworkConstants()

# @formatter:on
# fmt: on
