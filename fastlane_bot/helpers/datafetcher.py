"""
Data fetcher helpers for the Fastlane project.

(c) Copyright Bprotocol foundation 2023.
Licensed under MIT
"""
import itertools
import random
import time
from dataclasses import dataclass, asdict
from typing import List, Union, Any, Dict, Tuple, Optional
# import eth_abi
# import math
import pandas as pd
# import requests
# from _decimal import Decimal
from alchemy import Network, Alchemy
from brownie.network.transaction import TransactionReceipt
from eth_utils import to_hex
from web3 import Web3
from web3._utils.threads import Timeout
from web3._utils.transactions import fill_nonce
from web3.contract import ContractFunction
from web3.exceptions import TimeExhausted
from web3.types import TxParams, TxReceipt
from fastlane_bot.abi import *      # TODO: PRECISE THE IMPORTS or from .. import abi
from fastlane_bot.config import *   # TODO: PRECISE THE IMPORTS or from .. import config
# from fastlane_bot.models import Token, session, Pool
# from carbon.tools.cpc import ConstantProductCurve


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

