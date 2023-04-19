"""
Utility functions for FastLane project

(c) Copyright Bprotocol foundation 2023.
Licensed under MIT
"""
import itertools
import json
import os.path
import random
import time
from dataclasses import dataclass
from typing import Tuple, List, Dict, Any

import math
import pandas as pd
import requests
from _decimal import Decimal
from brownie import Contract
from web3 import Web3

from carbon.abi import (
    UNISWAP_V3_POOL_ABI,
    UNISWAP_V2_POOL_ABI,
    SUSHISWAP_POOLS_ABI,
    BANCOR_V2_CONVERTER_ABI,
    BANCOR_V3_NETWORK_INFO_ABI,
)
from carbon.config import (
    ETHERSCAN_TOKEN,
    COINGECKO_URL,
    w3,
    ETH_ADDRESS,
    UNISWAP_V2_NAME,
    UNISWAP_V3_NAME,
    SUSHISWAP_V2_NAME,
    BANCOR_V3_NAME,
    BANCOR_V2_NAME,
)


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
        return f"selling {s.token} @ ({1/s.p_start}..{1/s.p_end})  [TKNwei] per {s.token}wei"

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
        data = int(sqrt(value) * cls.ONE)
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


@dataclass
class UniV3Helper:
    """
    Handles math for Uni V3 pools.
    """

    contract_initialized: bool
    fee: str
    tick: int
    sqrt_price_q96: Decimal
    liquidity: Decimal

    _sqrt_price_q96_upper_bound: Decimal = None
    _sqrt_price_q96_lower_bound: Decimal = None
    TICK_BASE = Decimal("1.0001")
    Q96 = Decimal("2") ** Decimal("96")
    tkn0_decimal: int = None
    tkn1_decimal: int = None
    tick_spacing: int = None

    # def calc_sqrt_price_q96(self, price: Decimal) -> Decimal:
    #     """
    #     Returns the sqrt price.
    #     """
    #     return lambda price: math.sqrt(price) * self.Q96
    #
    # def price1_f(self, price: Decimal) -> Decimal:
    #     """
    #     Returns the price.
    #     """
    #     sqrt_price_q96 = self.calc_sqrt_price_q96(price)
    #     return lambda sqrt_price_q96: (int(sqrt_price_q96) / self.Q96) ** 2
    #
    # def price_f(self, sqrt_price_q96: Decimal) -> Decimal:
    #     """
    #     Returns the price.
    #     """
    #     sqrt_price_q96 = self.calc_sqrt_price_q96(sqrt_price_q96)
    #     return lambda sqrt_price_q96: (int(sqrt_price_q96) ** 2 / 2 ** 192)

    @staticmethod
    def dec_factor(dtkn0: int, dtkn1: int) -> Decimal:
        """
        Returns the decimal factor.
        """
        return Decimal(str(10 ** (dtkn0 - dtkn1)))

    def sqrt_price_x96_to_uint(
        self, sqrt_price_x96: Decimal, decimals_token0: int, decimals_token1: int
    ) -> Decimal:
        """
        Returns the sqrt price.
        """

        numerator1 = Decimal(str(sqrt_price_x96)) ** Decimal("2")
        numerator2 = self.dec_factor(decimals_token0, decimals_token1)
        return Decimal(str(numerator1 * numerator2 // Decimal(str(2**192))))

    @property
    def Pmarg(self) -> Decimal:
        """
        Returns the margin price.
        """
        return self.sqrt_price_x96_to_uint(
            self.sqrt_price_q96, self.tkn0_decimal, self.tkn1_decimal
        )

    @property
    def Pa(self) -> Decimal:
        """
        Returns the price of token 0.
        """
        return self.sqrt_price_x96_to_uint(
            self.sqrt_price_q96_lower_bound, self.tkn0_decimal, self.tkn1_decimal
        )

    @property
    def Pb(self) -> Decimal:
        """
        Returns the price of token 1.
        """
        return self.sqrt_price_x96_to_uint(
            self.sqrt_price_q96_upper_bound, self.tkn0_decimal, self.tkn1_decimal
        )

    # @property
    # def decimal_converter(self):
    #     return Decimal(
    #         10 ** (self.tkn1_decimal - self.tkn0_decimal)
    #     ) if self.tkn0_decimal != self.tkn1_decimal else Decimal(self.tkn0_decimal)

    @property
    def L(self) -> Decimal:
        """
        Returns the liquidity of the pool.
        """
        return self.liquidity / Decimal("10") ** (
            Decimal("0.5") * (self.tkn0_decimal + self.tkn1_decimal)
        )

    @property
    def sqrt_price_q96_upper_bound(self) -> Decimal:
        """
        Returns the upper bound of the price range.
        """
        return (
            self._sqrt_price_q96_upper_bound
            if self._sqrt_price_q96_upper_bound is not None
            else self.tick_to_sqrt_price_q96(self.upper_tick)
        )

    @property
    def sqrt_price_q96_lower_bound(self) -> Decimal:
        """
        Returns the lower bound of the price range.
        """
        return (
            self._sqrt_price_q96_lower_bound
            if self._sqrt_price_q96_lower_bound is not None
            else self.tick_to_sqrt_price_q96(self.lower_tick)
        )

    def tick_to_sqrt_price_q96(self, tick: Decimal) -> Decimal:
        """returns the price given a tick"""
        return (
            Decimal((self.TICK_BASE ** Decimal((tick / Decimal("2")))) * self.Q96)
            if self.contract_initialized
            else None
        )

    @property
    def lower_tick(self) -> Decimal:
        """
        Returns the lower tick of the pool.
        """
        if self.contract_initialized:
            return Decimal(
                math.floor(self.tick / self.tick_spacing) * self.tick_spacing
            )
        else:
            return Decimal(0)

    @property
    def upper_tick(self) -> Decimal:
        """
        Returns the upper tick of the pool.
        """
        if self.contract_initialized:
            return Decimal(self.lower_tick + self.tick_spacing)
        else:
            return Decimal(0)

    def __post_init__(self):
        self._sqrt_price_q96_upper_bound = self.tick_to_sqrt_price_q96(self.upper_tick)
        self._sqrt_price_q96_lower_bound = self.tick_to_sqrt_price_q96(self.lower_tick)


@dataclass
class DataFetcher:
    """
    Class to fetch data from Yahoo Finance and create random limit orders
    """

    token_pairs: list
    data: pd.DataFrame = None

    def get_token_combinations(self):
        """
        Returns a list of all possible token combinations
        """
        combinations = list(itertools.combinations(self.token_pairs, 2))
        return [f"{c[0]}/{c[1]}" for c in combinations]

    def fetch(self):
        """
        Fetches data from Yahoo Finance for all token pairs
        """
        import yfinance as yf

        date_30d_from_today = pd.Timestamp.today() - pd.Timedelta(days=30)
        date_30d_from_today_to_str = date_30d_from_today.strftime("%Y-%m-%d")
        end_today = pd.Timestamp.today()
        end_today_to_str = end_today.strftime("%Y-%m-%d")

        lst = []
        for pair in self.token_pairs:
            print(f"Fetching {pair} data...")
            try:
                data = yf.download(
                    pair,
                    start=date_30d_from_today_to_str,
                    end=end_today_to_str,
                    interval="5m",
                )
                data["pair"] = [pair for _ in range(len(data))]
                data.reset_index(inplace=True)
                lst.append(data)
            except Exception as e:
                print(f"Error fetching {pair} data: {e}")
            time.sleep(2)  # Add delay to avoid rate limiting

        self.data = pd.concat(lst, ignore_index=True)

    @staticmethod
    def calculate_mean_prices(df, n=100):
        """
        Calculates the mean low and high prices for the last n rows of a dataframe
        :param df: Dataframe containing the data
        :param n:  Number of rows to consider
        :return:  Datetime of the last row, mean low price, mean high price
        """
        most_recent_df = df.sort_values(by="Datetime", ascending=False)[:n]
        mean_low = most_recent_df["Low"].mean()
        mean_high = most_recent_df["High"].mean()
        max_datetime = most_recent_df["Datetime"].max()
        return max_datetime, mean_low, mean_high

    def create_limit_orders(
        self, data: pd.DataFrame = None, n: int = 10
    ) -> pd.DataFrame:
        """
        Creates limit orders for all token pairs
        :param data: Dataframe containing the data
        :param n: Number of limit orders to create
        :return: Dataframe containing the limit orders
        """
        if data is None:
            data = self.data
        lst = []
        token_combinations = [
            pair
            for pair in self.get_token_combinations()
            if pair.split("/")[0] != pair.split("/")[1]
        ]

        for _ in range(n):
            for pair in token_combinations:
                tkn0, tkn1 = pair.split("/")
                if (tkn0 == "USDC-USD") and (tkn1 == "DAI-USD"):
                    continue

                tkn0_data = data[data["pair"] == tkn0][["Datetime", "Low", "High"]]
                tkn1_data = data[data["pair"] == tkn1][["Datetime", "Low", "High"]]

                (
                    datetime_tkn0,
                    mean_low_tkn0,
                    mean_high_tkn0,
                ) = self.calculate_mean_prices(tkn0_data)
                (
                    datetime_tkn1,
                    mean_low_tkn1,
                    mean_high_tkn1,
                ) = self.calculate_mean_prices(tkn1_data)

                tkn0_data = pd.DataFrame(
                    {
                        "Datetime": [datetime_tkn0],
                        "Low_0": [mean_low_tkn0 + random.uniform(-0.0001, 0.0001)],
                        "High_0": [mean_high_tkn0 + random.uniform(-0.0001, 0.0001)],
                    }
                )

                tkn1_data = pd.DataFrame(
                    {
                        "Datetime": [datetime_tkn1],
                        "Low_1": [mean_low_tkn1 + random.uniform(-0.0001, 0.0001)],
                        "High_1": [mean_high_tkn1 + random.uniform(-0.0001, 0.0001)],
                    }
                )

                dfx = pd.merge(tkn1_data, tkn0_data, on="Datetime", how="left")
                dfx["pair"] = [
                    f"{tkn0.split('-')[0]}/{tkn1.split('-')[0]}"
                    for _ in range(len(dfx))
                ]
                dfx = dfx[["Datetime", "pair", "Low_0", "Low_1", "High_0", "High_1"]]
                lst.append(dfx)

                if len(lst) >= n:
                    break

        return pd.concat(lst, ignore_index=True)


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
