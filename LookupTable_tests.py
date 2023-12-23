import pandas as pd
from typing import List, Dict, Any
from dataclasses import dataclass, field
import json
import time

json_path = "latest_pool_data.json"

with open(json_path) as f:
    json_data = json.load(f)


@dataclass
class BaseComparison:

    SUPPORTED_EXCHANGES: List[str] = field(default_factory=list)
    keys: List[str] = field(default_factory=list)
    alchemy_max_block_fetch: int = 2000

    def __post_init__(self):
        self.keys = [
            "address",
            "tkn0_address",
            "tkn1_address",
            "exchange_name",
            "last_updated_block",
            "numerical_index",
        ]
        self.SUPPORTED_EXCHANGES = [
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


@dataclass
class RefactoredLookupTable(BaseComparison):

    pool_data: pd.DataFrame = None

    def __post_init__(self):
        self.df = pd.DataFrame(
            self.pool_data,
            columns=[
                "cid",
                "last_updated",
                "last_updated_block",
                "descr",
                "pair_name",
                "exchange_name",
                "fee",
                "fee_float",
                "address",
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
            ],
        )
        self.df[self.keys] = self.df[self.keys].fillna("")
        indexes = []
        for key in self.keys:
            col = f"{key}_index"
            self.df[col] = self.df[key].values
            indexes.append(col)

        self.df.set_index(indexes, level=self.keys, inplace=True)

    def get_rows_to_update(self, update_from_contract_block: int) -> List[int]:
        def func(x):
            print(f"x: {x}")
            return self.df.get_level_values("last_updated_block", x) < (
                update_from_contract_block - self.alchemy_max_block_fetch
            )

        return self.df.groupby(level=self.keys).apply(func).index.tolist()


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


# Setup test data
update_from_contract_block = max(pool["last_updated_block"] for pool in json_data)
refactored_lookup_table = RefactoredLookupTable(pool_data=json_data)
# deprecated_lookup_table = DeprecatedLookupTable(pool_data=json_data)
#
#
# def test_get_rows_to_update():
#     start = time.time()
#     refactored_lookup_table.get_rows_to_update(update_from_contract_block)
#     end = time.time()
#     refactored_time = end - start
#     print(f"Refactored lookup table took {refactored_time} seconds")
#
#     start = time.time()
#     deprecated_lookup_table.get_rows_to_update(update_from_contract_block)
#     end = time.time()
#     deprecated_time = end - start
#     print(f"Deprecated lookup table took {deprecated_time} seconds")
#
#     # assert the refactored version is faster
#     assert (
#         refactored_time < deprecated_time
#     ), "Refactored version is not faster than deprecated version"
#
#     # assert the refactored version is faster by at least 50%
#     assert (
#         refactored_time < deprecated_time * 0.5
#     ), "Refactored version is not at least 50% faster than deprecated version"
#
#     # print the speedup
#     print(
#         f"Refactored version is {round(deprecated_time / refactored_time, 3)} times faster than deprecated version"
#     )
#
#     # assert the correct results are returned
#     assert refactored_lookup_table.get_rows_to_update(
#         update_from_contract_block
#     ) == deprecated_lookup_table.get_rows_to_update(
#         update_from_contract_block
#     ), "Refactored and deprecated versions do not return the same thing"
#
#
# test_get_rows_to_update()
