# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:light
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.14.7
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# +
import json

from fastlane_bot import Bot
from fastlane_bot.tools.cpc import ConstantProductCurve as CPC
from fastlane_bot.events.exchanges import UniswapV2, UniswapV3, SushiswapV2, CarbonV1, BancorV3
from fastlane_bot.data.abi import UNISWAP_V2_POOL_ABI, UNISWAP_V3_POOL_ABI, SUSHISWAP_POOLS_ABI, BANCOR_V3_POOL_COLLECTION_ABI, \
    CARBON_CONTROLLER_ABI
from unittest.mock import Mock
import pytest

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
# -

with open('fastlane_bot/data/event_test_data.json', 'r') as f:
    setup_data = json.load(f)

mocked_contract = Mock()
mocked_contract.functions.token0.return_value.call.return_value = 'token0'
mocked_contract.functions.token1.return_value.call.return_value = 'token1'
mocked_contract.functions.fee.return_value.call.return_value = 3000
mocked_contract.caller.tradingFeePPM.return_value = 2000

# ## test_uniswap_v2_exchange

uniswap_v2_exchange = UniswapV2()
assert (uniswap_v2_exchange.get_abi() == UNISWAP_V2_POOL_ABI)
assert (uniswap_v2_exchange.get_fee('', mocked_contract) == ('0.003', 0.003))
assert (uniswap_v2_exchange.get_tkn0('', mocked_contract, {}) == mocked_contract.functions.token0().call())

# ## test_uniswap_v3_exchange

uniswap_v3_exchange = UniswapV3()
assert (uniswap_v3_exchange.get_abi() == UNISWAP_V3_POOL_ABI)
assert (uniswap_v3_exchange.get_fee('', mocked_contract) == (mocked_contract.functions.fee().call(), (float(mocked_contract.functions.fee().call()) / 1000000.0)))
assert (uniswap_v3_exchange.get_tkn0('', mocked_contract, {}) == mocked_contract.functions.token0().call())

# ## test_sushiswap_v2_exchange

sushiswap_v2_exchange = SushiswapV2()
assert (sushiswap_v2_exchange.get_abi() == SUSHISWAP_POOLS_ABI)
assert (sushiswap_v2_exchange.get_fee('', mocked_contract) == ('0.003', 0.003))
assert (sushiswap_v2_exchange.get_tkn0('', mocked_contract, {}) == mocked_contract.functions.token0().call())

# ## test_bancor_v3_exchange

bancor_v3_exchange = BancorV3()
assert (bancor_v3_exchange.get_abi() == BANCOR_V3_POOL_COLLECTION_ABI)
assert (bancor_v3_exchange.get_fee('', mocked_contract) == ('0.000', 0.0))
assert (bancor_v3_exchange.get_tkn0('', mocked_contract, setup_data['bancor_v3_event']) == bancor_v3_exchange.BNT_ADDRESS)

# ## test_carbon_v1_exchange_update

# +
from fastlane_bot.data.abi import CARBON_CONTROLLER_ABI_WITH_FEES

carbon_v1_exchange = CarbonV1()

assert (carbon_v1_exchange.get_abi() == CARBON_CONTROLLER_ABI_WITH_FEES)
assert (carbon_v1_exchange.get_fee('', mocked_contract) == ('2000', 0.002))
assert (carbon_v1_exchange.get_tkn0('', mocked_contract, setup_data['carbon_v1_event_update']) == setup_data['carbon_v1_event_update']['args']['token0'])
# -

# ## test_carbon_v1_exchange_create

carbon_v1_exchange = CarbonV1()
assert (carbon_v1_exchange.get_abi() == CARBON_CONTROLLER_ABI)
assert (carbon_v1_exchange.get_fee('', mocked_contract) == ('0.002', 0.002))
assert (carbon_v1_exchange.get_tkn0('', mocked_contract, setup_data['carbon_v1_event_create']) == setup_data['carbon_v1_event_create']['args']['token0'])

# ## test_carbon_v1_exchange_delete

carbon_v1_exchange = CarbonV1()
assert (carbon_v1_exchange.get_abi() == CARBON_CONTROLLER_ABI)
cid = setup_data['carbon_v1_event_delete']['args']['id']
