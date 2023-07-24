# coding=utf-8
"""
Contains the pools classes

(c) Copyright Bprotocol foundation 2023.
Licensed under MIT
"""
import pandas as pd

from fastlane_bot.events.pools.bancor_v3 import BancorV3Pool
from fastlane_bot.events.pools.carbon_v1 import CarbonV1Pool
from fastlane_bot.events.pools.factory import pool_factory
from fastlane_bot.events.pools.sushiswap_v2 import SushiswapV2Pool
from fastlane_bot.events.pools.uniswap_v2 import UniswapV2Pool
from fastlane_bot.events.pools.uniswap_v3 import UniswapV3Pool

# register your pool types
pool_factory.register_format("uniswap_v3", UniswapV3Pool)
pool_factory.register_format("uniswap_v2", UniswapV2Pool)
pool_factory.register_format("sushiswap_v2", SushiswapV2Pool)
pool_factory.register_format("bancor_v3", BancorV3Pool)
pool_factory.register_format("carbon_v1", CarbonV1Pool)
