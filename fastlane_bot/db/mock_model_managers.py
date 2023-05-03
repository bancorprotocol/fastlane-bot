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
from fastlane_bot.helpers.poolandtokens import PoolAndTokens

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
    tokens = load_csv_data("tokens.csv")

    def get_pool(self, **kwargs) -> Optional[namedtuple]:
        for pool in self.pools:
            if all(pool[key] == str(value) for key, value in kwargs.items()):
                return namedtuple("Pool", pool.keys())(*pool.values())
        return None

    def get_pools(self) -> List[namedtuple]:
        return [namedtuple("Pool", pool.keys())(*pool.values()) for pool in self.pools]

    def get_pool_data_with_tokens(self) -> List[PoolAndTokens]:
        tokens_dict = {token['key']: token for token in self.tokens}

        pool_and_tokens_data = []
        for pool in self.pools:
            tkn0_key, tkn1_key = pool["pair_name"].split("/")
            tkn0 = tokens_dict.get(tkn0_key)
            tkn1 = tokens_dict.get(tkn1_key)
            if tkn0 and tkn1:
                pool_and_tokens_data.append(
                    (
                        pool,
                        tkn0_key,
                        tkn1_key,
                        tkn0["address"],
                        int(tkn0["decimals"]),
                        tkn1["address"],
                        int(tkn1["decimals"]),
                    )
                )

        return [
            PoolAndTokens(
                ConfigObj=self.ConfigObj,
                id=row[0]['id'],
                cid=row[0]['cid'],
                last_updated=row[0]['last_updated'],
                last_updated_block=row[0]['last_updated_block'],
                descr=row[0]['descr'],
                pair_name=row[0]['pair_name'],
                exchange_name=row[0]['exchange_name'],
                fee=row[0]['fee'],
                tkn0_balance=row[0]['tkn0_balance'],
                tkn1_balance=row[0]['tkn1_balance'],
                z_0=row[0]['z_0'],
                y_0=row[0]['y_0'],
                A_0=row[0]['A_0'],
                B_0=row[0]['B_0'],
                z_1=row[0]['z_1'],
                y_1=row[0]['y_1'],
                A_1=row[0]['A_1'],
                B_1=row[0]['B_1'],
                sqrt_price_q96=row[0]['sqrt_price_q96'],
                tick=row[0]['tick'],
                tick_spacing=row[0]['tick_spacing'],
                liquidity=row[0]['liquidity'],
                address=row[0]['address'],
                anchor=row[0]['anchor'],
                tkn0=row[1],
                tkn1=row[2],
                tkn0_address=row[3],
                tkn0_decimals=row[4],
                tkn1_address=row[5],
                tkn1_decimals=row[6],
            )
            for row in pool_and_tokens_data
        ]


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
    #     #raise ValueError("This is a mock database manager, it does not have a session")
    #     print("[session] DAFUQ YOU CALLING ME FOR? I'M A MOCK DATABASE MANAGER!")
    #     return ("MOVE ALONG, NOTHING TO SEE HERE")
    
    # @property
    # def engine(self):
    #     """dummy property for compatibility"""
    #     raise ValueError("This is a mock database manager, it does not have a session")
    
 