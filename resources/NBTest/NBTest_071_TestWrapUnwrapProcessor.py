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

from fastlane_bot import Config
from fastlane_bot.events.interface import QueryInterface
from fastlane_bot.helpers import TradeInstruction, TxRouteHandler, WrapUnwrapProcessor, CarbonTradeSplitter
from fastlane_bot.testing import *
from fastlane_bot.config.network import *

import json
from dataclasses import asdict
from typing import Dict
from fastlane_bot.testing import *

plt.rcParams['figure.figsize'] = [12,6]
from fastlane_bot import __VERSION__
require("3.0", __VERSION__)

# +
cfg = Config.new(config=Config.CONFIG_MAINNET, blockchain="ethereum")
pools = None
with open('fastlane_bot/data/tests/latest_pool_data_testing.json') as f:
    pools = json.load(f)
state = [pool for pool in pools]
exchanges = list({ex['exchange_name'] for ex in state})
db = QueryInterface(state=state, ConfigObj=cfg, exchanges=exchanges)


ETH_ADDRESS = "0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE"
USDC_ADDRESS = "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48"
WETH_ADDRESS = "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2"
WBTC_ADDRESS = "0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599"
BNT_ADDRESS = "0x1F573D6Fb3F13d689FF844B4cE37794d79a7FF1C"

# +
#### WETH ####
raw_tx_0 = {
                    "cid": "67035626283424877302284797664058337657416-0",
                    "tknin": "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2",
                    "amtin": 10,
                    "_amtin_wei": 10000000000000000000,
                    "tknout": "0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599",
                    "amtout": 1,
                    "_amtout_wei": 100000000,
                    }
#### ETH ####
raw_tx_1 = {
                    "cid": "9187623906865338513511114400657741709505-0",
                    "tknin": "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2",
                    "amtin": 5,
                    "_amtin_wei": 5000000000000000000,
                    "tknout": "0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599",
                    "amtout": 0.5,
                    "_amtout_wei": 50000000,
                    }

#### NEITHER ####
raw_tx_2 = {
                    "cid": "2381976568446569244243622252022377480572-0",
                    "tknin": "0x1F573D6Fb3F13d689FF844B4cE37794d79a7FF1C",
                    "amtin": 10,
                    "_amtin_wei": 10000000000000000000,
                    "tknout": "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48",
                    "amtout": 100,
                    "_amtout_wei": 100000000,
                    }
raw_tx_3 = {
                    "cid": "2381976568446569244243622252022377480676-0",
                    "tknin": "0x1F573D6Fb3F13d689FF844B4cE37794d79a7FF1C",
                    "amtin": 5,
                    "_amtin_wei": 5000000000000000000,
                    "tknout": "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48",
                    "amtout": 50,
                    "_amtout_wei": 50000000,
                    }

#### MIX ####
raw_tx_list_0 = [raw_tx_0, raw_tx_1]

#### WETH ONLY ####
raw_tx_list_1 = [raw_tx_0, raw_tx_0]

#### ETH ONLY ####
raw_tx_list_2 = [raw_tx_1, raw_tx_1]


#### NEITHER ####
raw_tx_list_3 = [raw_tx_2, raw_tx_3]


raw_tx_str_0 = str(raw_tx_list_0)
raw_tx_str_1 = str(raw_tx_list_1)
raw_tx_str_2 = str(raw_tx_list_2)

raw_tx_str_3 = str(raw_tx_list_3)

#### MIX ####
trade_instruction_0 = TradeInstruction(
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

#### WETH ONLY ####
trade_instruction_1 = TradeInstruction(
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
    raw_txs=raw_tx_str_1,
)

#### ETH ONLY ####
trade_instruction_2 = TradeInstruction(
    cid='67035626283424877302284797664058337657416-0',
    tknin='0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2',
    amtin=10,
    tknout='0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599',
    amtout=1,
    ConfigObj=cfg,
    db = db,
    tknin_dec_override =  18,
    tknout_dec_override = 8,
    tknin_addr_override = '0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2',
    tknout_addr_override = '0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599',
    exchange_override = 'carbon_v1',
    raw_txs=raw_tx_str_2,
)

#### Uni V3 WBTC > WETH ####
trade_instruction_3 = TradeInstruction(
    cid='0x6be8339b6f982a8d4a3c9485b7e8b97c088c6f1049dd4365fe4492fa88713c23',
    tknin='0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599',
    amtin=2,
    tknout='0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2',
    amtout=20,
    ConfigObj=cfg,
    db = db,
    tknin_dec_override =  8,
    tknout_dec_override = 18,
    tknin_addr_override = '0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599',
    tknout_addr_override = '0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2',
    exchange_override = 'uniswap_v3',
)

#### Uni V3 WBTC > WETH ####
trade_instruction_4 = TradeInstruction(
    cid='0x6be8339b6f982a8d4a3c9485b7e8b97c088c6f1049dd4365fe4492fa88713c23',
    tknin='0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599',
    amtin=1,
    tknout='0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2',
    amtout=10,
    ConfigObj=cfg,
    db = db,
    tknin_dec_override =  8,
    tknout_dec_override = 18,
    tknin_addr_override = '0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599',
    tknout_addr_override = '0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2',
    exchange_override = 'uniswap_v3',
)
#### Carbon NEITHER BNT > USDC ####
trade_instruction_5 = TradeInstruction(
    cid='67035626283424877302284797664058337657416-0',
    tknin='0x1F573D6Fb3F13d689FF844B4cE37794d79a7FF1C',
    amtin=15,
    tknout='0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48',
    amtout=150,
    ConfigObj=cfg,
    db = db,
    tknin_dec_override =  18,
    tknout_dec_override = 6,
    tknin_addr_override = '0x1F573D6Fb3F13d689FF844B4cE37794d79a7FF1C',
    tknout_addr_override = '0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48',
    exchange_override = 'carbon_v1',
    raw_txs=raw_tx_str_3,
)

#### Bancor V2 USDC > BNT ####
trade_instruction_6 = TradeInstruction(
    cid='0xa680dccded6454dcad79d49c3a7f246fdb551bf782fcd020ca73bef2c5e0f074-0',
    tknin='0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48',
    amtin=150,
    tknout='0x1F573D6Fb3F13d689FF844B4cE37794d79a7FF1C',
    amtout=15,
    ConfigObj=cfg,
    db = db,
    tknin_dec_override =  6,
    tknout_dec_override = 18,
    tknin_addr_override = '0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48',
    tknout_addr_override = '0x1F573D6Fb3F13d689FF844B4cE37794d79a7FF1C',
    exchange_override = 'bancor_v2',
)
#### MIX ####
trade_instructions_0 = [trade_instruction_0, trade_instruction_3]
#### WETH ONLY ####
trade_instructions_1 = [trade_instruction_1, trade_instruction_3]
#### ETH ONLY ####
trade_instructions_2 = [trade_instruction_2, trade_instruction_4]
#### NEITHER ####
trade_instructions_3 = [trade_instruction_5, trade_instruction_6]

#### MIX ####
txroutehandler_ethereum_0 = TxRouteHandler(trade_instructions=trade_instructions_0)
#### ALL WETH ####
txroutehandler_ethereum_1 = TxRouteHandler(trade_instructions=trade_instructions_1)
#### ALL WETH ####
txroutehandler_ethereum_2 = TxRouteHandler(trade_instructions=trade_instructions_2)
#### NEITHER ####
txroutehandler_ethereum_3 = TxRouteHandler(trade_instructions=trade_instructions_3)


split_trade_instructions_0_splitter = CarbonTradeSplitter(cfg).split_carbon_trades(trade_instructions_0)
split_trade_instructions_1_splitter = CarbonTradeSplitter(cfg).split_carbon_trades(trade_instructions_1)
split_trade_instructions_2_splitter = CarbonTradeSplitter(cfg).split_carbon_trades(trade_instructions_2)
split_trade_instructions_3_splitter = CarbonTradeSplitter(cfg).split_carbon_trades(trade_instructions_3)

# Encode the trade instructions
encoded_trade_instructions_0 = txroutehandler_ethereum_0.custom_data_encoder(split_trade_instructions_0_splitter)
encoded_trade_instructions_1 = txroutehandler_ethereum_1.custom_data_encoder(split_trade_instructions_1_splitter)
encoded_trade_instructions_2 = txroutehandler_ethereum_2.custom_data_encoder(split_trade_instructions_2_splitter)
encoded_trade_instructions_3 = txroutehandler_ethereum_3.custom_data_encoder(split_trade_instructions_3_splitter)

# Get the deadline
deadline = 12345678

flashloan_struct_0 = txroutehandler_ethereum_0.generate_flashloan_struct(trade_instructions_objects=split_trade_instructions_0_splitter)
flashloan_struct_1 = txroutehandler_ethereum_1.generate_flashloan_struct(trade_instructions_objects=split_trade_instructions_1_splitter)
flashloan_struct_2 = txroutehandler_ethereum_2.generate_flashloan_struct(trade_instructions_objects=split_trade_instructions_2_splitter)
flashloan_struct_3 = txroutehandler_ethereum_3.generate_flashloan_struct(trade_instructions_objects=split_trade_instructions_3_splitter)

# Get the route struct
route_struct_0 = [
    asdict(rs)
    for rs in txroutehandler_ethereum_0.get_route_structs(
        trade_instructions=encoded_trade_instructions_0, deadline=deadline
    )
]
route_struct_1 = [
    asdict(rs)
    for rs in txroutehandler_ethereum_1.get_route_structs(
        trade_instructions=encoded_trade_instructions_1, deadline=deadline
    )
]
route_struct_2 = [
    asdict(rs)
    for rs in txroutehandler_ethereum_2.get_route_structs(
        trade_instructions=encoded_trade_instructions_2, deadline=deadline
    )
]
route_struct_3 = [
    asdict(rs)
    for rs in txroutehandler_ethereum_3.get_route_structs(
        trade_instructions=encoded_trade_instructions_3, deadline=deadline
    )
]



# -

# ## Test Split Carbon Trades

# ### Test _init_balance_tracker

# +
def test_init_balance_tracker():
    _processor_0 = WrapUnwrapProcessor(cfg=cfg)
    _processor_1 = WrapUnwrapProcessor(cfg=cfg)
    _processor_2 = WrapUnwrapProcessor(cfg=cfg)
    _processor_3 = WrapUnwrapProcessor(cfg=cfg)

    _processor_0._init_balance_tracker(flashloan_struct_0)
    _processor_1._init_balance_tracker(flashloan_struct_1)
    _processor_2._init_balance_tracker(flashloan_struct_2)
    _processor_3._init_balance_tracker(flashloan_struct_3)

    def _check_balances(_balance_dict, _flashloan_struct):
        for _tkn in _balance_dict.keys():
            assert _tkn in _flashloan_struct[0]["sourceTokens"]

    _check_balances(_processor_0.balance_tracker, flashloan_struct_0)
    _check_balances(_processor_1.balance_tracker, flashloan_struct_1)
    _check_balances(_processor_2.balance_tracker, flashloan_struct_2)
    _check_balances(_processor_3.balance_tracker, flashloan_struct_3)



# +
def test_ensure_unique_flashloan_token():
    _processor_0 = WrapUnwrapProcessor(cfg=cfg)
    _processor_1 = WrapUnwrapProcessor(cfg=cfg)

    _processor_0.flashloan_wrapped_gas_token = True
    _processor_0.flashloan_native_gas_token = False

    _processor_1.flashloan_wrapped_gas_token = True
    _processor_1.flashloan_native_gas_token = True
    

    assert not raises(_processor_0._ensure_unique_flashloan_token)
    assert raises(_processor_1._ensure_unique_flashloan_token).startswith("[WrapUnwrapProcessor _ensure_unique_flashloan_token]")



# +
def test_segment_routes():
    _processor_0 = WrapUnwrapProcessor(cfg=cfg)

    _segments_0 = _processor_0._segment_routes(split_trade_instructions_0_splitter, route_struct_0)
    assert len(_segments_0.keys()) == 3

    for trade in route_struct_0:
        pair = trade["sourceToken"] + "/" + trade["targetToken"]
        assert pair in _segments_0
        assert isinstance(_segments_0[pair]["amt_in"], int)
        assert isinstance(_segments_0[pair]["amt_out"], int)
        assert isinstance(_segments_0[pair]["token_in"], str)
        assert isinstance(_segments_0[pair]["token_out"], str)
        assert _segments_0[pair]["amt_in"] > 0
        assert _segments_0[pair]["amt_out"] > 0
        assert len(_segments_0[pair]["trades"]) > 0


    


# +
def test_handle_wrap_or_unwrap():
    _deadline = 12345678
    _processor_0 = WrapUnwrapProcessor(cfg=cfg)
    _processor_1 = WrapUnwrapProcessor(cfg=cfg)
    _processor_2 = WrapUnwrapProcessor(cfg=cfg)

    _key_0 = '0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE/0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599'
    _key_1 = '0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2/0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599'
    _key_2 = '0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599/0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2'
    _segments_0 = {'0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE/0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599': {'amt_out': 50000000, 'amt_in': 5000000000000000000, 'token_in': '0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE', 'token_out': '0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599', 'trades': {0: 'carbon_v1'}}}
    _segments_1 = {'0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2/0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599': {'amt_out': 100000000, 'amt_in': 10000000000000000000, 'token_in': '0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2', 'token_out': '0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599', 'trades': {1: 'carbon_v1'}}}
    _segments_2 = {'0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599/0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2': {'amt_out': 20000000000000000000, 'amt_in': 200000000, 'token_in': '0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599', 'token_out': '0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2', 'trades': {2: 'uniswap_v3'}}}

    _processor_0.balance_tracker = {'0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE': 0, '0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2': 5000000000000000000}
    _processor_1.balance_tracker = {'0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE': 0, '0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2': 10000000000000000000}
    _processor_2.balance_tracker = {'0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE': 0, '0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2': 5000000000000000000, '0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599': 200000000}

    _new_route_struct_0 = []
    _new_route_struct_1 = []
    _new_route_struct_2 = []
    _processor_0._handle_wrap_or_unwrap(segment=_segments_0[_key_0], deadline=_deadline, new_route_struct=_new_route_struct_0)
    _processor_1._handle_wrap_or_unwrap(segment=_segments_1[_key_1], deadline=_deadline, new_route_struct=_new_route_struct_1)
    _processor_2._handle_wrap_or_unwrap(segment=_segments_2[_key_2], deadline=_deadline, new_route_struct=_new_route_struct_2)

    # Check that balance tracker was updated correctly
    assert _processor_0.balance_tracker['0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE'] == 5000000000000000000
    assert _processor_0.balance_tracker['0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2'] == 0
    assert _processor_1.balance_tracker['0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE'] == 0
    assert _processor_1.balance_tracker['0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2'] == 10000000000000000000
    assert _processor_2.balance_tracker['0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE'] == 0
    assert _processor_2.balance_tracker['0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2'] == 5000000000000000000
    assert _processor_2.balance_tracker['0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599'] == 200000000

    # Check that trade was added when expected
    assert len(_new_route_struct_0) == 1
    assert len(_new_route_struct_1) == 0
    assert len(_new_route_struct_2) == 0


    


# +
def test_adjust_balance_for_wrap_unwrap():
    _processor_0 = WrapUnwrapProcessor(cfg=cfg)
    _processor_1 = WrapUnwrapProcessor(cfg=cfg)
    _processor_0.balance_tracker = {'0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE': 0, '0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2': 5000000000000000000}
    _processor_1.balance_tracker = {'0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE': 10000000000000000000, '0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2': 0}

    _processor_0._adjust_balance_for_wrap_unwrap(is_wrapping=False, amount=5000000000000000000)
    _processor_1._adjust_balance_for_wrap_unwrap(is_wrapping=True, amount=5000000000000000000)

    # Check that balances have been updated
    assert _processor_0.balance_tracker['0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE'] == 5000000000000000000
    assert _processor_0.balance_tracker['0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2'] == 0
    assert _processor_1.balance_tracker['0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE'] == 5000000000000000000
    assert _processor_1.balance_tracker['0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2'] == 5000000000000000000



# +
def test_update_token_balance():
    _processor_0 = WrapUnwrapProcessor(cfg=cfg)
    _processor_1 = WrapUnwrapProcessor(cfg=cfg)
    _processor_2 = WrapUnwrapProcessor(cfg=cfg)

    _processor_0.balance_tracker = {'0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE': 0, '0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2': 5000000000000000000}
    _processor_1.balance_tracker = {'0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE': 10000000000000000000, '0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2': 0}
    _processor_2.balance_tracker = {'0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE': 10000000000000000000, '0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2': 0}

    _processor_0._update_token_balance(token_address='0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2', token_amount=5000000000000000000, add=True)
    _processor_1._update_token_balance(token_address='0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE', token_amount=5000000000000000000, add=False)
    _processor_2._update_token_balance(token_address='0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599', token_amount=5000000000000000000, add=True)

    assert _processor_0.balance_tracker['0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2'] == 5000000000000000000 + 5000000000000000000
    assert _processor_1.balance_tracker['0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE'] == 10000000000000000000 - 5000000000000000000
    assert _processor_2.balance_tracker['0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599'] == 5000000000000000000



# +
def test_append_trades_based_on_exchange():
    _processor_0 = WrapUnwrapProcessor(cfg=cfg)
    _processor_1 = WrapUnwrapProcessor(cfg=cfg)
    _processor_2 = WrapUnwrapProcessor(cfg=cfg)

    _key_0 = '0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE/0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599'
    _key_1 = '0x1F573D6Fb3F13d689FF844B4cE37794d79a7FF1C/0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48'
    _key_2 = '0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599/0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2'
    _segments_0 = {'0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE/0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599': {'amt_out': 50000000, 'amt_in': 5000000000000000000, 'token_in': '0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE', 'token_out': '0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599', 'trades': {0: 'carbon_v1', 2: 'uniswap_v3'}}}
    _segments_1 = {'0x1F573D6Fb3F13d689FF844B4cE37794d79a7FF1C/0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48': {'amt_out': 100000000, 'amt_in': 10000000000000000000, 'token_in': '0x1F573D6Fb3F13d689FF844B4cE37794d79a7FF1C', 'token_out': '0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48', 'trades': {1: 'bancor_v2', 0: 'carbon_v1'}}}
    _segments_2 = {'0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599/0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2': {'amt_out': 20000000000000000000, 'amt_in': 200000000, 'token_in': '0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599', 'token_out': '0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2', 'trades': {1: 'uniswap_v3'}}}

    _processor_0.balance_tracker = {'0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE': 5000000000000000000, '0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2': 0}
    _processor_1.balance_tracker = {'0x1F573D6Fb3F13d689FF844B4cE37794d79a7FF1C': 20000000000000000000}
    _processor_2.balance_tracker = {'0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE': 0, '0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2': 5000000000000000000, '0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599': 200000000}

    _new_route_struct_0 = []
    _new_route_struct_1 = []
    _new_route_struct_2 = []

    # Test trades are added with Carbon trades being last.
    _processor_0._append_trades_based_on_exchange(segment=_segments_0[_key_0], route_struct=route_struct_0, new_route_struct=_new_route_struct_0)
    _processor_1._append_trades_based_on_exchange(segment=_segments_1[_key_1], route_struct=route_struct_3, new_route_struct=_new_route_struct_1)
    _processor_2._append_trades_based_on_exchange(segment=_segments_2[_key_2], route_struct=route_struct_2, new_route_struct=_new_route_struct_2)

    assert len(_new_route_struct_0) == len(_segments_0[_key_0]['trades'])
    assert len(_new_route_struct_1) == len(_segments_1[_key_1]['trades'])
    assert len(_new_route_struct_2) == len(_segments_2[_key_2]['trades'])

    assert _new_route_struct_0[0]['platformId'] == 4
    assert _new_route_struct_0[1]['platformId'] == 6
    assert _new_route_struct_1[0]['platformId'] == 1
    assert _new_route_struct_1[1]['platformId'] == 6
    assert _new_route_struct_2[0]['platformId'] == 4
    
    # Test that balances are updated for tkns in & out
    assert _processor_0.balance_tracker['0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE'] == 0
    assert _processor_0.balance_tracker['0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599'] == 50000000
    assert _processor_1.balance_tracker['0x1F573D6Fb3F13d689FF844B4cE37794d79a7FF1C'] == 10000000000000000000
    assert _processor_1.balance_tracker['0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48'] == 100000000
    assert _processor_2.balance_tracker['0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE'] == 0
    assert _processor_2.balance_tracker['0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2'] == 25000000000000000000
    assert _processor_2.balance_tracker['0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599'] == 0




# +
def test_handle_final_balance():
    _deadline = 12345678
    _processor_0 = WrapUnwrapProcessor(cfg=cfg)
    _processor_1 = WrapUnwrapProcessor(cfg=cfg)
    _processor_2 = WrapUnwrapProcessor(cfg=cfg)

    _processor_0.flashloan_native_gas_token = True
    _processor_0.flashloan_wrapped_gas_token = False

    _processor_1.flashloan_native_gas_token = False
    _processor_1.flashloan_wrapped_gas_token = True

    _processor_2.flashloan_native_gas_token = False
    _processor_2.flashloan_wrapped_gas_token = False

    _new_route_struct_0 = []
    _new_route_struct_1 = []
    _new_route_struct_2 = []

    _processor_0.balance_tracker = {'0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE': 0, '0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2': 5000000000000000000}
    _processor_1.balance_tracker = {'0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE': 0, '0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2': 5000000000000000000, '0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599': 200000000}
    _processor_2.balance_tracker = {'0x1F573D6Fb3F13d689FF844B4cE37794d79a7FF1C': 20000000000000000000}

    _processor_0._handle_final_balance(deadline=_deadline, new_route_struct=_new_route_struct_0)
    _processor_1._handle_final_balance(deadline=_deadline, new_route_struct=_new_route_struct_1)
    _processor_2._handle_final_balance(deadline=_deadline, new_route_struct=_new_route_struct_2)

    assert len(_new_route_struct_0) == 1
    assert len(_new_route_struct_1) == 0
    assert len(_new_route_struct_2) == 0

    assert _new_route_struct_0[0]['platformId'] == 10
    assert _new_route_struct_0[0]['sourceAmount'] == 0




# +
def test_get_wrap_or_unwrap_native_gas_tkn_struct():
    _deadline = 12345678
    _processor_0 = WrapUnwrapProcessor(cfg=cfg)

    _result_0 = _processor_0._get_wrap_or_unwrap_native_gas_tkn_struct(deadline=_deadline, wrap=True, source_amount=1000)
    _result_1 = _processor_0._get_wrap_or_unwrap_native_gas_tkn_struct(deadline=_deadline, wrap=False, source_amount=5000)

    assert _result_0['deadline'] == _deadline
    assert _result_0['platformId'] == 10
    assert isinstance(_result_0['sourceAmount'], int)
    assert isinstance(_result_0['minTargetAmount'], int)
    assert _result_0['sourceToken'] == '0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE'
    assert _result_0['targetToken'] == '0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2'

    assert _result_1['deadline'] == _deadline
    assert _result_1['platformId'] == 10
    assert isinstance(_result_1['sourceAmount'], int)
    assert isinstance(_result_1['minTargetAmount'], int)
    assert _result_1['sourceToken'] == '0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2'
    assert _result_1['targetToken'] == '0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE'

    for key in _result_0:
        assert not isinstance(_result_0[key], float)
    for key in _result_1:
        assert not isinstance(_result_1[key], float)




# -








