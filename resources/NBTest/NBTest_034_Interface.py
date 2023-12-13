# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:light
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.14.5
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# +
from dataclasses import asdict
from unittest.mock import MagicMock
from unittest.mock import Mock

import pytest

from fastlane_bot import Bot
from fastlane_bot.events.exchanges import UniswapV2, UniswapV3, SushiswapV2, CarbonV1, BancorV3
from fastlane_bot.events.interface import QueryInterface, Token
from fastlane_bot.tools.cpc import ConstantProductCurve as CPC

print("{0.__name__} v{0.__VERSION__} ({0.__DATE__})".format(CPC))
print("{0.__name__} v{0.__VERSION__} ({0.__DATE__})".format(Bot))
print("{0.__name__} v{0.__VERSION__} ({0.__DATE__})".format(UniswapV2))
print("{0.__name__} v{0.__VERSION__} ({0.__DATE__})".format(UniswapV3))
print("{0.__name__} v{0.__VERSION__} ({0.__DATE__})".format(SushiswapV2))
print("{0.__name__} v{0.__VERSION__} ({0.__DATE__})".format(CarbonV1))
print("{0.__name__} v{0.__VERSION__} ({0.__DATE__})".format(BancorV3))
print("{0.__name__} v{0.__VERSION__} ({0.__DATE__})".format(QueryInterface))
print("{0.__name__} v{0.__VERSION__} ({0.__DATE__})".format(Token))

from fastlane_bot.testing import *

#plt.style.use('seaborn-dark')
plt.rcParams['figure.figsize'] = [12,6]
from fastlane_bot import __VERSION__
require("3.0", __VERSION__)
# -

cfg_mock = Mock()
cfg_mock.logger = MagicMock()
cfg_mock.GAS_TKN_IN_FLASHLOAN_TOKENS = False
qi = QueryInterface(mgr=None, ConfigObj=cfg_mock)
qi.state = [{'exchange_name': 'uniswap_v2', 'address': '0x123', 'tkn0_key': 'TKN-0x123', 'tkn1_key': 'TKN-0x456', 'pair_name': 'Pair-0x789', 'liquidity': 10}, {'exchange_name': 'sushiswap_v2', 'address': '0xabc', 'tkn0_key': 'TKN-0xabc', 'tkn1_key': 'TKN-0xdef', 'pair_name': 'Pair-0xghi', 'liquidity': 0}]

# ## test_remove_unsupported_exchanges

qi.exchanges = ['uniswap_v2', 'fakeswap']
qi.remove_unsupported_exchanges()
assert (len(qi.state) == 1)

# ## test_has_balance

qi.state = [{'exchange_name': 'uniswap_v2', 'address': '0x123', 'tkn0_key': 'TKN-0x123', 'tkn1_key': 'TKN-0x456', 'pair_name': 'Pair-0x789', 'liquidity': 10}, {'exchange_name': 'sushiswap_v2', 'address': '0xabc', 'tkn0_key': 'TKN-0xabc', 'tkn1_key': 'TKN-0xdef', 'pair_name': 'Pair-0xghi', 'liquidity': 0}]
assert (qi.has_balance(qi.state[0], ['liquidity']) == True)
assert (qi.has_balance(qi.state[1], ['liquidity']) == False)

# ## test_filter_pools

assert (len(qi.filter_pools('uniswap_v2')) == 1)

# ## test_cleanup_token_key

assert (qi.cleanup_token_key('TKN-Hello-0x123') == 'TKN_Hello-0x123')

# ## test_update_state

new_state = [{'exchange_name': 'bancor_v2', 'address': '0xabc', 'tkn0_key': 'TKN-0xabc', 'tkn1_key': 'TKN-0xdef', 'pair_name': 'Pair-0xghi', 'liquidity': 10}]
qi.update_state(new_state)

# ## test_get_token

# +
new_state = [{'exchange_name': 'bancor_v2', 'address': '0xabc', 'descr': 'TKN-0x123/TKN-0xdef', 'tkn0_key': 'TKN-0x123', 'tkn1_key': 'TKN-0xdef', 'pair_name': 'Pair-0xghi', 'liquidity': 10}]
qi.update_state(new_state)
token = qi.get_token('TKN-0x123')

assert isinstance(token, Token)
# -

# ## test_get_pool

new_state = [{'last_updated_block': 17614344, 'address': '0xC537e898CD774e2dCBa3B14Ea6f34C93d5eA45e1', 'exchange_name': 'carbon_v1', 'tkn0_address': '0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE', 'tkn1_address': '0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48', 'tkn0_symbol': 'ETH', 'tkn1_symbol': 'USDC', 'tkn0_decimals': 18, 'tkn1_decimals': 6, 'cid': 1701411834604692317316873037158841057365, 'tkn0_key': 'ETH-EEeE', 'tkn1_key': 'USDC-eB48', 'pair_name': 'ETH-EEeE/USDC-eB48', 'fee_float': 0.002, 'fee': '0.002', 'descr': 'carbon_v1 ETH-EEeE/USDC-eB48 0.002', 'y_0': 9882507039899549, 'y_1': 0, 'z_0': 9882507039899549, 'z_1': 17936137, 'A_0': 0, 'A_1': 99105201, 'B_0': 0, 'B_1': 11941971885}]
qi.update_state(new_state)
pool = qi.get_pool(cid=1701411834604692317316873037158841057365)


