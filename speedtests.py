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
    ["exchange_name", "tkn0_address", "tkn1_address", "cid", "address"], inplace=True
)

# Optimize the data types for the 'last_updated_block' column
pool_data_df["last_updated_block"] = pool_data_df["last_updated_block"].astype("int32")


def query_1():
    return [
        i
        for i, pool_info in enumerate(pool_data)
        if pool_info["last_updated_block"]
        < update_from_contract_block - alchemy_max_block_fetch
    ]


def query_2():
    return [
        (p["tkn0_address"], p["tkn1_address"])
        for p in pool_data
        if p["exchange_name"] == "carbon_v1"
    ]


def query_3():
    pairs = [
        (
            "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2",
            "0xdAC17F958D2ee523a2206206994597C13D831ec7",
        )
    ]
    return [
        pool["cid"]
        for pool in pool_data
        if pool["exchange_name"] == "carbon_v1"
        and (pool["tkn0_address"], pool["tkn1_address"]) in pairs
        or (pool["tkn1_address"], pool["tkn0_address"]) in pairs
    ]


def query_4():
    cid = "0x72489592d291e402a4881f28823983b97a028e5ac5efbf87c428db2dbf06c81b"
    return [pool for pool in pool_data if pool["cid"] == cid][0]


def query_5():
    return sorted(pool_data, key=lambda x: x["last_updated_block"], reverse=True)


def query_6():
    seen = set()
    return [d for d in pool_data if d["cid"] not in seen and not seen.add(d["cid"])]


def query_7():
    return [
        idx
        for idx in rows_to_update
        if pool_data[idx]["exchange_name"]
        not in ["carbon_v1", "bancor_v3", "bancor_pol"]
    ]


def query_8():
    return [pool["cid"] for pool in pool_data]


def query_9():
    address = "0x0d4a11d5EEaaC28EC3F61d100daF4d40471f1852"
    return [pool for pool in pool_data if pool["address"] == address][0]


def pd_query_1():
    threshold_block = update_from_contract_block - alchemy_max_block_fetch
    return (
        pool_data_df[pool_data_df["last_updated_block"] < threshold_block]
        .index.get_level_values("cid")
        .tolist()
    )


def pd_query_2():
    carbon_v1_pools = pool_data_df.xs("carbon_v1", level="exchange_name")
    return [(idx[1], idx[2]) for idx in carbon_v1_pools.index]


def pd_query_3():
    pairs = [
        (
            "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2",
            "0xdAC17F958D2ee523a2206206994597C13D831ec7",
        )
    ]
    carbon_v1_pools = pool_data_df.xs("carbon_v1", level="exchange_name")
    # Filter pools that match the pair in any order
    pair_query = (
        carbon_v1_pools.index.isin([pair[0] for pair in pairs], level="tkn0_address")
        & carbon_v1_pools.index.isin([pair[1] for pair in pairs], level="tkn1_address")
    ) | (
        carbon_v1_pools.index.isin([pair[1] for pair in pairs], level="tkn0_address")
        & carbon_v1_pools.index.isin([pair[0] for pair in pairs], level="tkn1_address")
    )
    return carbon_v1_pools[pair_query].index.get_level_values("cid").tolist()


def pd_query_4():
    cid = "0x72489592d291e402a4881f28823983b97a028e5ac5efbf87c428db2dbf06c81b"
    return pool_data_df.xs(cid, level="cid").iloc[0].to_dict()


def pd_query_5():
    return (
        pool_data_df.sort_values("last_updated_block", ascending=False)
        .index.get_level_values("cid")
        .tolist()
    )


def pd_query_6():
    # 'cid' is already unique due to it being part of the index
    return pool_data_df.index.get_level_values("cid").unique().tolist()


def pd_query_7():
    excluded_exchanges = ["carbon_v1", "bancor_v3", "bancor_pol"]
    return [
        pool_data_df.iloc[idx].name[3]
        for idx in rows_to_update
        if pool_data_df.iloc[idx].name[0] not in excluded_exchanges
    ]


def pd_query_8():
    # 'cid' is part of the index, so we can directly access it
    return pool_data_df.index.get_level_values("cid").tolist()


def pd_query_9():
    address = "0x0d4a11d5EEaaC28EC3F61d100daF4d40471f1852"
    return pool_data_df.xs(address, level="address").iloc[0]


def run_time_tests(
    structure_name, func1, func2, func3, func4, func5, func6, func7, func8, func9
):
    print("\n\nRunning queries...")
    start_time = time.time()
    func1()
    q1_time = time.time() - start_time
    print(f"--- query_1: {q1_time} seconds ---")

    start_time = time.time()
    func2()
    q2_time = time.time() - start_time
    print(f"--- query_2: {q2_time} seconds ---")

    start_time = time.time()
    func3()
    q3_time = time.time() - start_time
    print(f"--- query_3: {q3_time} seconds ---")

    start_time = time.time()
    func4()
    q4_time = time.time() - start_time
    print(f"--- query_4: {q4_time} seconds ---")

    start_time = time.time()
    func5()
    q5_time = time.time() - start_time
    print(f"--- query_5: {q5_time} seconds ---")

    start_time = time.time()
    func6()
    q6_time = time.time() - start_time
    print(f"--- query_6: {q6_time} seconds ---")

    start_time = time.time()
    func7()
    q7_time = time.time() - start_time
    print(f"--- query_7: {q7_time} seconds ---")

    start_time = time.time()
    func8()
    q8_time = time.time() - start_time
    print(f"--- query_8: {q8_time} seconds ---")

    start_time = time.time()
    func9()
    q9_time = time.time() - start_time
    print(f"--- query_9: {q9_time} seconds ---")

    total_time = (
        q1_time
        + q2_time
        + q3_time
        + q4_time
        + q5_time
        + q6_time
        + q7_time
        + q8_time
        + q9_time
    )
    print(f"*** {structure_name}: total_time: {total_time} seconds *** \n\n")
    return total_time


orig_time = run_time_tests(
    "Original Structure",
    query_1,
    query_2,
    query_3,
    query_4,
    query_5,
    query_6,
    query_7,
    query_8,
    query_9,
)
pandas_time = run_time_tests(
    "Pandas Structure",
    pd_query_1,
    pd_query_2,
    pd_query_3,
    pd_query_4,
    pd_query_5,
    pd_query_6,
    pd_query_7,
    pd_query_8,
    pd_query_9,
)

print(f"*** Total time difference: {pandas_time - orig_time} seconds ***")

# What % faster is pandas?
print(f"*** Total time difference: {100 * (pandas_time - orig_time) / orig_time} % ***")
