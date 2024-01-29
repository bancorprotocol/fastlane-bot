# ------------------------------------------------------------
# Auto generated test file `test_049_CustomTradingFees.py`
# ------------------------------------------------------------
# source file   = NBTest_049_CustomTradingFees.py
# test id       = 049
# test comment  = CustomTradingFees
# ------------------------------------------------------------



from unittest.mock import Mock, patch, call

import pytest
from unittest.mock import MagicMock

from fastlane_bot import Bot, Config
from fastlane_bot.events.exchanges import UniswapV2, UniswapV3,  CarbonV1, BancorV3
from fastlane_bot.events.managers.manager import Manager
Base = None
from fastlane_bot.tools.cpc import ConstantProductCurve as CPC

print("{0.__name__} v{0.__VERSION__} ({0.__DATE__})".format(CPC))
print("{0.__name__} v{0.__VERSION__} ({0.__DATE__})".format(Bot))
print("{0.__name__} v{0.__VERSION__} ({0.__DATE__})".format(UniswapV2))
print("{0.__name__} v{0.__VERSION__} ({0.__DATE__})".format(UniswapV3))

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
# Test      049
# File      test_049_CustomTradingFees.py
# Segment   test_update_from_event_carbon_v1_pair_create
# ------------------------------------------------------------
def test_test_update_from_event_carbon_v1_pair_create():
# ------------------------------------------------------------
    
    # +
    event = event_data['carbon_v1_event_pair_created']
    assert (event['args']['token0'], event['args']['token1']) not in manager.fee_pairs
    
    manager.update_from_event(event)
    
    assert (event['args']['token0'], event['args']['token1']) in manager.fee_pairs
    
    # -
    

# ------------------------------------------------------------
# Test      049
# File      test_049_CustomTradingFees.py
# Segment   test_update_from_event_carbon_v1_trading_fee_updated
# ------------------------------------------------------------
def test_test_update_from_event_carbon_v1_trading_fee_updated():
# ------------------------------------------------------------
    #
    
    # +
    event = event_data['carbon_v1_trading_fee_updated']
    prevFeePPM = event['args']['prevFeePPM']
    newFeePPM = event['args']['newFeePPM']
    
    mocked_contract = Mock()
    mocked_contract.functions.tradingFeePPM.return_value.call.return_value = prevFeePPM
    assert int(manager.exchanges['carbon_v1'].get_fee('', mocked_contract)[0]) == prevFeePPM
    
    # find all pools with fee==prevFeePPM
    prev_default_pools = [idx for idx, pool in enumerate(manager.pool_data) if pool['fee'] == prevFeePPM]
    
    manager.update_from_event(event)
    
    for idx in prev_default_pools:
        assert manager.pool_data[idx]['fee'] == newFeePPM
    
    mocked_contract.functions.tradingFeePPM.return_value.call.return_value = newFeePPM
    
    assert int(manager.exchanges['carbon_v1'].get_fee('', mocked_contract)[0]) == newFeePPM
    # -
    

# ------------------------------------------------------------
# Test      049
# File      test_049_CustomTradingFees.py
# Segment   test_update_from_event_carbon_v1_pair_trading_fee_updated
# ------------------------------------------------------------
def test_test_update_from_event_carbon_v1_pair_trading_fee_updated():
# ------------------------------------------------------------
    
    # +
    event = event_data['carbon_v1_pair_trading_fee_updated']
    prevFeePPM = event['args']['prevFeePPM']
    newFeePPM = event['args']['newFeePPM']
    token0 = event['args']['token0']
    token1 = event['args']['token1']
    
    # set the fee for the pair to prevFeePPM
    idxs = [idx for idx, pool in enumerate(manager.pool_data) if pool['tkn0_address'] == token0 and pool['tkn1_address'] == token1 and pool['exchange_name'] == 'carbon_v1']
    for idx in idxs:
        manager.pool_data[idx]['fee'] = f"{prevFeePPM}"
        manager.pool_data[idx]['fee_float'] = prevFeePPM / 1e6
    
    # set all other pools with a different fee than prevFeePPM
    others = [i for i, pool in enumerate(manager.pool_data) if i not in idxs and pool['exchange_name'] == 'carbon_v1']
    for i in others:
        manager.pool_data[i]['fee'] = f"{prevFeePPM-1}"
        manager.pool_data[i]['fee_float'] = (prevFeePPM-1) / 1e6
    
    manager.update_from_event(event)
    
    # check that the fee for the pair is now newFeePPM
    for idx in idxs:
        assert manager.pool_data[idx]['fee'] == f"{newFeePPM}"
        assert manager.pool_data[idx]['fee_float'] == newFeePPM / 1e6
        
    # check that all other pools have not been changed
    for i in others:
        assert manager.pool_data[i]['fee'] == f"{prevFeePPM-1}"
        assert manager.pool_data[i]['fee_float'] == (prevFeePPM-1) / 1e6
    
    # -
    
    #
    
    #