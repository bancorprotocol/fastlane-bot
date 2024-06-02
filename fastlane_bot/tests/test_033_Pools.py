# ------------------------------------------------------------
# Auto generated test file `test_033_Pools.py`
# ------------------------------------------------------------
# source file   = NBTest_033_Pools.py
# test id       = 033
# test comment  = Pools
# ------------------------------------------------------------



import json

from arb_optimizer import ConstantProductCurve as CPC

from fastlane_bot import Bot
from fastlane_bot.events.interfaces.event import Event
from fastlane_bot.events.pools import BancorPolPool, BancorV2Pool, BancorV3Pool, CarbonV1Pool, SolidlyV2Pool, \
    UniswapV2Pool, UniswapV3Pool

print("{0.__name__} v{0.__VERSION__} ({0.__DATE__})".format(CPC))
print("{0.__name__} v{0.__VERSION__} ({0.__DATE__})".format(Bot))
print("{0.__name__} v{0.__VERSION__} ({0.__DATE__})".format(UniswapV2Pool))
print("{0.__name__} v{0.__VERSION__} ({0.__DATE__})".format(UniswapV3Pool))
print("{0.__name__} v{0.__VERSION__} ({0.__DATE__})".format(CarbonV1Pool))
print("{0.__name__} v{0.__VERSION__} ({0.__DATE__})".format(BancorV3Pool))
print("{0.__name__} v{0.__VERSION__} ({0.__DATE__})".format(BancorV2Pool))
print("{0.__name__} v{0.__VERSION__} ({0.__DATE__})".format(BancorPolPool))
print("{0.__name__} v{0.__VERSION__} ({0.__DATE__})".format(SolidlyV2Pool))


from fastlane_bot.testing import *

#plt.style.use('seaborn-dark')
plt.rcParams['figure.figsize'] = [12,6]
from fastlane_bot import __VERSION__
require("3.0", __VERSION__)

with open('fastlane_bot/tests/_data/event_test_data.json', 'r') as f:
    setup_data = json.load(f)


# ------------------------------------------------------------
# Test      033
# File      test_033_Pools.py
# Segment   test_uniswap_v2_pool
# ------------------------------------------------------------
def test_test_uniswap_v2_pool():
# ------------------------------------------------------------
    
    uniswap_v2_pool = UniswapV2Pool()
    uniswap_v2_pool.update_from_event(Event.from_dict(setup_data['uniswap_v2_event']), {'cid': '0x', 'fee': '0.000', 'fee_float': 0.0, 'exchange_name': 'sushiswap_v2', 'reserve0': setup_data['uniswap_v2_event']['args']['reserve0'], 'reserve1': setup_data['uniswap_v2_event']['args']['reserve1'], 'tkn0_symbol': 'tkn0', 'tkn1_symbol': 'tkn1'})
    assert (uniswap_v2_pool.state['tkn0_balance'] == setup_data['uniswap_v2_event']['args']['reserve0'])
    

# ------------------------------------------------------------
# Test      033
# File      test_033_Pools.py
# Segment   test_solidly_v2_pool
# ------------------------------------------------------------
def test_test_solidly_v2_pool():
# ------------------------------------------------------------
    
    solidly_v2_pool = SolidlyV2Pool()
    solidly_v2_pool.update_from_event(Event.from_dict(setup_data['solidly_v2_event']), {'cid': '0x', 'fee': '0.000', 'fee_float': 0.0, 'exchange_name': 'velocimeter_v2', 'reserve0': setup_data['solidly_v2_event']['args']['reserve0'], 'reserve1': setup_data['solidly_v2_event']['args']['reserve1'], 'tkn0_symbol': 'tkn0', 'tkn1_symbol': 'tkn1'})
    assert (solidly_v2_pool.state['tkn0_balance'] == setup_data['solidly_v2_event']['args']['reserve0'])
    

# ------------------------------------------------------------
# Test      033
# File      test_033_Pools.py
# Segment   test_bancor_v2_pool
# ------------------------------------------------------------
def test_test_bancor_v2_pool():
# ------------------------------------------------------------
    
    bancor_v2_pool = BancorV2Pool()
    bancor_v2_pool.state['tkn0_address'] = '0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE'
    bancor_v2_pool.state['tkn1_address'] = '0x1F573D6Fb3F13d689FF844B4cE37794d79a7FF1C'
    bancor_v2_pool.state['anchor']= '0xb1CD6e4153B2a390Cf00A6556b0fC1458C4A5533'
    bancor_v2_pool.update_from_event(Event.from_dict(setup_data['bancor_v2_event']), {'cid': '0x', 'fee': '0.000', 'fee_float': 0.0, 'exchange_name': 'bancor_v2'})
    assert (5698079648237338312679700 == setup_data['bancor_v2_event']['args']['_rateN']), f"expected {bancor_v2_pool.state['tkn0_balance']}, found {setup_data['bancor_v2_event']['args']['_rateN']}"
    assert (1404376232459809237924 == setup_data['bancor_v2_event']['args']['_rateD']), f"expected {bancor_v2_pool.state['tkn1_balance']}, found {setup_data['bancor_v2_event']['args']['_rateD']}"
    

# ------------------------------------------------------------
# Test      033
# File      test_033_Pools.py
# Segment   test_pancakeswap_v2_pool
# ------------------------------------------------------------
def test_test_pancakeswap_v2_pool():
# ------------------------------------------------------------
    
    pancakeswap_v2_pool = UniswapV2Pool()
    pancakeswap_v2_pool.update_from_event(Event.from_dict(setup_data['pancakeswap_v2_event']), {'cid': '0x', 'fee': '0.000', 'fee_float': 0.0, 'exchange_name': 'pancakeswap_v2', 'reserve0': setup_data['pancakeswap_v2_event']['args']['reserve0'], 'reserve1': setup_data['pancakeswap_v2_event']['args']['reserve1'], 'tkn0_symbol': 'tkn0', 'tkn1_symbol': 'tkn1'})
    assert (pancakeswap_v2_pool.state['tkn0_balance'] == setup_data['pancakeswap_v2_event']['args']['reserve0'])
    

# ------------------------------------------------------------
# Test      033
# File      test_033_Pools.py
# Segment   test_uniswap_v3_pool
# ------------------------------------------------------------
def test_test_uniswap_v3_pool():
# ------------------------------------------------------------
    
    uniswap_v3_pool = UniswapV3Pool()
    uniswap_v3_pool.update_from_event(Event.from_dict(setup_data['uniswap_v3_event']), {'cid': '0x', 'fee': '0.000', 'fee_float': 0.0, 'exchange_name': 'uniswap_v3', 'liquidity': setup_data['uniswap_v3_event']['args']['liquidity'], 'sqrtPriceX96': setup_data['uniswap_v3_event']['args']['sqrtPriceX96'], 'tick': setup_data['uniswap_v3_event']['args']['tick'], 'tkn0_symbol': 'tkn0', 'tkn1_symbol': 'tkn1'})
    assert (uniswap_v3_pool.state['liquidity'] == setup_data['uniswap_v3_event']['args']['liquidity'])
    assert (uniswap_v3_pool.state['sqrt_price_q96'] == setup_data['uniswap_v3_event']['args']['sqrtPriceX96'])
    

# ------------------------------------------------------------
# Test      033
# File      test_033_Pools.py
# Segment   test_pancakeswap_v3_pool
# ------------------------------------------------------------
def test_test_pancakeswap_v3_pool():
# ------------------------------------------------------------
    
    pancakeswap_v3_pool = UniswapV3Pool()
    pancakeswap_v3_pool.update_from_event(Event.from_dict(setup_data['pancakeswap_v3_event']), {'cid': '0x', 'fee': '0.000', 'fee_float': 0.0, 'exchange_name': 'pancakeswap_v3', 'liquidity': setup_data['pancakeswap_v3_event']['args']['liquidity'], 'sqrtPriceX96': setup_data['pancakeswap_v3_event']['args']['sqrtPriceX96'], 'tick': setup_data['pancakeswap_v3_event']['args']['tick'], 'tkn0_symbol': 'tkn0', 'tkn1_symbol': 'tkn1'})
    assert (pancakeswap_v3_pool.state['liquidity'] == setup_data['pancakeswap_v3_event']['args']['liquidity'])
    assert (pancakeswap_v3_pool.state['sqrt_price_q96'] == setup_data['pancakeswap_v3_event']['args']['sqrtPriceX96'])
    

# ------------------------------------------------------------
# Test      033
# File      test_033_Pools.py
# Segment   test_bancor_v3_pool
# ------------------------------------------------------------
def test_test_bancor_v3_pool():
# ------------------------------------------------------------
    
    bancor_v3_pool = BancorV3Pool()
    bancor_v3_pool.update_from_event(Event.from_dict(setup_data['bancor_v3_event']), {'cid': '0x', 'fee': '0.000', 'fee_float': 0.0, 'exchange_name': 'bancor_v3', 'tkn0_balance': setup_data['bancor_v3_event']['args']['newLiquidity'], 'tkn1_balance': 0, 'tkn0_symbol': 'tkn0', 'tkn1_symbol': 'tkn1'})
    

# ------------------------------------------------------------
# Test      033
# File      test_033_Pools.py
# Segment   test_carbon_v1_pool_update
# ------------------------------------------------------------
def test_test_carbon_v1_pool_update():
# ------------------------------------------------------------
    
    carbon_v1_pool = CarbonV1Pool()
    carbon_v1_pool.update_from_event(Event.from_dict(setup_data['carbon_v1_event_create_for_update']), {})
    strat_id = setup_data['carbon_v1_event_update']['args']['id']
    assert (strat_id == carbon_v1_pool.state['strategy_id'])
    assert (carbon_v1_pool.state['y_0'] == 0)
    assert (carbon_v1_pool.state['z_0'] == 0)
    assert (carbon_v1_pool.state['A_0'] == 0)
    assert (carbon_v1_pool.state['B_0'] == 0)
    assert (carbon_v1_pool.state['y_1'] == 0)
    assert (carbon_v1_pool.state['z_1'] == 0)
    assert (carbon_v1_pool.state['A_1'] == 0)
    assert (carbon_v1_pool.state['B_1'] == 0)
    carbon_v1_pool.update_from_event(Event.from_dict(setup_data['carbon_v1_event_update']), {})
    assert (carbon_v1_pool.state['y_0'] == setup_data['carbon_v1_event_update']['args']['order0'][0])
    assert (carbon_v1_pool.state['z_0'] == setup_data['carbon_v1_event_update']['args']['order0'][1])
    assert (carbon_v1_pool.state['A_0'] == setup_data['carbon_v1_event_update']['args']['order0'][2])
    assert (carbon_v1_pool.state['B_0'] == setup_data['carbon_v1_event_update']['args']['order0'][3])
    assert (carbon_v1_pool.state['y_1'] == setup_data['carbon_v1_event_update']['args']['order1'][0])
    assert (carbon_v1_pool.state['z_1'] == setup_data['carbon_v1_event_update']['args']['order1'][1])
    assert (carbon_v1_pool.state['A_1'] == setup_data['carbon_v1_event_update']['args']['order1'][2])
    

# ------------------------------------------------------------
# Test      033
# File      test_033_Pools.py
# Segment   test_carbon_v1_pool_delete
# ------------------------------------------------------------
def test_test_carbon_v1_pool_delete():
# ------------------------------------------------------------
    
    carbon_v1_pool = CarbonV1Pool()
    carbon_v1_pool.update_from_event(Event.from_dict(setup_data['carbon_v1_event_create_for_delete']), {})
    strat_id = setup_data['carbon_v1_event_update']['args']['id']
    assert (strat_id == carbon_v1_pool.state['strategy_id'])
    assert (carbon_v1_pool.state['y_0'] == setup_data['carbon_v1_event_delete']['args']['order0'][0])
    assert (carbon_v1_pool.state['z_0'] == setup_data['carbon_v1_event_delete']['args']['order0'][1])
    assert (carbon_v1_pool.state['A_0'] == setup_data['carbon_v1_event_delete']['args']['order0'][2])
    assert (carbon_v1_pool.state['B_0'] == setup_data['carbon_v1_event_delete']['args']['order0'][3])
    assert (carbon_v1_pool.state['y_1'] == setup_data['carbon_v1_event_delete']['args']['order1'][0])
    assert (carbon_v1_pool.state['z_1'] == setup_data['carbon_v1_event_delete']['args']['order1'][1])
    assert (carbon_v1_pool.state['A_1'] == setup_data['carbon_v1_event_delete']['args']['order1'][2])
    assert (carbon_v1_pool.state['B_1'] == setup_data['carbon_v1_event_delete']['args']['order1'][3])
    carbon_v1_pool.update_from_event(Event.from_dict(setup_data['carbon_v1_event_delete']), {})
    assert (carbon_v1_pool.state['y_0'] == 0)
    assert (carbon_v1_pool.state['z_0'] == 0)
    assert (carbon_v1_pool.state['A_0'] == 0)
    assert (carbon_v1_pool.state['B_0'] == 0)
    assert (carbon_v1_pool.state['y_1'] == 0)
    assert (carbon_v1_pool.state['z_1'] == 0)
    assert (carbon_v1_pool.state['A_1'] == 0)
    
    #
    

# ------------------------------------------------------------
# Test      033
# File      test_033_Pools.py
# Segment   test_bancor_pol_token_traded_event
# ------------------------------------------------------------
def test_test_bancor_pol_token_traded_event():
# ------------------------------------------------------------
    
    bancor_pol_pool = BancorPolPool()
    bancor_pol_pool.state['tkn0_address'] = setup_data['bancor_pol_token_traded_event']['args']['token']
    bancor_pol_pool.state['tkn0_balance'] = 10 + setup_data['bancor_pol_token_traded_event']['args']['amount']
    bancor_pol_pool.update_from_event(Event.from_dict(setup_data['bancor_pol_token_traded_event']), 
                      {'cid': '0x', 
                       'fee': '0.000', 
                       'fee_float': 0.0, 
                       'exchange_name': 'bancor_pol', 
                       'token': setup_data['bancor_pol_token_traded_event']['args']['token'], 
                       'amount': setup_data['bancor_pol_token_traded_event']['args']['amount'], 
                       'ethReceived': setup_data['bancor_pol_token_traded_event']['args']['ethReceived'], 
                       'tkn0_symbol': 'tkn0', 
                       'tkn1_symbol': 'tkn1',}
    )
    assert (bancor_pol_pool.state['tkn0_balance'] == 10 + setup_data['bancor_pol_token_traded_event']['args']['amount'])
    

# ------------------------------------------------------------
# Test      033
# File      test_033_Pools.py
# Segment   test_bancor_pol_trading_enabled_event
# ------------------------------------------------------------
def test_test_bancor_pol_trading_enabled_event():
# ------------------------------------------------------------
    
    bancor_pol_pool = BancorPolPool()
    bancor_pol_pool.state['tkn0_address'] = None
    bancor_pol_pool.update_from_event(Event.from_dict(setup_data['bancor_pol_trading_enabled_event']),
                                      {'cid': '0x',
                                       'fee': '0.000',
                                       'fee_float': 0.0,
                                       'exchange_name': 'bancor_pol',
                                       'token': setup_data['bancor_pol_trading_enabled_event']['args']['token'],
                                       'tkn0_symbol': 'tkn0',
                                       'tkn1_symbol': 'tkn1'}
                                      )
    assert (bancor_pol_pool.state['tkn0_address'] == setup_data['bancor_pol_trading_enabled_event']['args']['token'])