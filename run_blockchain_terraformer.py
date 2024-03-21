import math
from dataclasses import dataclass
from typing import Tuple, List, Dict

import pandas as pd
from dotenv import load_dotenv
from joblib import parallel_backend, Parallel, delayed
from pandas import DataFrame
from web3.contract import Contract

load_dotenv()
import os
import requests
import asyncio
import nest_asyncio

from web3 import Web3, AsyncWeb3

from fastlane_bot.data.abi import *
from fastlane_bot.utils import safe_int
from fastlane_bot.events.exchanges.solidly_v2 import SolidlyV2
from fastlane_bot.events.exchanges.solidly_v2 import EXCHANGE_INFO as SOLIDLY_EXCHANGE_INFO

nest_asyncio.apply()

ETHEREUM = "ethereum"
POLYGON = "polygon"
POLYGON_ZKEVM = "polygon_zkevm"
ARBITRUM_ONE = "arbitrum_one"
OPTIMISM = "optimism"
BASE = "coinbase_base"
FANTOM = "fantom"
MANTLE = "mantle"

coingecko_network_map = {
    "ethereum": "ethereum",
    "coinbase_base": "base",
    "polygon": "polygon-pos",
    "polygon_zkevm": "polygon-zkevm",
    "optimism": "optimistic-ethereum",
    "arbitrum_one": "arbitrum-one",
    "fantom": "fantom",
    "arbitrum_nova": "arbitrum-nova",
    "avalanche": "avalanche",
    "tron": "tron",
    "neon": "neon-evm",
    "moonbeam": "moonbeam",
    "linea": "linea",
    "cosmos": "cosmos",
    "kava": "kava",
    "mantle": "mantle",
}

BLOCK_CHUNK_SIZE_MAP = {
    "ethereum": 50000,
    "polygon": 250000,
    "polygon_zkevm": 500000,
    "arbitrum_one": 500000,
    "optimism": 500000,
    "coinbase_base": 250000,
    "fantom": 2000,
    "mantle": 10000000,
}

ALCHEMY_KEY_DICT = {
    "ethereum": "WEB3_ALCHEMY_PROJECT_ID",
    "polygon": "WEB3_ALCHEMY_POLYGON",
    "polygon_zkevm": "WEB3_ALCHEMY_POLYGON_ZKEVM",
    "arbitrum_one": "WEB3_ALCHEMY_ARBITRUM",
    "optimism": "WEB3_ALCHEMY_OPTIMISM",
    "coinbase_base": "WEB3_ALCHEMY_BASE",
    "fantom": "WEB3_FANTOM",
    "mantle": "WEB3_MANTLE",
}

ALCHEMY_RPC_LIST = {
    "ethereum": "https://eth-mainnet.alchemyapi.io/v2/",
    "polygon": "https://polygon-mainnet.g.alchemy.com/v2/",
    "polygon_zkevm": "https://polygonzkevm-mainnet.g.alchemy.com/v2/",
    "arbitrum_one": "https://arb-mainnet.g.alchemy.com/v2/",
    "optimism": "https://opt-mainnet.g.alchemy.com/v2/",
    "coinbase_base": "https://base-mainnet.g.alchemy.com/v2/",
    "fantom": "https://fantom-mainnet.blastapi.io/",
    "mantle": "https://rpc.mantle.xyz/",
}

BALANCER_SUBGRAPH_CHAIN_URL = {
    "ethereum": "https://api.thegraph.com/subgraphs/name/balancer-labs/balancer-v2",
    "polygon": "https://api.thegraph.com/subgraphs/name/balancer-labs/balancer-polygon-v2",
    "polygon_zkevm": "https://api.studio.thegraph.com/query/24660/balancer-polygon-zk-v2/version/latest",
    "arbitrum_one": "https://api.thegraph.com/subgraphs/name/balancer-labs/balancer-arbitrum-v2",
    "optimism": "https://api.thegraph.com/subgraphs/name/balancer-labs/balancer-optimism-v2",
    "coinbase_base": "https://api.studio.thegraph.com/query/24660/balancer-base-v2/version/latest",
    "avalanche": "https://api.thegraph.com/subgraphs/name/balancer-labs/balancer-avalanche-v2",
    "fantom": "https://api.thegraph.com/subgraphs/name/beethovenxfi/beethovenx",

}

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
AERODROME_V2_NAME = "aerodrome_v2"
VELOCIMETER_V2_NAME = "velocimeter_v2"
CARBON_POL_NAME = "bancor_pol"
SHIBA_V2_NAME = "shiba_v2"
SCALE_V2_NAME = "scale_v2"
EQUALIZER_V2_NAME = "equalizer_v2"
SOLIDLY_V2_NAME = "solidly_v2"
VELODROME_V2_NAME = "velodrome_v2"
CLEOPATRA_V2_NAME = "cleopatra_v2"
STRATUM_V2_NAME = "stratum_v2"

SOLIDLY_FORKS = [AERODROME_V2_NAME, VELOCIMETER_V2_NAME, SCALE_V2_NAME, VELODROME_V2_NAME, CLEOPATRA_V2_NAME, STRATUM_V2_NAME]


EXCHANGE_IDS = {
    BANCOR_V2_NAME: 1,
    BANCOR_V3_NAME: 2,
    UNISWAP_V2_NAME: 3,
    UNISWAP_V3_NAME: 4,
    SUSHISWAP_V2_NAME: 3,
    SUSHISWAP_V3_NAME: 4,
    CARBON_V1_NAME: 6,
    BALANCER_NAME: 7,
    CARBON_POL_NAME: 8,
    PANCAKESWAP_V2_NAME: 3,
    PANCAKESWAP_V3_NAME: 4,
    SOLIDLY_V2_NAME: 11,
    VELOCIMETER_V2_NAME: 11,
    SCALE_V2_NAME: 11,
    EQUALIZER_V2_NAME: 11,
    VELODROME_V2_NAME: 12,
    AERODROME_V2_NAME: 12,
    CLEOPATRA_V2_NAME: 12,
    STRATUM_V2_NAME: 12,
}

EXCHANGE_POOL_CREATION_EVENT_NAMES = {
    UNISWAP_V2_NAME: "PairCreated",
    UNISWAP_V3_NAME: "PoolCreated",
    AERODROME_V2_NAME: "PoolCreated",
    VELOCIMETER_V2_NAME: "PairCreated",
    SCALE_V2_NAME: "PairCreated",
    CLEOPATRA_V2_NAME: "PairCreated",
    STRATUM_V2_NAME: "PairCreated",
}

dataframe_key = [
    "cid",
    "strategy_id",
    "last_updated",
    "last_updated_block",
    "descr",
    "pair_name",
    "exchange_name",
    "fee",
    "fee_float",
    "address",
    "anchor",
    "tkn0_address",
    "tkn1_address",
    "tkn0_decimals",
    "tkn1_decimals",
    "exchange_id",
    "tkn0_symbol",
    "tkn1_symbol",
    "timestamp",
    "tkn0_balance",
    "tkn1_balance",
    "liquidity",
    "sqrt_price_q96",
    "tick",
    "tick_spacing",
    "exchange",
    "pool_type",
    "tkn0_weight",
    "tkn1_weight",
    "tkn2_address",
    "tkn2_decimals",
    "tkn2_symbol",
    "tkn2_balance",
    "tkn2_weight",
    "tkn3_address",
    "tkn3_decimals",
    "tkn3_symbol",
    "tkn3_balance",
    "tkn3_weight",
    "tkn4_address",
    "tkn4_decimals",
    "tkn4_symbol",
    "tkn4_balance",
    "tkn4_weight",
    "tkn5_address",
    "tkn5_decimals",
    "tkn5_symbol",
    "tkn5_balance",
    "tkn5_weight",
    "tkn6_address",
    "tkn6_decimals",
    "tkn6_symbol",
    "tkn6_balance",
    "tkn6_weight",
    "tkn7_address",
    "tkn7_decimals",
    "tkn7_symbol",
    "tkn7_balance",
    "tkn7_weight",
]
skip_token_list = ["0xaD67F7a72BA2ca971390B2a1dD907303bD577a4F".lower()]


@dataclass
class TokenManager:
    token_dict: Dict


def get_all_token_details(web3: Web3, network: str, write_path: str) -> TokenManager:
    """
    This function collects the number of decimals and symbol of a token, and formats it for use in a dataframe.
    :param web3: the Web3 reference
    :param network: the network name

    :returns: Dict
    """

    token_path = os.path.join(write_path, "tokens.csv")
    token_file_exists = os.path.exists(token_path)
    if token_file_exists:
        token_df = pd.read_csv(token_path, index_col=False)

        token_dict = {}
        for idx, row in token_df.iterrows():
            address, decimals, symbol = row
            token_dict[address] = {"address": address, "decimals": decimals, "symbol": symbol}

        return TokenManager(token_dict)

    url = f"https://tokens.coingecko.com/{coingecko_network_map[network]}/all.json"
    response = requests.get(url).json()["tokens"]
    token_dict = {
        "0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE": {"address": "0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE",
                                                       "decimals": 18, "symbol": "ETH"}
    } if network in ["ethereum", "coinbase_base", "arbitrum_one", "optimism"] else {}
    for token in response:
        address = web3.to_checksum_address(token.get("address"))
        symbol = token.get("symbol")
        decimals = token.get("decimals")
        try:
            # try to write to csv
            pd.DataFrame(
                {"token": [address], "symbol": [symbol], "decimals": [decimals]}
            ).to_csv("token_details.csv")
            token_dict[address] = {
                "address": address,
                "decimals": decimals,
                "symbol": symbol,
            }
        except Exception as e:
            print(f"Failed to get token details for token: {address} with error: {e}")
            continue
    return TokenManager(token_dict=token_dict)


def get_token_details_from_contract(
        token: str, web3
) -> Tuple[str, int] or Tuple[None, None]:
    """
    This function collects the number of decimals and symbol of a token, and formats it for use in a dataframe.
    :param token: the token address
    :param web3: the Web3 object

    Returns: a Tuple containing the token symbol & decimals, or None, None if the contract call failed.
    """
    if token == "0x9f8F72aA9304c8B593d555F12eF6589cC3A579A2":
        symbol = "MKR"
        decimals = 18
    elif token == "0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE":
        symbol = "ETH"
        decimals = 18
    if token.lower() in skip_token_list:
        return None, None
    else:
        contract = web3.eth.contract(
            address=web3.to_checksum_address(token), abi=ERC20_ABI
        )
        try:
            contract = web3.eth.contract(
                address=web3.to_checksum_address(token), abi=ERC20_ABI
            )
            decimals = contract.caller.decimals()

        except:
            print(f"Cannot get token details for token: {token}")
            skip_token_list.append(token.lower())
            return None, None
        try:
            symbol = contract.caller.symbol()
            # attempt to write to csv
            pd.DataFrame(
                {"token": [token], "symbol": [symbol], "decimals": [decimals]}
            ).to_csv("token_details.csv")
        except Exception as e:
            symbol = "SYMBOL_FAILED"
    return symbol, decimals


def get_token_details(
        tkn: str, token_manager: TokenManager, web3: Web3
) -> Tuple[str, int] or Tuple[None, None]:
    """
    :param tkn: the token address
    :param token_manager: the token lookup dict
    :param web3: the Web3 object

    Returns: a Tuple containing the token symbol & decimals, or None, None if the contract call failed.
    """
    tkn = web3.to_checksum_address(tkn)
    if tkn in token_manager.token_dict:
        symbol = token_manager.token_dict.get(tkn).get("symbol")
        decimal = token_manager.token_dict.get(tkn).get("decimals")
    else:
        symbol, decimal = get_token_details_from_contract(token=tkn, web3=web3)
        if type(decimal) == int and type(symbol) == str:
            token_manager.token_dict[tkn] = {"address": tkn, "decimals": decimal, "symbol": symbol}
    return symbol, decimal


def fix_missing_symbols(symbol: str, addr: str) -> str:
    """
    This function fixes specific tokens that have an issue getting their Symbol from the contract.

    :param symbol: the token symbol
    :param addr: the token address

    returns: str
    """
    if addr == "0x9f8f72aa9304c8b593d555f12ef6589cc3a579a2":
        return "MKR"
    elif (
            addr == "0xF1290473E210b2108A85237fbCd7b6eb42Cc654F"
            or addr.lower() == "0xF1290473E210b2108A85237fbCd7b6eb42Cc654F".lower()
    ):
        return "HEDG"
    else:
        return symbol


def skip_tokens(addr: str) -> bool:
    """
    This function checks against a list of tokens that should be skipped due to problems in their contract, etc.
    :param addr: the token address

    retuns: bool
    """
    if addr.lower() in skip_token_list:
        return True
    else:
        return False


def get_token_prices_coingecko(token_list: Dict) -> Dict:
    """
    :param token_list: the list of tokens for which to fetch prices

    Returns token prices using Coingecko API
    """

    max_size = 100
    tkn_addresses = list(token_list.keys())
    tkn_sublists = [
        tkn_addresses[x: x + max_size] for x in range(0, len(tkn_addresses), max_size)
    ]

    for tkn_sublist in tkn_sublists:
        tokens = ",".join(tkn_sublist)
        url = f"https://api.coingecko.com/api/v3/simple/token_price/ethereum?contract_addresses={tokens}&vs_currencies=USD&include_market_cap=false&include_24hr_vol=false&include_24hr_change=false&include_last_updated_at=false"
        response = requests.get(url)

        if response.status_code == 200:
            data = response.json()
            if data is not None:
                prices = []
                for tkn in data.keys():
                    try:
                        prices.append((tkn, data[tkn]["usd"]))
                    except KeyError:
                        prices.append((tkn, 0))
                        continue

                for tkn in prices:
                    for tkn_addrs in token_list.keys():
                        if tkn[0].lower() == tkn_addrs.lower():
                            token_list[tkn_addrs]["usd"] = float(tkn[1])
    return token_list


def generate_token_price_map(pool_data: Dict, web3: Web3) -> Dict:
    """
    This function retrieves token prices from Coingecko
    :param pool_data: list of pools
    :param web3: the Web3 object

    returns: a dict containing token prices

    """
    token_prices = {}

    for pool in pool_data:
        tokens = pool["tokens"]
        for tkn in tokens:
            address = tkn["address"]
            if skip_tokens(addr=address):
                continue
            symbol = tkn["symbol"]
            symbol = fix_missing_symbols(addr=address, symbol=symbol)

            address = web3.to_checksum_address(address)
            token_prices[str(address)] = {"tokenSymbol": str(symbol), "usd": None}

    token_prices = get_token_prices_coingecko(token_list=token_prices)
    return token_prices


def organize_pool_details_uni_v3(
        pool_data: Dict, token_manager: TokenManager, exchange: str, web3: Web3
) -> Dict:
    """
    This function organizes pool details for Uni V3 pools.
    :param pool_data: the pool data from the pool creation event
    :param token_manager: the token lookup dict
    :param exchange: the exchange name
    :param web3: the Web3 object

    returns: dict of pool information
    """
    skip_pool = False
    pool_address = pool_data["args"]["pool"]
    pool_address = web3.to_checksum_address(pool_address)
    last_updated_block = pool_data["blockNumber"]
    token_info = {}
    pair = ""
    tick_spacing = pool_data["args"]["tickSpacing"]
    if "tkn0_address" in pool_data["args"]:
        tokens = [pool_data["args"]["tkn0_address"], pool_data["args"]["tkn1_address"]]
    elif "token0" in pool_data["args"]:
        tokens = [pool_data["args"]["token0"], pool_data["args"]["token1"]]
    else:
        print(f"failed to get tkn0_address for exchange: {exchange} from pool_data: {pool_data}")
        assert False
    if len(tokens) > 2:
        return None
    token_info, pair, skip_pool = process_token_details(
        tokens=tokens, token_manager=token_manager, web3=web3
    )
    if skip_pool:
        return None
    pair = pair[:-1]
    fee = pool_data["args"]["fee"]

    description = exchange + " " + pair + " " + str(fee)

    pool_info = {
        "cid": pool_address,
        "strategy_id": 0,
        "last_updated": "",
        "last_updated_block": last_updated_block,
        "descr": description,
        "pair_name": pair,
        "exchange_name": exchange,
        "fee": fee,
        "fee_float": float(fee) / 1000000,
        "address": pool_address,
        "anchor": "",
        "tkn0_address": token_info["tkn0_address"],
        "tkn1_address": token_info["tkn1_address"],
        "tkn0_decimals": token_info["tkn0_decimals"],
        "tkn1_decimals": token_info["tkn1_decimals"],
        "exchange_id": EXCHANGE_IDS.get("uniswap_v3"),
        "tkn0_symbol": token_info["tkn0_symbol"],
        "tkn1_symbol": token_info["tkn1_symbol"],
        "timestamp": 0,
        "tkn0_balance": 0,
        "tkn1_balance": 0,
        "liquidity": 0,
        "sqrt_price_q96": 0,
        "tick": 0,
        "tick_spacing": tick_spacing,
        "exchange": exchange,
    }
    pool = {**pool_info, **token_info}
    return pool


def process_token_details(
        tokens: List[str], token_manager: TokenManager, web3: Web3
) -> Tuple[Dict, str, bool] or Tuple[None, None, bool]:
    """
    This function processes token details & generates the token pair

    :param tokens: the list of tokens
    :param token_manager: the token information dict
    :param web3: the Web3 object

    returns: tuple containing a dict with token information, the pair name as a string, and a bool that indicates if all tokens were successfully added.
    """
    token_info = {}
    pair = ""
    for idx, tkn in enumerate(tokens):
        tkn_num = "tkn" + str(idx)
        address = tkn

        if skip_tokens(addr=address):
            return None, None, True
        address = web3.to_checksum_address(address)
        symbol, decimals = get_token_details(
            token_manager=token_manager, tkn=address, web3=web3
        )
        if symbol is None:
            return None, None, True
        symbol = fix_missing_symbols(addr=address, symbol=symbol)
        token_info[tkn_num + "_decimals"] = decimals
        token_info[tkn_num + "_address"] = address
        token_info[tkn_num + "_symbol"] = symbol
        token_info[tkn_num + "_balance"] = 0

        pair += address + "/"
    pair = pair[:-1]

    return token_info, pair, False


def organize_pool_details_balancer(
        pool_data: Dict, token_prices: Dict, web3: Web3, min_usd: int = 100000
):
    """
    This function organizes pool details for Uni V3 pools.
    :param pool_data: the pool data from the pool creation event
    :param token_prices: the token prices
    :param web3: the Web3 object
    :param min_usd: the minimum pool balance in USD to include the pool

    returns: dict of pool information
    """
    skip_pool = False
    if pool_data["swapEnabled"] != True:
        return None

    pool_id = pool_data["id"]
    pool_type = pool_data["poolType"]
    pool_address = pool_data["address"]
    pool_address = web3.to_checksum_address(pool_address)
    token_info = {}
    tokens = pool_data["tokens"]

    pair = ""

    pool_total_liquidity_usd = 0

    for idx, tkn in enumerate(tokens):
        tkn_num = "tkn" + str(idx)
        address = tkn["address"]
        address = web3.to_checksum_address(address)
        if skip_tokens(addr=address):
            skip_pool = True
            break

        symbol = tkn["symbol"]
        symbol = fix_missing_symbols(addr=address, symbol=symbol)

        # Currently unused - this gets the pool balance, but is only usable accurately on Mainnet
        # balance = float(tkn["balance"])
        # tkn_price = 0 if token_prices[address]["usd"] is None else float(token_prices[address]["usd"])
        # tkn_val_usd = balance * tkn_price
        # pool_total_liquidity_usd += tkn_val_usd

        token_info[tkn_num + "_address"] = address
        token_info[tkn_num + "_symbol"] = symbol
        token_info[tkn_num + "_decimals"] = tkn["decimals"]
        token_info[tkn_num + "_weight"] = tkn["weight"]
        token_info[tkn_num + "_balance"] = 0

        pair += address + "/"

    # if pool_total_liquidity_usd < min_usd:
    #     print(f"pool eliminated due to low liquidity: {pool_total_liquidity_usd} vs min {min_usd}")
    #     return None

    if skip_pool:
        return None

    pair = pair[:-1]
    fee = pool_data["swapFee"]
    exchange = "balancer"

    description = exchange + " " + pair + " " + str(fee)

    pool_info = {
        "cid": pool_id,
        "strategy_id": 0,
        "last_updated": "",
        "last_updated_block": 0,
        "descr": description,
        "pair_name": pair,
        "exchange_name": exchange,
        "fee": float(fee) * 10 ** 18,
        "fee_float": float(fee),
        "address": pool_address,
        "anchor": pool_id,
        "tkn0_address": token_info["tkn0_address"],
        "tkn1_address": token_info["tkn1_address"],
        "tkn0_decimals": token_info["tkn0_decimals"],
        "tkn1_decimals": token_info["tkn1_decimals"],
        "exchange_id": 7,
        "tkn0_symbol": token_info["tkn0_symbol"],
        "tkn1_symbol": token_info["tkn1_symbol"],
        "timestamp": 0,
        "tkn0_balance": 0,
        "tkn1_balance": 0,
        "liquidity": 0,
        "sqrt_price_q96": 0,
        "tick": 0,
        "tick_spacing": 0,
        "exchange": "balancer",
        "pool_type": pool_type,
    }
    pool = {**pool_info, **token_info}

    return pool


def organize_pool_details_uni_v2(
        pool_data, token_manager: TokenManager, exchange, default_fee, web3
):
    """
    This function organizes pool details for Uni V2 pools.
    :param pool_data: the pool data from the pool creation event
    :param token_addr_lookup: the token lookup dict
    :param exchange: the exchange name
    :param default_fee: the fee for the exchange
    :param web3: the Web3 object

    returns: dict of pool information
    """
    skip_pool = False
    pool_address = pool_data["args"]["pair"]
    pool_address = web3.to_checksum_address(pool_address)
    last_updated_block = pool_data["blockNumber"]
    token_info = {}
    pair = ""
    if default_fee == "TBD":
        return None
    default_fee = float(default_fee)
    if "tkn0_address" in pool_data["args"]:
        tokens = [pool_data["args"]["tkn0_address"], pool_data["args"]["tkn1_address"]]
    elif "token0" in pool_data["args"]:
        tokens = [pool_data["args"]["token0"], pool_data["args"]["token1"]]
    else:
        print(f"failed to get tkn0_address for exchange: {exchange} from pool_data: {pool_data}")
        assert False
    if len(tokens) > 2:
        return None
    token_info, pair, skip_pool = process_token_details(
        tokens=tokens, token_manager=token_manager, web3=web3
    )
    if skip_pool:
        return None
    description = exchange + " " + pair

    pool_info = {
        "cid": pool_address,
        "strategy_id": 0,
        "last_updated": "",
        "last_updated_block": last_updated_block,
        "descr": description,
        "pair_name": pair,
        "exchange_name": exchange,
        "fee": default_fee,
        "fee_float": default_fee,
        "address": pool_address,
        "anchor": "",
        "tkn0_address": token_info["tkn0_address"],
        "tkn1_address": token_info["tkn1_address"],
        "tkn0_decimals": token_info["tkn0_decimals"],
        "tkn1_decimals": token_info["tkn1_decimals"],
        "exchange_id": EXCHANGE_IDS.get("uniswap_v2"),
        "tkn0_symbol": token_info["tkn0_symbol"],
        "tkn1_symbol": token_info["tkn1_symbol"],
        "timestamp": 0,
        "tkn0_balance": 0,
        "tkn1_balance": 0,
        "exchange": exchange,
    }
    pool = {**pool_info, **token_info}

    return pool


def organize_pool_details_solidly_v2(
        pool_data, token_manager, exchange, exchange_object, web3, async_web3,
):
    """
    This function organizes pool details for Solidly pools.

    :param pool_data: the pool data from the pool creation event
    :param token_manager: the token lookup dict
    :param exchange: the exchange name
    :param factory_contract: the exchange's Factory contract - initialized
    :param web3: the Web3 object
    :param web3: the async Web3 object
    returns: dict of pool information
    """
    skip_pool = False
    if "pool" in pool_data or "pool" in pool_data["args"]:
        pool_address = pool_data["args"]["pool"]
    elif "pair" in pool_data or "pair" in pool_data["args"]:
        pool_address = pool_data["args"]["pair"]
    else:
        print(f"COULD NOT FIND KEY IN EVENT for exchange {exchange}: {pool_data}")
    pool_address = web3.to_checksum_address(pool_address)

    last_updated_block = pool_data["blockNumber"]

    stable_pool = "stable" if pool_data["args"]["stable"] else "volatile"
    pool_contract = async_web3.eth.contract(address=pool_address, abi=exchange_object.get_abi())
    fee_str, fee_float = asyncio.get_event_loop().run_until_complete(asyncio.gather(exchange_object.get_fee(address=pool_address, contract=pool_contract)))[0]


    tokens = [pool_data["args"]["token0"], pool_data["args"]["token1"]]

    if len(tokens) > 2:
        return None
    token_info, pair, skip_pool = process_token_details(
        tokens=tokens, token_manager=token_manager, web3=web3
    )
    if skip_pool:
        return None
    description = exchange + " " + pair

    pool_info = {
        "cid": pool_address,
        "strategy_id": 0,
        "last_updated": "",
        "last_updated_block": last_updated_block,
        "descr": description,
        "pair_name": pair,
        "exchange_name": exchange,
        "fee": fee_str,
        "fee_float": fee_float,
        "address": pool_address,
        "anchor": "",
        "tkn0_address": token_info["tkn0_address"],
        "tkn1_address": token_info["tkn1_address"],
        "tkn0_decimals": token_info["tkn0_decimals"],
        "tkn1_decimals": token_info["tkn1_decimals"],
        "exchange_id": EXCHANGE_IDS.get(exchange),
        "tkn0_symbol": token_info["tkn0_symbol"],
        "tkn1_symbol": token_info["tkn1_symbol"],
        "timestamp": 0,
        "tkn0_balance": 0,
        "tkn1_balance": 0,
        "exchange": exchange,
        "pool_type": stable_pool,
    }
    pool = {**pool_info, **token_info}

    return pool


def _get_events(contract, blockchain: str, exchange: str, start_block: int) -> list:
    end_block = contract.w3.eth.block_number + 1
    chunk_size = BLOCK_CHUNK_SIZE_MAP[blockchain]
    block_numbers = list(range(start_block, end_block, chunk_size)) + [end_block]
    event_method = contract.events[EXCHANGE_POOL_CREATION_EVENT_NAMES[exchange]].get_logs
    events_list = [event_method(fromBlock=block_numbers[n-1], toBlock=block_numbers[n]-1) for n in range(1, len(block_numbers))]
    return [event for events in events_list for event in events]


def get_uni_v3_pools(
        token_manager: TokenManager,
        exchange: str,
        factory_contract,
        start_block: int,
        web3: Web3,
        blockchain: str
) -> Tuple[DataFrame, DataFrame]:
    """
    This function retrieves Uniswap V3 pool generation events and organizes them into two Dataframes

    :param token_addr_lookup: the dict containing token information
    :param factory_contract: the initialized Factory contract
    :param start_block: the block number from which to start
    :param web3: the Web3 object
    :param exchange: the name of the exchange
    :param blockchain: the blockchain name

    returns: a tuple containing a Dataframe of pool creation and a Dataframe of Uni V3 pool mappings
    """
    pool_data = _get_events(factory_contract, blockchain, UNISWAP_V3_NAME, start_block)

    with parallel_backend(n_jobs=-1, backend="threading"):
        pools = Parallel(n_jobs=-1)(
            delayed(organize_pool_details_uni_v3)(
                pool_data=pool,
                token_manager=token_manager,
                exchange=exchange,
                web3=web3,
            )
            for pool in pool_data
        )

    pools = [pool for pool in pools if pool is not None]
    df = pd.DataFrame(pools, columns=dataframe_key)
    pool_mapping = [
        {"exchange": pool["exchange"], "address": pool["address"]} for pool in pools
    ]
    mapdf = pd.DataFrame(pool_mapping, columns=["exchange", "address"])
    mapdf = mapdf.reset_index(drop=True)
    # mapdf = mapdf.set_index("exchange")
    #return mapdf
    return df, mapdf

def get_uni_v2_pools(
        token_manager: TokenManager,
        exchange: str,
        factory_contract,
        start_block: int,
        default_fee: float,
        web3: Web3,
        blockchain: str
) -> Tuple[DataFrame, DataFrame]:
    """
    This function retrieves Uniswap V2 pool generation events and organizes them into two Dataframes

    :param token_addr_lookup: the dict containing token information
    :param factory_contract: the initialized Factory contract
    :param start_block: the block number from which to start
    :param web3: the Web3 object
    :param exchange: the name of the exchange
    :param default_fee: the fee for the exchange
    :param blockchain: the blockchain name
    returns: a tuple containing a Dataframe of pool creation and a Dataframe of Uni V3 pool mappings
    """
    pool_data = _get_events(factory_contract, blockchain, UNISWAP_V2_NAME, start_block)

    with parallel_backend(n_jobs=-1, backend="threading"):
        pools = Parallel(n_jobs=-1)(
            delayed(organize_pool_details_uni_v2)(
                pool_data=pool,
                token_manager=token_manager,
                default_fee=default_fee,
                exchange=exchange,
                web3=web3,
            )
            for pool in pool_data
        )
    pools = [pool for pool in pools if pool is not None]
    df = pd.DataFrame(pools, columns=dataframe_key)
    pool_mapping = [
        {"exchange": pool["exchange"], "address": pool["address"]} for pool in pools
    ]

    mapdf = pd.DataFrame(pool_mapping, columns=["exchange", "address"])
    mapdf = mapdf.reset_index(drop=True)
    #return mapdf
    return df, mapdf

def get_solidly_v2_pools(
        token_manager: TokenManager,
        exchange: str,
        async_factory_contract,
        factory_contract,
        start_block: int,
        web3: Web3,
        async_web3: AsyncWeb3,
        blockchain: str
) -> Tuple[DataFrame, DataFrame]:
    """
    This function retrieves Solidly pool generation events and organizes them into two Dataframes
    :param token_manager: the dict containing token information
    :param factory_contract: the initialized Factory contract
    :param start_block: the block number from which to start
    :param web3: the Web3 object
    :param async_web3: the Async Web3 object
    :param exchange: the name of the exchange
    :param default_fee: the fee for the exchange
    :param blockchain: the blockchain name

    returns: a tuple containing a Dataframe of pool creation and a Dataframe of Uni V3 pool mappings
    """
    pool_data = _get_events(factory_contract, blockchain, exchange, start_block)
    solidly_exchange = SolidlyV2(exchange_name=exchange, factory_contract=async_factory_contract)

    with parallel_backend(n_jobs=-1, backend="threading"):
        pools = Parallel(n_jobs=-1)(
            delayed(organize_pool_details_solidly_v2)(
                pool_data=pool,
                token_manager=token_manager,
                exchange=exchange,
                exchange_object=solidly_exchange,
                web3=web3,
                async_web3=async_web3,
            )
            for pool in pool_data
        )
    pools = [pool for pool in pools if pool is not None]
    df = pd.DataFrame(pools, columns=dataframe_key)
    pool_mapping = [
        {"exchange": pool["exchange"], "address": pool["address"]} for pool in pools
    ]

    mapdf = pd.DataFrame(pool_mapping, columns=["exchange", "address"])
    mapdf = mapdf.reset_index(drop=True)
    # return mapdf
    return df, mapdf


def get_multichain_addresses(network: str, exchanges: List[str] = None) -> pd.DataFrame:
    """
    Create dataframe of addresses for the selected network
    :param network: the network in which to get addresses
    :param exchanges: (Optional) the list of exchanges for which to get data
    returns:
    A dataframe that contains items from the selected network
    """
    multichain_address_path = os.path.normpath(
        "fastlane_bot/data/multichain_addresses.csv"
    )
    chain_addresses_df = pd.read_csv(multichain_address_path)
    network_df = chain_addresses_df.loc[chain_addresses_df["chain"] == network]
    if exchanges is not None:
        return network_df.loc[chain_addresses_df["exchange"] in exchanges]

    return network_df


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


# Balancer subgraph query
query = """
{
pools(
    orderBy: totalLiquidity
    orderDirection: desc
    first: 1000
    where: {poolType_contains: "Weighted", totalLiquidity_gt: 50000 }
  ) {
    id
    poolType
    swapFee
    swapEnabled
    tokens {
      balance
      symbol
      decimals
      address
      weight
    }
    address
  }
}
"""


# function to use requests.post to make an API call to the subgraph url
def run_query(subgraph_query: str, subgraph_url: str) -> json:
    """
    This function executes the Balancer Subgraph query
    :param subgraph_query: the Balancer query for the Graph
    :param subgraph_url: the URL of the relevant Balancer subgraph

    returns: a JSON object containing pool details
    """
    # endpoint where you are making the request
    url = subgraph_url

    request = requests.post(url, json={"query": subgraph_query})
    if request.status_code == 200:
        return request.json()
    else:
        raise Exception(
            "Query failed. return code is {}.      {}".format(
                request.status_code, subgraph_query
            )
        )


def get_balancer_pools(subgraph_url: str, web3: Web3) -> pd.DataFrame:
    """
    This function gets Balancer pool details from the Balancer subgraph

    :param subgraph_url: the URL of the Balancer subgraph
    :param web3: the Web3 object
    """
    pool_data = run_query(subgraph_query=query, subgraph_url=subgraph_url)["data"][
        "pools"
    ]

    token_prices = generate_token_price_map(pool_data=pool_data, web3=web3)
    # print(token_prices)
    pools = []
    for pool in pool_data:
        pools.append(
            organize_pool_details_balancer(
                pool_data=pool, token_prices=token_prices, web3=web3
            )
        )
    pools = [pool for pool in pools if pool is not None]
    df = pd.DataFrame(pools, columns=dataframe_key)
    return df


def add_to_exchange_ids(exchange: str, fork: str):
    """
    This function adds an exchange if it is not listed in the Exchange Ids dict

    :param exchange: the exchange name
    :param fork: the fork name
    """
    if exchange not in EXCHANGE_IDS:
        platform_id = 0
        if fork in ["uniswap_v2", "solidly_v1", "solidly_v2"]:
            platform_id = 3
        elif fork in "uniswap_v3":
            platform_id = 4
        elif fork in "balancer":
            platform_id = 7
        elif fork in "carbon_v1":
            platform_id = 6
        EXCHANGE_IDS[exchange] = platform_id


def get_web3_for_network(network_name: str) -> Tuple[Web3, AsyncWeb3]:
    """
    This function gets a web3 object for a specific network. This is meant for use when the terraformer is a standalone script.
    :param network_name: the name of the blockchain from which to get data

    returns: web3 object
    """
    try:
        alchemy_rpc = ALCHEMY_RPC_LIST[network_name]
        ALCHEMY_API_KEY = os.environ.get(ALCHEMY_KEY_DICT[network_name])
    except ValueError:
        print(
            f"Terraformer: network {network_name} does not have Alchemy RPC set. Add an RPC to continue"
        )
        return None
    return Web3(Web3.HTTPProvider(f"{alchemy_rpc}{ALCHEMY_API_KEY}")), AsyncWeb3(AsyncWeb3.AsyncHTTPProvider(f"{alchemy_rpc}{ALCHEMY_API_KEY}"))


def get_last_block_updated(df: pd.DataFrame, exchange: str) -> int:
    """
    This function retrieves the highest block number for relevant exchanges
    :param df: the Dataframe containing static pool data
    :param exchange: the exchange for which to get the latest block it was updated

    returns: int
    """

    ex_df = df[df["exchange"] == exchange]

    # if the `last_updated_block` column contains `None` values, then `max` returns a value of type `float`
    # we should therefore verify that this value is nevertheless integer
    # and only then can we safely convert it to type `int`
    return safe_int(ex_df["last_updated_block"].max())


def save_token_data(token_dict: TokenManager, write_path: str):
    """
    Saves token data to a CSV

    """

    token_path = os.path.join(write_path, "tokens.csv")
    token_list = []

    for key in token_dict.token_dict.keys():
        token_list.append(token_dict.token_dict[key])

    token_df = pd.DataFrame(token_list, columns=["address", "decimals", "symbol"])
    token_df.set_index("address", inplace=True)
    token_df.to_csv(token_path)


def terraform_blockchain(network_name: str, web3: Web3 = None, async_web3: AsyncWeb3 = None, start_block: int = None, save_tokens: bool = False):
    """
    This function collects all pool creation events for Uniswap V2/V3 and Solidly pools for a given network. The factory addresses for each exchange for which to extract pools must be defined in fastlane_bot/data/multichain_addresses.csv

    :param network_name: the name of the blockchain from which to get data
    :param web3: the Web3 object
    :param async_web3: the async Web3 object
    :param start_block: the block from which to get data. If this is None, it uses the factory creation block for each exchange.
    """

    assert network_name in BLOCK_CHUNK_SIZE_MAP.keys(), f"Blockchain: {network_name} not supported. Supported blockchains: {BLOCK_CHUNK_SIZE_MAP.keys()}"

    if web3 is None:
        web3, async_web3 = get_web3_for_network(network_name=network_name)

    assert web3.is_connected(), f"Web3 is not connected for network: {network_name}"

    PROJECT_PATH = os.path.normpath(f"{os.getcwd()}")
    write_path = os.path.normpath(
        f"{PROJECT_PATH}/fastlane_bot/data/blockchain_data/{network_name}"
    )
    path_exists = os.path.exists(write_path)
    data_path = os.path.normpath(write_path + "/static_pool_data.csv")
    data_exists = os.path.exists(data_path)
    fresh_data = False
    token_manager = get_all_token_details(web3, network=network_name, write_path=write_path)

    if not path_exists:
        os.makedirs(write_path)
    if not data_exists:
        exchange_df = pd.DataFrame(columns=dataframe_key)
        univ2_mapdf = pd.DataFrame(columns=["exchange", "address"])
        univ3_mapdf = pd.DataFrame(columns=["exchange", "address"])
        solidly_v2_mapdf = pd.DataFrame(columns=["exchange", "address"])
        fresh_data = True
    else:
        exchange_df = pd.read_csv(
            write_path + "/static_pool_data.csv",
            low_memory=False,
            dtype=str,
            index_col=False,
        )
        univ2_mapdf = pd.read_csv(
            write_path + "/uniswap_v2_event_mappings.csv", index_col=False
        )
        univ3_mapdf = pd.read_csv(
            write_path + "/uniswap_v3_event_mappings.csv", index_col=False
        )
        solidly_v2_mapdf = pd.read_csv(
            write_path + "/solidly_v2_event_mappings.csv", index_col=False
        )

    if save_tokens:
        save_token_data(token_dict=token_manager, write_path=write_path)

    multichain_df = get_multichain_addresses(network=network_name)

    for row in multichain_df.iterrows():
        exchange_name = row[1]["exchange_name"]
        chain = row[1]["chain"]
        fork = row[1]["fork"]
        factory_address = row[1]["factory_address"]
        router_address = row[1]["router_address"]
        fee = row[1]["fee"]

        if row[1]["active"] == "FALSE":
            continue

        if fresh_data and not start_block:
            from_block = int(row[1]["start_block"]) if not math.isnan(row[1]["start_block"]) else 0
        if start_block is None:
            from_block = int(row[1]["start_block"]) if not math.isnan(row[1]["start_block"]) else 0
        if factory_address is None or type(factory_address) != str:
            print(
                f"Terraformer: No factory contract address for exchange: {exchange_name}"
            )
            continue
        elif factory_address == "TBD":
            continue
        print(f"********************** Terraforming **********************\nStarting exchange: {exchange_name} from block {from_block}")

        if fork in "uniswap_v2":
            if fee == "TBD":
                continue
            if fork in SOLIDLY_FORKS:
                continue

            if exchange_name in "alienbase_v2":
                factory_abi = ALIENBASE_V2_FACTORY_ABI
            elif exchange_name in ["pancakeswap_v2", "alienbase_v2", "baseswap_v2"]:
                factory_abi = PANCAKESWAP_V2_FACTORY_ABI
            else:
                factory_abi = UNISWAP_V2_FACTORY_ABI
            add_to_exchange_ids(exchange=exchange_name, fork=fork)

            factory_contract = web3.eth.contract(
                address=factory_address, abi=factory_abi
            )
            u_df, m_df = get_uni_v2_pools(
                token_manager=token_manager,
                exchange=exchange_name,
                factory_contract=factory_contract,
                default_fee=fee,
                start_block=from_block,
                web3=web3,
                blockchain=network_name
            )
            m_df = m_df.reset_index(drop=True)
            univ2_mapdf = pd.concat([univ2_mapdf, m_df], ignore_index=True)
        elif fork in "uniswap_v3":
            if fee == "TBD":
                continue
            add_to_exchange_ids(exchange=exchange_name, fork=fork)
            factory_abi = UNISWAP_V3_FACTORY_ABI if exchange_name not in ["pancakeswap_v3"] else PANCAKESWAP_V3_FACTORY_ABI
            factory_contract = web3.eth.contract(
                address=factory_address, abi=factory_abi
            )
            u_df, m_df = get_uni_v3_pools(
                token_manager=token_manager,
                exchange=exchange_name,
                factory_contract=factory_contract,
                start_block=from_block,
                web3=web3,
                blockchain=network_name
            )
            m_df = m_df.reset_index(drop=True)
            univ3_mapdf = pd.concat([univ3_mapdf, m_df], ignore_index=True)
        elif "solidly" in fork:
            add_to_exchange_ids(exchange=exchange_name, fork=fork)

            factory_abi = SOLIDLY_EXCHANGE_INFO[exchange_name]["factory_abi"]
            factory_contract = web3.eth.contract(
                address=factory_address, abi=factory_abi
            )

            async_factory_contract = async_web3.eth.contract(
                address=factory_address, abi=factory_abi
            )
            u_df, m_df = get_solidly_v2_pools(
                token_manager=token_manager,
                exchange=exchange_name,
                factory_contract=factory_contract,
                async_factory_contract=async_factory_contract,
                start_block=from_block,
                web3=web3,
                async_web3=async_web3,
                blockchain=network_name
            )
            m_df = m_df.reset_index(drop=True)
            solidly_v2_mapdf = pd.concat([solidly_v2_mapdf, m_df], ignore_index=True)
        elif "balancer" in fork:
            try:
                subgraph_url = BALANCER_SUBGRAPH_CHAIN_URL[network_name]
                u_df = get_balancer_pools(subgraph_url=subgraph_url, web3=web3)
            except:
                print(f"Could not find Balancer subgraph URL for chain: {network_name}")
                continue
        else:
            print(f"Fork {fork} for exchange {exchange_name} not in supported forks.")
            continue
        exchange_df = pd.concat([exchange_df, u_df])

    if save_tokens:
        save_token_data(token_dict=token_manager, write_path=write_path)

    exchange_df.to_csv((write_path + "/static_pool_data.csv"), index=False)
    univ2_mapdf.to_csv((write_path + "/uniswap_v2_event_mappings.csv"), index=False)
    univ3_mapdf.to_csv((write_path + "/uniswap_v3_event_mappings.csv"), index=False)
    solidly_v2_mapdf.to_csv((write_path + "/solidly_v2_event_mappings.csv"), index=False)
    return exchange_df, univ2_mapdf, univ3_mapdf, solidly_v2_mapdf


#terraform_blockchain(network_name="mantle", save_tokens=True)
