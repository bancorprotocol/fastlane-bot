"""
Fastlane bot config -- network
"""
__VERSION__ = "1.0.3-RESTRICTED"
__DATE__ = "02/May 2023"

from typing import List, Dict

import pandas as pd

from .base import ConfigBase
from . import selectors as S

import os
from dotenv import load_dotenv

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
        exchange_name = row[1][0]
        fork = row[1][2]
        contract_name = row[1][3]
        address = row[1][4]
        if fork in fork_name and contract_name in [S.ROUTER_ADDRESS, S.CARBON_CONTROLLER]:
            fork_map[exchange_name] = address
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
        exchange_name = row[1][0]
        fork = row[1][2]
        contract_name = row[1][3]
        fee = row[1][5]
        if fork in fork_name and contract_name == S.ROUTER_ADDRESS:
            fork_map[exchange_name] : fee
    return fork_map

def get_row_from_address(address: str, df: pd.DataFrame) -> pd.DataFrame:
    if df["address"].isin([address]).any():
        return df[df["address"] == address]
    return None


def get_exchange_from_address(address: str, df: pd.DataFrame) -> str or None:
    row = get_row_from_address(address=address, df=df)
    if row is None:
        return None
    return row["exchange_name"].values[0]


def get_items_from_exchange(
    item_names: List[str],
    exchange_name: str,
    contract_name: str,
    fork: str,
    df: pd.DataFrame,
) -> List[str or float]:
    df_ex = df[
        (df["exchange_name"] == exchange_name)
        & (df["fork"] == fork)
        & (df["contract_name"] == contract_name)
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
        item_names=["address"],
        exchange_name=exchange_name,
        fork=fork,
        contract_name="ROUTER_ADDRESS",
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
        contract_name="FACTORY_ADDRESS",
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
    BNT_KEY = "BNT-FF1C"
    ETH_KEY = "ETH-EEeE"
    WBTC_KEY = "WBTC-c599"
    USDC_KEY = "USDC-eB48"
    LINK_KEY = "LINK-86CA"
    USDT_KEY = "USDT-1ec7"


    # ACCOUNTS SECTION
    #######################################################################################
    BINANCE8_WALLET_ADDRESS = "0xF977814e90dA44bFA03b6295A0616a897441aceC"
    BINANCE14_WALLET_ADDRESS = "0x28c6c06298d514db089934071355e5743bf21d60"

    # EXCHANGE IDENTIFIERS SECTION
    #######################################################################################
    BANCOR_V2_NAME = "bancor_v2"
    BANCOR_V3_NAME = "bancor_v3"
    CARBON_POL_NAME = "bancor_pol"
    UNISWAP_V2_NAME = "uniswap_v2"
    UNISWAP_V3_NAME = "uniswap_v3"
    SUSHISWAP_V2_NAME = "sushiswap_v2"
    SUSHISWAP_V3_NAME = "sushiswap_v3"
    CARBON_V1_NAME = "carbon_v1"
    BANCOR_POL_NAME = "bancor_pol"
    BALANCER_NAME = "balancer"
    PANCAKESWAP_V2_NAME = "pancakeswap_v2"
    PANCAKESWAP_V3_NAME = "pancakeswap_v3"
    SOLIDLY_V2_NAME = "solidly_v2"
    SHIBA_V2_NAME = "shiba_v2"

    # Base Exchanges
    AERODROME_V2_NAME = "aerodrome_v2"
    AERODROME_V3_NAME = "aerodrome_v3"
    ALIENBASE_V2_NAME = "alienbase_v2"
    ALIENBASE_V3_NAME = "alienbase_v3"
    BASESWAP_V2_NAME = "baseswap_v2"
    BASESWAP_V3_NAME = "baseswap_v3"
    SWAPBASED_V2_NAME = "swap_based_v2"
    # SWAPBASED_V3_NAME = "swap_based_v3" # This uses Algebra DEX
    SYNTHSWAP_V2_NAME = "synthswap_v2"
    SYNTHSWAP_V3_NAME = "synthswap_v3"
    SMARDEX_V2_NAME = "smardex_v2"
    # SMARDEX_V3_NAME = "smardex_v3" # This uses Algebra DEX
    VELOCIMETER_V1_NAME = "velocimeter_v1"
    VELOCIMETER_V2_NAME = "velocimeter_v2"

    PLATFORM_NAME_WRAP_UNWRAP = "wrap_or_unwrap"
    PLATFORM_ID_WRAP_UNWRAP = 10

    EXCHANGE_IDS = {
        BANCOR_V2_NAME: 1,
        BANCOR_V3_NAME: 2,
        UNISWAP_V2_NAME: 3,
        UNISWAP_V3_NAME: 4,
        SUSHISWAP_V2_NAME: 5,
        CARBON_V1_NAME: 6,
        BALANCER_NAME: 7,
        CARBON_POL_NAME: 8,
        PLATFORM_ID_WRAP_UNWRAP : 10
    }

    # SOLIDLY_V2_FORKS = [AERODROME_V3_NAME, VELOCIMETER_V2_NAME, SOLIDLY_V2_NAME]
    CARBON_V1_FORKS = [CARBON_V1_NAME]

    SUPPORTED_EXCHANGES = list(EXCHANGE_IDS)
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

    # DEFAULT VALUES SECTION
    #######################################################################################
    UNIV3_FEE_LIST = [80, 100, 450, 500, 2500, 3000, 10000]
    MIN_BNT_LIQUIDITY = 2_000_000_000_000_000_000
    DEFAULT_GAS = 950_000
    DEFAULT_GAS_PRICE = 0
    DEFAULT_GAS_PRICE_OFFSET = 1.09
    DEFAULT_GAS_SAFETY_OFFSET = 25_000
    DEFAULT_POLL_INTERVAL = 12
    DEFAULT_BLOCKTIME_DEVIATION = 13 * 500 * 100  # 10 block time deviation
    DEFAULT_MAX_SLIPPAGE = Decimal("1")  # 1%
    _PROJECT_PATH = os.path.normpath(f"{os.getcwd()}")  # TODO: FIX THIS
    DEFAULT_CURVES_DATAFILE = os.path.normpath(
        f"{_PROJECT_PATH}/carbon/data/curves.csv.gz"
    )
    CARBON_STRATEGY_CHUNK_SIZE = 200
    Q96 = Decimal("2") ** Decimal("96")
    DEFAULT_TIMEOUT = 60
    CARBON_FEE = Decimal("0.002")
    BANCOR_V3_FEE = Decimal("0.0")
    DEFAULT_REWARD_PERCENT = Decimal("0.5")
    LIMIT_BANCOR3_FLASHLOAN_TOKENS = True
    DEFAULT_MIN_PROFIT_GAS_TOKEN = Decimal("0.02")

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

    # FLAGS
    #######################################################################################
    GAS_TKN_IN_FLASHLOAN_TOKENS = None

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
        elif network == cls.NETWORK_TENDERLY:
            return _ConfigNetworkTenderly(_direct=False)
        else:
            raise ValueError(f"Invalid network: {network}")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.__post_init__()

    def __post_init__(self):
        assert self.NETWORK is not None
        self.network_df = get_multichain_addresses(network=self.NETWORK)

        self.UNI_V2_ROUTER_MAPPING = get_fork_map(df=self.network_df, fork_name=S.UNISWAP_V2)
        self.UNI_V2_FEE_MAPPING = get_fee_map(df=self.network_df, fork_name=S.UNISWAP_V2)
        self.UNI_V3_ROUTER_MAPPING = get_fork_map(df=self.network_df, fork_name=S.UNISWAP_V3)
        self.SOLIDLY_ROUTER_MAPPING = get_fork_map(df=self.network_df, fork_name=S.SOLIDLY)
        self.SOLIDLY_FEE_MAPPING = get_fee_map(df=self.network_df, fork_name=S.SOLIDLY)
        self.UNI_V2_FORKS = [key for key in self.UNI_V2_ROUTER_MAPPING.keys()] + ["uniswap_v2"]
        self.UNI_V3_FORKS = [key for key in self.UNI_V3_ROUTER_MAPPING.keys()]
        self.SOLIDLY_V2_FORKS = [key for key in self.SOLIDLY_ROUTER_MAPPING.keys()]
        self.CARBON_CONTROLLER_MAPPING = get_fork_map(df=self.network_df, fork_name=S.CARBON_V1)

        self.CHAIN_SPECIFIC_EXCHANGES = self.CHAIN_SPECIFIC_EXCHANGES + [ex for ex in self.UNI_V2_ROUTER_MAPPING.keys()] + [ex for ex in self.UNI_V3_ROUTER_MAPPING.keys()] + [ex for ex in self.SOLIDLY_ROUTER_MAPPING.keys()] + [ex for ex in self.CARBON_CONTROLLER_MAPPING.keys()] + ["balancer" if self.BALANCER_VAULT_ADDRESS is not None else None]
        self.CHAIN_SPECIFIC_EXCHANGES = [ex for ex in self.CHAIN_SPECIFIC_EXCHANGES if ex is not None]

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

    MULTICALL_CONTRACT_ADDRESS = "0x5BA1e12693Dc8F9c48aAD8770482f4739bEeD696"
    NATIVE_GAS_TOKEN_KEY = "ETH-EEeE"
    WRAPPED_GAS_TOKEN_KEY = "WETH-6Cc2"
    STABLECOIN_KEY = "USDC-eB48"
    
    NATIVE_GAS_TOKEN_ADDRESS = "0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE"
    WRAPPED_GAS_TOKEN_ADDRESS = "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2"
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

    BALANCER_VAULT_ADDRESS = "0xBA12222222228d8Ba445958a75a0704d566BF2C8"
    CHAIN_FLASHLOAN_TOKENS = {"WBTC-C599": "0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599","BNT-FF1C": "0x1F573D6Fb3F13d689FF844B4cE37794d79a7FF1C","WETH-6Cc2":"0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2" ,"USDC-eB48": "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48", "USDT-1ec7": "0xdAC17F958D2ee523a2206206994597C13D831ec7",  "LINK-86CA": "0x514910771AF9Ca656af840dff83E8264EcF986CA"}
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
    MULTICALL_CONTRACT_ADDRESS = "" # TODO
    
    NATIVE_GAS_TOKEN_KEY = "ETH-EEeE"
    WRAPPED_GAS_TOKEN_KEY = "WETH-bab1"
    STABLECOIN_KEY = "USDC-5831"
    
    NATIVE_GAS_TOKEN_ADDRESS = "0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE"
    WRAPPED_GAS_TOKEN_ADDRESS = "0x82aF49447D8a07e3bd95BD0d56f35241523fBab1"
    STABLECOIN_ADDRESS = "0xaf88d065e77c8cC2239327C5EDb3A432268e5831"

    BALANCER_VAULT_ADDRESS = "0xBA12222222228d8Ba445958a75a0704d566BF2C8"

    CHAIN_FLASHLOAN_TOKENS = {"WETH-bab1": "0x82aF49447D8a07e3bd95BD0d56f35241523fBab1", "USDC-5831": "0xaf88d065e77c8cC2239327C5EDb3A432268e5831", "USDT-cbb9": "0xFd086bC7CD5C481DCC9C85ebE478A1C0b69FCbb9", "WBTC-5b0f": "0x2f2a2543B76A4166549F7aaB2e75Bef0aefC5B0f", }

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
    MULTICALL_CONTRACT_ADDRESS = "" # TODO
    
    NATIVE_GAS_TOKEN_KEY = "MATIC-1010"
    WRAPPED_GAS_TOKEN_KEY = "WMATIC-1270"
    STABLECOIN_KEY = "USDC-4174"

    NATIVE_GAS_TOKEN_ADDRESS = "0x0000000000000000000000000000000000001010"
    WRAPPED_GAS_TOKEN_ADDRESS = "0x0d500B1d8E8eF31E21C99d1Db9A6444d3ADf1270"
    STABLECOIN_ADDRESS = "0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174"

    BALANCER_VAULT_ADDRESS = "0xBA12222222228d8Ba445958a75a0704d566BF2C8"

    CHAIN_FLASHLOAN_TOKENS = {"WETH-f619": "0x7ceB23fD6bC0adD59E62ac25578270cFf1b9f619", "USDC-4174": "0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174", "USDT-8e8f": "0xc2132D05D31c914a87C6611C10748AEb04B58e8F", "WBTC-bfd6": "0x1BFD67037B42Cf73acF2047067bd4F2C47D9BfD6", "MATIC-1010": "0x0000000000000000000000000000000000001010", "WMATIC": "0x0d500B1d8E8eF31E21C99d1Db9A6444d3ADf1270"}

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
    MULTICALL_CONTRACT_ADDRESS = "" # TODO
    NATIVE_GAS_TOKEN_KEY = "ETH-EEeE"
    WRAPPED_GAS_TOKEN_KEY = "WETH-E6e9"
    STABLECOIN_KEY = "USDC-c035"

    NATIVE_GAS_TOKEN_ADDRESS = "0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE"
    WRAPPED_GAS_TOKEN_ADDRESS = "0x4F9A0e7FD2Bf6067db6994CF12E4495Df938E6e9"
    STABLECOIN_ADDRESS = "0xA8CE8aee21bC2A48a5EF670afCc9274C7bbbC035"

    BALANCER_VAULT_ADDRESS = "0xBA12222222228d8Ba445958a75a0704d566BF2C8"
    CHAIN_FLASHLOAN_TOKENS = {"WETH-e6e9": "0x4F9A0e7FD2Bf6067db6994CF12E4495Df938E6e9", "USDC-c035": "0xA8CE8aee21bC2A48a5EF670afCc9274C7bbbC035", "USDT-d41d": "0x1E4a5963aBFD975d8c9021ce480b42188849D41d", "WBTC-08e1": "0xEA034fb02eB1808C2cc3adbC15f447B93CbE08e1", }

    # Add any exchanges unique to the chain here
    CHAIN_SPECIFIC_EXCHANGES = []

class _ConfigNetworkOptimism(ConfigNetwork):
    NETWORK = S.NETWORK_OPTIMISM
    NETWORK_ID = "10"
    NETWORK_NAME = "optimism"
    DEFAULT_PROVIDER = S.PROVIDER_ALCHEMY
    RPC_ENDPOINT = "https://opt-mainnet.g.alchemy.com/v2/"
    WEB3_ALCHEMY_PROJECT_ID = os.environ.get("WEB3_ALCHEMY_OPTIMISM")

    FASTLANE_CONTRACT_ADDRESS = ""  # TODO
    MULTICALL_CONTRACT_ADDRESS = "" # TODO
    
    NATIVE_GAS_TOKEN_KEY = "ETH-EEeE"
    WRAPPED_GAS_TOKEN_KEY = "WETH-0006"
    STABLECOIN_KEY = "USDC-ff85"

    NATIVE_GAS_TOKEN_ADDRESS = "0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE"
    WRAPPED_GAS_TOKEN_ADDRESS = "0x4200000000000000000000000000000000000006"
    STABLECOIN_ADDRESS = "0x0b2C639c533813f4Aa9D7837CAf62653d097Ff85"

    BALANCER_VAULT_ADDRESS = "0xBA12222222228d8Ba445958a75a0704d566BF2C8"
    CHAIN_FLASHLOAN_TOKENS = {"WETH-0006": "0x4200000000000000000000000000000000000006", "USDC-ff85": "0x0b2C639c533813f4Aa9D7837CAf62653d097Ff85", "USDT-cbb9": "0xFd086bC7CD5C481DCC9C85ebE478A1C0b69FCbb9",
                              "WBTC-2095": "0x68f180fcCe6836688e9084f035309E29Bf0A2095", }
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

    network_df = get_multichain_addresses(network="coinbase_base")
    FASTLANE_CONTRACT_ADDRESS = "0x2AE2404cD44c830d278f51f053a08F54b3756e1c"
    MULTICALL_CONTRACT_ADDRESS = "0xcA11bde05977b3631167028862bE2a173976CA11"
    
    CARBON_CONTROLLER_ADDRESS = GRAPHENE_CONTROLLER_ADDRESS = "0xfbF069Dbbf453C1ab23042083CFa980B3a672BbA"
    CARBON_CONTROLLER_VOUCHER = GRAPHENE_CONTROLLER_VOUCHER = "0x907F03ae649581EBFF369a21C587cb8F154A0B84"
    NATIVE_GAS_TOKEN_KEY = "ETH-EEeE"
    WRAPPED_GAS_TOKEN_KEY = "WETH-0006"
    STABLECOIN_KEY = "USDC-2913"

    NATIVE_GAS_TOKEN_ADDRESS = "0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE"
    WRAPPED_GAS_TOKEN_ADDRESS = "0x4200000000000000000000000000000000000006"
    STABLECOIN_ADDRESS = "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913"

    # Balancer
    BALANCER_VAULT_ADDRESS = "0xBA12222222228d8Ba445958a75a0704d566BF2C8"

    CHAIN_FLASHLOAN_TOKENS = {"WETH-0006": "0x4200000000000000000000000000000000000006",
                              "USDC-2913": "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913"}
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

    NATIVE_GAS_TOKEN_KEY = "ETH-EEeE"
    WRAPPED_GAS_TOKEN_KEY = "WETH-6Cc2"
    STABLECOIN_KEY = "USDC-eB48"

    NATIVE_GAS_TOKEN_ADDRESS = "0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE"
    WRAPPED_GAS_TOKEN_ADDRESS = "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2"
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
    MULTICALL_CONTRACT_ADDRESS = "0x5BA1e12693Dc8F9c48aAD8770482f4739bEeD696"

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


