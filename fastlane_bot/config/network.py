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
        if fork in fork_name and contract_name == S.ROUTER_ADDRESS:
            fork_map[exchange_name] : address
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
    USDC_ADDRESS = "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48"
    MKR_ADDRESS = "0x9f8F72aA9304c8B593d555F12eF6589cC3A579A2"
    LINK_ADDRESS = "0x514910771AF9Ca656af840dff83E8264EcF986CA"
    WBTC_ADDRESS = "0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599"
    ETH_ADDRESS = "0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE"
    BNT_ADDRESS = "0x1F573D6Fb3F13d689FF844B4cE37794d79a7FF1C"
    USDT_ADDRESS = "0xdAC17F958D2ee523a2206206994597C13D831ec7"
    WETH_ADDRESS = WETH9_ADDRESS = "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2"
    BNT_KEY = "BNT-FF1C"
    ETH_KEY = "ETH-EEeE"
    WBTC_KEY = "WBTC-2c599"
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

    CARBON_POL_NAME = "bancor_pol"
    SHIBA_V2_NAME = "shiba_v2"
    VELOCIMETER_V1_NAME = "velocimeter_v1"
    VELOCIMETER_V2_NAME = "velocimeter_v2"

    EXCHANGE_IDS = {
        BANCOR_V2_NAME: 1,
        BANCOR_V3_NAME: 2,
        UNISWAP_V2_NAME: 3,
        UNISWAP_V3_NAME: 4,
        SUSHISWAP_V2_NAME: 5,
        CARBON_V1_NAME: 6,
        BALANCER_NAME: 7,
        CARBON_POL_NAME: 8,
    }
    UNI_V2_FORKS = [
        UNISWAP_V2_NAME,
        SUSHISWAP_V2_NAME,
        PANCAKESWAP_V2_NAME,
        SHIBA_V2_NAME,
        SMARDEX_V2_NAME,
        SWAPBASED_V2_NAME,
        BASESWAP_V2_NAME,
        ALIENBASE_V2_NAME,
        AERODROME_V2_NAME,
        VELOCIMETER_V1_NAME,
        SOLIDLY_V2_NAME,
    ]
    UNI_V3_FORKS = [
        UNISWAP_V3_NAME,
        SUSHISWAP_V3_NAME,
        PANCAKESWAP_V3_NAME,
        BASESWAP_V3_NAME,
    ]
    SOLIDLY_V2_FORKS = [AERODROME_V3_NAME, VELOCIMETER_V2_NAME, SOLIDLY_V2_NAME]
    CARBON_V1_FORKS = [CARBON_V1_NAME]
    UNI_V2_FEE_MAPPING = {
        UNISWAP_V2_NAME: 0.003,
        SUSHISWAP_V2_NAME: 0.0025,
        PANCAKESWAP_V2_NAME: 0.0025,
    }

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
    UNIV3_FEE_LIST = [100, 500, 2500, 3000, 10000]
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
    DEFAULT_MIN_PROFIT_BNT = Decimal("80")
    DEFAULT_MIN_PROFIT = Decimal("80")

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

    network_df = get_multichain_addresses(network="polygon")

    MULTICALL_CONTRACT_ADDRESS = "0x5BA1e12693Dc8F9c48aAD8770482f4739bEeD696"

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

    # Uni V2 & V3 Router Mapping
    UNI_V2_ROUTER_MAPPING = get_fork_map(df=network_df, fork_name=S.UNISWAP_V2)
    UNI_V2_FEE_MAPPING = get_fee_map(df=network_df, fork_name=S.UNISWAP_V2)
    UNI_V3_ROUTER_MAPPING = get_fork_map(df=network_df, fork_name=S.UNISWAP_V3)
    SOLIDLY_ROUTER_MAPPING = get_fork_map(df=network_df, fork_name=S.SOLIDLY)
    SOLIDLY_FEE_MAPPING = get_fee_map(df=network_df, fork_name=S.SOLIDLY)
    CARBON_CONTROLLER_MAPPING = get_fork_map(df=network_df, fork_name=S.CARBON_V1)

    BALANCER_VAULT_ADDRESS = "0xBA12222222228d8Ba445958a75a0704d566BF2C8"

    ALL_EXCHANGES = [ex for ex in UNI_V2_ROUTER_MAPPING.keys()] + [ex for ex in UNI_V3_ROUTER_MAPPING.keys()] + [ex for ex in SOLIDLY_ROUTER_MAPPING.keys()] + ["balancer" if BALANCER_VAULT_ADDRESS is not None else None]
    ALL_EXCHANGES += ["carbon_v1", "bancor_v2", "bancor_v3", "bancor_pol"]
    ALL_EXCHANGES = [ex for ex in ALL_EXCHANGES if ex is not None]

class _ConfigNetworkArbitrumOne(ConfigNetwork):
    NETWORK = S.NETWORK_ARBITRUM
    NETWORK_ID = "42161"
    NETWORK_NAME = "arbitrum_one"
    DEFAULT_PROVIDER = S.PROVIDER_ALCHEMY
    RPC_ENDPOINT = "https://arb-mainnet.g.alchemy.com/v2/"
    WEB3_ALCHEMY_PROJECT_ID = os.environ.get("WEB3_ALCHEMY_ARBITRUM")

    FASTLANE_CONTRACT_ADDRESS = ""  # TODO
    MULTICALL_CONTRACT_ADDRESS = "" # TODO

    network_df = get_multichain_addresses(network="arbitrum_one")

    UNI_V2_ROUTER_MAPPING = get_fork_map(df=network_df, fork_name=S.UNISWAP_V2)
    UNI_V2_FEE_MAPPING = get_fee_map(df=network_df, fork_name=S.UNISWAP_V2)
    UNI_V3_ROUTER_MAPPING = get_fork_map(df=network_df, fork_name=S.UNISWAP_V3)
    SOLIDLY_ROUTER_MAPPING = get_fork_map(df=network_df, fork_name=S.SOLIDLY)
    SOLIDLY_FEE_MAPPING = get_fee_map(df=network_df, fork_name=S.SOLIDLY)
    CARBON_CONTROLLER_MAPPING = get_fork_map(df=network_df, fork_name=S.CARBON_V1)

    BALANCER_VAULT_ADDRESS = "0xBA12222222228d8Ba445958a75a0704d566BF2C8"

    ALL_EXCHANGES = [ex for ex in UNI_V2_ROUTER_MAPPING.keys()] + [ex for ex in UNI_V3_ROUTER_MAPPING.keys()] + [ex for ex in SOLIDLY_ROUTER_MAPPING.keys()] + [ex for ex in CARBON_CONTROLLER_MAPPING.keys()] + ["balancer" if BALANCER_VAULT_ADDRESS is not None else None]
    ALL_EXCHANGES = [ex for ex in ALL_EXCHANGES if ex is not None]


class _ConfigNetworkPolygon(ConfigNetwork):
    NETWORK = S.NETWORK_POLYGON
    NETWORK_ID = "137"
    NETWORK_NAME = "polygon"
    DEFAULT_PROVIDER = S.PROVIDER_ALCHEMY
    RPC_ENDPOINT = "https://polygonzkevm-mainnet.g.alchemy.com/v2/"
    WEB3_ALCHEMY_PROJECT_ID = os.environ.get("WEB3_ALCHEMY_POLYGON")

    FASTLANE_CONTRACT_ADDRESS = ""  # TODO
    MULTICALL_CONTRACT_ADDRESS = "" # TODO

    network_df = get_multichain_addresses(network="polygon")

    UNI_V2_ROUTER_MAPPING = get_fork_map(df=network_df, fork_name=S.UNISWAP_V2)
    UNI_V2_FEE_MAPPING = get_fee_map(df=network_df, fork_name=S.UNISWAP_V2)
    UNI_V3_ROUTER_MAPPING = get_fork_map(df=network_df, fork_name=S.UNISWAP_V3)
    SOLIDLY_ROUTER_MAPPING = get_fork_map(df=network_df, fork_name=S.SOLIDLY)
    SOLIDLY_FEE_MAPPING = get_fee_map(df=network_df, fork_name=S.SOLIDLY)
    CARBON_CONTROLLER_MAPPING = get_fork_map(df=network_df, fork_name=S.CARBON_V1)
    BALANCER_VAULT_ADDRESS = "0xBA12222222228d8Ba445958a75a0704d566BF2C8"

    ALL_EXCHANGES = [ex for ex in UNI_V2_ROUTER_MAPPING.keys()] + [ex for ex in UNI_V3_ROUTER_MAPPING.keys()] + [ex for ex in SOLIDLY_ROUTER_MAPPING.keys()] + [ex for ex in CARBON_CONTROLLER_MAPPING.keys()] + ["balancer" if BALANCER_VAULT_ADDRESS is not None else None]
    ALL_EXCHANGES = [ex for ex in ALL_EXCHANGES if ex is not None]


class _ConfigNetworkPolygonZkevm(ConfigNetwork):
    NETWORK = S.NETWORK_POLYGON_ZKEVM
    NETWORK_ID = "1101"
    NETWORK_NAME = "polygon_zkevm"
    DEFAULT_PROVIDER = S.PROVIDER_ALCHEMY
    RPC_ENDPOINT = "https://polygonzkevm-mainnet.g.alchemy.com/v2/"
    WEB3_ALCHEMY_PROJECT_ID = os.environ.get("WEB3_ALCHEMY_POLYGON_ZKEVM")

    FASTLANE_CONTRACT_ADDRESS = ""  # TODO
    MULTICALL_CONTRACT_ADDRESS = "" # TODO

    network_df = get_multichain_addresses(network="polygon_zkevm")

    UNI_V2_ROUTER_MAPPING = get_fork_map(df=network_df, fork_name=S.UNISWAP_V2)
    UNI_V2_FEE_MAPPING = get_fee_map(df=network_df, fork_name=S.UNISWAP_V2)
    UNI_V3_ROUTER_MAPPING = get_fork_map(df=network_df, fork_name=S.UNISWAP_V3)
    SOLIDLY_ROUTER_MAPPING = get_fork_map(df=network_df, fork_name=S.SOLIDLY)
    SOLIDLY_FEE_MAPPING = get_fee_map(df=network_df, fork_name=S.SOLIDLY)
    CARBON_CONTROLLER_MAPPING = get_fork_map(df=network_df, fork_name=S.CARBON_V1)
    BALANCER_VAULT_ADDRESS = "0xBA12222222228d8Ba445958a75a0704d566BF2C8"

    ALL_EXCHANGES = [ex for ex in UNI_V2_ROUTER_MAPPING.keys()] + [ex for ex in UNI_V3_ROUTER_MAPPING.keys()] + [ex for ex in SOLIDLY_ROUTER_MAPPING.keys()] + [ex for ex in CARBON_CONTROLLER_MAPPING.keys()] + ["balancer" if BALANCER_VAULT_ADDRESS is not None else None]
    ALL_EXCHANGES = [ex for ex in ALL_EXCHANGES if ex is not None]


class _ConfigNetworkOptimism(ConfigNetwork):
    NETWORK = S.NETWORK_OPTIMISM
    NETWORK_ID = "10"
    NETWORK_NAME = "optimism"
    DEFAULT_PROVIDER = S.PROVIDER_ALCHEMY
    RPC_ENDPOINT = "https://opt-mainnet.g.alchemy.com/v2/"
    WEB3_ALCHEMY_PROJECT_ID = os.environ.get("WEB3_ALCHEMY_OPTIMISM")

    network_df = get_multichain_addresses(network="optimism")

    FASTLANE_CONTRACT_ADDRESS = ""  # TODO
    MULTICALL_CONTRACT_ADDRESS = "" # TODO

    UNI_V2_ROUTER_MAPPING = get_fork_map(df=network_df, fork_name=S.UNISWAP_V2)
    UNI_V2_FEE_MAPPING = get_fee_map(df=network_df, fork_name=S.UNISWAP_V2)
    UNI_V3_ROUTER_MAPPING = get_fork_map(df=network_df, fork_name=S.UNISWAP_V3)
    SOLIDLY_ROUTER_MAPPING = get_fork_map(df=network_df, fork_name=S.SOLIDLY)
    SOLIDLY_FEE_MAPPING = get_fee_map(df=network_df, fork_name=S.SOLIDLY)
    CARBON_CONTROLLER_MAPPING = get_fork_map(df=network_df, fork_name=S.CARBON_V1)
    BALANCER_VAULT_ADDRESS = "0xBA12222222228d8Ba445958a75a0704d566BF2C8"

    ALL_EXCHANGES = [ex for ex in UNI_V2_ROUTER_MAPPING.keys()] + [ex for ex in UNI_V3_ROUTER_MAPPING.keys()] + [ex for ex in SOLIDLY_ROUTER_MAPPING.keys()] + [ex for ex in CARBON_CONTROLLER_MAPPING.keys()] + ["balancer" if BALANCER_VAULT_ADDRESS is not None else None]
    ALL_EXCHANGES = [ex for ex in ALL_EXCHANGES if ex is not None]


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

    FASTLANE_CONTRACT_ADDRESS = ""  # TODO
    MULTICALL_CONTRACT_ADDRESS = "0xcA11bde05977b3631167028862bE2a173976CA11"

    UNI_V2_ROUTER_MAPPING = get_fork_map(df=network_df, fork_name=S.UNISWAP_V2)
    UNI_V2_FEE_MAPPING = get_fee_map(df=network_df, fork_name=S.UNISWAP_V2)
    UNI_V3_ROUTER_MAPPING = get_fork_map(df=network_df, fork_name=S.UNISWAP_V3)
    SOLIDLY_ROUTER_MAPPING = get_fork_map(df=network_df, fork_name=S.SOLIDLY)
    SOLIDLY_FEE_MAPPING = get_fee_map(df=network_df, fork_name=S.SOLIDLY)
    CARBON_CONTROLLER_MAPPING = get_fork_map(df=network_df, fork_name=S.CARBON_V1)
    #Balancer
    BALANCER_VAULT_ADDRESS = "0xBA12222222228d8Ba445958a75a0704d566BF2C8"

    ALL_EXCHANGES = [ex for ex in UNI_V2_ROUTER_MAPPING.keys()] + [ex for ex in UNI_V3_ROUTER_MAPPING.keys()] + [ex for ex in SOLIDLY_ROUTER_MAPPING.keys()] + [ex for ex in CARBON_CONTROLLER_MAPPING.keys()] + ["balancer" if BALANCER_VAULT_ADDRESS is not None else None]
    ALL_EXCHANGES = [ex for ex in ALL_EXCHANGES if ex is not None]

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

    UNI_V2_ROUTER_MAPPING = {
        ConfigNetwork.UNISWAP_V2_NAME: UNISWAP_V2_ROUTER_ADDRESS,
        ConfigNetwork.SUSHISWAP_V2_NAME: SUSHISWAP_V2_ROUTER_ADDRESS,
        ConfigNetwork.PANCAKESWAP_V2_NAME: PANCAKESWAP_V2_ROUTER_ADDRESS,
        ConfigNetwork.SHIBA_V2_NAME: SHIBA_V2_ROUTER_ADDRESS,
    }
    UNI_V3_ROUTER_MAPPING = {
        ConfigNetwork.UNISWAP_V3_NAME: UNISWAP_V3_ROUTER_ADDRESS,
        ConfigNetwork.SUSHISWAP_V3_NAME: SUSHISWAP_V3_ROUTER_ADDRESS,
        ConfigNetwork.PANCAKESWAP_V3_NAME: PANCAKESWAP_V3_ROUTER_ADDRESS,
    }
    UNI_V2_FORK_FACTORY_ADDRESS_TO_EXCHANGE_NAME = {
        UNISWAP_V2_FACTORY_ADDRESS: ConfigNetwork.UNISWAP_V2_NAME,
        SUSHISWAP_V2_FACTORY_ADDRESS: ConfigNetwork.SUSHISWAP_V2_NAME,
        PANCAKESWAP_V2_FACTORY_ADDRESS: ConfigNetwork.PANCAKESWAP_V2_NAME,
        SHIBA_V2_FACTORY_ADDRESS: ConfigNetwork.SHIBA_V2_NAME,
    }

    UNI_V2_FORK_FACTORY_ADDRESS_TO_ROUTER = {
        UNISWAP_V2_FACTORY_ADDRESS: UNISWAP_V2_ROUTER_ADDRESS,
        SUSHISWAP_V2_FACTORY_ADDRESS: SUSHISWAP_V2_ROUTER_ADDRESS,
        PANCAKESWAP_V2_FACTORY_ADDRESS: PANCAKESWAP_V2_ROUTER_ADDRESS,
        SHIBA_V2_FACTORY_ADDRESS: SHIBA_V2_ROUTER_ADDRESS,
    }
    UNI_V3_FORK_FACTORY_ADDRESS_TO_ROUTER = {
        UNISWAP_V3_FACTORY_ADDRESS: UNISWAP_V3_ROUTER_ADDRESS,
        SUSHISWAP_V3_FACTORY_ADDRESS: SUSHISWAP_V3_ROUTER_ADDRESS,
        PANCAKESWAP_V3_FACTORY_ADDRESS: PANCAKESWAP_V3_ROUTER_ADDRESS,
    }
    UNI_V3_FORK_FACTORY_ADDRESS_TO_EXCHANGE_NAME = {
        UNISWAP_V3_FACTORY_ADDRESS: ConfigNetwork.UNISWAP_V3_NAME,
        SUSHISWAP_V3_FACTORY_ADDRESS: ConfigNetwork.SUSHISWAP_V3_NAME,
        PANCAKESWAP_V3_FACTORY_ADDRESS: ConfigNetwork.PANCAKESWAP_V3_NAME,
    }

    def __init__(self, **kwargs):
        super().__init__(**kwargs)


