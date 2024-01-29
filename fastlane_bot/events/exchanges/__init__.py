# coding=utf-8
"""
Contains the exchanges classes

(c) Copyright Bprotocol foundation 2023.
Licensed under MIT
"""

from fastlane_bot.events.exchanges.bancor_v3 import BancorV3
from fastlane_bot.events.exchanges.carbon_v1 import CarbonV1
from fastlane_bot.events.exchanges.factory import ExchangeFactory
from fastlane_bot.events.exchanges.solidly_v2 import SolidlyV2
from fastlane_bot.events.exchanges.uniswap_v2 import UniswapV2
from fastlane_bot.events.exchanges.uniswap_v3 import UniswapV3
from fastlane_bot.events.exchanges.bancor_v2 import BancorV2
from fastlane_bot.events.exchanges.bancor_pol import BancorPol
from fastlane_bot.events.exchanges.balancer import Balancer

# Create a single instance of ExchangeFactory
exchange_factory = ExchangeFactory()

# Register the exchanges with the factory
exchange_factory.register_exchange("uniswap_v2", UniswapV2)
exchange_factory.register_exchange("uniswap_v3", UniswapV3)
exchange_factory.register_exchange("bancor_v3", BancorV3)
exchange_factory.register_exchange("carbon_v1", CarbonV1)
exchange_factory.register_exchange("bancor_v2", BancorV2)
exchange_factory.register_exchange("bancor_pol", BancorPol)
exchange_factory.register_exchange("balancer", Balancer)
exchange_factory.register_exchange("solidly_v2", SolidlyV2)
