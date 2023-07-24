# coding=utf-8
"""
This module contains the tests for the exchanges classes
"""
from fastlane_bot import Bot, Config
from fastlane_bot.bot import CarbonBot
from fastlane_bot.tools.cpc import ConstantProductCurve as CPC
from fastlane_bot.events.exchanges import UniswapV2, UniswapV3, SushiswapV2, CarbonV1, BancorV3
from fastlane_bot.events.interface import QueryInterface
from fastlane_bot.helpers.poolandtokens import PoolAndTokens
import pytest

print("{0.__name__} v{0.__VERSION__} ({0.__DATE__})".format(CPC))
print("{0.__name__} v{0.__VERSION__} ({0.__DATE__})".format(Bot))
print("{0.__name__} v{0.__VERSION__} ({0.__DATE__})".format(UniswapV2))
print("{0.__name__} v{0.__VERSION__} ({0.__DATE__})".format(UniswapV3))
print("{0.__name__} v{0.__VERSION__} ({0.__DATE__})".format(SushiswapV2))
print("{0.__name__} v{0.__VERSION__} ({0.__DATE__})".format(CarbonV1))
print("{0.__name__} v{0.__VERSION__} ({0.__DATE__})".format(BancorV3))
from fastlane_bot.testing import *

plt.style.use('seaborn-dark')
plt.rcParams['figure.figsize'] = [12,6]
from fastlane_bot import __VERSION__
require("3.0", __VERSION__)

# Setup

@pytest.fixture(scope="module")
def setup_bot():
    C = Config.new(config=Config.CONFIG_MAINNET)
    assert C.NETWORK == C.NETWORK_MAINNET
    assert C.PROVIDER == C.PROVIDER_ALCHEMY
    setup_bot = CarbonBot(ConfigObj=C)
    pools = [PoolAndTokens(ConfigObj=C, id=87, cid=12590447576074723148144860474975423823949, last_updated=None, last_updated_block=17632852, descr='carbon_v1 BAM-4AaB/ETH-EEeE 0.002', pair_name='BAM-4AaB/ETH-EEeE', exchange_name='carbon_v1', fee='0.002', fee_float=0.002, tkn0_balance=None, tkn1_balance=None, z_0=0, y_0=0, A_0=0, B_0=5232231541229414, z_1=0, y_1=0, A_1=46278427, B_1=1688849860, sqrt_price_q96=None, tick=None, tick_spacing=None, liquidity=None, address='0xC537e898CD774e2dCBa3B14Ea6f34C93d5eA45e1', anchor=None, tkn0='BAM', tkn1='ETH', tkn0_address='0x9DB0FB0Aebe6A925B7838D16e3993A3976A64AaB', tkn0_decimals=18, tkn1_address='0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE', tkn1_decimals=18, tkn0_key='BAM-4AaB', tkn1_key='ETH-EEeE'), PoolAndTokens(ConfigObj=C, id=88, cid=12930729942995661611608235082407192035408, last_updated=None, last_updated_block=17632852, descr='carbon_v1 stETH-fE84/WETH-6Cc2 0.002', pair_name='stETH-fE84/WETH-6Cc2', exchange_name='carbon_v1', fee='0.002', fee_float=0.002, tkn0_balance=None, tkn1_balance=None, z_0=0, y_0=0, A_0=11537531850305, B_0=267164224749167, z_1=1000000000000000000, y_1=1000000000000000000, A_1=4298139552137, B_1=274347871120865, sqrt_price_q96=None, tick=None, tick_spacing=None, liquidity=None, address='0xC537e898CD774e2dCBa3B14Ea6f34C93d5eA45e1', anchor=None, tkn0='stETH', tkn1='WETH', tkn0_address='0xae7ab96520DE3A18E5e111B5EaAb095312D7fE84', tkn0_decimals=18, tkn1_address='0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2', tkn1_decimals=18, tkn0_key='stETH-fE84', tkn1_key='WETH-6Cc2'), PoolAndTokens(ConfigObj=C, id=46, cid='0xfc4a2b96bc1cbe2515f7c0bb784c80757a75fd8851a2ff4ecbad69cb1869ddfa', last_updated=10, last_updated_block=17632857, descr='bancor_v3 BNT-FF1C/BAT-87EF 0.000', pair_name='BNT-FF1C/BAT-87EF', exchange_name='bancor_v3', fee='0.000', fee_float=0.0, tkn0_balance=517690761518839476171134, tkn1_balance=1017685474801793344376721, z_0=0, y_0=0, A_0=0, B_0=0, z_1=0, y_1=0, A_1=0, B_1=0, sqrt_price_q96=10, tick=10, tick_spacing=0, liquidity=10, address='0x3506424F91fD33084466F402d5D97f05F8e3b4AF', anchor=10, tkn0='BNT', tkn1='BAT', tkn0_address='0x1F573D6Fb3F13d689FF844B4cE37794d79a7FF1C', tkn0_decimals=18, tkn1_address='0x0D8775F648430679A709E98d2b0Cb6250d2887EF', tkn1_decimals=18, tkn0_key='BNT-FF1C', tkn1_key='BAT-87EF'), PoolAndTokens(ConfigObj=C, id=47, cid='0x1cff7b0388c4532d7def9430fd2685224af19257fbbe12b99d4362f059e7dbd7', last_updated=10, last_updated_block=17632857, descr='bancor_v3 BNT-FF1C/BBS-B430 0.000', pair_name='BNT-FF1C/BBS-B430', exchange_name='bancor_v3', fee='0.000', fee_float=0.0, tkn0_balance=32805970640508809330829, tkn1_balance=1044245786489813870187767, z_0=0, y_0=0, A_0=0, B_0=0, z_1=0, y_1=0, A_1=0, B_1=0, sqrt_price_q96=10, tick=10, tick_spacing=0, liquidity=10, address='0xc12d099be31567add4e4e4d0D45691C3F58f5663', anchor=10, tkn0='BNT', tkn1='BBS', tkn0_address='0x1F573D6Fb3F13d689FF844B4cE37794d79a7FF1C', tkn0_decimals=18, tkn1_address='0xFe459828c90c0BA4bC8b42F5C5D44F316700B430', tkn1_decimals=18, tkn0_key='BNT-FF1C', tkn1_key='BBS-B430'), PoolAndTokens(ConfigObj=C, id=0, cid='0x7c746d3518854384f7a73a6d2da821454319d305a2af4b7015bbf8734a394e49', last_updated=None, last_updated_block=17632854, descr='uniswap_v3 WETH-6Cc2/USDT-1ec7 500', pair_name='WETH-6Cc2/USDT-1ec7', exchange_name='uniswap_v3', fee=500, fee_float=0.0005, tkn0_balance=None, tkn1_balance=None, z_0=0, y_0=0, A_0=0, B_0=0, z_1=0, y_1=0, A_1=0, B_1=0, sqrt_price_q96=3471749971564948777178138, tick=-200719, tick_spacing=10, liquidity=9272761710152634655, address='0x11b815efB8f581194ae79006d24E0d814B7697F6', anchor=None, tkn0='WETH', tkn1='USDT', tkn0_address='0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2', tkn0_decimals=18, tkn1_address='0xdAC17F958D2ee523a2206206994597C13D831ec7', tkn1_decimals=6, tkn0_key='WETH-6Cc2', tkn1_key='USDT-1ec7'), PoolAndTokens(ConfigObj=C, id=1, cid='0x71fa9967e86d546c3103642dd0876f28a32d4665a1a487d18083421cfd3eff02', last_updated=None, last_updated_block=17632853, descr='uniswap_v3 LDO-1B32/WETH-6Cc2 3000', pair_name='LDO-1B32/WETH-6Cc2', exchange_name='uniswap_v3', fee=3000, fee_float=0.003, tkn0_balance=None, tkn1_balance=None, z_0=0, y_0=0, A_0=0, B_0=0, z_1=0, y_1=0, A_1=0, B_1=0, sqrt_price_q96=2621090548713608947690718187, tick=-68179, tick_spacing=60, liquidity=404595565356008216313141, address='0xa3f558aebAecAf0e11cA4b2199cC5Ed341edfd74', anchor=None, tkn0='LDO', tkn1='WETH', tkn0_address='0x5A98FcBEA516Cf06857215779Fd812CA3beF1B32', tkn0_decimals=18, tkn1_address='0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2', tkn1_decimals=18, tkn0_key='LDO-1B32', tkn1_key='WETH-6Cc2')]
    state = [pool.__dict__ for pool in pools]
    exchanges = list({ex['exchange_name'] for ex in state})
    mock_qi = QueryInterface(state=state,
                             ConfigObj = C,
                             exchanges=exchanges,
    )
    setup_bot.db = mock_qi
    return setup_bot

# Test bot
@pytest.mark.unittest
def test_bot_and_query_interface(setup_bot):
    assert str(type(setup_bot.db)) == "<class 'fastlane_bot.events.interface.QueryInterface'>"
    pools = setup_bot.db.get_pools()
    assert len(pools) > 0
    assert isinstance(pools, list)
    assert all(
        str(type(pool)).startswith("<class 'fastlane_bot.") for pool in pools
    )
    assert setup_bot.db.get_pools()[0].fee_float is not None, "Incorrect pools.csv file see MockPoolManager data"


@pytest.mark.unittest
def test_setup_curves():
    cc1 = CPC.from_carbon(pair="WETH-6Cc2/USDC-eB48", tkny="WETH-6Cc2", yint=10, y=10, pa=1/2000, pb=1/2010,
                          cid="1701411834604692317316873037158841057285-1", params={"exchange":'carbon_v1'})
    assert iseq(1/2000, cc1.p, cc1.p_max)
    assert iseq(1/2010, cc1.p_min)
    assert cc1.p_convention() == 'WETH per USDC'
    assert cc1.p_min < cc1.p_max
