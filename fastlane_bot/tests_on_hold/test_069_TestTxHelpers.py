# ------------------------------------------------------------
# Auto generated test file `test_069_TestTxHelpers.py`
# ------------------------------------------------------------
# source file   = NBTest_069_TestTxHelpers.py
# test id       = 069
# test comment  = TestTxHelpers
# ------------------------------------------------------------



"""
This module contains the tests for the exchanges classes
"""
from arb_optimizer import ConstantProductCurve as CPC

from fastlane_bot import Bot, Config
from fastlane_bot.bot import CarbonBot
from fastlane_bot.events.exchanges import UniswapV2, UniswapV3,  CarbonV1, BancorV3
from fastlane_bot.events.interface import QueryInterface
from fastlane_bot.events.interface import QueryInterface
from fastlane_bot.testing import *
from fastlane_bot.config.network import *
import json
print("{0.__name__} v{0.__VERSION__} ({0.__DATE__})".format(CPC))
print("{0.__name__} v{0.__VERSION__} ({0.__DATE__})".format(Bot))
print("{0.__name__} v{0.__VERSION__} ({0.__DATE__})".format(UniswapV2))
print("{0.__name__} v{0.__VERSION__} ({0.__DATE__})".format(UniswapV3))
print("{0.__name__} v{0.__VERSION__} ({0.__DATE__})".format(CarbonV1))
print("{0.__name__} v{0.__VERSION__} ({0.__DATE__})".format(BancorV3))
from fastlane_bot.testing import *

plt.rcParams['figure.figsize'] = [12,6]
from fastlane_bot import __VERSION__
require("3.0", __VERSION__)

cfg = Config.new(config=Config.CONFIG_MAINNET, blockchain="ethereum")
cfg.network.SOLIDLY_V2_FORKS = ["solidly_v2"]
setup_bot = CarbonBot(ConfigObj=cfg)
pools = None
with open('fastlane_bot/tests/_data/latest_pool_data_testing.json') as f:
    pools = json.load(f)
pools = [pool for pool in pools]
pools[0]
static_pools = pools
state = pools
exchanges = list({ex['exchange_name'] for ex in state})
db = QueryInterface(state=state, ConfigObj=cfg, exchanges=exchanges)





# ------------------------------------------------------------
# Test      069
# File      test_069_TestTxHelpers.py
# Segment   Test_HAS_LAYER_ONE_GAS_FEE
# ------------------------------------------------------------
def test_test_has_layer_one_gas_fee():
# ------------------------------------------------------------
    
    # +
    ethereum_cfg = Config.new(config=Config.CONFIG_MAINNET, blockchain="ethereum")
    polygon_cfg = Config.new(config=Config.CONFIG_MAINNET, blockchain="polygon")
    optimism_cfg = Config.new(config=Config.CONFIG_MAINNET, blockchain="optimism")
    polygon_zkevm_cfg = Config.new(config=Config.CONFIG_MAINNET, blockchain="polygon_zkevm")
    arbitrum_cfg = Config.new(config=Config.CONFIG_MAINNET, blockchain="arbitrum_one")
    base_cfg = Config.new(config=Config.CONFIG_MAINNET, blockchain="coinbase_base")
    
    
    assert not ethereum_cfg.network.GAS_ORACLE_ADDRESS
    assert not polygon_cfg.network.GAS_ORACLE_ADDRESS
    assert not polygon_zkevm_cfg.network.GAS_ORACLE_ADDRESS
    assert not arbitrum_cfg.network.GAS_ORACLE_ADDRESS
    assert optimism_cfg.network.GAS_ORACLE_ADDRESS
    assert base_cfg.network.GAS_ORACLE_ADDRESS
    # -
    