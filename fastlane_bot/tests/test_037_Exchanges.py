# ------------------------------------------------------------
# Auto generated test file `test_037_Exchanges.py`
# ------------------------------------------------------------
# source file   = NBTest_037_Exchanges.py
# test id       = 037
# test comment  = Exchanges
# ------------------------------------------------------------



import json

from fastlane_bot import Bot
from fastlane_bot.events.interfaces.event import Event
from fastlane_bot.events.exchanges.balancer import Balancer
from fastlane_bot.tools.cpc import ConstantProductCurve as CPC
from fastlane_bot.events.exchanges import UniswapV2, UniswapV3, CarbonV1, BancorV3, BancorV2, BancorPol, SolidlyV2
from fastlane_bot.data.abi import UNISWAP_V2_POOL_ABI, UNISWAP_V3_POOL_ABI, BANCOR_V3_POOL_COLLECTION_ABI, \
    CARBON_CONTROLLER_ABI, BANCOR_V2_CONVERTER_ABI, BANCOR_POL_ABI, BALANCER_VAULT_ABI, PANCAKESWAP_V3_POOL_ABI, SOLIDLY_V2_POOL_ABI

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
print("{0.__name__} v{0.__VERSION__} ({0.__DATE__})".format(SolidlyV2))

from fastlane_bot.testing import *

#plt.style.use('seaborn-dark')
plt.rcParams['figure.figsize'] = [12,6]
from fastlane_bot import __VERSION__
require("3.0", __VERSION__)

with open('fastlane_bot/tests/_data/event_test_data.json', 'r') as f:
    setup_data = json.load(f)


mocked_contract = Mock()

mocked_contract.caller.token0 = AsyncMock(return_value='token0')
mocked_contract.caller.token1 = AsyncMock(return_value='token1')
mocked_contract.caller._token0 = AsyncMock(return_value='token0')
mocked_contract.caller._token1 = AsyncMock(return_value='token1')
mocked_contract.caller.conversionFee = AsyncMock(return_value=3000)
mocked_contract.caller.fee = AsyncMock(return_value=3000)
mocked_contract.caller.tradingFeePPM = AsyncMock(return_value=2000)
mocked_contract.caller.getSwapFeePercentage = AsyncMock(return_value="10000000000000000" or 0.01)


# ------------------------------------------------------------
# Test      037
# File      test_037_Exchanges.py
# Segment   test_balancer_exchange
# ------------------------------------------------------------
def test_test_balancer_exchange():
# ------------------------------------------------------------
    
    balancer_exchange = Balancer()

    @pytest.mark.asyncio
    async def test_balancer_exchange():
        assert (balancer_exchange.get_abi() == BALANCER_VAULT_ABI)
        #assert (await balancer_exchange.get_fee('', mocked_contract) == ("10000000000000000", 0.01))
        #assert (await balancer_exchange.get_tokens('', mocked_contract, {}) == mocked_contract.caller.token0())
    # Run the test in an event loop
    asyncio.run(test_balancer_exchange())
    

# ------------------------------------------------------------
# Test      037
# File      test_037_Exchanges.py
# Segment   test_solidly_v2_exchange
# ------------------------------------------------------------
def test_test_solidly_v2_exchange():
# ------------------------------------------------------------
    
    # +
    
    
    solidly_v2_exchange = SolidlyV2(exchange_name="velocimeter_v2", fee="0.003", router_address="jeffs_router")
    
    @pytest.mark.asyncio
    async def test_solidly_v2_exchange():
        assert (solidly_v2_exchange.get_abi() == SOLIDLY_V2_POOL_ABI)
        #assert (await solidly_v2_exchange.get_fee('', mocked_contract) == ('0.003', 0.003)), f"{await solidly_v2_exchange.get_fee('', mocked_contract)}"
        assert (await solidly_v2_exchange.get_tkn0('', mocked_contract, None) == await mocked_contract.caller.token0())
        assert (solidly_v2_exchange.router_address == "jeffs_router")
    
    # Run the test in an event loop
    asyncio.run(test_solidly_v2_exchange())
    # -
    

# ------------------------------------------------------------
# Test      037
# File      test_037_Exchanges.py
# Segment   test_solidly_v2_exchange_fork
# ------------------------------------------------------------
def test_test_solidly_v2_exchange_fork():
# ------------------------------------------------------------
    
    # +
    velocimeter_v2_exchange = SolidlyV2(exchange_name="velocimeter_v2", fee="0.0025", router_address="jjs_router")
    
    @pytest.mark.asyncio
    async def test_uniswap_v2_exchange():
        assert (velocimeter_v2_exchange.exchange_name in "velocimeter_v2"), f"Wrong exchange name. Expected velocimeter_v2, got {velocimeter_v2_exchange.exchange_name}"
        assert (velocimeter_v2_exchange.base_exchange_name in "solidly_v2"), f"Wrong base exchange name. Expected solidly_v2, got {velocimeter_v2_exchange.base_exchange_name}"    
        assert (velocimeter_v2_exchange.get_abi() == SOLIDLY_V2_POOL_ABI)
        #assert (await velocimeter_v2_exchange.get_fee('', mocked_contract) == ('0.0025', 0.0025)), f"{await velocimeter_v2_exchange.get_fee('', mocked_contract)}"
        assert (await velocimeter_v2_exchange.get_tkn0('', mocked_contract, None) == await mocked_contract.caller.token0())
        assert (velocimeter_v2_exchange.router_address == "jjs_router")
    
    # Run the test in an event loop
    asyncio.run(test_uniswap_v2_exchange())
    # -
    

# ------------------------------------------------------------
# Test      037
# File      test_037_Exchanges.py
# Segment   test_uniswap_v2_exchange
# ------------------------------------------------------------
def test_test_uniswap_v2_exchange():
# ------------------------------------------------------------
    
    # +
    
    
    uniswap_v2_exchange = UniswapV2(fee="0.003", router_address="bobs_router")
    
    @pytest.mark.asyncio
    async def test_uniswap_v2_exchange():
        assert (uniswap_v2_exchange.get_abi() == UNISWAP_V2_POOL_ABI)
        assert (await uniswap_v2_exchange.get_fee('', mocked_contract) == ('0.003', 0.003)), f"{await uniswap_v2_exchange.get_fee('', mocked_contract)}"
        assert (await uniswap_v2_exchange.get_tkn0('', mocked_contract, None) == await mocked_contract.caller.token0())
        assert (uniswap_v2_exchange.router_address == "bobs_router")
    
    # Run the test in an event loop
    asyncio.run(test_uniswap_v2_exchange())
    # -
    

# ------------------------------------------------------------
# Test      037
# File      test_037_Exchanges.py
# Segment   test_uniswap_v2_exchange_fork
# ------------------------------------------------------------
def test_test_uniswap_v2_exchange_fork():
# ------------------------------------------------------------
    
    # +
    
    
    pancake_v2_exchange = UniswapV2(exchange_name="pancakeswap_v2",fee="0.0025", router_address="freds_router")
    
    @pytest.mark.asyncio
    async def test_uniswap_v2_exchange_fork():
        assert (pancake_v2_exchange.exchange_name in "pancakeswap_v2"), f"Wrong exchange name. Expected pancakeswap_v2, got {pancake_v2_exchange.exchange_name}"
        assert (pancake_v2_exchange.base_exchange_name in "uniswap_v2"), f"Wrong base exchange name. Expected uniswap_v2, got {pancake_v2_exchange.base_exchange_name}"    
        assert (pancake_v2_exchange.get_abi() == UNISWAP_V2_POOL_ABI)
        assert (await pancake_v2_exchange.get_fee('', mocked_contract) == ('0.0025', 0.0025)), f"{await uniswap_v2_exchange.get_fee('', mocked_contract)}"
        assert (await pancake_v2_exchange.get_tkn0('', mocked_contract, None) == await mocked_contract.caller.token0())
        assert (pancake_v2_exchange.router_address == "freds_router")
    
    # Run the test in an event loop
    asyncio.run(test_uniswap_v2_exchange_fork())
    # -
    

# ------------------------------------------------------------
# Test      037
# File      test_037_Exchanges.py
# Segment   test_uniswap_v3_exchange
# ------------------------------------------------------------
def test_test_uniswap_v3_exchange():
# ------------------------------------------------------------
    
    # +
    uniswap_v3_exchange = UniswapV3(router_address="bobs_router")
    
    @pytest.mark.asyncio
    async def test_uniswap_v3_exchange():
        assert (uniswap_v3_exchange.get_abi() == UNISWAP_V3_POOL_ABI)
        assert (await uniswap_v3_exchange.get_fee('', mocked_contract) == (await mocked_contract.caller.fee(), (float(await mocked_contract.caller.fee()) / 1000000.0)))
        assert (await uniswap_v3_exchange.get_tkn0('', mocked_contract, {}) == await mocked_contract.caller.token0())
        assert (uniswap_v3_exchange.router_address == "bobs_router")
    # Run the test in an event loop
    asyncio.run(test_uniswap_v3_exchange())
    # -
    

# ------------------------------------------------------------
# Test      037
# File      test_037_Exchanges.py
# Segment   test_uniswap_v3_exchange_fork
# ------------------------------------------------------------
def test_test_uniswap_v3_exchange_fork():
# ------------------------------------------------------------
    
    # +
    pancake_v3_exchange = UniswapV3(exchange_name="pancakeswap_v3",router_address="bobs_router")
    
    @pytest.mark.asyncio
    async def test_uniswap_v3_exchange():
        assert (pancake_v3_exchange.exchange_name in "pancakeswap_v3"), f"Wrong exchange name. Expected pancakeswap_v3, got {pancake_v3_exchange.exchange_name}"
        assert (pancake_v3_exchange.base_exchange_name in "uniswap_v3"), f"Wrong base exchange name. Expected uniswap_v3, got {pancake_v3_exchange.base_exchange_name}"    
        assert (pancake_v3_exchange.get_abi() == PANCAKESWAP_V3_POOL_ABI)
        assert (await pancake_v3_exchange.get_fee('', mocked_contract) == (await mocked_contract.caller.fee(), (float(await mocked_contract.caller.fee()) / 1000000.0)))
        assert (await pancake_v3_exchange.get_tkn0('', mocked_contract, {}) == await mocked_contract.caller.token0())
        assert (pancake_v3_exchange.router_address == "bobs_router")
    # Run the test in an event loop
    asyncio.run(test_uniswap_v3_exchange())
    # -
    

# ------------------------------------------------------------
# Test      037
# File      test_037_Exchanges.py
# Segment   test_bancor_v3_exchange
# ------------------------------------------------------------
def test_test_bancor_v3_exchange():
# ------------------------------------------------------------
    
    # +
    bancor_v3_exchange = BancorV3()
    
    @pytest.mark.asyncio
    async def test_bancor_v3_exchange():
        assert (bancor_v3_exchange.get_abi() == BANCOR_V3_POOL_COLLECTION_ABI)
        assert (await bancor_v3_exchange.get_fee('', mocked_contract) == ('0.000', 0.0))
        assert (await bancor_v3_exchange.get_tkn0('', mocked_contract, setup_data['bancor_v3_event']) == bancor_v3_exchange.BNT_ADDRESS)
    # Run the test in an event loop
    asyncio.run(test_bancor_v3_exchange())
    # -
    

# ------------------------------------------------------------
# Test      037
# File      test_037_Exchanges.py
# Segment   test_bancor_v2_exchange
# ------------------------------------------------------------
def test_test_bancor_v2_exchange():
# ------------------------------------------------------------
    
    # +
    bancor_v2_exchange = BancorV2()
    
    @pytest.mark.asyncio
    async def test_bancor_v2_exchange():
        assert (bancor_v2_exchange.get_abi() == BANCOR_V2_CONVERTER_ABI)
        assert (await bancor_v2_exchange.get_fee('', mocked_contract) == (3000, 0.003))
        assert (await bancor_v2_exchange.get_tkn0('', mocked_contract, Event.from_dict(setup_data['bancor_v2_event'])) == '0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE')
        
    # Run the test in an event loop
    asyncio.run(test_bancor_v2_exchange())
    # -
    

# ------------------------------------------------------------
# Test      037
# File      test_037_Exchanges.py
# Segment   test_carbon_v1_exchange_update
# ------------------------------------------------------------
def test_test_carbon_v1_exchange_update():
# ------------------------------------------------------------
    
    # +
    carbon_v1_exchange = CarbonV1()
    
    @pytest.mark.asyncio
    async def test_carbon_v1_exchange_update():
        assert (carbon_v1_exchange.get_abi() == CARBON_CONTROLLER_ABI)
        assert (await carbon_v1_exchange.get_fee('', mocked_contract) == ('2000', 0.002))
        assert (await carbon_v1_exchange.get_tkn0('', mocked_contract, Event.from_dict(setup_data['carbon_v1_event_update'])) == setup_data['carbon_v1_event_update']['args']['token0'])
        
    # Run the test in an event loop
    asyncio.run(test_carbon_v1_exchange_update())
    # -
    

# ------------------------------------------------------------
# Test      037
# File      test_037_Exchanges.py
# Segment   test_carbon_v1_exchange_create
# ------------------------------------------------------------
def test_test_carbon_v1_exchange_create():
# ------------------------------------------------------------
    
    # +
    carbon_v1_exchange = CarbonV1()
    
    @pytest.mark.asyncio
    async def test_carbon_v1_exchange_create():
        assert (carbon_v1_exchange.get_abi() == CARBON_CONTROLLER_ABI)
        assert (await carbon_v1_exchange.get_fee('', mocked_contract) == ('2000', 0.002))
        assert (await carbon_v1_exchange.get_tkn0('', mocked_contract, Event.from_dict(setup_data['carbon_v1_event_create'])) == setup_data['carbon_v1_event_create']['args']['token0'])
        
    # Run the test in an event loop
    asyncio.run(test_carbon_v1_exchange_create())
    # -
    

# ------------------------------------------------------------
# Test      037
# File      test_037_Exchanges.py
# Segment   test_carbon_v1_exchange_delete
# ------------------------------------------------------------
def test_test_carbon_v1_exchange_delete():
# ------------------------------------------------------------
    
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
        assert (await bancor_pol_exchange.get_tkn0('', mocked_contract, Event.from_dict(setup_data['bancor_pol_trading_enabled_event'])) == "0x86772b1409b61c639EaAc9Ba0AcfBb6E238e5F83")
        
    # Run the test in an event loop
    asyncio.run(test_bancor_pol_exchange())