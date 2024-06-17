import math
from typing import Tuple, List, Dict

import pandas as pd
from dotenv import load_dotenv
from joblib import parallel_backend, Parallel, delayed
from pandas import DataFrame

load_dotenv()
import os
import requests
import pathlib

from web3 import Web3, AsyncWeb3

from fastlane_bot.utils import safe_int
from fastlane_bot.events.exchanges.solidly_v2 import SolidlyV2
from fastlane_bot.data.abi import ERC20_ABI, UNISWAP_V2_FACTORY_ABI, UNISWAP_V3_FACTORY_ABI

import asyncio
import nest_asyncio
import threading

def start_background_loop(loop):
    asyncio.set_event_loop(loop)
    loop.run_forever()

_LOOP = asyncio.new_event_loop()
_LOOP_THREAD = threading.Thread(target=start_background_loop, args=(_LOOP,), daemon=True)
_LOOP_THREAD.start()

def asyncio_gather(*futures, return_exceptions=False) -> list:
    """
    A version of asyncio.gather that runs on the internal event loop
    """
    async def gather():
        return await asyncio.gather(*futures, return_exceptions=return_exceptions)
    return asyncio.run_coroutine_threadsafe(gather(), loop=_LOOP).result()

nest_asyncio.apply()

ETHEREUM = "ethereum"
POLYGON = "polygon"
POLYGON_ZKEVM = "polygon_zkevm"
ARBITRUM_ONE = "arbitrum_one"
OPTIMISM = "optimism"
BASE = "coinbase_base"
FANTOM = "fantom"
MANTLE = "mantle"
LINEA = "linea"
SEI = "sei"

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
    "sei": "sei",
}

BLOCK_CHUNK_SIZE_MAP = {
    "ethereum": 0,
    "polygon": 0,
    "polygon_zkevm": 0,
    "arbitrum_one": 0,
    "optimism": 0,
    "coinbase_base": 0,
    "fantom": 5000,
    "mantle": 0,
    "linea": 0,
    "sei": 2000,
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
    "linea": "WEB3_LINEA",
    "sei": "WEB3_SEI",
}

ALCHEMY_RPC_LIST = {
    "ethereum": "https://eth-mainnet.alchemyapi.io/v2/",
    "polygon": "https://polygon-mainnet.g.alchemy.com/v2/",
    "polygon_zkevm": "https://polygonzkevm-mainnet.g.alchemy.com/v2/",
    "arbitrum_one": "https://arb-mainnet.g.alchemy.com/v2/",
    "optimism": "https://opt-mainnet.g.alchemy.com/v2/",
    "coinbase_base": "https://base-mainnet.g.alchemy.com/v2/",
    "fantom": "https://fantom.blockpi.network/v1/rpc/",
    "mantle": "https://rpc.mantle.xyz/",
    "linea": "https://rpc.linea.build/",
    "sei": "https://evm-rpc.sei-apis.com/?x-apikey=",
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
    "sei": "https://graph2.mainnet.jellyverse.org/subgraphs/name/jelly/verse" # TODO verify this for mainnet

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
LYNEX_V2_NAME = "lynex_v2"
NILE_V2_NAME = "nile_v2"
XFAI_V0_NAME = "xfai_v0"

SOLIDLY_FORKS = [
    AERODROME_V2_NAME,
    VELOCIMETER_V2_NAME,
    SCALE_V2_NAME,
    EQUALIZER_V2_NAME,
    VELODROME_V2_NAME,
    CLEOPATRA_V2_NAME,
    STRATUM_V2_NAME,
    XFAI_V0_NAME,
]

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
    XFAI_V0_NAME: 13,
}

EXCHANGE_POOL_CREATION_EVENT_NAMES = {
    UNISWAP_V2_NAME: "PairCreated",
    UNISWAP_V3_NAME: "PoolCreated",
    AERODROME_V2_NAME: "PoolCreated",
    VELOCIMETER_V2_NAME: "PairCreated",
    SCALE_V2_NAME: "PairCreated",
    EQUALIZER_V2_NAME: "PairCreated",
    CLEOPATRA_V2_NAME: "PairCreated",
    STRATUM_V2_NAME: "PairCreated",
    LYNEX_V2_NAME: "PairCreated",
    NILE_V2_NAME: "PairCreated",
    XFAI_V0_NAME: "PoolCreated",
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

skip_token_list = set(["0xaD67F7a72BA2ca971390B2a1dD907303bD577a4F"])


def get_all_token_details(network: str, write_path: str) -> dict:
    """
    This function collects the number of decimals and symbol of a token, and formats it for use in a dataframe.
    :param network: the network name

    :returns: the token lookup table
    """

    token_path = os.path.join(write_path, "tokens.csv")
    token_file_exists = os.path.exists(token_path)
    if token_file_exists:
        token_df = pd.read_csv(token_path, index_col=False)

        token_manager = {}
        for idx, row in token_df.iterrows():
            address, decimals, symbol = row
            token_manager[address] = {"address": address, "decimals": decimals, "symbol": symbol}

        return token_manager

    url = f"https://tokens.coingecko.com/{coingecko_network_map[network]}/all.json"
    response = requests.get(url).json()["tokens"]
    token_manager = {
        "0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE": {"address": "0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE",
                                                       "decimals": 18, "symbol": "ETH"}
    } if network in ["ethereum", "coinbase_base", "arbitrum_one", "optimism"] else {}
    for token in response:
        address = Web3.to_checksum_address(token["address"])
        symbol = token["symbol"]
        decimals = token["decimals"]
        try:
            # try to write to csv
            pd.DataFrame(
                {"token": [address], "symbol": [symbol], "decimals": [decimals]}
            ).to_csv("token_details.csv")
            token_manager[address] = {
                "address": address,
                "decimals": decimals,
                "symbol": symbol,
            }
        except Exception as e:
            print(f"Failed to get token details for token: {address} with error: {e}")
            continue
    return token_manager


def get_token_details_from_contract(
        token: str, web3
) -> Tuple[str, int] or Tuple[None, None]:
    """
    This function collects the number of decimals and symbol of a token, and formats it for use in a dataframe.
    :param token: the token address
    :param web3: the Web3 object

    Returns: a Tuple containing the token symbol & decimals, or None, None if the contract call failed.
    """
    if token in skip_token_list:
        return None, None
    elif token == "0x9f8F72aA9304c8B593d555F12eF6589cC3A579A2":
        symbol = "MKR"
        decimals = 18
    elif token == "0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE":
        symbol = "ETH"
        decimals = 18
    else:
        contract = web3.eth.contract(address=token, abi=ERC20_ABI)
        try:
            decimals = contract.caller.decimals()
        except:
            print(f"Cannot get token details for token: {token}")
            skip_token_list.add(token)
            return None, None
        try:
            symbol = contract.caller.symbol()
        except:
            symbol = "SYMBOL_FAILED"
        else:
            symbol = symbol.replace(os.linesep, "") or "???"
        pd.DataFrame(
            {"token": [token], "symbol": [symbol], "decimals": [decimals]}
        ).to_csv("token_details.csv")
    return symbol, decimals


def get_token_details(
        tkn: str, token_manager: dict, web3: Web3
) -> Tuple[str, int] or Tuple[None, None]:
    """
    :param tkn: the token address
    :param token_manager: the token lookup table
    :param web3: the Web3 object

    Returns: a Tuple containing the token symbol & decimals, or None, None if the contract call failed.
    """
    tkn = Web3.to_checksum_address(tkn)
    if tkn in token_manager:
        symbol = token_manager[tkn]["symbol"]
        decimal = token_manager[tkn]["decimals"]
    else:
        symbol, decimal = get_token_details_from_contract(token=tkn, web3=web3)
        if type(decimal) == int and type(symbol) == str:
            token_manager[tkn] = {"address": tkn, "decimals": decimal, "symbol": symbol}
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
    elif addr == "0xF1290473E210b2108A85237fbCd7b6eb42Cc654F":
        return "HEDG"
    else:
        return symbol


def organize_pool_details_uni_v3(
        pool_data: dict, token_manager: dict, exchange: str, web3: Web3
) -> dict:
    """
    This function organizes pool details for Uni V3 pools.
    :param pool_data: the pool data from the pool creation event
    :param token_manager: the token lookup table
    :param exchange: the exchange name
    :param web3: the Web3 object

    returns: dict of pool information
    """
    pool_address = pool_data["args"]["pool"]
    pool_address = Web3.to_checksum_address(pool_address)
    last_updated_block = pool_data["blockNumber"]
    tick_spacing = pool_data["args"]["tickSpacing"]
    tokens = [pool_data["args"]["token0"], pool_data["args"]["token1"]]
    token_info, pair, skip_pool = process_token_details(
        tokens=tokens, token_manager=token_manager, web3=web3
    )
    if skip_pool:
        return None

    fee = pool_data["args"]["fee"]

    pool_info = {
        "cid": pool_address,
        "strategy_id": 0,
        "last_updated": "",
        "last_updated_block": last_updated_block,
        "descr": f"{exchange} {pair} {fee}",
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
        "exchange_id": EXCHANGE_IDS["uniswap_v3"],
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

    return {**pool_info, **token_info}


def process_token_details(
        tokens: List[str], token_manager: dict, web3: Web3
) -> Tuple[Dict, str, bool] or Tuple[None, None, bool]:
    """
    This function processes token details & generates the token pair

    :param tokens: the list of tokens
    :param token_manager: the token lookup table
    :param web3: the Web3 object

    returns: tuple containing a dict with token information, the pair name as a string, and a bool that indicates if all tokens were successfully added.
    """
    token_info = {}
    addresses = []
    for idx, tkn in enumerate(tokens):
        address = Web3.to_checksum_address(tkn)

        if address in skip_token_list:
            return None, None, True
        symbol, decimals = get_token_details(
            token_manager=token_manager, tkn=address, web3=web3
        )
        if symbol is None:
            return None, None, True
        symbol = fix_missing_symbols(addr=address, symbol=symbol)
        token_info[f"tkn{idx}_decimals"] = decimals
        token_info[f"tkn{idx}_address"] = address
        token_info[f"tkn{idx}_symbol"] = symbol
        token_info[f"tkn{idx}_balance"] = 0

        addresses += [address]

    return token_info, "/".join(addresses), False


def organize_pool_details_balancer(pool_data: dict) -> dict:
    """
    This function organizes pool details for Uni V3 pools.
    :param pool_data: the pool data from the pool creation event

    returns: dict of pool information
    """
    if pool_data["swapEnabled"] != True:
        return None

    token_info = {}
    addresses = []

    for idx, tkn in enumerate(pool_data["tokens"]):
        address = Web3.to_checksum_address(tkn["address"])
        if address in skip_token_list:
            return None

        token_info[f"tkn{idx}_address"] = address
        token_info[f"tkn{idx}_symbol"] = fix_missing_symbols(addr=address, symbol=tkn["symbol"])
        token_info[f"tkn{idx}_decimals"] = tkn["decimals"]
        token_info[f"tkn{idx}_weight"] = tkn["weight"]
        token_info[f"tkn{idx}_balance"] = 0

        addresses += [address]

    pair = "/".join(addresses)
    fee = pool_data["swapFee"]

    pool_info = {
        "cid": pool_data["id"],
        "strategy_id": 0,
        "last_updated": "",
        "last_updated_block": 0,
        "descr": f"balancer {pair} {fee}",
        "pair_name": pair,
        "exchange_name": "balancer",
        "fee": float(fee) * 10 ** 18,
        "fee_float": float(fee),
        "address": Web3.to_checksum_address(pool_data["address"]),
        "anchor": pool_data["id"],
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
        "pool_type": pool_data["poolType"],
    }

    return {**pool_info, **token_info}


def organize_pool_details_uni_v2(
        pool_data, token_manager: dict, exchange, default_fee, web3
):
    """
    This function organizes pool details for Uni V2 pools.
    :param pool_data: the pool data from the pool creation event
    :param token_manager: the token lookup table
    :param exchange: the exchange name
    :param default_fee: the fee for the exchange
    :param web3: the Web3 object

    returns: dict of pool information
    """
    pool_address = pool_data["args"]["pair"]
    pool_address = Web3.to_checksum_address(pool_address)
    last_updated_block = pool_data["blockNumber"]
    if default_fee == "TBD":
        return None
    default_fee = float(default_fee)
    tokens = [pool_data["args"]["token0"], pool_data["args"]["token1"]]
    token_info, pair, skip_pool = process_token_details(
        tokens=tokens, token_manager=token_manager, web3=web3
    )
    if skip_pool:
        return None

    pool_info = {
        "cid": pool_address,
        "strategy_id": 0,
        "last_updated": "",
        "last_updated_block": last_updated_block,
        "descr": f"{exchange} {pair}",
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
        "exchange_id": EXCHANGE_IDS["uniswap_v2"],
        "tkn0_symbol": token_info["tkn0_symbol"],
        "tkn1_symbol": token_info["tkn1_symbol"],
        "timestamp": 0,
        "tkn0_balance": 0,
        "tkn1_balance": 0,
        "exchange": exchange,
    }

    return {**pool_info, **token_info}


def organize_pool_details_solidly_v2(
        pool_data, token_manager, exchange, exchange_object, web3, async_web3,
):
    """
    This function organizes pool details for Solidly pools.

    :param pool_data: the pool data from the pool creation event
    :param token_manager: the token lookup table
    :param exchange: the exchange name
    :param factory_contract: the exchange's Factory contract - initialized
    :param web3: the Web3 object
    :param async_web3: the Async Web3 object
    returns: dict of pool information
    """
    if "pool" in pool_data or "pool" in pool_data["args"]:
        pool_address = pool_data["args"]["pool"]
    elif "pair" in pool_data or "pair" in pool_data["args"]:
        pool_address = pool_data["args"]["pair"]
    else:
        print(f"COULD NOT FIND KEY IN EVENT for exchange {exchange}: {pool_data}")
    pool_address = Web3.to_checksum_address(pool_address)

    last_updated_block = pool_data["blockNumber"]

    if exchange == XFAI_V0_NAME:
        stable_pool = "volatile"
        tokens = [pool_data["args"]["token"], "0xe5D7C2a44FfDDf6b295A15c148167daaAf5Cf34f"] # TODO Use the constant WRAPPED_GAS_TOKEN_ADDRESS for this network
    else:
        stable_pool = "stable" if pool_data["args"]["stable"] else "volatile"
        tokens = [pool_data["args"]["token0"], pool_data["args"]["token1"]]

    pool_contract = async_web3.eth.contract(address=pool_address, abi=exchange_object.get_abi())
    fee_str, fee_float = asyncio_gather(exchange_object.get_fee(address=pool_address, contract=pool_contract))[0]

    token_info, pair, skip_pool = process_token_details(
        tokens=tokens, token_manager=token_manager, web3=web3
    )
    if skip_pool:
        return None

    pool_info = {
        "cid": pool_address,
        "strategy_id": 0,
        "last_updated": "",
        "last_updated_block": last_updated_block,
        "descr": f"{exchange} {pair}",
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
        "exchange_id": EXCHANGE_IDS[exchange],
        "tkn0_symbol": token_info["tkn0_symbol"],
        "tkn1_symbol": token_info["tkn1_symbol"],
        "timestamp": 0,
        "tkn0_balance": 0,
        "tkn1_balance": 0,
        "exchange": exchange,
        "pool_type": stable_pool,
    }

    return {**pool_info, **token_info}


def get_events(contract: any, blockchain: str, exchange: str, start_block: int, end_block: int) -> list:
    chunk_size = BLOCK_CHUNK_SIZE_MAP[blockchain]
    get_logs = contract.events[EXCHANGE_POOL_CREATION_EVENT_NAMES[exchange]].get_logs
    if chunk_size > 0:
        return get_events_iterative(get_logs, start_block, end_block, chunk_size)
    else:
        return get_events_recursive(get_logs, start_block, end_block)


def get_events_iterative(get_logs: any, start_block: int, end_block: int, chunk_size: int) -> list:
    block_numbers = list(range(start_block, end_block + 1, chunk_size)) + [end_block + 1]
    event_lists = [get_logs(fromBlock=block_numbers[n-1], toBlock=block_numbers[n]-1) for n in range(1, len(block_numbers))]
    return [event for event_list in event_lists for event in event_list]


def get_events_recursive(get_logs: any, start_block: int, end_block: int) -> list:
    if start_block <= end_block:
        try:
            return get_logs(fromBlock=start_block, toBlock=end_block)
        except Exception as e:
            assert "eth_getLogs" in str(e), str(e)
            if start_block < end_block:
                mid_block = (start_block + end_block) // 2
                event_list_1 = get_events_recursive(get_logs, start_block, mid_block)
                event_list_2 = get_events_recursive(get_logs, mid_block + 1, end_block)
                return event_list_1 + event_list_2
            else:
                raise e
    raise Exception(f"Illegal log query range: {start_block} -> {end_block}")


def get_uni_v3_pools(
        token_manager: dict,
        exchange: str,
        factory_contract,
        start_block: int,
        end_block: int,
        web3: Web3,
        blockchain: str
) -> Tuple[DataFrame, DataFrame]:
    """
    This function retrieves Uniswap V3 pool generation events and organizes them into two Dataframes
    :param token_manager: the token lookup table
    :param factory_contract: the initialized Factory contract
    :param start_block: the block number from which to start
    :param end_block: the block number at which to end
    :param web3: the Web3 object
    :param exchange: the name of the exchange
    :param blockchain: the blockchain name
    returns: a tuple containing a Dataframe of pool creation and a Dataframe of Uni V3 pool mappings
    """
    pool_data = get_events(factory_contract, blockchain, UNISWAP_V3_NAME, start_block, end_block)

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
    pool_mapping = [{"exchange": pool["exchange"], "address": pool["address"]} for pool in pools]
    mapdf = pd.DataFrame(pool_mapping, columns=["exchange", "address"]).reset_index(drop=True)
    return df, mapdf

def get_uni_v2_pools(
        token_manager: dict,
        exchange: str,
        factory_contract,
        start_block: int,
        end_block: int,
        default_fee: float,
        web3: Web3,
        blockchain: str
) -> Tuple[DataFrame, DataFrame]:
    """
    This function retrieves Uniswap V2 pool generation events and organizes them into two Dataframes
    :param token_manager: the token lookup table
    :param factory_contract: the initialized Factory contract
    :param start_block: the block number from which to start
    :param end_block: the block number at which to end
    :param web3: the Web3 object
    :param exchange: the name of the exchange
    :param default_fee: the fee for the exchange
    :param blockchain: the blockchain name
    returns: a tuple containing a Dataframe of pool creation and a Dataframe of Uni V3 pool mappings
    """
    pool_data = get_events(factory_contract, blockchain, UNISWAP_V2_NAME, start_block, end_block)

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
    pool_mapping = [{"exchange": pool["exchange"], "address": pool["address"]} for pool in pools]
    mapdf = pd.DataFrame(pool_mapping, columns=["exchange", "address"]).reset_index(drop=True)
    return df, mapdf

def get_solidly_v2_pools(
        token_manager: dict,
        exchange: str,
        async_factory_contract,
        factory_contract,
        start_block: int,
        end_block: int,
        web3: Web3,
        async_web3: AsyncWeb3,
        blockchain: str
) -> Tuple[DataFrame, DataFrame]:
    """
    This function retrieves Solidly pool generation events and organizes them into two Dataframes
    :param token_manager: the token lookup table
    :param factory_contract: the initialized Factory contract
    :param start_block: the block number from which to start
    :param end_block: the block number at which to end
    :param web3: the Web3 object
    :param async_web3: the Async Web3 object
    :param exchange: the name of the exchange
    :param default_fee: the fee for the exchange
    :param blockchain: the blockchain name
    returns: a tuple containing a Dataframe of pool creation and a Dataframe of Uni V3 pool mappings
    """
    pool_data = get_events(factory_contract, blockchain, exchange, start_block, end_block)
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
    pool_mapping = [{"exchange": pool["exchange"], "address": pool["address"]} for pool in pools]
    mapdf = pd.DataFrame(pool_mapping, columns=["exchange", "address"]).reset_index(drop=True)
    return df, mapdf


def get_multichain_addresses(network_name: str) -> pd.DataFrame:
    """
    Create dataframe of addresses for the selected network
    :param network_name: the name of the network in which to get addresses
    returns:
    A dataframe that contains items from the selected network
    """
    multichain_address_path = os.path.normpath("fastlane_bot/data/multichain_addresses.csv")
    chain_addresses_df = pd.read_csv(multichain_address_path)
    return chain_addresses_df.loc[chain_addresses_df["chain"] == network_name]


balancer_subgraph_query = """
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


def get_balancer_pools(subgraph_url: str) -> pd.DataFrame:
    """
    This function gets Balancer pool details from the Balancer subgraph

    :param subgraph_url: the URL of the Balancer subgraph
    """
    response = requests.post(subgraph_url, json={"query": balancer_subgraph_query})
    assert response.status_code == 200, f"Balancer subgraph query failed with {response}"
    pool_data_list = response.json()["data"]["pools"]

    pools = [organize_pool_details_balancer(pool_data) for pool_data in pool_data_list]
    return pd.DataFrame([pool for pool in pools if pool is not None], columns=dataframe_key)


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


def save_token_data(token_manager: dict, write_path: str):
    """
    Saves token data to a CSV

    """

    token_path = os.path.join(write_path, "tokens.csv")
    token_df = pd.DataFrame(token_manager.values(), columns=["address", "decimals", "symbol"])
    token_df.set_index("address", inplace=True)
    token_df.to_csv(token_path)


def terraform_blockchain(network_name: str):
    """
    This function collects all pool creation events for Uniswap V2/V3 and Solidly pools for a given network.
    The factory addresses for each exchange for which to extract pools must be defined in fastlane_bot/data/multichain_addresses.csv.

    :param network_name: the name of the blockchain from which to get data
    """

    url = ALCHEMY_RPC_LIST[network_name] + os.environ.get(ALCHEMY_KEY_DICT[network_name])
    web3 = Web3(Web3.HTTPProvider(url))
    async_web3 = AsyncWeb3(AsyncWeb3.AsyncHTTPProvider(url))

    PROJECT_PATH = os.path.normpath(f"{os.getcwd()}")
    write_path = os.path.normpath(f"{PROJECT_PATH}/fastlane_bot/data/blockchain_data/{network_name}")
    path_exists = os.path.exists(write_path)
    data_path = os.path.normpath(write_path + "/static_pool_data.csv")
    data_exists = os.path.exists(data_path)
    token_manager = get_all_token_details(network=network_name, write_path=write_path)

    if not path_exists:
        os.makedirs(write_path)
    if not data_exists:
        exchange_df = pd.DataFrame(columns=dataframe_key)
        univ2_mapdf = pd.DataFrame(columns=["exchange", "address"])
        univ3_mapdf = pd.DataFrame(columns=["exchange", "address"])
        solidly_v2_mapdf = pd.DataFrame(columns=["exchange", "address"])
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

    save_token_data(token_manager=token_manager, write_path=write_path)

    to_block = web3.eth.block_number

    for row in get_multichain_addresses(network_name=network_name).iterrows():
        exchange_name = row[1]["exchange_name"]
        chain = row[1]["chain"]
        fork = row[1]["fork"]
        factory_address = row[1]["factory_address"]
        fee = row[1]["fee"]

        if row[1]["active"] == "FALSE":
            continue

        from_block = int(row[1]["start_block"]) if not math.isnan(row[1]["start_block"]) else 0
        if factory_address is None or type(factory_address) != str or factory_address == "TBD":
            print(f"No factory contract address for exchange {exchange_name} on {chain}")
            continue
        print(f"*** Terraforming {chain} / {exchange_name} from block {from_block:,} to block {to_block:,} ***")

        if fork in "uniswap_v2":
            if fee == "TBD":
                continue
            if fork in SOLIDLY_FORKS:
                continue

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
                end_block=to_block,
                web3=web3,
                blockchain=network_name
            )
            m_df = m_df.reset_index(drop=True)
            univ2_mapdf = pd.concat([univ2_mapdf, m_df], ignore_index=True)
        elif fork in "uniswap_v3":
            if fee == "TBD":
                continue
            add_to_exchange_ids(exchange=exchange_name, fork=fork)
            factory_abi = UNISWAP_V3_FACTORY_ABI
            factory_contract = web3.eth.contract(
                address=factory_address, abi=factory_abi
            )
            u_df, m_df = get_uni_v3_pools(
                token_manager=token_manager,
                exchange=exchange_name,
                factory_contract=factory_contract,
                start_block=from_block,
                end_block=to_block,
                web3=web3,
                blockchain=network_name
            )
            m_df = m_df.reset_index(drop=True)
            univ3_mapdf = pd.concat([univ3_mapdf, m_df], ignore_index=True)
        elif "solidly" in fork:
            add_to_exchange_ids(exchange=exchange_name, fork=fork)
            solidly_exchange = SolidlyV2(exchange_name=exchange_name)
            factory_abi = solidly_exchange.factory_abi

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
                end_block=to_block,
                web3=web3,
                async_web3=async_web3,
                blockchain=network_name
            )
            m_df = m_df.reset_index(drop=True)
            solidly_v2_mapdf = pd.concat([solidly_v2_mapdf, m_df], ignore_index=True)
        elif "balancer" in fork:
            try:
                subgraph_url = BALANCER_SUBGRAPH_CHAIN_URL[network_name]
                u_df = get_balancer_pools(subgraph_url=subgraph_url)
            except Exception as e:
                print(f"Fetching balancer pools for chain {network_name} failed:\n{e}")
                continue
        else:
            print(f"Fork {fork} for exchange {exchange_name} not in supported forks.")
            continue
        exchange_df = pd.concat([exchange_df, u_df])

    save_token_data(token_manager=token_manager, write_path=write_path)

    exchange_df.to_csv((write_path + "/static_pool_data.csv"), index=False)
    univ2_mapdf.to_csv((write_path + "/uniswap_v2_event_mappings.csv"), index=False)
    univ3_mapdf.to_csv((write_path + "/uniswap_v3_event_mappings.csv"), index=False)
    solidly_v2_mapdf.to_csv((write_path + "/solidly_v2_event_mappings.csv"), index=False)

    for path in pathlib.Path(write_path).glob("**/*.csv"):
        file_desc = open(f"{path}", "r")
        lines = file_desc.readlines()
        file_desc.close()
        file_desc = open(f"{path}", "w")
        file_desc.writelines(list(dict.fromkeys(lines)))
        file_desc.close()


#terraform_blockchain(network_name=ETHEREUM)
#terraform_blockchain(network_name=BASE)
#terraform_blockchain(network_name=FANTOM)
#terraform_blockchain(network_name=MANTLE)
#terraform_blockchain(network_name=LINEA)
#terraform_blockchain(network_name=SEI)
