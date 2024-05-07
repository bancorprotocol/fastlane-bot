# ------------------------------------------------------------
# Auto generated test file `test_062_TestRouteHandler.py`
# ------------------------------------------------------------
# source file   = NBTest_062_TestRouteHandler.py
# test id       = 062
# test comment  = TestRouteHandler
# ------------------------------------------------------------



"""
This module contains the tests for the exchanges classes
"""
from unittest.mock import Mock

from arb_optimizer import ConstantProductCurve as CPC

from fastlane_bot import Bot, Config
from fastlane_bot.bot import CarbonBot
from fastlane_bot.events.exchanges import UniswapV2, UniswapV3,  CarbonV1, BancorV3
from fastlane_bot.events.interface import QueryInterface
from fastlane_bot.helpers import TradeInstruction, TxRouteHandler
from fastlane_bot.events.interface import QueryInterface
from fastlane_bot.testing import *
from fastlane_bot.config.network import *
import json
from typing import Dict
print("{0.__name__} v{0.__VERSION__} ({0.__DATE__})".format(CPC))
print("{0.__name__} v{0.__VERSION__} ({0.__DATE__})".format(Bot))
print("{0.__name__} v{0.__VERSION__} ({0.__DATE__})".format(UniswapV2))
print("{0.__name__} v{0.__VERSION__} ({0.__DATE__})".format(UniswapV3))
print("{0.__name__} v{0.__VERSION__} ({0.__DATE__})".format(CarbonV1))
print("{0.__name__} v{0.__VERSION__} ({0.__DATE__})".format(BancorV3))
from fastlane_bot.testing import *

plt.rcParams['figure.figsize'] = [12,6]
from fastlane_bot import __VERSION__
require("3.0", __VERSION__)

cfg = Config.new(config=Config.CONFIG_MAINNET, blockchain="ethereum")
cfg.network.SOLIDLY_V2_FORKS = ["solidly_v2"]
setup_bot = CarbonBot(ConfigObj=cfg)
pools = None
with open('fastlane_bot/tests/_data/latest_pool_data_testing.json') as f:
    pools = json.load(f)
pools = [pool for pool in pools]
pools[0]
static_pools = pools
state = pools
exchanges = list({ex['exchange_name'] for ex in state})
db = QueryInterface(state=state, ConfigObj=cfg, exchanges=exchanges)





# ------------------------------------------------------------
# Test      062
# File      test_062_TestRouteHandler.py
# Segment   Test_Solve_Trade_Output
# ------------------------------------------------------------
def test_test_solve_trade_output():
# ------------------------------------------------------------
    
    # +
    
    trade_instruction_0 = TradeInstruction(
        cid='0xaf541ca0647c91d8e84500ed7bc4ab47d259a8f62c088731b73999d976155839',
        tknin='0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2',
        amtin=5000,
        tknout='0x514910771AF9Ca656af840dff83E8264EcF986CA',
        amtout=1,
        ConfigObj=cfg,
        db = db,
        tknin_dec_override =  18,
        tknout_dec_override = 18,
        tknin_addr_override = '0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2',
        tknout_addr_override = '0x514910771AF9Ca656af840dff83E8264EcF986CA',
        exchange_override = 'solidly_v2'
    )
    trade_instruction_1 = TradeInstruction(
        cid='0xaf541ca0647c91d8e84500ed7bc4ab47d259a8f62c088731b73999d976155839',
        tknin='0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2',
        amtin=5000,
        tknout='0x514910771AF9Ca656af840dff83E8264EcF986CA',
        amtout=1,
        ConfigObj=cfg,
        db = db,
        tknin_dec_override =  18,
        tknout_dec_override = 18,
        tknin_addr_override = '0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2',
        tknout_addr_override = '0x514910771AF9Ca656af840dff83E8264EcF986CA',
        exchange_override = 'uniswap_v2'
    )
    
    mock_curve_0 = Mock()
    mock_curve_0.exchange_name = "uniswap_v2"
    mock_curve_0.pair_name = "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2/0x514910771AF9Ca656af840dff83E8264EcF986CA"
    mock_curve_0.tkn0_balance = Decimal("1000")
    mock_curve_0.tkn1_balance = Decimal("500000")
    mock_curve_0.fee = Decimal("0.003")
    mock_curve_0.fee_float = Decimal("0.003")
    
    mock_curve_1 = Mock()
    mock_curve_1.exchange_name = "solidly_v2"
    mock_curve_1.pair_name = "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2/0x514910771AF9Ca656af840dff83E8264EcF986CA"
    mock_curve_1.tkn0_balance = Decimal("1000")
    mock_curve_1.tkn1_balance = Decimal("500000")
    mock_curve_1.fee = Decimal("0.003")
    mock_curve_1.fee_float = Decimal("0.003")
    mock_curve_1.pool_type = "volatile"
    
    
    mock_curve_3 = Mock()
    mock_curve_3.exchange_name = "solidly_v2"
    mock_curve_3.pair_name = "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2/0x514910771AF9Ca656af840dff83E8264EcF986CA"
    mock_curve_3.tkn0_balance = Decimal("1000")
    mock_curve_3.tkn1_balance = Decimal("500000")
    mock_curve_3.fee = Decimal("0.003")
    mock_curve_3.fee_float = Decimal("0.003")
    mock_curve_3.pool_type = "stable"
    
    txroutehandler = TxRouteHandler(trade_instructions=[trade_instruction_0, trade_instruction_1])
    
    # Test that a Solidly V2 Stable pool throws an error since it isn't supported yet
    assert raises(txroutehandler._solve_trade_output, mock_curve_3, trade_instruction_0, Decimal("0.05")).startswith("[routerhandler.py _solve_trade_output] Solidly V2 stable pools are not yet supported"), f"[NBTest 062 TestRouteHandler] Expected _solve_trade_output to raise an error for a Solidly V2 Stable pool"
    assert not raises(txroutehandler._solve_trade_output, mock_curve_1, trade_instruction_0, Decimal("0.05")), f"[NBTest 062 TestRouteHandler] Expected _solve_trade_output to not raise an error for a Solidly V2 Volatile pool"
    
    # Test that Solidly V2 Volatile pool returns the same format as a Uni V2 pool
    solidly_output = txroutehandler._solve_trade_output(curve=mock_curve_0, trade=trade_instruction_0, amount_in=Decimal("0.05"))[0]
    uni_v2_output = txroutehandler._solve_trade_output(curve=mock_curve_0, trade=trade_instruction_1, amount_in=Decimal("0.05"))[0]
    assert type(solidly_output) == Decimal, f"[NBTest 062 TestRouteHandler] Expected type of output for Solidly V2 Volatile pool to be of type Decimal, found {type(solidly_output)}"
    assert solidly_output == uni_v2_output, f"[NBTest 062 TestRouteHandler] Expected output for Solidly V2 Volatile pool to the same as Uni V2 pool, found {solidly_output} vs {uni_v2_output}"
    # -
    

# ------------------------------------------------------------
# Test      062
# File      test_062_TestRouteHandler.py
# Segment   Test_Uniswap_V3_Router_Switch
# ------------------------------------------------------------
def test_test_uniswap_v3_router_switch():
# ------------------------------------------------------------
    
    # +
    cfg = Config.new(config=Config.CONFIG_MAINNET, blockchain="ethereum")
    cfg.network.SOLIDLY_V2_FORKS = ["solidly_v2"]
    cfg.network.NETWORK = "ethereum"
    
    trade_instruction_0 = TradeInstruction(
        cid='0xaf541ca0647c91d8e84500ed7bc4ab47d259a8f62c088731b73999d976155839',
        tknin='0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2',
        amtin=5000,
        tknout='0x514910771AF9Ca656af840dff83E8264EcF986CA',
        amtout=1,
        ConfigObj=cfg,
        db = db,
        tknin_dec_override =  18,
        tknout_dec_override = 18,
        tknin_addr_override = '0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2',
        tknout_addr_override = '0x514910771AF9Ca656af840dff83E8264EcF986CA',
        exchange_override = 'uniswap_v3'
    )
    trade_instruction_1 = TradeInstruction(
        cid='0xaf541ca0647c91d8e84500ed7bc4ab47d259a8f62c088731b73999d976155839',
        tknin='0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2',
        amtin=5000,
        tknout='0x514910771AF9Ca656af840dff83E8264EcF986CA',
        amtout=1,
        ConfigObj=cfg,
        db = db,
        tknin_dec_override =  18,
        tknout_dec_override = 18,
        tknin_addr_override = '0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2',
        tknout_addr_override = '0x514910771AF9Ca656af840dff83E8264EcF986CA',
        exchange_override = 'baseswap_v2'
    )
    
    trade_instruction_2 = TradeInstruction(
        cid='0xaf541ca0647c91d8e84500ed7bc4ab47d259a8f62c088731b73999d976155839',
        tknin='0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2',
        amtin=5000,
        tknout='0x514910771AF9Ca656af840dff83E8264EcF986CA',
        amtout=1,
        ConfigObj=cfg,
        db = db,
        tknin_dec_override =  18,
        tknout_dec_override = 18,
        tknin_addr_override = '0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2',
        tknout_addr_override = '0x514910771AF9Ca656af840dff83E8264EcF986CA',
        exchange_override = 'pancakeswap_v3'
    )
    
    
    txroutehandler = TxRouteHandler(trade_instructions=[trade_instruction_0, trade_instruction_1, trade_instruction_2])
    
    
    custom_data_input = "0x"
    
    
    platform_id_uni_v2 = cfg.network.EXCHANGE_IDS.get(cfg.network.UNISWAP_V2_NAME)
    platform_id_uni_v3 = cfg.network.EXCHANGE_IDS.get(cfg.network.UNISWAP_V3_NAME)
    
    
    custom_data_not_uni_v3_ethereum = txroutehandler._handle_custom_data_extras(platform_id=platform_id_uni_v2, custom_data=custom_data_input, exchange_name="uniswap_v2")
    custom_data_uni_v3_ethereum = txroutehandler._handle_custom_data_extras(platform_id=platform_id_uni_v3, custom_data=custom_data_input, exchange_name="uniswap_v2")
    
    # Non Uni V3 pool custom data field on Ethereum
    assert custom_data_not_uni_v3_ethereum in custom_data_input, f"[NBTest 062 TestRouteHandler] Expected non Uni V3 route custom data field to not be changed, however {custom_data_not_uni_v3_ethereum} not in {custom_data_input}"
    assert type(custom_data_not_uni_v3_ethereum) == type(custom_data_input), f"[NBTest 062 TestRouteHandler] Expected non Uni V3 route custom data field type to equal its original type, however {type(custom_data_not_uni_v3_ethereum)} != {type(custom_data_input)}"
    
    # Uni V3 custom data field on Ethereum
    assert custom_data_uni_v3_ethereum not in custom_data_input, f"[NBTest 062 TestRouteHandler] Expected Uni V3 route custom data field type to be changed, found {(custom_data_uni_v3_ethereum)} vs {custom_data_input}"
    assert type(custom_data_uni_v3_ethereum)  == str, f"[NBTest 062 TestRouteHandler] Expected Uni V3 route custom data field type to equal str, found {type(custom_data_uni_v3_ethereum)}"
    assert custom_data_uni_v3_ethereum in "0x0000000000000000000000000000000000000000000000000000000000000000", f"[NBTest 062 TestRouteHandler] Expected Uni V3 route custom data field type to equal '0x0000000000000000000000000000000000000000000000000000000000000000', found {custom_data_uni_v3_ethereum}"
    
    
    # +
    
    ################### Base #####################
    cfg = Config.new(config=Config.CONFIG_MAINNET, blockchain="coinbase_base")
    
    platform_id_uni_v3 = cfg.network.EXCHANGE_IDS.get(cfg.network.UNISWAP_V3_NAME)
    platform_id_solidly = cfg.network.EXCHANGE_IDS.get(cfg.network.SOLIDLY_V2_NAME)
    platform_id_aerodrome = cfg.network.EXCHANGE_IDS.get(cfg.network.AERODROME_V2_NAME)
    
    
    trade_instruction_3 = TradeInstruction(
        cid='0xaf541ca0647c91d8e84500ed7bc4ab47d259a8f62c088731b73999d976155839',
        tknin='0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2',
        amtin=5000,
        tknout='0x514910771AF9Ca656af840dff83E8264EcF986CA',
        amtout=1,
        ConfigObj=cfg,
        db = db,
        tknin_dec_override =  18,
        tknout_dec_override = 18,
        tknin_addr_override = '0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2',
        tknout_addr_override = '0x514910771AF9Ca656af840dff83E8264EcF986CA',
        exchange_override = 'aerodrome_v2'
    )
    
    trade_instruction_4 = TradeInstruction(
        cid='0xaf541ca0647c91d8e84500ed7bc4ab47d259a8f62c088731b73999d976155839',
        tknin='0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2',
        amtin=5000,
        tknout='0x514910771AF9Ca656af840dff83E8264EcF986CA',
        amtout=1,
        ConfigObj=cfg,
        db = db,
        tknin_dec_override =  18,
        tknout_dec_override = 18,
        tknin_addr_override = '0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2',
        tknout_addr_override = '0x514910771AF9Ca656af840dff83E8264EcF986CA',
        exchange_override = 'velocimeter_v2'
    )
    txroutehandler_base = TxRouteHandler(trade_instructions=[trade_instruction_3, trade_instruction_4])
    
    custom_data_not_uni_v3_base = txroutehandler_base._handle_custom_data_extras(platform_id=platform_id_uni_v2, custom_data=custom_data_input, exchange_name="sushiswap_v2")
    custom_data_uni_v3_base = txroutehandler_base._handle_custom_data_extras(platform_id=platform_id_uni_v3, custom_data=custom_data_input, exchange_name="uniswap_v3")
    
    custom_data_pancake_v3_base = txroutehandler_base._handle_custom_data_extras(platform_id=platform_id_uni_v3, custom_data=custom_data_input, exchange_name="pancakeswap_v3")
    custom_data_aerodrome = txroutehandler_base._handle_custom_data_extras(platform_id=platform_id_aerodrome, custom_data=custom_data_input, exchange_name="aerodrome_v2")
    custom_data_velocimeter = txroutehandler_base._handle_custom_data_extras(platform_id=platform_id_solidly, custom_data=custom_data_input, exchange_name="velocimeter_v2")
    
    
    assert type(platform_id_uni_v3) == int
    assert type(platform_id_solidly) == int
    assert type(platform_id_aerodrome) == int
    
    
    # Non Uni V3 pool custom data field NOT on Ethereum
    assert custom_data_not_uni_v3_base in custom_data_input, f"[NBTest 062 TestRouteHandler] Expected non Uni V3 route custom data field to not be changed, however {custom_data_not_uni_v3_base} not in {custom_data_input}"
    assert type(custom_data_not_uni_v3_ethereum) == type(custom_data_input), f"[NBTest 062 TestRouteHandler] Expected non Uni V3 route custom data field type to equal its original type, however {type(custom_data_not_uni_v3_base)} != {type(custom_data_input)}"
    
    # Uni V3 custom data field NOT on Ethereum
    assert custom_data_uni_v3_base not in custom_data_input, f"[NBTest 062 TestRouteHandler] Expected Uni V3 route custom data field to be changed, found {(custom_data_uni_v3_base)} vs {custom_data_input}"
    assert type(custom_data_uni_v3_base)  == str, f"[NBTest 062 TestRouteHandler] Expected Uni V3 route custom data field type to equal str, found {type(custom_data_uni_v3_base)}"
    assert custom_data_uni_v3_base in "0x0100000000000000000000000000000000000000000000000000000000000000", f"[NBTest 062 TestRouteHandler] Expected Uni V3 route custom data field type to equal '0x0100000000000000000000000000000000000000000000000000000000000000', found {custom_data_uni_v3_base}"
    
    # Pancakeswap V3 on Base - ensure we use the original Uni V3 router
    assert custom_data_pancake_v3_base not in custom_data_input, f"[NBTest 062 TestRouteHandler] Expected Pancakeswap V3 route custom data field type to be changed, found {(custom_data_uni_v3_base)} vs {custom_data_input}"
    assert type(custom_data_pancake_v3_base)  == str, f"[NBTest 062 TestRouteHandler] Expected Pancakeswap V3 route custom data field type to equal str, found {type(custom_data_uni_v3_base)}"
    assert custom_data_pancake_v3_base in "0x0000000000000000000000000000000000000000000000000000000000000000", f"[NBTest 062 TestRouteHandler] Expected Uni Pancakeswap route custom data field type to equal '0x0000000000000000000000000000000000000000000000000000000000000000', found {custom_data_pancake_v3_base}"
    
    # Aerodrome on Base - ensure we make changes nothing
    
    assert custom_data_aerodrome not in custom_data_input, f"[NBTest 062 TestRouteHandler] Expected Aerodrome route custom data field type to be changed, found {(custom_data_aerodrome)} vs {custom_data_input}"
    assert type(custom_data_aerodrome)  == str, f"[NBTest 062 TestRouteHandler] Expected Aerodromeroute custom data field type to equal str, found {type(custom_data_aerodrome)}"
    assert custom_data_aerodrome in "0x000000000000000000000000420dd381b31aef6683db6b902084cb0ffece40da", f"[NBTest 062 TestRouteHandler] Expected Aerodrome route custom data field type to equal '0x000000000000000000000000420dd381b31aef6683db6b902084cb0ffece40da', found {custom_data_aerodrome}"
    
    # Velocimeter on Base - ensure we add the Factory address
    assert custom_data_velocimeter in custom_data_input, f"[NBTest 062 TestRouteHandler] Expected Velocimeter route custom data field type to not be changed, found {(custom_data_velocimeter)} vs {custom_data_input}"
    assert type(custom_data_velocimeter)  == str, f"[NBTest 062 TestRouteHandler] Expected Velocimeter route custom data field type to equal str, found {type(custom_data_velocimeter)}"
    assert custom_data_velocimeter in "0x", f"[NBTest 062 TestRouteHandler] Expected Velocimeterroute custom data field type to equal '0x', found {custom_data_velocimeter}"
    # -
    

# ------------------------------------------------------------
# Test      062
# File      test_062_TestRouteHandler.py
# Segment   Test get_custom_int
# ------------------------------------------------------------
def test_test_get_custom_int():
# ------------------------------------------------------------
    
    # +
    cfg = Config.new(config=Config.CONFIG_MAINNET, blockchain="coinbase_base")
    cfg.network.SOLIDLY_V2_FORKS = ["solidly_v2", "velocimeter_v2"]
    cfg.network.NETWORK = "coinbase_base"
    
    trade_instruction_0 = TradeInstruction(
        cid='0xaf541ca0647c91d8e84500ed7bc4ab47d259a8f62c088731b73999d976155839',
        tknin='0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2',
        amtin=5000,
        tknout='0x514910771AF9Ca656af840dff83E8264EcF986CA',
        amtout=1,
        ConfigObj=cfg,
        db = db,
        tknin_dec_override =  18,
        tknout_dec_override = 18,
        tknin_addr_override = '0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2',
        tknout_addr_override = '0x514910771AF9Ca656af840dff83E8264EcF986CA',
        exchange_override = 'uniswap_v3'
    )
    trade_instruction_5 = TradeInstruction(
        cid='0x94b2e6453bf0532ca7f2b046099e805b60a40b4f89d938f7d9f92c560513103e',
        tknin='0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2',
        amtin=5000,
        tknout='0x514910771AF9Ca656af840dff83E8264EcF986CA',
        amtout=1,
        ConfigObj=cfg,
        db = db,
        tknin_dec_override =  18,
        tknout_dec_override = 18,
        tknin_addr_override = '0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2',
        tknout_addr_override = '0x514910771AF9Ca656af840dff83E8264EcF986CA',
        exchange_override = 'balancer'
    )
    trade_instruction_4 = TradeInstruction(
        cid='0x43aab96c7ac642d2f543e56ea23981a2796496f769898371827a3a3301e0f0ed',
        tknin='0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2',
        amtin=5000,
        tknout='0x514910771AF9Ca656af840dff83E8264EcF986CA',
        amtout=1,
        ConfigObj=cfg,
        db = db,
        tknin_dec_override =  18,
        tknout_dec_override = 18,
        tknin_addr_override = '0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2',
        tknout_addr_override = '0x514910771AF9Ca656af840dff83E8264EcF986CA',
        exchange_override = 'velocimeter_v2'
    )
    trade_instruction_6 = TradeInstruction(
        cid='0x7859232d6c4abd5d093b86f49aeca311a515e3714f0d4fb2a45942a0a8e2b0d2',
        tknin='0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2',
        amtin=5000,
        tknout='0x514910771AF9Ca656af840dff83E8264EcF986CA',
        amtout=1,
        ConfigObj=cfg,
        db = db,
        tknin_dec_override =  18,
        tknout_dec_override = 18,
        tknin_addr_override = '0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2',
        tknout_addr_override = '0x514910771AF9Ca656af840dff83E8264EcF986CA',
        exchange_override = 'velocimeter_v2'
    )
    
    uni_v3_custom_int = trade_instruction_0.custom_int
    solidly_custom_int_volatile = trade_instruction_4.custom_int
    solidly_custom_int_stable = trade_instruction_6.custom_int
    balancer_custom_int = trade_instruction_5.custom_int
    
    
    assert type(uni_v3_custom_int) == int, f"[NBTest 062, testing get_custom_int in tradeinstruction.py, expected type == int, found {type(uni_v3_custom_int)}]"
    assert type(solidly_custom_int_volatile) == int, f"[NBTest 062, testing get_custom_int in tradeinstruction.py, expected type == int, found {type(solidly_custom_int_volatile)}]"
    assert type(solidly_custom_int_stable) == int, f"[NBTest 062, testing get_custom_int in tradeinstruction.py, expected type == int, found {type(solidly_custom_int_stable)}]"
    assert type(balancer_custom_int) == int, f"[NBTest 062, testing get_custom_int in tradeinstruction.py, expected type == int, found {type(balancer_custom_int)}]"
    
    assert uni_v3_custom_int == 10000, f"[NBTest 062, testing get_custom_int in tradeinstruction.py, expected 10000, found {uni_v3_custom_int}]"
    assert solidly_custom_int_volatile == 0, f"[NBTest 062, testing get_custom_int in tradeinstruction.py, expected 0, found {solidly_custom_int_volatile}]"
    assert solidly_custom_int_stable == 1, f"[NBTest 062, testing get_custom_int in tradeinstruction.py, expected 1, found {solidly_custom_int_stable}]"
    assert balancer_custom_int == 70911184602319403714296547319574681768227301686592151818369995176900963599553, f"[NBTest 062, testing get_custom_int in tradeinstruction.py, expected 0x9cc64ee4cb672bc04c54b00a37e1ed75b2cc19dd0002000000000000000004c1, found {balancer_custom_int}]"
    # -
    

# ------------------------------------------------------------
# Test      062
# File      test_062_TestRouteHandler.py
# Segment   Test_native_gas_token_to_wrapped
# ------------------------------------------------------------
def test_test_native_gas_token_to_wrapped():
# ------------------------------------------------------------
    
    # +
    cfg = Config.new(config=Config.CONFIG_MAINNET, blockchain="ethereum")
    trade_instruction_3 = TradeInstruction(
        cid='0xaf541ca0647c91d8e84500ed7bc4ab47d259a8f62c088731b73999d976155839',
        tknin='0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2',
        amtin=5000,
        tknout='0x514910771AF9Ca656af840dff83E8264EcF986CA',
        amtout=1,
        ConfigObj=cfg,
        db = db,
        tknin_dec_override =  18,
        tknout_dec_override = 18,
        tknin_addr_override = '0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2',
        tknout_addr_override = '0x514910771AF9Ca656af840dff83E8264EcF986CA',
        exchange_override = 'velocimeter_v2'
    )
    trade_instruction_4 = TradeInstruction(
        cid='0xaf541ca0647c91d8e84500ed7bc4ab47d259a8f62c088731b73999d976155839',
        tknin='0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2',
        amtin=5000,
        tknout='0x514910771AF9Ca656af840dff83E8264EcF986CA',
        amtout=1,
        ConfigObj=cfg,
        db = db,
        tknin_dec_override =  18,
        tknout_dec_override = 18,
        tknin_addr_override = '0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2',
        tknout_addr_override = '0x514910771AF9Ca656af840dff83E8264EcF986CA',
        exchange_override = 'velocimeter_v2'
    )
    txroutehandler_base = TxRouteHandler(trade_instructions=[trade_instruction_3, trade_instruction_4])
    
    
    native_gas_token = "0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE"
    wrapped_gas_token = "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2"
    input_token_0 = "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913"
    input_token_1 = native_gas_token
    input_token_2 = wrapped_gas_token
    
    
    test_input_0 = txroutehandler_base.native_gas_token_to_wrapped(tkn=input_token_0)
    test_input_1 = txroutehandler_base.native_gas_token_to_wrapped(tkn=input_token_1)
    test_input_2 = txroutehandler_base.native_gas_token_to_wrapped(tkn=input_token_2)
    
    assert test_input_0 == input_token_0, f"Expected input token to not change, went from {input_token_0} to {test_input_0}"
    assert test_input_1 == wrapped_gas_token, f"Expected input token to be converted from native token to wrapped, result = {test_input_1}, expected = {wrapped_gas_token}"
    assert test_input_2 == wrapped_gas_token, f"Expected input token not to change, result = {test_input_2}, expected = {wrapped_gas_token}"
    
    
    # -
    
    