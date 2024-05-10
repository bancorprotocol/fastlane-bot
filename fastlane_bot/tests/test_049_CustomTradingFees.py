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
from fastlane_bot.events.interfaces.event import Event
from fastlane_bot.events.exchanges import UniswapV2, UniswapV3,  CarbonV1, BancorV3
from fastlane_bot.events.managers.manager import Manager
Base = None
from fastlane_bot.tools.cpc import ConstantProductCurve as CPC
import asyncio
from unittest.mock import AsyncMock
import nest_asyncio
nest_asyncio.apply()
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

nest_asyncio

import json

with open("fastlane_bot/tests/_data/event_test_data.json", "r") as f:
    event_data = json.load(f)

with open("fastlane_bot/tests/_data/test_pool_data.json", "r") as f:
    pool_data = json.load(f)


cfg = Config.new(config=Config.CONFIG_MAINNET)

manager = Manager(web3=cfg.w3,
    w3_async=cfg.w3_async,
    cfg=cfg, 
    pool_data=pool_data, 
    alchemy_max_block_fetch=20, 
    SUPPORTED_EXCHANGES=['bancor_v3', 'carbon_v1', 'uniswap_v2', 'uniswap_v3'])



# ------------------------------------------------------------
# Test      049
# File      test_049_CustomTradingFees.py
# Segment   test_update_from_event_carbon_v1_pair_create
# ------------------------------------------------------------
def test_test_update_from_event_carbon_v1_pair_create():
# ------------------------------------------------------------
    
    # +
    event = event_data['carbon_v1_event_pair_created']

    exchange_name = 'carbon_v1'

    manager.fee_pairs[exchange_name] = {}

    assert (event['args']['token0'], event['args']['token1']) not in manager.fee_pairs[exchange_name]

    manager.update_from_event(Event.from_dict(event))

    assert (event['args']['token0'], event['args']['token1']) in manager.fee_pairs[exchange_name]
    

    

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
    new_mocked_contract = Mock()
    mocked_contract.caller.tradingFeePPM =  AsyncMock(return_value=prevFeePPM)
    new_mocked_contract.caller.tradingFeePPM = AsyncMock(return_value=newFeePPM)
    
    @pytest.mark.asyncio
    async def test_update_from_event_carbon_v1_trading_fee_updated():
        val = await manager.exchanges['carbon_v1'].get_fee('', mocked_contract)
        assert int(val[0]) == prevFeePPM
        
        # find all pools with fee==prevFeePPM
        prev_default_pools = [idx for idx, pool in enumerate(manager.pool_data) if pool['fee'] == prevFeePPM]
        
        manager.update_from_event(Event.from_dict(event))
    
        for idx in prev_default_pools:
            assert manager.pool_data[idx]['fee'] == newFeePPM
        
        val2 = await manager.exchanges['carbon_v1'].get_fee('', new_mocked_contract)
        assert int(val2[0]) == newFeePPM
    
    # Run the test in an event loop
    asyncio.run(test_update_from_event_carbon_v1_trading_fee_updated())
    # -
