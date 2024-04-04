"""
Contains the pools classes

[DOC-TODO-OPTIONAL-longer description in rst format]

---
(c) Copyright Bprotocol foundation 2023-24.
All rights reserved.
Licensed under MIT.
"""
from fastlane_bot.events.pools.bancor_v3 import BancorV3Pool
from fastlane_bot.events.pools.carbon_v1 import CarbonV1Pool
from fastlane_bot.events.pools.factory import pool_factory
from fastlane_bot.events.pools.solidly_v2 import SolidlyV2Pool
from fastlane_bot.events.pools.uniswap_v2 import UniswapV2Pool
from fastlane_bot.events.pools.uniswap_v3 import UniswapV3Pool
from fastlane_bot.events.pools.bancor_v2 import BancorV2Pool
from fastlane_bot.events.pools.bancor_pol import BancorPolPool
from fastlane_bot.events.pools.balancer import BalancerPool


# register your pool types
pool_factory.register_format("uniswap_v3", UniswapV3Pool)
pool_factory.register_format("uniswap_v2", UniswapV2Pool)
pool_factory.register_format("bancor_v3", BancorV3Pool)
pool_factory.register_format("carbon_v1", CarbonV1Pool)
pool_factory.register_format("bancor_v2", BancorV2Pool)
pool_factory.register_format("bancor_pol", BancorPolPool)
pool_factory.register_format("balancer", BalancerPool)
pool_factory.register_format("solidly_v2", SolidlyV2Pool)
