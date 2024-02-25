# -*- coding: utf-8 -*-
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
# coding=utf-8
"""
This module contains the tests for the exchanges classes
"""
from unittest.mock import Mock

from fastlane_bot import Bot, Config
from fastlane_bot.bot import CarbonBot
from fastlane_bot.tools.cpc import ConstantProductCurve as CPC
from fastlane_bot.events.exchanges import UniswapV2, UniswapV3,  CarbonV1, BancorV3
from fastlane_bot.events.interface import QueryInterface
from fastlane_bot.helpers import TradeInstruction, TxRouteHandler, WrapUnwrapProcessor, CarbonTradeSplitter
from fastlane_bot.events.interface import QueryInterface
from fastlane_bot.testing import *
from fastlane_bot.config.network import *

import json
from dataclasses import asdict
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
# -

cfg = Config.new(config=Config.CONFIG_MAINNET, blockchain="ethereum")
cfg.network.SOLIDLY_V2_FORKS = ["solidly_v2"]
setup_bot = CarbonBot(ConfigObj=cfg)
pools = None
with open('fastlane_bot/data/tests/latest_pool_data_testing.json') as f:
    pools = json.load(f)
pools = [pool for pool in pools]
pools[0]
static_pools = pools
state = pools
exchanges = list({ex['exchange_name'] for ex in state})
db = QueryInterface(state=state, ConfigObj=cfg, exchanges=exchanges)


# # Test_Route_Handler_Solve_Trade_Output [NBTest062]

# ## Test_Solve_Trade_Output

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

# ## Test_Uniswap_V3_Router_Switch

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


custom_data_not_uni_v3_ethereum = txroutehandler.handle_custom_data_extras(platform_id=platform_id_uni_v2, custom_data=custom_data_input, exchange_name="uniswap_v2")
custom_data_uni_v3_ethereum = txroutehandler.handle_custom_data_extras(platform_id=platform_id_uni_v3, custom_data=custom_data_input, exchange_name="uniswap_v2")

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

custom_data_not_uni_v3_base = txroutehandler_base.handle_custom_data_extras(platform_id=platform_id_uni_v2, custom_data=custom_data_input, exchange_name="sushiswap_v2")
custom_data_uni_v3_base = txroutehandler_base.handle_custom_data_extras(platform_id=platform_id_uni_v3, custom_data=custom_data_input, exchange_name="uniswap_v3")

custom_data_pancake_v3_base = txroutehandler_base.handle_custom_data_extras(platform_id=platform_id_uni_v3, custom_data=custom_data_input, exchange_name="pancakeswap_v3")
custom_data_aerodrome = txroutehandler_base.handle_custom_data_extras(platform_id=platform_id_aerodrome, custom_data=custom_data_input, exchange_name="aerodrome_v2")
custom_data_velocimeter = txroutehandler_base.handle_custom_data_extras(platform_id=platform_id_solidly, custom_data=custom_data_input, exchange_name="velocimeter_v2")


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

# ## Test get_custom_int

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

# ## Test_native_gas_token_to_wrapped

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



# ## Test Split Carbon Trades

# +
cfg = Config.new(config=Config.CONFIG_MAINNET, blockchain="ethereum")
cfg.network.NETWORK = "ethereum"

raw_tx_1 = {
                    "cid": "67035626283424877302284797664058337657416-0",
                    "tknin": "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2",
                    "amtin": 10,
                    "_amtin_wei": 10000000000000000000,
                    "tknout": "0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599",
                    "amtout": 1,
                    "_amtout_wei": 100000000,
                    }
raw_tx_2 = {
                    "cid": "9187623906865338513511114400657741709505-0",
                    "tknin": "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2",
                    "amtin": 5,
                    "_amtin_wei": 5000000000000000000,
                    "tknout": "0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599",
                    "amtout": 0.5,
                    "_amtout_wei": 50000000,
                    }

raw_tx_list_0 = [raw_tx_1, raw_tx_2]
raw_tx_list_1 = [raw_tx_1, raw_tx_2]
raw_tx_list_2 = [raw_tx_1, raw_tx_1]

raw_tx_str_0 = str(raw_tx_list_0)
raw_tx_str_1 = str(raw_tx_list_1)
raw_tx_str_2 = str(raw_tx_list_2)

trade_instruction_6 = TradeInstruction(
    cid='0x6be8339b6f982a8d4a3c9485b7e8b97c088c6f1049dd4365fe4492fa88713c23',
    tknin='0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599',
    amtin=200000000,
    tknout='0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2',
    amtout=20000000000000000000,
    ConfigObj=cfg,
    db = db,
    tknin_dec_override =  8,
    tknout_dec_override = 18,
    tknin_addr_override = '0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599',
    tknout_addr_override = '0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2',
    exchange_override = 'uniswap_v3',
)

trade_instruction_7 = TradeInstruction(
    cid='67035626283424877302284797664058337657416-0',
    tknin='0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2',
    amtin=20,
    tknout='0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599',
    amtout=2,
    ConfigObj=cfg,
    db = db,
    tknin_dec_override =  18,
    tknout_dec_override = 8,
    tknin_addr_override = '0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2',
    tknout_addr_override = '0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599',
    exchange_override = 'carbon_v1',
    raw_txs=raw_tx_str_2,
)

trade_instruction_8 = TradeInstruction(
    cid='67035626283424877302284797664058337657416-0',
    tknin='0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2',
    amtin=15,
    tknout='0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599',
    amtout=1.5,
    ConfigObj=cfg,
    db = db,
    tknin_dec_override =  18,
    tknout_dec_override = 8,
    tknin_addr_override = '0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2',
    tknout_addr_override = '0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599',
    exchange_override = 'carbon_v1',
    raw_txs=raw_tx_str_0,
)

trade_instruction_9 = TradeInstruction(
    cid='0x6be8339b6f982a8d4a3c9485b7e8b97c088c6f1049dd4365fe4492fa88713c23',
    tknin='0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599',
    amtin=5000,
    tknout='0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2',
    amtout=1,
    ConfigObj=cfg,
    db = db,
    tknin_dec_override =  8,
    tknout_dec_override = 18,
    tknin_addr_override = '0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599',
    tknout_addr_override = '0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2',
    exchange_override = 'uniswap_v3',
)

trade_instruction_10 = TradeInstruction(
    cid='67035626283424877302284797664058337657416-0',
    tknin='0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2',
    amtin=15,
    tknout='0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599',
    amtout=1.5,
    ConfigObj=cfg,
    db = db,
    tknin_dec_override =  18,
    tknout_dec_override = 8,
    tknin_addr_override = '0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2',
    tknout_addr_override = '0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599',
    exchange_override = 'carbon_v1',
    raw_txs=raw_tx_str_1,
)

trade_instructions_0 = [trade_instruction_8, trade_instruction_9]
trade_instructions_1 = [trade_instruction_10, trade_instruction_9]
trade_instructions_2 = [trade_instruction_7, trade_instruction_6]

txroutehandler_ethereum_0 = TxRouteHandler(trade_instructions=trade_instructions_0)
txroutehandler_ethereum_1 = TxRouteHandler(trade_instructions=trade_instructions_1)
txroutehandler_ethereum_2 = TxRouteHandler(trade_instructions=trade_instructions_2)


#print(len(trade_instructions_0))

split_trade_instructions_0_splitter = CarbonTradeSplitter(cfg).split_carbon_trades(trade_instructions_0)
split_trade_instructions_1_splitter = CarbonTradeSplitter(cfg).split_carbon_trades(trade_instructions_1)
split_trade_instructions_2_splitter = CarbonTradeSplitter(cfg).split_carbon_trades(trade_instructions_2)


assert len(trade_instructions_0) == 2

assert len(split_trade_instructions_0_splitter) == 3
assert len(split_trade_instructions_1_splitter) == 3
assert len(split_trade_instructions_2_splitter) == 2


assert split_trade_instructions_0_splitter[0].tknin == "0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE"


# print(len(split_trade_instructions_0))
# print(len(split_trade_instructions_1))


assert split_trade_instructions_0_splitter == split_trade_instructions_1_splitter


for idx, trade in enumerate(split_trade_instructions_2_splitter):
    assert trade_instructions_2[idx].tknin == split_trade_instructions_2_splitter[idx].tknin
    assert trade_instructions_2[idx].tknout == split_trade_instructions_2_splitter[idx].tknout
    assert trade_instructions_2[idx].amtin_wei == split_trade_instructions_2_splitter[idx].amtin_wei
    assert trade_instructions_2[idx].amtout_wei == split_trade_instructions_2_splitter[idx].amtout_wei
    assert trade_instructions_2[idx].raw_txs == split_trade_instructions_2_splitter[idx].raw_txs

# -

# ## Test Add Wrap Unwrap V4

# +
cfg = Config.new(config=Config.CONFIG_MAINNET, blockchain="ethereum")
cfg.network.NETWORK = "ethereum"
flashloan_struct_0=[{'platformId': 7, 'sourceTokens': ['0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2'], 'sourceAmounts': [15000000000000000000]}]
flashloan_struct_1=[{'platformId': 2, 'sourceTokens': ['0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE'], 'sourceAmounts': [15000000000000000000]}]

wrap_unwrap_processor_0, wrap_unwrap_processor_1, wrap_unwrap_processor_2, wrap_unwrap_processor_3 = WrapUnwrapProcessor(cfg=cfg), WrapUnwrapProcessor(cfg=cfg), WrapUnwrapProcessor(cfg=cfg), WrapUnwrapProcessor(cfg=cfg)


raw_tx_0 = {
                    "cid": "67035626283424877302284797664058337657416-0",
                    "tknin": "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2",
                    "amtin": 10,
                    "_amtin_wei": 10000000000000000000,
                    "tknout": "0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599",
                    "amtout": 1,
                    "_amtout_wei": 100000000,
                    }
raw_tx_1 = {
                    "cid": "9187623906865338513511114400657741709505-0",
                    "tknin": "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2",
                    "amtin": 5,
                    "_amtin_wei": 5000000000000000000,
                    "tknout": "0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599",
                    "amtout": 0.5,
                    "_amtout_wei": 50000000,
                    }
raw_tx_2 = {
                    "cid": "67035626283424877302284797664058337657416-0",
                    "tknin": "0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599",
                    "amtin": 1,
                    "_amtin_wei": 100000000,
                    "tknout": "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2",
                    "amtout": 10,
                    "_amtout_wei": 10000000000000000000,
                    }
raw_tx_3 = {
                    "cid": "9187623906865338513511114400657741709505-0",
                    "tknin": "0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599",
                    "amtin": 0.5,
                    "_amtin_wei": 50000000,
                    "tknout": "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2",
                    "amtout": 5,
                    "_amtout_wei": 5000000000000000000,
                    }
raw_tx_list_0 = [raw_tx_0, raw_tx_1]
raw_tx_list_1 = [raw_tx_1, raw_tx_0]
raw_tx_list_2 = [raw_tx_2, raw_tx_3]
raw_tx_list_3 = [raw_tx_3, raw_tx_2]
raw_tx_str_0 = str(raw_tx_list_0)
raw_tx_str_1 = str(raw_tx_list_1)
raw_tx_str_2 = str(raw_tx_list_2)
raw_tx_str_3 = str(raw_tx_list_3)

trade_instruction_8 = TradeInstruction(
    cid='67035626283424877302284797664058337657416-0',
    tknin='0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2',
    amtin=15,
    tknout='0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599',
    amtout=1.5,
    ConfigObj=cfg,
    db = db,
    tknin_dec_override =  18,
    tknout_dec_override = 8,
    tknin_addr_override = '0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2',
    tknout_addr_override = '0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599',
    exchange_override = 'carbon_v1',
    raw_txs=raw_tx_str_0,
)

trade_instruction_9 = TradeInstruction(
    cid='0x6be8339b6f982a8d4a3c9485b7e8b97c088c6f1049dd4365fe4492fa88713c23',
    tknin='0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599',
    amtin=1.5,
    tknout='0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2',
    amtout=15,
    ConfigObj=cfg,
    db = db,
    tknin_dec_override =  8,
    tknout_dec_override = 18,
    tknin_addr_override = '0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599',
    tknout_addr_override = '0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2',
    exchange_override = 'uniswap_v3',
)

trade_instruction_10 = TradeInstruction(
    cid='67035626283424877302284797664058337657416-0',
    tknin='0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2',
    amtin=15,
    tknout='0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599',
    amtout=1.5,
    ConfigObj=cfg,
    db = db,
    tknin_dec_override =  18,
    tknout_dec_override = 8,
    tknin_addr_override = '0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2',
    tknout_addr_override = '0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599',
    exchange_override = 'carbon_v1',
    raw_txs=raw_tx_str_1,
)


trade_instruction_11 = TradeInstruction(
    cid='67035626283424877302284797664058337657416-0',
    tknin='0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599',
    amtin=1.5,
    tknout='0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2',
    amtout=15,
    ConfigObj=cfg,
    db = db,
    tknin_dec_override =  8,
    tknout_dec_override = 18,
    tknin_addr_override = '0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599',
    tknout_addr_override = '0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2',
    exchange_override = 'carbon_v1',
    raw_txs=raw_tx_str_2,
)

trade_instruction_12 = TradeInstruction(
    cid='0x6be8339b6f982a8d4a3c9485b7e8b97c088c6f1049dd4365fe4492fa88713c23',
    tknin='0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2',
    amtin=15,
    tknout='0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599',
    amtout=1.5,
    ConfigObj=cfg,
    db = db,
    tknin_dec_override =  18,
    tknout_dec_override = 8,
    tknin_addr_override = '0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2',
    tknout_addr_override = '0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599',
    exchange_override = 'uniswap_v3',
)

trade_instruction_13 = TradeInstruction(
    cid='67035626283424877302284797664058337657416-0',
    tknin='0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599',
    amtin=1.5,
    tknout='0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2',
    amtout=15,
    ConfigObj=cfg,
    db = db,
    tknin_dec_override = 8,
    tknout_dec_override = 18,
    tknin_addr_override = '0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599',
    tknout_addr_override = '0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2',
    exchange_override = 'carbon_v1',
    raw_txs=raw_tx_str_3,
)


trade_instructions_0 = [trade_instruction_8, trade_instruction_9]
trade_instructions_1 = [trade_instruction_10, trade_instruction_9]
trade_instructions_2 = [trade_instruction_12, trade_instruction_11]
trade_instructions_3 = [trade_instruction_12, trade_instruction_13]

txroutehandler_ethereum_0 = TxRouteHandler(trade_instructions=trade_instructions_0)
txroutehandler_ethereum_1 = TxRouteHandler(trade_instructions=trade_instructions_1)
txroutehandler_ethereum_2 = TxRouteHandler(trade_instructions=trade_instructions_2)
txroutehandler_ethereum_3 = TxRouteHandler(trade_instructions=trade_instructions_3)


split_trade_instructions_0_split = CarbonTradeSplitter(cfg).split_carbon_trades(trade_instructions_0)
split_trade_instructions_1_split = CarbonTradeSplitter(cfg).split_carbon_trades(trade_instructions_1)
split_trade_instructions_2_split = CarbonTradeSplitter(cfg).split_carbon_trades(trade_instructions_2)
split_trade_instructions_3_split = CarbonTradeSplitter(cfg).split_carbon_trades(trade_instructions_3)


encoded_0 = txroutehandler_ethereum_0.custom_data_encoder(
            split_trade_instructions_0_split
        )
encoded_1 = txroutehandler_ethereum_1.custom_data_encoder(
            split_trade_instructions_1_split
        )
encoded_2 = txroutehandler_ethereum_2.custom_data_encoder(
            split_trade_instructions_2_split
        )
encoded_3 = txroutehandler_ethereum_3.custom_data_encoder(
            split_trade_instructions_3_split
        )


route_struct_0 = [
            asdict(rs)
            for rs in txroutehandler_ethereum_1.get_route_structs(
                trade_instructions=encoded_0, deadline=5000
            )
        ]

route_struct_1 = [
            asdict(rs)
            for rs in txroutehandler_ethereum_1.get_route_structs(
                trade_instructions=encoded_1, deadline=5000
            )
        ]

route_struct_2 = [
            asdict(rs)
            for rs in txroutehandler_ethereum_1.get_route_structs(
                trade_instructions=encoded_2, deadline=5000
            )
        ]

route_struct_3 = [
            asdict(rs)
            for rs in txroutehandler_ethereum_1.get_route_structs(
                trade_instructions=encoded_3, deadline=5000
            )
        ]

wrap_unwrap_0_processor = wrap_unwrap_processor_0.add_wrap_or_unwrap_trades_to_route(split_trade_instructions_0_split, route_struct_0, flashloan_struct_0)
wrap_unwrap_1_processor = wrap_unwrap_processor_1.add_wrap_or_unwrap_trades_to_route(split_trade_instructions_1_split, route_struct_1, flashloan_struct_1)
wrap_unwrap_2_processor = wrap_unwrap_processor_2.add_wrap_or_unwrap_trades_to_route(split_trade_instructions_2_split, route_struct_2, flashloan_struct_0)
wrap_unwrap_3_processor = wrap_unwrap_processor_3.add_wrap_or_unwrap_trades_to_route(split_trade_instructions_3_split, route_struct_3, flashloan_struct_1)


flashloan_struct_0=[{'platformId': 7, 'sourceTokens': ['0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2'], 'sourceAmounts': [15000000000000000000]}]
flashloan_struct_1=[{'platformId': 2, 'sourceTokens': ['0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE'], 'sourceAmounts': [15000000000000000000]}]

balances_0 = {'0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2': 15000000000000000000, '0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE': 0, '0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599': 0}
balances_1 = {'0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2': 0, '0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE': 15000000000000000000, '0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599': 0}
balances_2 = {'0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2': 15000000000000000000, '0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE': 0, '0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599': 0}
balances_3 = {'0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2': 0, '0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE': 15000000000000000000, '0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599': 0}

balances_0_processor = {'0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2': 15000000000000000000, '0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE': 0, '0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599': 0}
balances_1_processor = {'0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2': 0, '0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE': 15000000000000000000, '0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599': 0}
balances_2_processor = {'0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2': 15000000000000000000, '0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE': 0, '0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599': 0}
balances_3_processor = {'0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2': 0, '0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE': 15000000000000000000, '0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599': 0}


def check_no_negative(balance_dict):
    for tkn in balance_dict.keys():
        assert balance_dict[tkn] >= 0, f"negative balance found: {balance_dict}"

def loop_balances(_route_struct, _balance):
    for trade in _route_struct:
        #print(f"balance before trade {_balance}")
        _balance[trade['sourceToken']] -= trade['sourceAmount']
        _balance[trade['targetToken']] += trade['minTargetAmount']
        check_no_negative(_balance)


for idx, (_route, _balance) in enumerate([(wrap_unwrap_0_processor, balances_0_processor), (wrap_unwrap_1_processor, balances_1_processor), (wrap_unwrap_2_processor, balances_2_processor), (wrap_unwrap_3_processor, balances_3_processor)]):
    #print(f"starting loop {idx}")
    loop_balances(_route, _balance)

## For Debugging
# flashloan_struct_0 = flashloan WETH
# flashloan_struct_1 = flashloan ETH
# print("wrap_unwrap_0")

# print("")
# for trade in wrap_unwrap_0:
#     print(trade)
# print("\nwrap_unwrap_1")
# print("")
# print(wrap_unwrap_1)
# print("")
# for trade in wrap_unwrap_1:
#     print(trade)
# print("\nwrap_unwrap_2")


# print(wrap_unwrap_2)
# print("")
# print(flashloan_struct_0)
# for trade in wrap_unwrap_2:
#     print(trade)
# print("\nwrap_unwrap_3")
# print(wrap_unwrap_3)
# print("")
# print(flashloan_struct_1)
# for trade in wrap_unwrap_3:
#     print(trade)
# print("")

# -




