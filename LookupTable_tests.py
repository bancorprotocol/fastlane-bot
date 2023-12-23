import random

import pandas as pd
from typing import List, Dict, Any, Tuple
from dataclasses import dataclass, field
import json
import time
import glob

json_path = glob.glob("logs/*/latest_pool_data.json")
json_path = [json_path[0]]

# json_path = "latest_pool_data.json"
json_data = []
for path in json_path:
    with open(path) as f:
        json_data += json.load(f)


@dataclass
class BaseComparison:

    keys: List[str] = field(
        default_factory=lambda: [
            "address",
            "tkn0_address",
            "tkn1_address",
            "exchange_name",
            # "last_updated_block",
            # "numerical_index",
        ]
    )
    SUPPORTED_EXCHANGES: List[str] = field(
        default_factory=lambda: [
            "carbon_v1",
            "bancor_v3",
            "bancor_v2",
            "bancor_pol",
            "uniswap_v3",
            "uniswap_v2",
            "sushiswap_v2",
            "balancer",
            "pancakeswap_v2",
            "pancakeswap_v3",
        ]
    )
    alchemy_max_block_fetch: int = 2000


@dataclass
class RefactoredLookupTable(BaseComparison):

    pool_data: List[dict] = None

    def __post_init__(self):
        self.df = pd.DataFrame(self.pool_data)
        self.df_address = self.df.set_index("address")
        self.df_tkn0_address = self.df.set_index("tkn0_address")
        self.df_tkn1_address = self.df.set_index("tkn1_address")
        self.df_exchange_name = self.df.set_index("exchange_name")
        self.df_tkns = self.df.set_index(["tkn0_address", "tkn1_address"])
        self.df.set_index("exchange_name", inplace=True)

    def get_rows_to_update(self, update_from_contract_block: int) -> List[int]:
        # Remains the same as the deprecated version. No faster way to do this was found.
        return [
            i
            for i, pool_info in enumerate(self.pool_data)
            if pool_info["last_updated_block"]
            < update_from_contract_block - self.alchemy_max_block_fetch
        ]

    def get_carbon_pairs_by_state(self) -> List[Tuple[str, str]]:
        # TODO: change 'uniswap_v2' to 'carbon_v1'
        cols = ["tkn0_address", "tkn1_address"]
        return self.df.loc["uniswap_v2", cols]

    def get_strats_by_state(self, pairs: List[List[Any]]) -> List[List[int]]:
        """
        Get the strategies by state.

        Parameters
        ----------
        pairs : List[Tuple[str, str, int, int]]
            The pairs.

        Returns
        -------
        List[List[Any]]
            The strategies retrieved from the state.

        """
        # gets the same result as get_strats_by_state_dep, but uses pandas instead of for loops
        cids = self.df_exchange_name.loc["carbon_v1", "cid"].values.tolist()
        strategies = []
        for cid in cids:
            pool_data = self.df_address.loc[cid].to_dict()

            # Constructing the orders based on the values from the pool_data dictionary
            order0 = [
                pool_data["y_0"],
                pool_data["z_0"],
                pool_data["A_0"],
                pool_data["B_0"],
            ]
            order1 = [
                pool_data["y_1"],
                pool_data["z_1"],
                pool_data["A_1"],
                pool_data["B_1"],
            ]

            # Fetching token addresses and converting them
            tkn0_address, tkn1_address = pool_data["tkn0"], pool_data["tkn1"]

            # Reconstructing the strategy object
            strategy = [cid, None, [tkn0_address, tkn1_address], [order0, order1]]

            # Appending the strategy to the list of strategies
            strategies.append(strategy)

        return strategies


@dataclass
class DeprecatedLookupTable(BaseComparison):

    pool_data: List[dict] = None

    def get_rows_to_update(self, update_from_contract_block: int) -> List[int]:
        return [
            i
            for i, pool_info in enumerate(self.pool_data)
            if pool_info["last_updated_block"]
            < update_from_contract_block - self.alchemy_max_block_fetch
        ]

    def get_carbon_pairs_by_state(self) -> List[Tuple[str, str]]:
        return [
            (p["tkn0_address"], p["tkn1_address"])
            for p in self.pool_data
            if p["exchange_name"] == "uniswap_v2"
        ]

    def get_strats_by_state(self, pairs: List[List[Any]]) -> List[List[int]]:
        """
        Get the strategies by state.

        Parameters
        ----------
        pairs : List[Tuple[str, str, int, int]]
            The pairs.

        Returns
        -------
        List[List[Any]]
            The strategies retrieved from the state.

        """
        cids = [
            pool["cid"]
            for pool in self.pool_data
            if pool["exchange_name"] == "carbon_v1"
            and (pool["tkn0_address"], pool["tkn1_address"]) in pairs
            or (pool["tkn1_address"], pool["tkn0_address"]) in pairs
        ]
        strategies = []
        for cid in cids:
            pool_data = [pool for pool in self.pool_data if pool["cid"] == cid][0]

            # Constructing the orders based on the values from the pool_data dictionary
            order0 = [
                pool_data["y_0"],
                pool_data["z_0"],
                pool_data["A_0"],
                pool_data["B_0"],
            ]
            order1 = [
                pool_data["y_1"],
                pool_data["z_1"],
                pool_data["A_1"],
                pool_data["B_1"],
            ]

            # Fetching token addresses and converting them
            tkn0_address, tkn1_address = pool_data["tkn0"], pool_data["tkn1"]

            # Reconstructing the strategy object
            strategy = [cid, None, [tkn0_address, tkn1_address], [order0, order1]]

            # Appending the strategy to the list of strategies
            strategies.append(strategy)

        return strategies


# Setup test data
update_from_contract_block = max(pool["last_updated_block"] for pool in json_data)
print(f"update_from_contract_block: {update_from_contract_block}")

refactored_lookup_table = RefactoredLookupTable(pool_data=json_data)
deprecated_lookup_table = DeprecatedLookupTable(pool_data=json_data)


# def test_get_rows_to_update(n):
#     def check_runs():
#         start = time.time()
#         refactored_lookup_table.get_rows_to_update(update_from_contract_block)
#         end = time.time()
#         refactored_time = end - start
#
#         start = time.time()
#         deprecated_lookup_table.get_rows_to_update(update_from_contract_block)
#         end = time.time()
#         deprecated_time = end - start
#
#         return refactored_time, deprecated_time
#
#     # run 100 tests and average the results
#     for i in range(n):
#         refactored_time, deprecated_time = check_runs()
#         refactored_times.append(refactored_time)
#         deprecated_times.append(deprecated_time)
#
#     refactored_time = sum(refactored_times) / len(refactored_times)
#     print(f"Refactored lookup table took {refactored_time} seconds")
#     deprecated_time = sum(deprecated_times) / len(deprecated_times)
#     print(f"Deprecated lookup table took {deprecated_time} seconds")
#     perc_faster = round((deprecated_time - refactored_time) / deprecated_time, 3) * 100
#     print(f"Refactored version is {perc_faster} % faster than deprecated version")
#
#     # assert the refactored version is faster
#     assert refactored_time < (
#         deprecated_time
#     ), "Refactored version is not faster than deprecated version"
#
#     # assert the correct results are returned
#     assert refactored_lookup_table.get_rows_to_update(
#         update_from_contract_block
#     ) == deprecated_lookup_table.get_rows_to_update(
#         update_from_contract_block
#     ), "Refactored and deprecated versions do not return the same thing"


def test_get_carbon_pairs_by_state(n):
    def check_runs():
        start = time.time()
        refactored_lookup_table.get_carbon_pairs_by_state()
        end = time.time()
        refactored_time = end - start

        start = time.time()
        deprecated_lookup_table.get_carbon_pairs_by_state()
        end = time.time()
        deprecated_time = end - start

        return refactored_time, deprecated_time

    refactored_times = []
    deprecated_times = []

    # run 100 tests and average the results
    for i in range(n):
        refactored_time, deprecated_time = check_runs()
        refactored_times.append(refactored_time)
        deprecated_times.append(deprecated_time)

    refactored_time = sum(refactored_times) / len(refactored_times)
    print(f"Refactored lookup table took {refactored_time} seconds")
    deprecated_time = sum(deprecated_times) / len(deprecated_times)
    print(f"Deprecated lookup table took {deprecated_time} seconds")
    perc_faster = round((deprecated_time - refactored_time) / deprecated_time, 3) * 100
    print(f"Refactored version is {perc_faster} % faster than deprecated version")

    # assert the refactored version is faster
    assert refactored_time < (
        deprecated_time
    ), "Refactored version is not faster than deprecated version"

    # assert the correct results are returned
    assert (
        refactored_lookup_table.get_carbon_pairs_by_state()
        == deprecated_lookup_table.get_carbon_pairs_by_state()
    ), "Refactored and deprecated versions do not return the same thing"


def test_get_strats_by_state(n):
    def check_runs():
        start = time.time()
        refactored_lookup_table.get_strats_by_state(
            refactored_lookup_table.get_carbon_pairs_by_state()
        )
        end = time.time()
        refactored_time = end - start

        start = time.time()
        deprecated_lookup_table.get_strats_by_state(
            deprecated_lookup_table.get_carbon_pairs_by_state()
        )
        end = time.time()
        deprecated_time = end - start

        return refactored_time, deprecated_time

    refactored_times = []
    deprecated_times = []
    # run 100 tests and average the results
    for i in range(n):
        refactored_time, deprecated_time = check_runs()
        refactored_times.append(refactored_time)
        deprecated_times.append(deprecated_time)

    refactored_time = sum(refactored_times) / len(refactored_times)
    print(f"Refactored lookup table took {refactored_time} seconds")
    deprecated_time = sum(deprecated_times) / len(deprecated_times)
    print(f"Deprecated lookup table took {deprecated_time} seconds")
    perc_faster = round((deprecated_time - refactored_time) / deprecated_time, 3) * 100
    print(f"Refactored version is {perc_faster} % faster than deprecated version")

    # assert the refactored version is faster
    assert refactored_time < (
        deprecated_time
    ), "Refactored version is not faster than deprecated version"

    # assert the correct results are returned
    assert refactored_lookup_table.get_strats_by_state(
        refactored_lookup_table.get_carbon_pairs_by_state()
    ) == deprecated_lookup_table.get_strats_by_state(
        deprecated_lookup_table.get_carbon_pairs_by_state()
    ), "Refactored and deprecated versions do not return the same thing"


n = 1000
# test_get_rows_to_update(n)
test_get_carbon_pairs_by_state(n)
test_get_strats_by_state(n)
