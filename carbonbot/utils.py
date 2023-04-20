"""
Utility functions for FastLane project

(c) Copyright Bprotocol foundation 2023.
Licensed under MIT
"""
import os.path
from typing import Tuple, List, Dict, Any

import pandas as pd
import requests
from _decimal import Decimal
from web3 import Web3

from carbonbot.abi import *
from carbonbot.config import *


def convert_decimals_to_wei_format(tkn_amt: Decimal, decimals: int) -> int:
    """
    param: tkn_amt: the number of tokens to convert
    param: token: the name of the token

    Returns:
    The number of tokens in WEI format according to the decimals used by the token
    """
    decimals = Decimal(str(decimals))
    tkn_amt = Decimal(str(tkn_amt))
    if decimals == 0:
        decimals = Decimal("1")
    return int(Decimal(tkn_amt * 10**decimals))


def get_coingecko_token_table() -> List[Dict[str, Any]]:
    """
    Get the token table from coingecko
    :return:  list of tokens
    """
    token_list = requests.get(url=COINGECKO_URL).json()["tokens"]

    tokens = [
        {
            "address": w3.toChecksumAddress(token["address"]),
            "symbol": token["symbol"],
            "decimals": token["decimals"],
            "name": token["name"],
        }
        for token in token_list
    ]
    tokens.append(
        {"address": ETH_ADDRESS, "symbol": "ETH", "decimals": 18, "name": "ETH"}
    )

    return tokens


# Initialize Contracts
def initialize_contract_with_abi(address: str, abi: List[Any], web3: Web3) -> Contract:
    """
    Initialize a contract with an abi
    :param address:  address of the contract
    :param abi:  abi of the contract
    :param web3:  web3 instance
    :return:  contract instance
    """
    return web3.eth.contract(address=address, abi=abi)


def initialize_contract_without_abi(address: str, web3):
    abi_endpoint = f"https://api.etherscan.io/api?module=contract&action=getabi&address={address}&apikey={ETHERSCAN_TOKEN}"
    abi = json.loads(requests.get(abi_endpoint).text)
    return web3.eth.contract(address=address, abi=abi["result"])


def initialize_contract(web3, address: str, abi=None) -> Contract:
    """
    Initialize a contract with an abi
    :param web3:    web3 instance
    :param address:  address of the contract
    :param abi:  abi of the contract
    :return:  contract instance
    """
    if abi is None:
        return initialize_contract_without_abi(address=address, web3=web3)
    else:
        return initialize_contract_with_abi(address=address, abi=abi, web3=web3)


def get_contract_from_abi(address: str, exchange_name: str) -> Contract:
    """
    The contract of the exchange.
    """
    return Contract.from_abi(
        name=f"{address}",
        address=f"{address}",
        abi=get_abi_and_router(exchange_name)[0],
    )


def convert_decimals(amt: Decimal, n: int) -> Decimal:
    """
    Utility function to convert to Decimaling point value of a specific precision.
    """
    if amt is None:
        return Decimal("0")
    return Decimal(str(amt / (Decimal("10") ** Decimal(str(n)))))


def get_abi_and_router(exchange: str) -> Tuple[list, str]:
    """
    Returns the ABI and router address for the pool

    :param exchange: The exchange to get the ABI and POOL_INFO_FOR_EXCHANGE for

    :return: The ABI and POOL_INFO_FOR_EXCHANGE
    """
    base_path = os.path.normpath(os.path.dirname(os.path.abspath(__file__)))
    POOL_INFO_FOR_EXCHANGE = pd.read_csv(f"{base_path}/pairs.csv")
    if exchange == BANCOR_V2_NAME:
        POOL_INFO_FOR_EXCHANGE = POOL_INFO_FOR_EXCHANGE[
            POOL_INFO_FOR_EXCHANGE["exchange"] == BANCOR_V2_NAME
        ]
        ABI = BANCOR_V2_CONVERTER_ABI
    elif exchange == BANCOR_V3_NAME:
        POOL_INFO_FOR_EXCHANGE = POOL_INFO_FOR_EXCHANGE[
            POOL_INFO_FOR_EXCHANGE["exchange"] == BANCOR_V3_NAME
        ]
        ABI = BANCOR_V3_NETWORK_INFO_ABI
    elif exchange == SUSHISWAP_V2_NAME:
        POOL_INFO_FOR_EXCHANGE = POOL_INFO_FOR_EXCHANGE[
            POOL_INFO_FOR_EXCHANGE["exchange"] == SUSHISWAP_V2_NAME
        ]
        ABI = SUSHISWAP_POOLS_ABI
    elif exchange == UNISWAP_V2_NAME:
        POOL_INFO_FOR_EXCHANGE = POOL_INFO_FOR_EXCHANGE[
            POOL_INFO_FOR_EXCHANGE["exchange"] == UNISWAP_V2_NAME
        ]
        ABI = UNISWAP_V2_POOL_ABI
    elif exchange == UNISWAP_V3_NAME:
        ABI = UNISWAP_V3_POOL_ABI
        POOL_INFO_FOR_EXCHANGE = POOL_INFO_FOR_EXCHANGE[
            POOL_INFO_FOR_EXCHANGE["exchange"] == UNISWAP_V3_NAME
        ]
    return ABI, POOL_INFO_FOR_EXCHANGE


class HexbytesEncoder(json.JSONEncoder):
    def default(self, obj):
        return obj.hex() if isinstance(obj, Hexbytes) else super().default(obj)


class Hexbytes:
    def __init__(self, value):
        self.value = value

    def hex(self):
        return self.value.hex()
