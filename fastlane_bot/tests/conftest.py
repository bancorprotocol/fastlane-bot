import pytest

import pandas as pd

from fastlane_bot import Config
from fastlane_bot.events.managers.manager import Manager


@pytest.fixture
def config():
    return Config.new(config=Config.CONFIG_MAINNET)


@pytest.fixture
def manager(config):
    static_pool_data_filename = "static_pool_data"
    static_pool_data = pd.read_csv(f"fastlane_bot/data/{static_pool_data_filename}.csv", low_memory=False)
    uniswap_v2_event_mappings = pd.read_csv("fastlane_bot/data/uniswap_v2_event_mappings.csv", low_memory=False)

    exchanges = "carbon_v1,bancor_v3,uniswap_v3,uniswap_v2,sushiswap_v2,bancor_pol,bancor_v2,balancer"
    exchanges = exchanges.split(",")

    alchemy_max_block_fetch = 20

    tokens = pd.read_csv("fastlane_bot/data/tokens.csv", low_memory=False)

    return Manager(
        web3=config.w3,
        w3_async=config.w3_async,
        cfg=config,
        pool_data=static_pool_data.to_dict(orient="records"),
        SUPPORTED_EXCHANGES=exchanges,
        alchemy_max_block_fetch=alchemy_max_block_fetch,
        uniswap_v2_event_mappings=uniswap_v2_event_mappings,
        tokens=tokens.to_dict(orient="records"),
    )
