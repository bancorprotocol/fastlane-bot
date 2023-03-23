"""
Utility functions for FastLane - Fast Arbitrage Bot for Uniswap V3

(c) Copyright Bprotocol foundation 2023.
Licensed under MIT
"""
import os
from decimal import *
from typing import Tuple, Sequence, Any, Generator

import numpy as np
import pandas as pd

from fastlane_bot.constants import ec

logger = ec.DEFAULT_LOGGER


def convert_weth_to_eth_symbol(symbol: str) -> str:
    """
    This function takes a pair and converts WETH to ETH
    """
    if symbol == "WETH":
        symbol = "ETH"
    return symbol


def convert_weth_to_eth(p):
    """
    This function takes a pair and converts WETH to ETH
    """
    if p[0] == "WETH":
        p[0] = "ETH"
    if p[1] == "WETH":
        p[1] = "ETH"
    return p


class classproperty:
    """Allows a function to be accessed as a class level property."""

    def __init__(self, func):
        self.func = func

    def __get__(self, _, klass):
        """Get property value."""
        return self.func(klass)


def swap_weth_to_bancor_eth(symbol: str) -> str:
    """
    This is a simple check that converts the WETH address to the Bancor ETH address
    Args:
        symbol: a token address

    Returns:
        this checks if a token is WETH and returns the address for ETH on Bancor if it is
    """

    return "ETH" if symbol == "WETH" else symbol


def get_exchange_version(exchange: str) -> Tuple[str, str, str, int, int]:
    """
    This function takes an exchange name and returns the exchange name, version, exchange ID and version ID
    """
    exchange_name, exchange_version = exchange.split("_")
    exchange_id, version_id = ec.EXCHANGE_IDS[exchange]
    return exchange_name, exchange_version, exchange, exchange_id, version_id


def get_exchange_type(exchange: str) -> str:
    """
    This function takes an exchange name and returns the exchange type
    """
    return (
        "Constant Function Pool"
        if exchange == "uniswap_v3"
        else "Constant Product Pool"
    )


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


def check_paths(base_path: str) -> Tuple[str, str, str]:
    """
    Checks that the `constants.py` defined paths exists, and creates them if they don't.

    :return: The test directory, archive directory, and transaction archive directory
    """
    collection_dir = os.path.normpath(f"{base_path}/fastlane_bot/data/collection")
    archive_dir = os.path.normpath(f"{base_path}/fastlane_bot/data/archive")
    transactions_dir = os.path.normpath(f"{base_path}/fastlane_bot/data/transactions")

    # create a directory to store the output if it doesn't exist
    if not os.path.exists(collection_dir):
        os.makedirs(collection_dir)
    if not os.path.exists(archive_dir):
        os.makedirs(archive_dir)
    if not os.path.exists(transactions_dir):
        os.makedirs(transactions_dir)
    return collection_dir, archive_dir, transactions_dir


def get_abi_and_router(exchange: str) -> Tuple[str, str]:
    """
    Returns the ABI and router address for the pool

    :param exchange: The exchange to get the ABI and POOL_INFO_FOR_EXCHANGE for

    :return: The ABI and POOL_INFO_FOR_EXCHANGE
    """
    POOL_INFO_FOR_EXCHANGE = ec.DB
    if exchange == ec.UNISWAP_V3_NAME:
        ABI = ec.UNISWAP_V3_POOL_ABI
        POOL_INFO_FOR_EXCHANGE = POOL_INFO_FOR_EXCHANGE[
            POOL_INFO_FOR_EXCHANGE["exchange"] == ec.UNISWAP_V3_NAME
        ]
    elif exchange == ec.UNISWAP_V2_NAME:
        POOL_INFO_FOR_EXCHANGE = POOL_INFO_FOR_EXCHANGE[
            POOL_INFO_FOR_EXCHANGE["exchange"] == ec.UNISWAP_V2_NAME
        ]
        ABI = ec.UNISWAP_V2_POOL_ABI
    elif exchange == ec.SUSHISWAP_NAME:
        POOL_INFO_FOR_EXCHANGE = POOL_INFO_FOR_EXCHANGE[
            POOL_INFO_FOR_EXCHANGE["exchange"] == ec.SUSHISWAP_NAME
        ]
        ABI = ec.SUSHISWAP_POOLS_ABI
    elif exchange == ec.BANCOR_V2_NAME:
        POOL_INFO_FOR_EXCHANGE = POOL_INFO_FOR_EXCHANGE[
            POOL_INFO_FOR_EXCHANGE["exchange"] == ec.BANCOR_V2_NAME
        ]
        ABI = ec.BANCOR_V2_CONVERTER_ABI
    elif exchange == ec.BANCOR_V3_NAME:
        POOL_INFO_FOR_EXCHANGE = POOL_INFO_FOR_EXCHANGE[
            POOL_INFO_FOR_EXCHANGE["exchange"] == ec.BANCOR_V3_NAME
        ]
        ABI = ec.BANCOR_V3_NETWORK_INFO_ABI
    return ABI, POOL_INFO_FOR_EXCHANGE


def split_dataframe(df, chunk_size=500):
    """
    Splits a dataframe into chunks of a specified size.

    :param df: The dataframe to be split.
    :param chunk_size: The size of the chunks to split the dataframe into.

    :return: A list of dataframes.
    """
    num_chunks = len(df) // chunk_size + 1
    return [df[i * chunk_size : (i + 1) * chunk_size] for i in range(num_chunks)]


def convert_decimals(amt: Decimal, n: int) -> Decimal:
    """
    Utility function to convert to Decimaling point value of a specific precision.
    """
    if amt is None:
        return Decimal("0")
    return Decimal(str(amt / (Decimal("10") ** Decimal(str(n)))))


def convert_to_correct_decimal(address: str, amt: Decimal) -> Decimal:
    """
    Uses decimal_ct_map to convert a Decimaling point value to the correct precision.
    """
    symbol = ec.SYMBOL_FROM_ADDRESS[address]
    decimals = ec.DECIMAL_FROM_SYMBOL[symbol]
    return convert_decimals(amt, n=decimals)


def swap_bancor_eth_to_weth(address: str) -> str:
    """If the address is the ETH address, it returns the WETH address for compatibility."""
    return ec.WETH_ADDRESS if address == ec.ETH_ADDRESS else address


def format_amt(amt, C: int = 6) -> str:
    """
    Formats an amount to a string
    """
    if str(amt) == "None":
        return "0"
    try:
        amt = Decimal(str(float(amt)))
        amt = amt * 10**C
        amt = "{:.6f}".format(amt)
        return amt.split(".")[0][:C] if "." in amt else amt[:C]
    except Exception as e:
        logger.debug(f"error while formatting {amt}: {e}")
        return "0"
