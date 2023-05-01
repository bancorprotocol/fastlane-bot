"""
Mock database objects for testing the Fastlane project.

(c) Copyright Bprotocol foundation 2023.
Licensed under MIT
"""
import csv
import os
from _decimal import Decimal
from typing import List, Optional
from collections import namedtuple

from fastlane_bot.db.manager import DatabaseManager
from fastlane_bot.db.model_managers import TokenManager, PairManager, PoolManager

PROJECT_PATH = os.path.normpath(f"{os.getcwd()}")


def load_csv_data(filename: str):
    """
    Load data from a CSV file.

    Parameters
    ----------
    filename
        The name of the CSV file to load.

    Returns
    -------
    data
        The data from the CSV file.

    """
    file_path = os.path.normpath(f"{PROJECT_PATH}/fastlane_bot/data/{filename}")
    data = []

    with open(file_path, mode="r") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            data.append(row)

    return data


class MockTokenManager(TokenManager):
    """
    A mock TokenManager class.
    """
    tokens = load_csv_data("tokens.csv")

    def get_token(self, **kwargs) -> Optional[namedtuple]:
        for token in self.tokens:
            if all(token[key] == str(value) for key, value in kwargs.items()):
                return namedtuple("Token", token.keys())(*token.values())
        return None

    def get_tokens(self) -> List[namedtuple]:
        return [namedtuple("Token", token.keys())(*token.values()) for token in self.tokens]


class MockPairManager(PairManager):
    """
    A mock PairManager class.
    """
    pairs = load_csv_data("pairs.csv")

    def get_pair(self, **kwargs) -> Optional[namedtuple]:
        for pair in self.pairs:
            if all(pair[key] == str(value) for key, value in kwargs.items()):
                return namedtuple("Pair", pair.keys())(*pair.values())
        return None

    def get_pairs(self) -> List[namedtuple]:
        return [namedtuple("Pair", pair.keys())(*pair.values()) for pair in self.pairs]


class MockPoolManager(PoolManager):
    """
    A mock PoolManager class.
    """
    pools = load_csv_data("pools.csv")

    def get_pool(self, **kwargs) -> Optional[namedtuple]:
        for pool in self.pools:
            if all(pool[key] == str(value) for key, value in kwargs.items()):
                return namedtuple("Pool", pool.keys())(*pool.values())
        return None

    def get_pools(self) -> List[namedtuple]:
        return [namedtuple("Pool", pool.keys())(*pool.values()) for pool in self.pools]


class MockDatabaseManager(MockTokenManager, MockPairManager, MockPoolManager, DatabaseManager):
    """
    A mock DatabaseManager class.
    """
    __name__ = "MockDatabaseManager"

    __DATE__ = "05-01-2023"
    __VERSION__ = "3.0.2"

    
    # @property
    # def session(self):
    #     """dummy property for compatibility"""
    #     return False
    
    # @property
    # def engine(self):
    #     """dummy property for compatibility"""
    #     return False
    
    # I BELIEVE MIKE DELETED THIS BUT JUST IN CASE [MERGE CONFLICT]
    # def _get_bnt_price_from_tokens(self, price, tkn) -> Decimal:
    #     """
    #     Gets the price of a token

    #     Parameters
    #     ----------
    #     tkn0 : str
    #         The token address
    #     tkn1 : str
    #         The token address

    #     Returns
    #     -------
    #     Optional[Decimal]
    #         The price
    #     """

    #     if tkn == 'BNT-FF1C':
    #         return Decimal(price)

    #     bnt_price_map_symbols = {token.split('-')[0]: self.bnt_price_map[token] for token in self.bnt_price_map}

    #     tkn_bnt_price = bnt_price_map_symbols.get(tkn.split('-')[0])

    #     if tkn_bnt_price is None:
    #         raise ValueError(f"Missing TKN/BNT price for {tkn}")

    #     return Decimal(price) * Decimal(tkn_bnt_price)
    
