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

    
    @property
    def session(self):
        """dummy property for compatibility"""
        #raise ValueError("This is a mock database manager, it does not have a session")
        print("[session] DAFUQ YOU CALLING ME FOR? I'M A MOCK DATABASE MANAGER!")
        return ("MOVE ALONG, NOTHING TO SEE HERE")
    
    # @property
    # def engine(self):
    #     """dummy property for compatibility"""
    #     raise ValueError("This is a mock database manager, it does not have a session")
    
 