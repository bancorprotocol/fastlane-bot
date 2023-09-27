# ------------------------------------------------------------
# Auto generated test file `test_036_Manager.py`
# ------------------------------------------------------------
# source file   = NBTest_036_Manager.py
# test id       = 036
# test comment  = Manager
# ------------------------------------------------------------



from unittest.mock import Mock, patch, call

import pytest
from unittest.mock import MagicMock

from fastlane_bot import Bot, Config
from fastlane_bot.events.exchanges import UniswapV2, UniswapV3, SushiswapV2, CarbonV1, BancorV3
from fastlane_bot.events.managers.manager import Manager
Base = None
from fastlane_bot.tools.cpc import ConstantProductCurve as CPC

print("{0.__name__} v{0.__VERSION__} ({0.__DATE__})".format(CPC))
print("{0.__name__} v{0.__VERSION__} ({0.__DATE__})".format(Bot))
print("{0.__name__} v{0.__VERSION__} ({0.__DATE__})".format(UniswapV2))
print("{0.__name__} v{0.__VERSION__} ({0.__DATE__})".format(UniswapV3))
print("{0.__name__} v{0.__VERSION__} ({0.__DATE__})".format(SushiswapV2))
print("{0.__name__} v{0.__VERSION__} ({0.__DATE__})".format(CarbonV1))
print("{0.__name__} v{0.__VERSION__} ({0.__DATE__})".format(BancorV3))
from fastlane_bot.testing import *

#plt.style.use('seaborn-dark')
plt.rcParams['figure.figsize'] = [12,6]
from fastlane_bot import __VERSION__
require("3.0", __VERSION__)


#

import json

with open("fastlane_bot/data/event_test_data.json", "r") as f:
    event_data = json.load(f)

with open("fastlane_bot/data/test_pool_data.json", "r") as f:
    pool_data = json.load(f)


cfg = Config.new(config=Config.CONFIG_MAINNET)

manager = Manager(cfg.w3, cfg, pool_data, 20, SUPPORTED_EXCHANGES=['bancor_v3', 'carbon_v1', 'uniswap_v2', 'uniswap_v3'])



# ------------------------------------------------------------
# Test      036
# File      test_036_Manager.py
# Segment   test_update_from_event_uniswap_v2
# ------------------------------------------------------------
def test_test_update_from_event_uniswap_v2():
# ------------------------------------------------------------
    
    # +
    event = event_data['uniswap_v2_event']
    
    assert event['args']['reserve0'] != [pool['tkn0_balance'] for pool in manager.pool_data if pool['address'] == event['address']][0]
    
    manager.update_from_event(event)
    
    assert event['address'] in [pool['address'] for pool in manager.pool_data]
    assert event['args']['reserve0'] == [pool['tkn0_balance'] for pool in manager.pool_data if pool['address'] == event['address']][0]
    # -
    

# ------------------------------------------------------------
# Test      036
# File      test_036_Manager.py
# Segment   test_update_from_event_uniswap_v3
# ------------------------------------------------------------
def test_test_update_from_event_uniswap_v3():
# ------------------------------------------------------------
    
    # +
    event = event_data['uniswap_v3_event']
    
    assert event['args']['liquidity'] != [pool['liquidity'] for pool in manager.pool_data if pool['address'] == event['address']][0]
    
    manager.update_from_event(event)
    
    assert event['address'] in [pool['address'] for pool in manager.pool_data]
    assert event['args']['liquidity'] == [pool['liquidity'] for pool in manager.pool_data if pool['address'] == event['address']][0]
    # -
    
    #
    

# ------------------------------------------------------------
# Test      036
# File      test_036_Manager.py
# Segment   test_update_from_event_carbon_v1_update
# ------------------------------------------------------------
def test_test_update_from_event_carbon_v1_update():
# ------------------------------------------------------------
    
    # +
    event_create_for_update = event_data['carbon_v1_event_create_for_update']
    event = event_data['carbon_v1_event_update']
    
    manager.update_from_event(event_create_for_update)
    assert event['args']['order0'][0] != [pool['y_0'] for pool in manager.pool_data if pool['cid'] == event['args']['id']][0]
    
    manager.update_from_event(event)
    
    assert event['args']['order0'][0] == [pool['y_0'] for pool in manager.pool_data if pool['cid'] == event['args']['id']][0]
    # -
    

# ------------------------------------------------------------
# Test      036
# File      test_036_Manager.py
# Segment   test_update_from_event_carbon_v1_create
# ------------------------------------------------------------
def test_test_update_from_event_carbon_v1_create():
# ------------------------------------------------------------
    #
    
    # +
    event = event_data['carbon_v1_event_create']
    manager.pool_data = [pool for pool in manager.pool_data if pool['cid'] != event['args']['id']]
    assert event['args']['id'] not in [pool['cid'] for pool in manager.pool_data]
    
    manager.update_from_event(event)
    
    assert event['args']['id'] in [pool['cid'] for pool in manager.pool_data]
    # -
    

# ------------------------------------------------------------
# Test      036
# File      test_036_Manager.py
# Segment   test_update_from_event_carbon_v1_delete
# ------------------------------------------------------------
def test_test_update_from_event_carbon_v1_delete():
# ------------------------------------------------------------
    
    # +
    event = event_data['carbon_v1_event_create']
    manager.pool_data = [pool for pool in manager.pool_data if pool['cid'] != event['args']['id']]
    assert event['args']['id'] not in [pool['cid'] for pool in manager.pool_data]
    
    manager.update_from_event(event)
    
    assert event['args']['id'] in [pool['cid'] for pool in manager.pool_data]
    
    event['event'] = 'StrategyDeleted'
    
    manager.update_from_event(event)
    
    assert event['args']['id'] not in [pool['cid'] for pool in manager.pool_data]
    # -
    
    #