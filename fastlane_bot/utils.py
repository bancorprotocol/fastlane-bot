"""
Utility functions for FastLane project

(c) Copyright Bprotocol foundation 2023.
Licensed under MIT
"""
import datetime
import glob
import logging
import math
import os.path
import time
from _decimal import Decimal
from dataclasses import dataclass
from hexbytes import HexBytes
from typing import Tuple, List, Dict, Any

import pandas as pd
import requests
from web3 import Web3
from web3.contract import Contract

from fastlane_bot.config import config as cfg
from fastlane_bot.data.abi import *


def safe_int(value: int or float) -> int:
    assert value == int(value), f"non-integer `float` value {value}"
    return int(value)


def int_prefix(string: str) -> int:
    return int(string[:-len(string.lstrip("0123456789"))])


def num_format(number):
    try:
        return "{0:.4f}".format(number)
    except Exception as e:
        return number


def num_format_float(number):
    try:
        return float("{0:.4f}".format(number))
    except Exception as e:
        return number


def log_format(log_data: {}, log_name: str = "new"):
    now = datetime.datetime.now()
    time_ts = str(int(now.timestamp()))  # timestamp (epoch)
    time_iso = now.isoformat().split(".")[0]
    # print(time_ts)
    # print(time_iso)

    log_string = f"[{time_iso}::{time_ts}] |{log_name}| == {log_data}"
    return log_string
    # return "\n".join("[{" + time_iso + "}::{" + time_ts + "}] |" + log_name + "| == {d}\n".format(d=(log_data)))


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
    abi_endpoint = f"https://api.etherscan.io/api?module=contract&action=getabi&address={address}&apikey={cfg.ETHERSCAN_TOKEN}"
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


def convert_decimals(amt: Decimal, n: int) -> Decimal:
    """
    Utility function to convert to Decimaling point value of a specific precision.
    """
    if amt is None:
        return Decimal("0")
    return Decimal(str(amt / (Decimal("10") ** Decimal(str(n)))))


@dataclass
class EncodedOrder:
    """
    a single curve as encoded by the SDK

    :token:      token address
    :y:          number of token wei to sell on the curve
    :z:          curve capacity in number of token wei
    :A:          curve parameter A, multiplied by 2**48, encoded
    :B:          curve parameter B, multiplied by 2**48, encoded
    ----
    :A_:         curve parameter A in proper units
    :B_:         curve parameter B in proper units
    :p_start:    start token wei price of the order (in dy/dx)
    :p_end:      end token wei price of the order (in dy/dx)
    """

    token: str
    y: int
    z: int
    A: int
    B: int

    ONE = 2**48

    @classmethod
    def from_sdk(cls, token, order):
        return cls(token=token, **order)

    @property
    def descr(self):
        s = self
        return f"selling {s.token} @ ({1 / s.p_start}..{1 / s.p_end})  [TKNwei] per {s.token}wei"

    def __getitem__(self, item):
        return getattr(self, item)

    @classmethod
    def decodeFloat(cls, value):
        """undoes the mantisse/exponent encoding in A,B"""
        return (value % cls.ONE) << (value // cls.ONE)

    @classmethod
    def decode(cls, value):
        """decodes A,B to float"""
        return cls.decodeFloat(int(value)) / cls.ONE

    @staticmethod
    def bitLength(value):
        "minimal number of bits needed to represent the value"
        return len(bin(value).lstrip("0b")) if value > 0 else 0

    @classmethod
    def encodeRate(cls, value):
        "encodes a rate float to an A,B (using cls.ONE for scaling)"
        data = int(math.sqrt(value) * cls.ONE)
        length = cls.bitLength(data // cls.ONE)
        return (data >> length) << length

    @classmethod
    def encodeFloat(cls, value):
        "encodes a long int value as mantisse/exponent into a shorter integer"
        exponent = cls.bitLength(value // cls.ONE)
        mantissa = value >> exponent
        return mantissa | (exponent * cls.ONE)

    @classmethod
    def encode(cls, y, p_start_hi, p_end_lo, p_marg=None, z=None, token=None):
        """
        alternative constructor: creates a new encoded order from the given parameters

        :y:             number of token wei currently available to sell on the curve (loading)
        :p_start_hi:    start token wei price of the order (in dy/dx; highest)
        :p_end_lo:      end token wei price of the order (in dy/dx; lowest)
        :p_marg:        marginal token wei price of the order (in dy/dx)*
        :z:             curve capacity in number of token wei*

        *at most one of p_marg and z can be given; if neither is given,
        z is assumed to be equal to y
        """
        if token is None:
            token = "TKN"
        if p_marg is not None and z is not None:
            raise ValueError("at most one of p_marg and z can be given")
        if z is None:
            if p_marg is not None and p_marg >= p_start_hi or p_marg is None:
                z = y
            else:
                z = y * (p_start_hi - p_end_lo) // (p_marg - p_start_hi)
        return cls(
            y=int(y),
            z=int(z),
            A=cls.encodeFloat(cls.encodeRate(p_start_hi) - cls.encodeRate(p_end_lo)),
            B=cls.encodeFloat(cls.encodeRate(p_end_lo)),
            token=token,
        )

    @classmethod
    def encode_yzAB(cls, y, z, A, B, token=None):
        """
        encode A,B into the SDK format

        :y:    number of token wei currently available to sell on the curve (loading; as int)
        :z:    curve capacity in number of token wei (as int)
        :A:    curve parameter A (as float)
        :B:    curve parameter B (as float)
        """
        return cls(
            y=int(y),
            z=int(z),
            A=cls.encodeFloat(A),
            B=cls.encodeFloat(B),
            token=str(token),
        )

    @dataclass
    class DecodedOrder:
        """
        a single curve with the values of A,B decoded and as floats
        """

        y: int
        z: int
        A: float
        B: float

    @property
    def decoded(self):
        """
        returns a the order with A, B decoded as floats
        """
        return self.DecodedOrder(y=self.y, z=self.z, A=self.A_, B=self.B_)

    @property
    def A_(self):
        return self.decode(self.A)

    @property
    def B_(self):
        return self.decode(self.B)

    @property
    def p_end(self):
        return self.B_ * self.B_

    @property
    def p_start(self):
        return (self.B_ + self.A_) ** 2

    @property
    def p_marg(self):
        if self.y == self.z:
            return self.p_start
        elif self.y == 0:
            return self.p_end
        raise NotImplementedError("p_marg not implemented for non-full / empty orders")
        A = self.decodeFloat(self.A)
        B = self.decodeFloat(self.B)
        return self.decode(B + A * self.y / self.z) ** 2
        # https://github.com/bancorprotocol/carbon-simulator/blob/beta/benchmark/core/trade/impl.py
        # 'marginalRate' : decodeRate(B + A if y == z else B + A * y / z),


def find_latest_timestamped_folder(logging_path=None):
    """
    Find the latest timestamped folder in the given directory or the default directory.

    Args:
        logging_path (str, optional): The custom logging path where the timestamped folders are. Defaults to None.

    Returns:
        str: Path to the latest timestamped folder, or None if no folder is found.
    """
    search_path = logging_path if logging_path else "."
    search_path = os.path.join(search_path, "logs/*")
    list_of_folders = glob.glob(search_path)

    if not list_of_folders:
        return None

    list_of_folders.sort(reverse=True)  # Sort the folders in descending order
    return list_of_folders[0]  # The first one is the latest


def count_bytes(data: HexBytes) -> (int, int):
    """
    This function counts the number of zero and non-zero bytes in a given input data.
    :param data: HexBytes
    returns Tuple(int, int):
        The zero & non zero count of bytes in the input
    """
    zero_bytes = len([byte for byte in data if byte == 0])
    non_zero_bytes = len(data) - zero_bytes
    return zero_bytes, non_zero_bytes
