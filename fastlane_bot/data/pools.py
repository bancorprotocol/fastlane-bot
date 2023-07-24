import pandas as pd

# load static data
static_data = pd.read_csv("fastlane_bot/data/static_pool_data.csv").to_dict("records")

# get all uniswap v2 pools
uniswap_v2_pools = [
    static_data[idx]["address"]
    for idx in range(len(static_data))
    if static_data[idx]["exchange_name"] == "uniswap_v2"
]

# get all sushiswap v2 pools
sushiswap_v2_pools = [
    static_data[idx]["address"]
    for idx in range(len(static_data))
    if static_data[idx]["exchange_name"] == "sushiswap_v2"
]

# get all uniswap v3 pools
uniswap_v3_pools = [
    static_data[idx]["address"]
    for idx in range(len(static_data))
    if static_data[idx]["exchange_name"] == "uniswap_v3"
]
del static_data  # clear static data to save memory