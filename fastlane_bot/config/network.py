"""
Network configuration (defines the ``ConfigNetwork`` class)

Used to configure the network for the fastlane bot.

---
(c) Copyright Bprotocol foundation 2023-24.
All rights reserved.
Licensed under MIT.
"""
__VERSION__ = "1.0.3-RESTRICTED"
__DATE__ = "02/May 2023"

import os
from typing import List, Dict

import pandas as pd
from dotenv import load_dotenv

from . import selectors as S
from .base import ConfigBase
from .constants import CARBON_V1_NAME
load_dotenv()

from decimal import Decimal

from dotenv import load_dotenv

load_dotenv()  # take environment variables from .env.

TENDERLY_FORK = os.environ.get("TENDERLY_FORK_ID")


def get_multichain_addresses(network: str):
    """
    Create dataframe of addresses for the selected network
    :param network: the network in which to get addresses

    returns:
    A dataframe that contains items from the selected network
    """
    multichain_address_path = os.path.normpath(
        "fastlane_bot/data/multichain_addresses.csv"
    )
    chain_addresses_df = pd.read_csv(multichain_address_path)
    network_df = chain_addresses_df.loc[chain_addresses_df["chain"] == network]
    return network_df


def get_fork_map(df: pd.DataFrame, fork_name: str) -> Dict:
    """
    Get a Dict of exchange_name : router
    :param df: the dataframe containing exchange details
    :param fork_name: the fork name

    returns: Dict containing: exchange_name : router_address

    """
    fork_map = {}
    for row in df.iterrows():
        exchange_name = row[1]["exchange_name"]
        fork = row[1]["fork"]
        factory_address = row[1]["factory_address"]
        router_address = row[1]["router_address"]
        if fork in fork_name:
            fork_map[exchange_name] = router_address
    return fork_map


def get_factory_map(df: pd.DataFrame, fork_names: [str]) -> Dict:
    """
    Get a Dict of factory : exchange name
    :param df: the dataframe containing exchange details
    :param fork_names: the list of fork names

    returns: Dict containing: factory_address : exchange_name

    """
    fork_map = {}
    for row in df.iterrows():
        exchange_name = row[1]["exchange_name"]
        fork = row[1]["fork"]
        factory_address = row[1]["factory_address"]
        router_address = row[1]["router_address"]
        if fork in fork_names:
            fork_map[factory_address] = exchange_name
            fork_map[exchange_name] = factory_address
    return fork_map

def get_fee_map(df: pd.DataFrame, fork_name: str) -> Dict:
    """
    Get a Dict of exchange_name : router
    :param df: the dataframe containing exchange details
    :param fork_name: the fork name

    returns: Dict containing: exchange_name : router_address

    """
    fork_map = {}
    for row in df.iterrows():
        exchange_name = row[1]["exchange_name"]
        fork = row[1]["fork"]
        fee = row[1]["fee"]
        if fork in fork_name:
            fork_map[exchange_name] = fee
    return fork_map


def get_row_from_address(address: str, df: pd.DataFrame) -> pd.DataFrame:
    if df["router_address"].isin([address]).any():
        return df[df["router_address"] == address]
    elif df["factory_address"].isin([address]).any():
        return df[df["factory_address"] == address]
    return None


def get_exchange_from_address(address: str, df: pd.DataFrame) -> str or None:
    row = get_row_from_address(address=address, df=df)
    if row is None:
        return None
    return row["exchange_name"].values[0]


def get_items_from_exchange(
    item_names: List[str],
    exchange_name: str,
    fork: str,
    df: pd.DataFrame,
) -> List[str or float]:
    df_ex = df[
        (df["exchange_name"] == exchange_name)
        & (df["fork"] == fork)
    ]
    if len(df_ex.index) == 0:
        return None
    items_to_return = []
    for item in item_names:
        items_to_return.append(df_ex[item].values[0])
    return items_to_return


def get_router_address_for_exchange(
    exchange_name: str, fork: str, df: pd.DataFrame
) -> str:
    router_address = get_items_from_exchange(
        item_names=["router_address"],
        exchange_name=exchange_name,
        fork=fork,
        df=df,
    )
    if router_address is None:
        raise ExchangeInfoNotFound(
            f"Router address could not be found for exchange: {exchange_name}, fork of: {fork}. Exchange must be mapped in fastlane_bot/data/multichain_addresses.csv"
        )
    return router_address[0]


def get_fee_for_exchange(
    exchange_name: str, fork: str, df: pd.DataFrame
) -> float or None:
    exchange_fee = get_items_from_exchange(
        item_names=["fee"],
        exchange_name=exchange_name,
        fork=fork,
        df=df,
    )
    if exchange_fee is None:
        raise ExchangeInfoNotFound(
            f"Fee could not be found for exchange: {exchange_name}, fork of: {fork}. Exchange must be mapped in fastlane_bot/data/multichain_addresses.csv"
        )
    return exchange_fee[0]


class ExchangeInfoNotFound(AssertionError):
    pass


class ConfigNetwork(ConfigBase):
    """
    Fastlane bot config -- network
    """

    __VERSION__ = __VERSION__
    __DATE__ = __DATE__
    # COMMONLY USED TOKEN ADDRESSES SECTION
    #######################################################################################
    ZERO_ADDRESS = "0x0000000000000000000000000000000000000000"
    ETH_ADDRESS = "0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE"
    USDC_ADDRESS = "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48"
    MKR_ADDRESS = "0x9f8F72aA9304c8B593d555F12eF6589cC3A579A2"
    LINK_ADDRESS = "0x514910771AF9Ca656af840dff83E8264EcF986CA"
    WBTC_ADDRESS = "0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599"
    BNT_ADDRESS = "0x1F573D6Fb3F13d689FF844B4cE37794d79a7FF1C"
    USDT_ADDRESS = "0xdAC17F958D2ee523a2206206994597C13D831ec7"
    WETH_ADDRESS = WETH9_ADDRESS = "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2"

    TAX_TOKENS = set([])

    # BNT_KEY = "BNT-FF1C"
    # ETH_KEY = "ETH-EEeE"
    # WBTC_KEY = "WBTC-c599"
    # USDC_KEY = "USDC-eB48"
    # LINK_KEY = "LINK-86CA"
    # USDT_KEY = "USDT-1ec7"
    SELF_FUND = False

    # ACCOUNTS SECTION
    #######################################################################################
    BINANCE8_WALLET_ADDRESS = "0xF977814e90dA44bFA03b6295A0616a897441aceC"
    BINANCE14_WALLET_ADDRESS = "0x28C6c06298d514Db089934071355E5743bf21d60"

    # EXCHANGE IDENTIFIERS SECTION
    #######################################################################################
    BANCOR_V2_NAME = "bancor_v2"
    BANCOR_V3_NAME = "bancor_v3"
    CARBON_POL_NAME = "bancor_pol"
    UNISWAP_V2_NAME = "uniswap_v2"
    UNISWAP_V3_NAME = "uniswap_v3"
    SUSHISWAP_V2_NAME = "sushiswap_v2"
    SUSHISWAP_V3_NAME = "sushiswap_v3"
    CARBON_V1_NAME = CARBON_V1_NAME
    BANCOR_POL_NAME = "bancor_pol"
    BALANCER_NAME = "balancer"
    PANCAKESWAP_V2_NAME = "pancakeswap_v2"
    PANCAKESWAP_V3_NAME = "pancakeswap_v3"
    SOLIDLY_V2_NAME = "solidly_v2"
    VELODROME_V2_NAME = "velodrome_v2"
    AERODROME_V2_NAME = "aerodrome_v2"
    VELOCIMETER_V2_NAME = "velocimeter_v2"
    XFAI_V0_NAME = "xfai_v0"

    WRAP_UNWRAP_NAME = "wrap_or_unwrap"

    GAS_ORACLE_ADDRESS = None

    MULTICALLABLE_EXCHANGES = [BANCOR_V3_NAME, BANCOR_POL_NAME, BALANCER_NAME]
    # BANCOR POL
    BANCOR_POL_START_BLOCK = 18184448
    BANCOR_POL_ADDRESS = "0xD06146D292F9651C1D7cf54A3162791DFc2bEf46"

    # CARBON EVENTS
    #######################################################################################
    CARBON_POOL_CREATED = f"{CARBON_V1_NAME}_PoolCreated"
    CARBON_STRATEGY_CREATED = f"{CARBON_V1_NAME}_StrategyCreated"
    CARBON_STRATEGY_DELETED = f"{CARBON_V1_NAME}_StrategyDeleted"
    CARBON_STRATEGY_UPDATED = f"{CARBON_V1_NAME}_StrategyUpdated"
    CARBON_TOKENS_TRADED = f"{CARBON_V1_NAME}_TokensTraded"

    # POOL IDENTIFIERS SECTION
    #######################################################################################
    POOL_TYPE_STABLE = "stable"
    POOL_TYPE_VOLATILE = "volatile"

    # DEFAULT VALUES SECTION
    #######################################################################################
    DEFAULT_GAS_SAFETY_OFFSET = 25_000
    DEFAULT_BLOCKTIME_DEVIATION = 13 * 500 * 100  # 10 block time deviation
    _PROJECT_PATH = os.path.normpath(f"{os.getcwd()}")  # TODO: FIX THIS
    Q96 = Decimal("2") ** Decimal("96")
    LIMIT_BANCOR3_FLASHLOAN_TOKENS = True
    DEFAULT_MIN_PROFIT_GAS_TOKEN = Decimal("0.02")

    IS_INJECT_POA_MIDDLEWARE = False
    # SUNDRY SECTION
    #######################################################################################
    COINGECKO_URL = "https://tokens.coingecko.com/uniswap/all.json"

    NETWORK_ETHEREUM = S.NETWORK_ETHEREUM
    NETWORK_MAINNET = S.NETWORK_MAINNET
    NETWORK_TENDERLY = S.NETWORK_TENDERLY
    NETWORK_BASE = S.NETWORK_BASE
    NETWORK_ARBITRUM = S.NETWORK_ARBITRUM
    NETWORK_POLYGON = S.NETWORK_POLYGON
    NETWORK_POLYGON_ZKEVM = S.NETWORK_POLYGON_ZKEVM
    NETWORK_OPTIMISM = S.NETWORK_OPTIMISM
    NETWORK_FANTOM = S.NETWORK_FANTOM
    NETWORK_MANTLE = S.NETWORK_MANTLE
    NETWORK_LINEA = S.NETWORK_LINEA
    NETWORK_SEI = S.NETWORK_SEI

    # FLAGS
    #######################################################################################
    IS_NO_FLASHLOAN_AVAILABLE = False

    # HOOKS
    #######################################################################################
    @staticmethod
    def gas_strategy(web3, avoid_max_priority_fee=False):
        gas_price = web3.eth.gas_price # send `eth_gasPrice` request
        max_priority_fee = 0
        if not avoid_max_priority_fee:
            max_priority_fee = web3.eth.max_priority_fee # send `eth_maxPriorityFeePerGas` request
        
        return {
            "maxFeePerGas": gas_price + max_priority_fee,
            "maxPriorityFeePerGas": max_priority_fee
        }

    @classmethod
    def new(cls, network=None):
        """
        Return a new ConfigNetworkes object for the specified network.
        """
        if network is None:
            network = cls.NETWORK_ETHEREUM
        if network == cls.NETWORK_ETHEREUM:
            return _ConfigNetworkMainnet(_direct=False)
        elif network == cls.NETWORK_BASE:
            return _ConfigNetworkBase(_direct=False)
        elif network == cls.NETWORK_ARBITRUM:
            return _ConfigNetworkArbitrumOne(_direct=False)
        elif network == cls.NETWORK_POLYGON:
            return _ConfigNetworkPolygon(_direct=False)
        elif network == cls.NETWORK_POLYGON_ZKEVM:
            return _ConfigNetworkPolygonZkevm(_direct=False)
        elif network == cls.NETWORK_OPTIMISM:
            return _ConfigNetworkOptimism(_direct=False)
        elif network == cls.NETWORK_FANTOM:
            return _ConfigNetworkFantom(_direct=False)
        elif network == cls.NETWORK_MANTLE:
            return _ConfigNetworkMantle(_direct=False)
        elif network == cls.NETWORK_LINEA:
            return _ConfigNetworkLinea(_direct=False)  
        elif network == cls.NETWORK_SEI:
            return _ConfigNetworkSei(_direct=False)    
        elif network == cls.NETWORK_TENDERLY:
            return _ConfigNetworkTenderly(_direct=False)
        else:
            raise ValueError(f"Invalid network: {network}")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.__post_init__()

    def __post_init__(self):
        assert self.NETWORK is not None

        network = self.NETWORK if "tenderly" not in self.NETWORK else "ethereum"
        self.network_df = get_multichain_addresses(network=network)

        self.UNI_V2_ROUTER_MAPPING = get_fork_map(
            df=self.network_df, fork_name=S.UNISWAP_V2
        )
        self.UNI_V2_FEE_MAPPING = get_fee_map(
            df=self.network_df, fork_name=S.UNISWAP_V2
        )
        self.UNI_V3_ROUTER_MAPPING = get_fork_map(
            df=self.network_df, fork_name=S.UNISWAP_V3
        )
        self.SOLIDLY_FEE_MAPPING = get_fee_map(df=self.network_df, fork_name=S.SOLIDLY_V2)
        self.UNI_V2_FORKS = [key for key in self.UNI_V2_ROUTER_MAPPING.keys()] + [
            "uniswap_v2"
        ]
        self.UNI_V3_FORKS = [key for key in self.UNI_V3_ROUTER_MAPPING.keys()]

        self.SOLIDLY_V2_ROUTER_MAPPING = get_fork_map(
            df=self.network_df, fork_name=S.SOLIDLY_V2
        )
        self.SOLIDLY_V2_FORKS = [key for key in self.SOLIDLY_V2_ROUTER_MAPPING.keys()]
        self.CARBON_CONTROLLER_MAPPING = get_fork_map(
            df=self.network_df, fork_name=CARBON_V1_NAME
        )
        self.CARBON_V1_FORKS = [key for key in self.CARBON_CONTROLLER_MAPPING.keys()]

        self.ALL_FORK_NAMES = self.UNI_V2_FORKS + self.UNI_V3_FORKS + self.SOLIDLY_V2_FORKS + self.CARBON_V1_FORKS
        self.ALL_FORK_NAMES_WITHOUT_CARBON = self.UNI_V2_FORKS + self.UNI_V3_FORKS + self.SOLIDLY_V2_FORKS
        self.FACTORY_MAPPING = get_factory_map(df=self.network_df, fork_names=[S.UNISWAP_V2, S.UNISWAP_V3, S.SOLIDLY_V2])

        self.CHAIN_SPECIFIC_EXCHANGES = (
            self.CHAIN_SPECIFIC_EXCHANGES
            + [ex for ex in self.UNI_V2_ROUTER_MAPPING.keys()]
            + [ex for ex in self.UNI_V3_ROUTER_MAPPING.keys()]
            + [ex for ex in self.SOLIDLY_V2_ROUTER_MAPPING.keys()]
            + [ex for ex in self.CARBON_CONTROLLER_MAPPING.keys()]
            + ["balancer" if self.BALANCER_VAULT_ADDRESS is not None else None]
        )
        self.CHAIN_SPECIFIC_EXCHANGES = [
            ex for ex in self.CHAIN_SPECIFIC_EXCHANGES if ex is not None
        ]
        self.ALL_KNOWN_EXCHANGES = list(set(self.ALL_FORK_NAMES + self.CHAIN_SPECIFIC_EXCHANGES))

        self.EXCHANGE_IDS = {
            self.BANCOR_V2_NAME: 1,
            self.BANCOR_V3_NAME: 2,
            self.BALANCER_NAME: 7,
            self.CARBON_POL_NAME: 8,
            self.WRAP_UNWRAP_NAME: 10,
            self.UNISWAP_V2_NAME: 3,
            self.UNISWAP_V3_NAME: 4,
            self.SOLIDLY_V2_NAME: 11,
            self.AERODROME_V2_NAME: 12,
            self.XFAI_V0_NAME: 13,
            self.CARBON_V1_NAME: 6,
        }
        for ex in self.UNI_V2_FORKS:
            self.EXCHANGE_IDS[ex] = 3
        for ex in self.UNI_V3_FORKS:
            self.EXCHANGE_IDS[ex] = 4
        for ex in self.CARBON_V1_FORKS:
            self.EXCHANGE_IDS[ex] = 6
        for ex in self.SOLIDLY_V2_FORKS:
            if ex in [self.AERODROME_V2_NAME, self.VELODROME_V2_NAME]:
                self.EXCHANGE_IDS[ex] = 12
            elif ex == self.XFAI_V0_NAME:
                self.EXCHANGE_IDS[ex] = 13
            else:
                self.EXCHANGE_IDS[ex] = 11
        self.SUPPORTED_EXCHANGES = list(self.EXCHANGE_IDS)


    def exchange_name_base_from_fork(self, exchange_name):
        if exchange_name in self.UNI_V2_FORKS:
            exchange_name = "uniswap_v2"
        elif exchange_name in self.UNI_V3_FORKS:
            exchange_name = "uniswap_v3"
        elif exchange_name in self.SOLIDLY_V2_FORKS:
            exchange_name = "solidly_v2"
        elif exchange_name in self.CARBON_V1_FORKS:
            exchange_name = "carbon_v1"
        return exchange_name

class _ConfigNetworkMainnet(ConfigNetwork):
    """
    Fastlane bot config -- network [Ethereum Mainnet]
    """

    NETWORK = S.NETWORK_ETHEREUM
    NETWORK_ID = "mainnet"
    NETWORK_NAME = "Ethereum Mainnet"
    DEFAULT_PROVIDER = S.PROVIDER_ALCHEMY
    RPC_ENDPOINT = "https://eth-mainnet.alchemyapi.io/v2/"
    WEB3_ALCHEMY_PROJECT_ID = os.environ.get("WEB3_ALCHEMY_PROJECT_ID")

    MULTICALL_CONTRACT_ADDRESS = "0xcA11bde05977b3631167028862bE2a173976CA11"
    # NATIVE_GAS_TOKEN_KEY = "ETH-EEeE"
    # WRAPPED_GAS_TOKEN_KEY = "WETH-6Cc2"
    # STABLECOIN_KEY = "USDC-eB48"

    NATIVE_GAS_TOKEN_ADDRESS = "0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE"
    WRAPPED_GAS_TOKEN_ADDRESS = "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2"
    NATIVE_GAS_TOKEN_SYMBOL = "ETH"
    WRAPPED_GAS_TOKEN_SYMBOL = "WETH"
    STABLECOIN_ADDRESS = "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48"

    TAX_TOKENS = set([
        "0x5a3e6A77ba2f983eC0d371ea3B475F8Bc0811AD5", # 0x0
        "0x72e4f9F808C49A2a61dE9C5896298920Dc4EEEa9", # BITCOIN
        "0x40E64405F18e4FB01c6fc39f4F0c78df5eF9D0E0", # COSMIC
        "0xae41b275aaAF484b541A5881a2dDED9515184CCA", # CSWAP
        "0xf94e7d0710709388bCe3161C32B4eEA56d3f91CC", # DSync
        "0x69420E3A3aa9E17Dea102Bb3a9b3B73dcDDB9528", # ELON
        "0x1258D60B224c0C5cD888D37bbF31aa5FCFb7e870", # GPU
        "0x292fcDD1B104DE5A00250fEBbA9bC6A5092A0076", # HASHAI
        "0xaa95f26e30001251fb905d264Aa7b00eE9dF6C18", # KENDU
        "0x6A7eFF1e2c355AD6eb91BEbB5ded49257F3FED98", # OPSEC
        "0x14feE680690900BA0ccCfC76AD70Fd1b95D10e16", # PAAL
    ])

    # FACTORY, CONVERTER, AND CONTROLLER ADDRESSES
    #######################################################################################
    BANCOR_V3_NETWORK_INFO_ADDRESS = "0x8E303D296851B320e6a697bAcB979d13c9D6E760"
    BANCOR_V3_NETWORK_ADDRESS = "0xeEF417e1D5CC832e619ae18D2F140De2999dD4fB"
    BANCOR_V3_NETWORK_SETTINGS = "0x83E1814ba31F7ea95D216204BB45FE75Ce09b14F"
    BANCOR_V3_VAULT = "0x649765821D9f64198c905eC0B2B037a4a52Bc373"
    BANCOR_V3_POOL_COLLECTOR_ADDRESS = "0xde1B3CcfC45e3F5bff7f43516F2Cd43364D883E4"
    BANCOR_V2_CONVERTER_REGISTRY_ADDRESS = "0xC0205e203F423Bcd8B2a4d6f8C8A154b0Aa60F19"
    # FASTLANE_CONTRACT_ADDRESS = "0x51a6D03B156af044bda570CF35a919DB851Cebd1"
    FASTLANE_CONTRACT_ADDRESS = "0x41Eeba3355d7D6FF628B7982F3F9D055c39488cB"
    CARBON_CONTROLLER_ADDRESS = "0xC537e898CD774e2dCBa3B14Ea6f34C93d5eA45e1"
    CARBON_CONTROLLER_VOUCHER = "0x3660F04B79751e31128f6378eAC70807e38f554E"

    BALANCER_VAULT_ADDRESS = "0xBA12222222228d8Ba445958a75a0704d566BF2C8"
    CHAIN_FLASHLOAN_TOKENS = {
        "WBTC": "0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599",
        "BNT": "0x1F573D6Fb3F13d689FF844B4cE37794d79a7FF1C",
        "WETH": "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2",
        "USDC": "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48",
        "USDT": "0xdAC17F958D2ee523a2206206994597C13D831ec7",
        "LINK": "0x514910771AF9Ca656af840dff83E8264EcF986CA",
    }
    # Add any exchanges unique to the chain here
    CHAIN_SPECIFIC_EXCHANGES = ["carbon_v1", "bancor_v2", "bancor_v3", "bancor_pol"]
    CHAIN_SPECIFIC_EXCHANGES = [ex for ex in CHAIN_SPECIFIC_EXCHANGES if ex is not None]


class _ConfigNetworkArbitrumOne(ConfigNetwork):
    NETWORK = S.NETWORK_ARBITRUM
    NETWORK_ID = "42161"
    NETWORK_NAME = "arbitrum_one"
    DEFAULT_PROVIDER = S.PROVIDER_ALCHEMY
    RPC_ENDPOINT = "https://arb-mainnet.g.alchemy.com/v2/"
    WEB3_ALCHEMY_PROJECT_ID = os.environ.get("WEB3_ALCHEMY_ARBITRUM")

    FASTLANE_CONTRACT_ADDRESS = ""  # TODO
    MULTICALL_CONTRACT_ADDRESS = ""  # TODO

    # NATIVE_GAS_TOKEN_KEY = "ETH-EEeE"
    # WRAPPED_GAS_TOKEN_KEY = "WETH-bab1"
    # STABLECOIN_KEY = "USDC-5831"

    NATIVE_GAS_TOKEN_ADDRESS = "0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE"
    WRAPPED_GAS_TOKEN_ADDRESS = "0x82aF49447D8a07e3bd95BD0d56f35241523fBab1"
    NATIVE_GAS_TOKEN_SYMBOL = "ETH"
    WRAPPED_GAS_TOKEN_SYMBOL = "WETH"
    STABLECOIN_ADDRESS = "0xaf88d065e77c8cC2239327C5EDb3A432268e5831"

    BALANCER_VAULT_ADDRESS = "0xBA12222222228d8Ba445958a75a0704d566BF2C8"

    CHAIN_FLASHLOAN_TOKENS = {
        "WETH": "0x82aF49447D8a07e3bd95BD0d56f35241523fBab1",
        "USDC": "0xaf88d065e77c8cC2239327C5EDb3A432268e5831",
        "USDT": "0xFd086bC7CD5C481DCC9C85ebE478A1C0b69FCbb9",
        "WBTC": "0x2f2a2543B76A4166549F7aaB2e75Bef0aefC5B0f",
    }

    # Add any exchanges unique to the chain here
    CHAIN_SPECIFIC_EXCHANGES = []


class _ConfigNetworkPolygon(ConfigNetwork):
    NETWORK = S.NETWORK_POLYGON
    NETWORK_ID = "137"
    NETWORK_NAME = "polygon"
    DEFAULT_PROVIDER = S.PROVIDER_ALCHEMY
    RPC_ENDPOINT = "https://polygon-mainnet.g.alchemy.com/v2/"
    WEB3_ALCHEMY_PROJECT_ID = os.environ.get("WEB3_ALCHEMY_POLYGON")

    FASTLANE_CONTRACT_ADDRESS = ""  # TODO
    MULTICALL_CONTRACT_ADDRESS = ""  # TODO

    # NATIVE_GAS_TOKEN_KEY = "MATIC-1010"
    # WRAPPED_GAS_TOKEN_KEY = "WMATIC-1270"
    # STABLECOIN_KEY = "USDC-4174"

    NATIVE_GAS_TOKEN_ADDRESS = "0x0000000000000000000000000000000000001010"
    WRAPPED_GAS_TOKEN_ADDRESS = "0x0d500B1d8E8eF31E21C99d1Db9A6444d3ADf1270"
    NATIVE_GAS_TOKEN_SYMBOL = "MATIC"
    WRAPPED_GAS_TOKEN_SYMBOL = "WMATIC"
    STABLECOIN_ADDRESS = "0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174"

    BALANCER_VAULT_ADDRESS = "0xBA12222222228d8Ba445958a75a0704d566BF2C8"

    CHAIN_FLASHLOAN_TOKENS = {
        "WETH": "0x7ceB23fD6bC0adD59E62ac25578270cFf1b9f619",
        "USDC": "0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174",
        "USDT": "0xc2132D05D31c914a87C6611C10748AEb04B58e8F",
        "WBTC": "0x1BFD67037B42Cf73acF2047067bd4F2C47D9BfD6",
        "MATIC": "0x0000000000000000000000000000000000001010",
        "WMATIC": "0x0d500B1d8E8eF31E21C99d1Db9A6444d3ADf1270",
    }

    # Add any exchanges unique to the chain here
    CHAIN_SPECIFIC_EXCHANGES = []


class _ConfigNetworkPolygonZkevm(ConfigNetwork):
    NETWORK = S.NETWORK_POLYGON_ZKEVM
    NETWORK_ID = "1101"
    NETWORK_NAME = "polygon_zkevm"
    DEFAULT_PROVIDER = S.PROVIDER_ALCHEMY
    RPC_ENDPOINT = "https://polygonzkevm-mainnet.g.alchemy.com/v2/"
    WEB3_ALCHEMY_PROJECT_ID = os.environ.get("WEB3_ALCHEMY_POLYGON_ZKEVM")

    FASTLANE_CONTRACT_ADDRESS = ""  # TODO
    MULTICALL_CONTRACT_ADDRESS = ""  # TODO
    # NATIVE_GAS_TOKEN_KEY = "ETH-EEeE"
    # WRAPPED_GAS_TOKEN_KEY = "WETH-E6e9"
    # STABLECOIN_KEY = "USDC-c035"

    NATIVE_GAS_TOKEN_ADDRESS = "0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE"
    WRAPPED_GAS_TOKEN_ADDRESS = "0x4F9A0e7FD2Bf6067db6994CF12E4495Df938E6e9"
    NATIVE_GAS_TOKEN_SYMBOL = "ETH"
    WRAPPED_GAS_TOKEN_SYMBOL = "WETH"
    STABLECOIN_ADDRESS = "0xA8CE8aee21bC2A48a5EF670afCc9274C7bbbC035"

    BALANCER_VAULT_ADDRESS = "0xBA12222222228d8Ba445958a75a0704d566BF2C8"
    CHAIN_FLASHLOAN_TOKENS = {
        "WETH": "0x4F9A0e7FD2Bf6067db6994CF12E4495Df938E6e9",
        "USDC": "0xA8CE8aee21bC2A48a5EF670afCc9274C7bbbC035",
        "USDT": "0x1E4a5963aBFD975d8c9021ce480b42188849D41d",
        "WBTC": "0xEA034fb02eB1808C2cc3adbC15f447B93CbE08e1",
    }

    # Add any exchanges unique to the chain here
    CHAIN_SPECIFIC_EXCHANGES = []


class _ConfigNetworkOptimism(ConfigNetwork):
    NETWORK = S.NETWORK_OPTIMISM
    NETWORK_ID = "10"
    NETWORK_NAME = "optimism"
    DEFAULT_PROVIDER = S.PROVIDER_ALCHEMY
    RPC_ENDPOINT = "https://opt-mainnet.g.alchemy.com/v2/"
    WEB3_ALCHEMY_PROJECT_ID = os.environ.get("WEB3_ALCHEMY_OPTIMISM")

    GAS_ORACLE_ADDRESS = "0x420000000000000000000000000000000000000F"  # source: https://docs.optimism.io/builders/tools/build/oracles#gas-oracle
    FASTLANE_CONTRACT_ADDRESS = ""  # TODO
    MULTICALL_CONTRACT_ADDRESS = ""  # TODO

    # NATIVE_GAS_TOKEN_KEY = "ETH-EEeE"
    # WRAPPED_GAS_TOKEN_KEY = "WETH-0006"
    # STABLECOIN_KEY = "USDC-ff85"

    NATIVE_GAS_TOKEN_ADDRESS = "0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE"
    WRAPPED_GAS_TOKEN_ADDRESS = "0x4200000000000000000000000000000000000006"
    NATIVE_GAS_TOKEN_SYMBOL = "ETH"
    WRAPPED_GAS_TOKEN_SYMBOL = "WETH"
    STABLECOIN_ADDRESS = "0x0b2C639c533813f4Aa9D7837CAf62653d097Ff85"

    BALANCER_VAULT_ADDRESS = "0xBA12222222228d8Ba445958a75a0704d566BF2C8"
    CHAIN_FLASHLOAN_TOKENS = {
        "WETH": "0x4200000000000000000000000000000000000006",
        "USDC": "0x0b2C639c533813f4Aa9D7837CAf62653d097Ff85",
        "USDT": "0xFd086bC7CD5C481DCC9C85ebE478A1C0b69FCbb9",
        "WBTC": "0x68f180fcCe6836688e9084f035309E29Bf0A2095",
    }
    # Add any exchanges unique to the chain here
    CHAIN_SPECIFIC_EXCHANGES = []


class _ConfigNetworkBase(ConfigNetwork):
    """
    Fastlane bot config -- network [Base Mainnet]
    """

    NETWORK = S.NETWORK_BASE
    NETWORK_ID = "8453"
    NETWORK_NAME = "coinbase_base"
    DEFAULT_PROVIDER = S.PROVIDER_ALCHEMY
    RPC_ENDPOINT = "https://base-mainnet.g.alchemy.com/v2/"
    WEB3_ALCHEMY_PROJECT_ID = os.environ.get("WEB3_ALCHEMY_BASE")

    GAS_ORACLE_ADDRESS = "0x420000000000000000000000000000000000000F"  # source: https://docs.optimism.io/builders/tools/build/oracles#gas-oracle
    network_df = get_multichain_addresses(network="coinbase_base")
    FASTLANE_CONTRACT_ADDRESS = "0x2AE2404cD44c830d278f51f053a08F54b3756e1c"
    MULTICALL_CONTRACT_ADDRESS = "0xcA11bde05977b3631167028862bE2a173976CA11"

    CARBON_CONTROLLER_ADDRESS = (
        GRAPHENE_CONTROLLER_ADDRESS
    ) = "0xfbF069Dbbf453C1ab23042083CFa980B3a672BbA"
    CARBON_CONTROLLER_VOUCHER = (
        GRAPHENE_CONTROLLER_VOUCHER
    ) = "0x907F03ae649581EBFF369a21C587cb8F154A0B84"
    # NATIVE_GAS_TOKEN_KEY = "ETH-EEeE"
    # WRAPPED_GAS_TOKEN_KEY = "WETH-0006"
    # STABLECOIN_KEY = "USDC-2913"

    NATIVE_GAS_TOKEN_ADDRESS = "0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE"
    WRAPPED_GAS_TOKEN_ADDRESS = "0x4200000000000000000000000000000000000006"
    NATIVE_GAS_TOKEN_SYMBOL = "ETH"
    WRAPPED_GAS_TOKEN_SYMBOL = "WETH"
    STABLECOIN_ADDRESS = "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913"

    # Balancer
    BALANCER_VAULT_ADDRESS = "0xBA12222222228d8Ba445958a75a0704d566BF2C8"

    CHAIN_FLASHLOAN_TOKENS = {
        "WETH": "0x4200000000000000000000000000000000000006",
        "USDC": "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913",
    }
    # Add any exchanges unique to the chain here
    CHAIN_SPECIFIC_EXCHANGES = []

class _ConfigNetworkFantom(ConfigNetwork):
    """
    Fastlane bot config -- network [Base Mainnet]
    """

    NETWORK = S.NETWORK_FANTOM
    NETWORK_ID = "250"
    NETWORK_NAME = "fantom"
    DEFAULT_PROVIDER = S.PROVIDER_ALCHEMY
    RPC_ENDPOINT = "https://fantom.blockpi.network/v1/rpc/"
    WEB3_ALCHEMY_PROJECT_ID = os.environ.get("WEB3_FANTOM")

    network_df = get_multichain_addresses(network=NETWORK_NAME)
    FASTLANE_CONTRACT_ADDRESS = "0xFe19CbA3aB1A189B7FC17cAa798Df64Ad2b54d4D"
    MULTICALL_CONTRACT_ADDRESS = "0xcA11bde05977b3631167028862bE2a173976CA11"

    CARBON_CONTROLLER_ADDRESS = (
        GRAPHENE_CONTROLLER_ADDRESS
    ) = "0xf37102e11E06276ac9D393277BD7b63b3393b361"
    CARBON_CONTROLLER_VOUCHER = (
        GRAPHENE_CONTROLLER_VOUCHER
    ) = "0x907F03ae649581EBFF369a21C587cb8F154A0B84"
    # NATIVE_GAS_TOKEN_KEY = "ETH-EEeE"
    # WRAPPED_GAS_TOKEN_KEY = "WETH-0006"
    # STABLECOIN_KEY = "USDC-2913"

    NATIVE_GAS_TOKEN_ADDRESS = "0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE"
    WRAPPED_GAS_TOKEN_ADDRESS = "0x21be370D5312f44cB42ce377BC9b8a0cEF1A4C83"
    NATIVE_GAS_TOKEN_SYMBOL = "FTM"
    WRAPPED_GAS_TOKEN_SYMBOL = "WFTM"
    STABLECOIN_ADDRESS = "0x28a92dde19D9989F39A49905d7C9C2FAc7799bDf"

    # Balancer
    BALANCER_VAULT_ADDRESS = "0x20dd72Ed959b6147912C2e529F0a0C651c33c9ce"

    CHAIN_FLASHLOAN_TOKENS = {
        "0x21be370D5312f44cB42ce377BC9b8a0cEF1A4C83": "WFTM",
        "0x28a92dde19D9989F39A49905d7C9C2FAc7799bDf": "USDC",
    }
    # Add any exchanges unique to the chain here
    CHAIN_SPECIFIC_EXCHANGES = []

class _ConfigNetworkMantle(ConfigNetwork):
    """
    Fastlane bot config -- network [Base Mainnet]
    """

    NETWORK = S.NETWORK_MANTLE
    NETWORK_ID = "5000"
    NETWORK_NAME = "mantle"
    DEFAULT_PROVIDER = S.PROVIDER_ALCHEMY
    # Provider website: https://drpc.org/chainlist
    RPC_ENDPOINT = "https://lb.drpc.org/ogrpc?network=mantle&dkey="
    WEB3_ALCHEMY_PROJECT_ID = os.environ.get("WEB3_MANTLE")

    GAS_ORACLE_ADDRESS = "0x420000000000000000000000000000000000000F"
    network_df = get_multichain_addresses(network=NETWORK_NAME)
    FASTLANE_CONTRACT_ADDRESS = "0xC7Dd38e64822108446872c5C2105308058c5C55C"
    MULTICALL_CONTRACT_ADDRESS = "0xcA11bde05977b3631167028862bE2a173976CA11"
    IS_NO_FLASHLOAN_AVAILABLE = True

    CARBON_CONTROLLER_ADDRESS = (
        GRAPHENE_CONTROLLER_ADDRESS
    ) = "0x7900f766F06e361FDDB4FdeBac5b138c4EEd8d4A"
    CARBON_CONTROLLER_VOUCHER = (
        GRAPHENE_CONTROLLER_VOUCHER
    ) = "0x953A6D3f9DB06027b2feb8b76a76AA2FC8334865"
    # NATIVE_GAS_TOKEN_KEY = "ETH-EEeE"
    # WRAPPED_GAS_TOKEN_KEY = "WETH-0006"
    # STABLECOIN_KEY = "USDC-2913"

    NATIVE_GAS_TOKEN_ADDRESS = "0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE"
    WRAPPED_GAS_TOKEN_ADDRESS = "0x78c1b0C915c4FAA5FffA6CAbf0219DA63d7f4cb8"
    NATIVE_GAS_TOKEN_SYMBOL = "MNT"
    WRAPPED_GAS_TOKEN_SYMBOL = "WMNT"
    STABLECOIN_ADDRESS = "0x09Bc4E0D864854c6aFB6eB9A9cdF58aC190D0dF9"

    # Balancer
    BALANCER_VAULT_ADDRESS = ""

    CHAIN_FLASHLOAN_TOKENS = {
        "0x78c1b0C915c4FAA5FffA6CAbf0219DA63d7f4cb8": "WMNT",
        "0x09Bc4E0D864854c6aFB6eB9A9cdF58aC190D0dF9": "USDC",
    }
    # Add any exchanges unique to the chain here
    CHAIN_SPECIFIC_EXCHANGES = []

class _ConfigNetworkLinea(ConfigNetwork):
    """
    Fastlane bot config -- network [Base Mainnet]
    """

    NETWORK = S.NETWORK_LINEA
    NETWORK_ID = "59144"
    NETWORK_NAME = "linea"
    DEFAULT_PROVIDER = S.PROVIDER_ALCHEMY
    RPC_ENDPOINT = "https://linea.blockpi.network/v1/rpc/"
    WEB3_ALCHEMY_PROJECT_ID = os.environ.get("WEB3_LINEA")

    network_df = get_multichain_addresses(network=NETWORK_NAME)
    FASTLANE_CONTRACT_ADDRESS = "0xC7Dd38e64822108446872c5C2105308058c5C55C"
    MULTICALL_CONTRACT_ADDRESS = "0xcA11bde05977b3631167028862bE2a173976CA11"

    CARBON_CONTROLLER_ADDRESS = "0x0000000000000000000000000000000000000000" #TODO - UPDATE WITH ACTUAL DEPLOYMENT WHEN THERE IS ONE
    CARBON_CONTROLLER_VOUCHER = "0x0000000000000000000000000000000000000000" #TODO - UPDATE WITH ACTUAL DEPLOYMENT WHEN THERE IS ONE

    NATIVE_GAS_TOKEN_ADDRESS = "0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE"
    WRAPPED_GAS_TOKEN_ADDRESS = "0xe5D7C2a44FfDDf6b295A15c148167daaAf5Cf34f"
    NATIVE_GAS_TOKEN_SYMBOL = "ETH"
    WRAPPED_GAS_TOKEN_SYMBOL = "WETH"
    STABLECOIN_ADDRESS = "0x176211869ca2b568f2a7d4ee941e073a821ee1ff"

    TAX_TOKENS = set([
        "0x1bE3735Dd0C0Eb229fB11094B6c277192349EBbf", # LUBE
    ])

    IS_INJECT_POA_MIDDLEWARE = True
    # Balancer
    BALANCER_VAULT_ADDRESS = "0x1d0188c4B276A09366D05d6Be06aF61a73bC7535" # velocore

    CHAIN_FLASHLOAN_TOKENS = {
        "0xe5D7C2a44FfDDf6b295A15c148167daaAf5Cf34f": "WETH",
        "0x176211869ca2b568f2a7d4ee941e073a821ee1ff": "USDC",
    }
    # Add any exchanges unique to the chain here
    CHAIN_SPECIFIC_EXCHANGES = []

class _ConfigNetworkSei(ConfigNetwork):
    """
    Fastlane bot config -- network [Base Mainnet]
    """

    NETWORK = S.NETWORK_SEI
    NETWORK_ID = "1329" # TODO
    NETWORK_NAME = "sei"
    DEFAULT_PROVIDER = S.PROVIDER_ALCHEMY
    RPC_ENDPOINT = "https://evm-rpc.sei-apis.com/?x-apikey="
    WEB3_ALCHEMY_PROJECT_ID = os.environ.get("WEB3_SEI")

    network_df = get_multichain_addresses(network=NETWORK_NAME)
    FASTLANE_CONTRACT_ADDRESS = "0xC56Eb3d03C5D7720DAf33a3718affb9BcAb03FBc"
    MULTICALL_CONTRACT_ADDRESS = "0xe033Bed7cae4114Af84Be1e9F1CA7DEa07Dfe1Cf"

    CARBON_CONTROLLER_ADDRESS = "0xe4816658ad10bF215053C533cceAe3f59e1f1087"
    CARBON_CONTROLLER_VOUCHER = "0xA4682A2A5Fe02feFF8Bd200240A41AD0E6EaF8d5"

    NATIVE_GAS_TOKEN_ADDRESS = "0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE"
    WRAPPED_GAS_TOKEN_ADDRESS = "0xE30feDd158A2e3b13e9badaeABaFc5516e95e8C7"
    NATIVE_GAS_TOKEN_SYMBOL = "SEI"
    WRAPPED_GAS_TOKEN_SYMBOL = "WSEI"
    STABLECOIN_ADDRESS = "0xace5f7Ea93439Af39b46d2748fA1aC19951c8d7C" #TODO USDC on devnet

    IS_INJECT_POA_MIDDLEWARE = False
    # Balancer
    BALANCER_VAULT_ADDRESS = "0x7ccBebeb88696f9c8b061f1112Bb970158e29cA5" # # TODO Jellyswap on devnet

    CHAIN_FLASHLOAN_TOKENS = {
        "0xE30feDd158A2e3b13e9badaeABaFc5516e95e8C7": "WSEI", 
        "0xace5f7Ea93439Af39b46d2748fA1aC19951c8d7C": "USDC", #TODO confirm for Mainnet
    }
    # Add any exchanges unique to the chain here
    CHAIN_SPECIFIC_EXCHANGES = []

class _ConfigNetworkTenderly(ConfigNetwork):
    """
    Fastlane bot config -- network [Ethereum Tenderly]
    """

    NETWORK = S.NETWORK_TENDERLY
    DEFAULT_PROVIDER = S.PROVIDER_TENDERLY
    NETWORK_ID = S.NETWORK_TENDERLY
    NETWORK_NAME = "tenderly"
    TENDERLY_FORK = TENDERLY_FORK

    # NATIVE_GAS_TOKEN_KEY = "ETH-EEeE"
    # WRAPPED_GAS_TOKEN_KEY = "WETH-6Cc2"
    # STABLECOIN_KEY = "USDC-eB48"

    NATIVE_GAS_TOKEN_ADDRESS = "0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE"
    WRAPPED_GAS_TOKEN_ADDRESS = "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2"
    NATIVE_GAS_TOKEN_SYMBOL = "ETH"
    WRAPPED_GAS_TOKEN_SYMBOL = "WETH"
    STABLECOIN_ADDRESS = "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48"

    # FACTORY, CONVERTER, AND CONTROLLER ADDRESSES
    #######################################################################################
    BANCOR_V3_NETWORK_INFO_ADDRESS = "0x8E303D296851B320e6a697bAcB979d13c9D6E760"
    BANCOR_V3_NETWORK_ADDRESS = "0xeEF417e1D5CC832e619ae18D2F140De2999dD4fB"
    BANCOR_V3_NETWORK_SETTINGS = "0x83E1814ba31F7ea95D216204BB45FE75Ce09b14F"
    BANCOR_V3_VAULT = "0x649765821D9f64198c905eC0B2B037a4a52Bc373"
    BANCOR_V3_POOL_COLLECTOR_ADDRESS = "0xde1B3CcfC45e3F5bff7f43516F2Cd43364D883E4"
    BANCOR_V2_CONVERTER_REGISTRY_ADDRESS = "0xC0205e203F423Bcd8B2a4d6f8C8A154b0Aa60F19"
    # FASTLANE_CONTRACT_ADDRESS = "0x51a6D03B156af044bda570CF35a919DB851Cebd1"
    FASTLANE_CONTRACT_ADDRESS = "0x41Eeba3355d7D6FF628B7982F3F9D055c39488cB"
    CARBON_CONTROLLER_ADDRESS = "0xC537e898CD774e2dCBa3B14Ea6f34C93d5eA45e1"
    CARBON_CONTROLLER_VOUCHER = "0x3660F04B79751e31128f6378eAC70807e38f554E"
    MULTICALL_CONTRACT_ADDRESS = "0xcA11bde05977b3631167028862bE2a173976CA11"

    # Uniswap
    UNISWAP_V2_ROUTER_ADDRESS = "0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D"
    UNISWAP_V2_FACTORY_ADDRESS = "0x5C69bEe701ef814a2B6a3EDD4B1652CB9cc5aA6f"
    UNISWAP_V3_ROUTER_ADDRESS = "0xE592427A0AEce92De3Edee1F18E0157C05861564"
    UNISWAP_V3_FACTORY_ADDRESS = "0x1F98431c8aD98523631AE4a59f267346ea31F984"

    # Pancake
    PANCAKESWAP_V2_ROUTER_ADDRESS = "0xEfF92A263d31888d860bD50809A8D171709b7b1c"
    PANCAKESWAP_V2_FACTORY_ADDRESS = "0x1097053Fd2ea711dad45caCcc45EfF7548fCB362"
    PANCAKESWAP_V3_ROUTER_ADDRESS = "0x1b81D678ffb9C0263b24A97847620C99d213eB14"
    PANCAKESWAP_V3_FACTORY_ADDRESS = "0x0BFbCF9fa4f9C56B0F40a671Ad40E0805A091865"

    # Sushi
    SUSHISWAP_V2_ROUTER_ADDRESS = "0xd9e1cE17f2641f24aE83637ab66a2cca9C378B9F"
    SUSHISWAP_V2_FACTORY_ADDRESS = "0xC0AEe478e3658e2610c5F7A4A2E1777cE9e4f2Ac"
    SUSHISWAP_V3_ROUTER_ADDRESS = "0x2E6cd2d30aa43f40aa81619ff4b6E0a41479B13F"
    SUSHISWAP_V3_FACTORY_ADDRESS = "0xbACEB8eC6b9355Dfc0269C18bac9d6E2Bdc29C4F"

    # Shiba
    SHIBA_V2_ROUTER_ADDRESS = "0x03f7724180AA6b939894B5Ca4314783B0b36b329"
    SHIBA_V2_FACTORY_ADDRESS = "0x115934131916C8b277DD010Ee02de363c09d037c"

    BALANCER_VAULT_ADDRESS = "0xBA12222222228d8Ba445958a75a0704d566BF2C8"

    CHAIN_SPECIFIC_EXCHANGES = ["carbon_v1", "bancor_v2", "bancor_v3", "bancor_pol"]
    CHAIN_SPECIFIC_EXCHANGES = [ex for ex in CHAIN_SPECIFIC_EXCHANGES if ex is not None]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
