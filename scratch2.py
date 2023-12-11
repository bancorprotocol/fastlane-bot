import json
import random
import time

import pandas as pd

# Original Structure
with open("fastlane_bot/data/test_pool_data.json", "r") as f:
    pool_data = json.load(f)

rows_to_update = random.sample(range(len(pool_data)), 100)
update_from_contract_block = 17721003
alchemy_max_block_fetch = 2000

# Pandas Structure
# Convert the data into a pandas DataFrame with dtype specification to handle NaN and large numbers
pool_data_df = pd.DataFrame(pool_data)

# Set the appropriate data types
for column in pool_data_df.columns:
    if pool_data_df[column].dtype == float and not any(pool_data_df[column].isnull()):
        pool_data_df[column] = pool_data_df[column].astype("int64")

# Create indices for the frequently queried columns
pool_data_df.set_index(
    ["exchange_name", "tkn0_address", "tkn1_address", "cid"], inplace=True
)

# Optimize the data types for the 'last_updated_block' column
pool_data_df["last_updated_block"] = pool_data_df["last_updated_block"].astype("int32")


def pd_query_3():
    pairs = [
        (
            "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2",
            "0xdAC17F958D2ee523a2206206994597C13D831ec7",
        )
    ]
    carbon_v1_pools = pool_data_df.xs("carbon_v1", level="exchange_name")
    return (
        carbon_v1_pools[
            carbon_v1_pools.index.isin(pairs, level=("tkn0_address", "tkn1_address"))
            | carbon_v1_pools.index.isin(pairs, level=("tkn1_address", "tkn0_address"))
        ]
        .index.get_level_values("cid")
        .tolist()
    )


pd_query_3()
