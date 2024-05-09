# ------------------------------------------------------------
# Auto generated test file `test_034_Interface.py`
# ------------------------------------------------------------
# source file   = NBTest_034_Interface.py
# test id       = 034
# test comment  = Interface
# ------------------------------------------------------------




from unittest.mock import MagicMock
from unittest.mock import Mock

from fastlane_bot import Bot
from fastlane_bot.events.exchanges import UniswapV2, UniswapV3, CarbonV1, BancorV3
from fastlane_bot.events.interface import QueryInterface, Token
from fastlane_bot.tools.cpc import ConstantProductCurve as CPC

print("{0.__name__} v{0.__VERSION__} ({0.__DATE__})".format(CPC))
print("{0.__name__} v{0.__VERSION__} ({0.__DATE__})".format(Bot))
print("{0.__name__} v{0.__VERSION__} ({0.__DATE__})".format(UniswapV2))
print("{0.__name__} v{0.__VERSION__} ({0.__DATE__})".format(UniswapV3))
print("{0.__name__} v{0.__VERSION__} ({0.__DATE__})".format(CarbonV1))
print("{0.__name__} v{0.__VERSION__} ({0.__DATE__})".format(BancorV3))
print("{0.__name__} v{0.__VERSION__} ({0.__DATE__})".format(QueryInterface))
print("{0.__name__} v{0.__VERSION__} ({0.__DATE__})".format(Token))

from fastlane_bot.testing import *

#plt.style.use('seaborn-dark')
plt.rcParams['figure.figsize'] = [12,6]
from fastlane_bot import __VERSION__
require("3.0", __VERSION__)

cfg_mock = Mock()
cfg_mock.logger = MagicMock()
qi = QueryInterface(mgr=None, ConfigObj=cfg_mock)
qi.state = [{'exchange_name': 'uniswap_v2', 'address': '0x123', 'tkn0_key': 'TKN-0x123', 'tkn1_key': 'TKN-0x456', 'pair_name': 'Pair-0x789', 'liquidity': 10}, {'exchange_name': 'sushiswap_v2', 'address': '0xabc', 'tkn0_key': 'TKN-0xabc', 'tkn1_key': 'TKN-0xdef', 'pair_name': 'Pair-0xghi', 'liquidity': 0}]


# ------------------------------------------------------------
# Test      034
# File      test_034_Interface.py
# Segment   test_remove_unsupported_exchanges
# ------------------------------------------------------------
def test_test_remove_unsupported_exchanges():
# ------------------------------------------------------------
    
    qi.exchanges = ['uniswap_v2', 'fakeswap']
    qi.remove_unsupported_exchanges()
    assert (len(qi.state) == 1)
    

# ------------------------------------------------------------
# Test      034
# File      test_034_Interface.py
# Segment   test_has_balance
# ------------------------------------------------------------
def test_test_has_balance():
# ------------------------------------------------------------
    
    qi.state = [{'exchange_name': 'uniswap_v2', 'address': '0x123', 'tkn0_key': 'TKN-0x123', 'tkn1_key': 'TKN-0x456', 'pair_name': 'Pair-0x789', 'liquidity': 10}, {'exchange_name': 'sushiswap_v2', 'address': '0xabc', 'tkn0_key': 'TKN-0xabc', 'tkn1_key': 'TKN-0xdef', 'pair_name': 'Pair-0xghi', 'liquidity': 0}]
    assert (qi.has_balance(qi.state[0], ['liquidity']) == True)
    assert (qi.has_balance(qi.state[1], ['liquidity']) == False)
    

# ------------------------------------------------------------
# Test      034
# File      test_034_Interface.py
# Segment   test_filter_pools
# ------------------------------------------------------------
def test_test_filter_pools():
# ------------------------------------------------------------
    
    assert (len(qi.filter_pools('uniswap_v2')) == 1)
    

# ------------------------------------------------------------
# Test      034
# File      test_034_Interface.py
# Segment   test_update_state
# ------------------------------------------------------------
def test_test_update_state():
# ------------------------------------------------------------
    
    new_state = [{'exchange_name': 'bancor_v2', 'address': '0xabc', 'tkn0_key': 'TKN-0xabc', 'tkn1_key': 'TKN-0xdef', 'pair_name': 'Pair-0xghi', 'liquidity': 10}]
    qi.update_state(new_state)
    

# ------------------------------------------------------------
# Test      034
# File      test_034_Interface.py
# Segment   test_get_token
# ------------------------------------------------------------
def test_test_get_token():
# ------------------------------------------------------------
    
    # +
    new_state = {'fee':'0','exchange_name': 'bancor_v2', 'address': '0xabc', 'pair_name': 'Pair-0xghi', 'liquidity': 10, 'tkn0_decimals': 18, 'tkn1_decimals': 6, 'tkn0_symbol': 'ETH', 'tkn1_symbol': 'USDC', 'tkn0_address': 'Ox9er', 'tkn1_address': 'Ox8er'}
    new_state['descr'] = new_state['exchange_name'] + ' ' + new_state['pair_name'] + ' ' + new_state['fee']
    qi.update_state([new_state])
    token = qi.get_token('Ox9er')
    
    assert isinstance(token, Token)
    # -
    

# ------------------------------------------------------------
# Test      034
# File      test_034_Interface.py
# Segment   test_get_pool
# ------------------------------------------------------------
def test_test_get_pool():
# ------------------------------------------------------------
    
    new_state = [{'last_updated_block': 17614344, 'address': '0xC537e898CD774e2dCBa3B14Ea6f34C93d5eA45e1', 'exchange_name': 'carbon_v1', 'tkn0_address': '0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE', 'tkn1_address': '0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48', 'tkn0_symbol': 'ETH', 'tkn1_symbol': 'USDC', 'tkn0_decimals': 18, 'tkn1_decimals': 6, 'cid': 1701411834604692317316873037158841057365, 'tkn0_key': 'ETH-EEeE', 'tkn1_key': 'USDC-eB48', 'pair_name': 'ETH-EEeE/USDC-eB48', 'fee_float': 0.002, 'fee': '0.002', 'descr': 'carbon_v1 ETH-EEeE/USDC-eB48 0.002', 'y_0': 9882507039899549, 'y_1': 0, 'z_0': 9882507039899549, 'z_1': 17936137, 'A_0': 0, 'A_1': 99105201, 'B_0': 0, 'B_1': 11941971885}]
    qi.update_state(new_state)
    pool = qi.get_pool(cid=1701411834604692317316873037158841057365)
    
    