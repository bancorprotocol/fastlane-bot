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
import json

from fastlane_bot import Bot
from fastlane_bot.events.exchanges.balancer import Balancer
from fastlane_bot.tools.cpc import ConstantProductCurve as CPC
from fastlane_bot.events.exchanges import UniswapV2, UniswapV3, CarbonV1, BancorV3, BancorV2, BancorPol
from fastlane_bot.data.abi import UNISWAP_V2_POOL_ABI, UNISWAP_V3_POOL_ABI, SUSHISWAP_POOLS_ABI, \
    BANCOR_V3_POOL_COLLECTION_ABI, \
    CARBON_CONTROLLER_ABI, BANCOR_V2_CONVERTER_ABI, BANCOR_POL_ABI, BALANCER_VAULT_ABI

from unittest.mock import Mock
import nest_asyncio
nest_asyncio.apply()
import pytest
import asyncio
from unittest.mock import AsyncMock


print("{0.__name__} v{0.__VERSION__} ({0.__DATE__})".format(CPC))
print("{0.__name__} v{0.__VERSION__} ({0.__DATE__})".format(Bot))
print("{0.__name__} v{0.__VERSION__} ({0.__DATE__})".format(UniswapV2))
print("{0.__name__} v{0.__VERSION__} ({0.__DATE__})".format(UniswapV3))
print("{0.__name__} v{0.__VERSION__} ({0.__DATE__})".format(CarbonV1))
print("{0.__name__} v{0.__VERSION__} ({0.__DATE__})".format(BancorV3))
print("{0.__name__} v{0.__VERSION__} ({0.__DATE__})".format(BancorV2))
print("{0.__name__} v{0.__VERSION__} ({0.__DATE__})".format(Balancer))


from fastlane_bot.testing import *

#plt.style.use('seaborn-dark')
plt.rcParams['figure.figsize'] = [12,6]
from fastlane_bot import __VERSION__
require("3.0", __VERSION__)
# -

with open('fastlane_bot/data/event_test_data.json', 'r') as f:
    setup_data = json.load(f)

# +

mocked_contract = Mock()

mocked_contract.functions.token0.return_value.call = AsyncMock(return_value='token0')
mocked_contract.functions.token1.return_value.call = AsyncMock(return_value='token1')
mocked_contract.functions._token0.return_value.call = AsyncMock(return_value='token0')
mocked_contract.functions._token1.return_value.call = AsyncMock(return_value='token1')
mocked_contract.functions.conversionFee.return_value.call = AsyncMock(return_value=3000)
mocked_contract.functions.fee.return_value.call = AsyncMock(return_value=3000)
mocked_contract.functions.tradingFeePPM.return_value.call = AsyncMock(return_value=2000)
mocked_contract.functions.getSwapFeePercentage.call = AsyncMock(return_value="10000000000000000" or 0.01)



#mocked_contract.functions.getPoolTokens().call().return_value = 
# -

# ## test_balancer_exchange

balancer_exchange = Balancer()
assert (balancer_exchange.get_abi() == BALANCER_VAULT_ABI)
#assert (balancer_exchange.get_fee('', mocked_contract) == ("10000000000000000", 0.01))
#assert (balancer_exchange.get_tokens('', mocked_contract, {}) == mocked_contract.functions.token0().call())

# ## test_uniswap_v2_exchange

# +


uniswap_v2_exchange = UniswapV2(fee="0.003", router_address="bobs_router")

@pytest.mark.asyncio
async def test_uniswap_v2_exchange():
    assert (uniswap_v2_exchange.get_abi() == UNISWAP_V2_POOL_ABI)
    assert (await uniswap_v2_exchange.get_fee('', mocked_contract) == ('0.003', 0.003)), f"{await uniswap_v2_exchange.get_fee('', mocked_contract)}"
    assert (await uniswap_v2_exchange.get_tkn0('', mocked_contract, None) == await mocked_contract.functions.token0().call())
    assert (uniswap_v2_exchange.router_address == "bobs_router")

# Run the test in an event loop
asyncio.run(test_uniswap_v2_exchange())
# -

# ## test_uniswap_v3_exchange

# +
uniswap_v3_exchange = UniswapV3(router_address="bobs_router")

@pytest.mark.asyncio
async def test_uniswap_v3_exchange():
    assert (uniswap_v3_exchange.get_abi() == UNISWAP_V3_POOL_ABI)
    assert (await uniswap_v3_exchange.get_fee('', mocked_contract) == (await mocked_contract.functions.fee().call(), (float(await mocked_contract.functions.fee().call()) / 1000000.0)))
    assert (await uniswap_v3_exchange.get_tkn0('', mocked_contract, {}) == await mocked_contract.functions.token0().call())
    assert (uniswap_v3_exchange.router_address == "bobs_router")
# Run the test in an event loop
asyncio.run(test_uniswap_v3_exchange())
# -

# ## test_bancor_v3_exchange

# +
bancor_v3_exchange = BancorV3()

assert (bancor_v3_exchange.get_abi() == BANCOR_V3_POOL_COLLECTION_ABI)
assert (bancor_v3_exchange.get_fee('', mocked_contract) == ('0.000', 0.0))
assert (bancor_v3_exchange.get_tkn0('', mocked_contract, setup_data['bancor_v3_event']) == bancor_v3_exchange.BNT_ADDRESS)

# -

# ## test_bancor_v2_exchange

# +
bancor_v2_exchange = BancorV2()

@pytest.mark.asyncio
async def test_bancor_v2_exchange():
    assert (bancor_v2_exchange.get_abi() == BANCOR_V2_CONVERTER_ABI)
    assert (await bancor_v2_exchange.get_fee('', mocked_contract) == (3000, 0.003))
    assert (await bancor_v2_exchange.get_tkn0('', mocked_contract, setup_data['bancor_v2_event']) == '0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE')
    
# Run the test in an event loop
asyncio.run(test_bancor_v2_exchange())
# -

# ## test_carbon_v1_exchange_update

# +
carbon_v1_exchange = CarbonV1()

@pytest.mark.asyncio
async def test_carbon_v1_exchange_update():
    assert (carbon_v1_exchange.get_abi() == CARBON_CONTROLLER_ABI)
    assert (await carbon_v1_exchange.get_fee('', mocked_contract) == ('2000', 0.002))
    assert (await carbon_v1_exchange.get_tkn0('', mocked_contract, setup_data['carbon_v1_event_update']) == setup_data['carbon_v1_event_update']['args']['token0'])
    
# Run the test in an event loop
asyncio.run(test_carbon_v1_exchange_update())
# -

# ## test_carbon_v1_exchange_create

# +
carbon_v1_exchange = CarbonV1()

@pytest.mark.asyncio
async def test_carbon_v1_exchange_create():
    assert (carbon_v1_exchange.get_abi() == CARBON_CONTROLLER_ABI)
    assert (await carbon_v1_exchange.get_fee('', mocked_contract) == ('2000', 0.002))
    assert (await carbon_v1_exchange.get_tkn0('', mocked_contract, setup_data['carbon_v1_event_create']) == setup_data['carbon_v1_event_create']['args']['token0'])
    
# Run the test in an event loop
asyncio.run(test_carbon_v1_exchange_create())
# -

# ## test_carbon_v1_exchange_delete

carbon_v1_exchange = CarbonV1()
assert (carbon_v1_exchange.get_abi() == CARBON_CONTROLLER_ABI)
cid = setup_data['carbon_v1_event_delete']['args']['id']

# test_bancor_pol_exchange

# +
bancor_pol_exchange = BancorPol()

@pytest.mark.asyncio
async def test_bancor_pol_exchange():
    assert (bancor_pol_exchange.get_abi() == BANCOR_POL_ABI)
    assert (await bancor_pol_exchange.get_fee('', mocked_contract) == ('0.000', 0.0))
    assert (await bancor_pol_exchange.get_tkn0('', mocked_contract, setup_data['bancor_pol_trading_enabled_event']) == "0x86772b1409b61c639EaAc9Ba0AcfBb6E238e5F83")
    
# Run the test in an event loop
asyncio.run(test_bancor_pol_exchange())
