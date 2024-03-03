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

# +
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


# -

# ## Test Split Carbon Trades

# ### Test _is_carbon_trade

# +

def test_is_carbon_trade():
    trade_splitter = CarbonTradeSplitter(ConfigObj=cfg)

    carbon_trades = [trade_instruction_0, trade_instruction_1, trade_instruction_2, trade_instruction_5]
    non_carbon_trades = [trade_instruction_3, trade_instruction_4, trade_instruction_6]


    for trade in carbon_trades:
        assert trade_splitter._is_carbon_trade(trade=trade)

    for trade in non_carbon_trades:
        assert not trade_splitter._is_carbon_trade(trade=trade)

test_is_carbon_trade()


# +
def test_get_real_tkn():
    trade_splitter = CarbonTradeSplitter(ConfigObj=cfg)
    
    # ETH 
    assert trade_splitter._get_real_tkn(token_address=ETH_ADDRESS, token_type=trade_splitter.NATIVE) == ETH_ADDRESS
    assert trade_splitter._get_real_tkn(token_address=ETH_ADDRESS, token_type=trade_splitter.WRAPPED) == WETH_ADDRESS
    
    # WETH
    assert trade_splitter._get_real_tkn(token_address=WETH_ADDRESS, token_type=trade_splitter.NATIVE) == ETH_ADDRESS
    assert trade_splitter._get_real_tkn(token_address=WETH_ADDRESS, token_type=trade_splitter.WRAPPED) == WETH_ADDRESS
    # OTHER

    assert trade_splitter._get_real_tkn(token_address=USDC_ADDRESS, token_type=trade_splitter.NATIVE) == USDC_ADDRESS
    assert trade_splitter._get_real_tkn(token_address=USDC_ADDRESS, token_type=trade_splitter.WRAPPED) == USDC_ADDRESS

test_get_real_tkn()


# +
def test_process_carbon_trades():
    trade_splitter = CarbonTradeSplitter(ConfigObj=cfg)
    ### MIX ###
    carbon_exchanges_0 = trade_splitter._process_carbon_trades(trade_instruction_0)
    ### WETH ###
    carbon_exchanges_1 = trade_splitter._process_carbon_trades(trade_instruction_1)
    ### ETH ###
    carbon_exchanges_2 = trade_splitter._process_carbon_trades(trade_instruction_2)
    ### NEITHER ###
    carbon_exchanges_3 = trade_splitter._process_carbon_trades(trade_instruction_5)


    def _assert_wrapped_or_native(is_native: bool, _raw_txs: List):
            match = ETH_ADDRESS if is_native else WETH_ADDRESS
            wrong_tkn = ETH_ADDRESS if not is_native else WETH_ADDRESS
            for tx in _raw_txs:
                assert (tx["tknin"] == match or tx["tknout"] == match) and (tx["tknin"] != wrong_tkn and tx["tknout"] != wrong_tkn)


    def _test_extracted_txs(_carbon_dict):
         _assert_wrapped_or_native(is_native=True, _raw_txs=_carbon_dict["carbon_v1"]["native"]["raw_txs"]), f"{_carbon_dict}"
         _assert_wrapped_or_native(is_native=False, _raw_txs=_carbon_dict["carbon_v1"]["wrapped"]["raw_txs"]), f"{_carbon_dict}"

    def _test_amts(_carbon_dict, _trade_instruction):
         assert _trade_instruction._amtin_wei == (_carbon_dict["carbon_v1"]["native"]["_amtin_wei"] + _carbon_dict["carbon_v1"]["wrapped"]["_amtin_wei"] + _carbon_dict["carbon_v1"]["neither"]["_amtin_wei"]), f'instruction amtin = {_trade_instruction._amtin_wei}, extracted={(_carbon_dict["carbon_v1"]["native"]["_amtin_wei"] + _carbon_dict["carbon_v1"]["wrapped"]["_amtin_wei"] + _carbon_dict["carbon_v1"]["neither"]["_amtin_wei"])}, native={_carbon_dict["carbon_v1"]["native"]["_amtin_wei"]}, wrapped={_carbon_dict["carbon_v1"]["wrapped"]["_amtin_wei"]}, neither={_carbon_dict["carbon_v1"]["neither"]["_amtin_wei"]}'
         assert _trade_instruction._amtout_wei == (_carbon_dict["carbon_v1"]["native"]["_amtout_wei"] + _carbon_dict["carbon_v1"]["wrapped"]["_amtout_wei"] + _carbon_dict["carbon_v1"]["neither"]["_amtout_wei"]), f'instruction amtout = {_trade_instruction._amtout_wei}, extracted={(_carbon_dict["carbon_v1"]["native"]["_amtout_wei"] + _carbon_dict["carbon_v1"]["wrapped"]["_amtout_wei"] + _carbon_dict["carbon_v1"]["neither"]["_amtout_wei"])}, native={_carbon_dict["carbon_v1"]["native"]["_amtout_wei"]}, wrapped={_carbon_dict["carbon_v1"]["wrapped"]["_amtout_wei"]}, neither={_carbon_dict["carbon_v1"]["neither"]["_amtout_wei"]}'


    assert len(carbon_exchanges_0["carbon_v1"]["neither"]["raw_txs"]) == 0
    assert len(carbon_exchanges_0["carbon_v1"]["native"]["raw_txs"]) == 1
    assert len(carbon_exchanges_0["carbon_v1"]["wrapped"]["raw_txs"]) == 1

    _test_extracted_txs(carbon_exchanges_0)
    _test_extracted_txs(carbon_exchanges_1)
    _test_extracted_txs(carbon_exchanges_2)
    _test_extracted_txs(carbon_exchanges_3)

    _test_amts(carbon_exchanges_0, trade_instruction_0)
    _test_amts(carbon_exchanges_1, trade_instruction_1)
    _test_amts(carbon_exchanges_2, trade_instruction_2)
    _test_amts(carbon_exchanges_3, trade_instruction_5)

    #print(carbon_exchanges_0)

test_process_carbon_trades()
# -

{'carbon_v1': {'native': {'raw_txs': [{'cid': '9187623906865338513511114400657741709505-0', 'tknin': '0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE', 'amtin': 5, '_amtin_wei': 5000000000000000000, 'tknout': '0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599', 'amtout': 0.5, '_amtout_wei': 50000000}], 'amtin': 5, 'amtout': 0.5, '_amtin_wei': 5000000000000000000, '_amtout_wei': 50000000, 'tknin': '0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE', 'tknout': '0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599'}, 
               'wrapped': {'raw_txs': [{'cid': '67035626283424877302284797664058337657416-0', 'tknin': '0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2', 'amtin': 10, '_amtin_wei': 10000000000000000000, 'tknout': '0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599', 'amtout': 1, '_amtout_wei': 100000000}], 'amtin': 10, 'amtout': 1, '_amtin_wei': 10000000000000000000, '_amtout_wei': 100000000, 'tknin': '0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2', 'tknout': '0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599'}, 
               'neither': {'raw_txs': [], 'amtin': 0, 'amtout': 0, '_amtin_wei': 0, '_amtout_wei': 0}}}


# +
def test_get_token_type():
    trade_splitter = CarbonTradeSplitter(ConfigObj=cfg)
    curve_0 = db.get_pool(cid=67035626283424877302284797664058337657416)
    curve_1 = db.get_pool(cid=9187623906865338513511114400657741709505)
    curve_2 = db.get_pool(cid=2381976568446569244243622252022377480572)

    assert trade_splitter._get_token_type(curve_0) == trade_splitter.WRAPPED
    assert trade_splitter._get_token_type(curve_1) == trade_splitter.NATIVE
    assert trade_splitter._get_token_type(curve_2) == trade_splitter.NEITHER

test_get_token_type()

# -

def test_returns_dictionary_with_correct_keys():
    # Arrange
    carbon_trade_splitter = CarbonTradeSplitter(ConfigObj=cfg)

    # Act
    result = carbon_trade_splitter._new_trade_data_structure()

    # Assert
    assert isinstance(result, dict)
    assert "raw_txs" in result
    assert "amtin" in result
    assert "amtout" in result
    assert "_amtin_wei" in result
    assert "_amtout_wei" in result
test_returns_dictionary_with_correct_keys()


# +
def test_initialize_exchange_data():
    trade_splitter = CarbonTradeSplitter(ConfigObj=cfg)
    init_data = trade_splitter._initialize_exchange_data()

    assert trade_splitter.NATIVE in init_data
    assert trade_splitter.WRAPPED in init_data
    assert trade_splitter.NEITHER in init_data

    for _item in init_data.keys():
        assert len(init_data[_item]["raw_txs"]) == 0
        assert init_data[_item]["amtin"] == 0
        assert init_data[_item]["amtout"] == 0
        assert init_data[_item]["_amtin_wei"] == 0
        assert init_data[_item]["_amtout_wei"] == 0


test_initialize_exchange_data()


# +
def test_valid_exchange_data():

    carbon_trade_splitter = CarbonTradeSplitter(cfg)

    # Arrange
    exchange_data_0 = carbon_trade_splitter._initialize_exchange_data()
    exchange_data_1 = carbon_trade_splitter._initialize_exchange_data()
    exchange_data_2 = carbon_trade_splitter._initialize_exchange_data()

    _tx_weth = raw_tx_0
    _tx_eth = raw_tx_1
    _tx_neither = raw_tx_2
    # Act
    carbon_trade_splitter._update_exchange_data(exchange_data_0, carbon_trade_splitter.NATIVE, _tx_eth, trade_instruction_0)
    carbon_trade_splitter._update_exchange_data(exchange_data_1, carbon_trade_splitter.WRAPPED, _tx_weth, trade_instruction_0)
    carbon_trade_splitter._update_exchange_data(exchange_data_1, carbon_trade_splitter.WRAPPED, _tx_weth, trade_instruction_0)
    carbon_trade_splitter._update_exchange_data(exchange_data_2, carbon_trade_splitter.NEITHER, _tx_neither, trade_instruction_5)

    assert exchange_data_0["native"]["amtin"] == raw_tx_1["amtin"]
    assert exchange_data_0["native"]["amtout"] == raw_tx_1["amtout"]
    assert exchange_data_0["native"]["_amtin_wei"] == raw_tx_1["_amtin_wei"]
    assert exchange_data_0["native"]["_amtout_wei"] == raw_tx_1["_amtout_wei"]

    assert exchange_data_1["wrapped"]["amtin"] == _tx_weth["amtin"] * 2
    assert exchange_data_1["wrapped"]["amtout"] == _tx_weth["amtout"] * 2
    assert exchange_data_1["wrapped"]["_amtin_wei"] == _tx_weth["_amtin_wei"] * 2
    assert exchange_data_1["wrapped"]["_amtout_wei"] == _tx_weth["_amtout_wei"] * 2

    assert exchange_data_2["neither"]["amtin"] == _tx_neither["amtin"]
    assert exchange_data_2["neither"]["amtout"] == _tx_neither["amtout"]
    assert exchange_data_2["neither"]["_amtin_wei"] == _tx_neither["_amtin_wei"]
    assert exchange_data_2["neither"]["_amtout_wei"] == _tx_neither["_amtout_wei"]

test_valid_exchange_data()


# +
def test_create_new_trades_from_carbon_exchanges():
    carbon_trade_splitter = CarbonTradeSplitter(cfg)
    _mix_trade = trade_instruction_0
    _weth_trade = trade_instruction_1
    _eth_trade = trade_instruction_2
    _neither_trade = trade_instruction_5

    carbon_exchanges_0 = carbon_trade_splitter._process_carbon_trades(_mix_trade)
    carbon_exchanges_1 = carbon_trade_splitter._process_carbon_trades(_weth_trade)
    carbon_exchanges_2 = carbon_trade_splitter._process_carbon_trades(_eth_trade)
    carbon_exchanges_3 = carbon_trade_splitter._process_carbon_trades(_neither_trade)


    new_trades_0 = carbon_trade_splitter._create_new_trades_from_carbon_exchanges(carbon_exchanges_0, _mix_trade)
    new_trades_1 = carbon_trade_splitter._create_new_trades_from_carbon_exchanges(carbon_exchanges_1, _weth_trade)
    new_trades_2 = carbon_trade_splitter._create_new_trades_from_carbon_exchanges(carbon_exchanges_2, _eth_trade)
    new_trades_3 = carbon_trade_splitter._create_new_trades_from_carbon_exchanges(carbon_exchanges_3, _neither_trade)

    assert len(new_trades_0) == 2
    assert len(new_trades_1) == 1
    assert len(new_trades_2) == 1
    assert len(new_trades_3) == 1

    assert new_trades_0[0].tknin == ETH_ADDRESS
    assert new_trades_0[1].tknin == WETH_ADDRESS
    assert new_trades_0[0].tknout == WBTC_ADDRESS
    assert new_trades_0[1].tknout == WBTC_ADDRESS

    assert new_trades_1[0].tknin == WETH_ADDRESS
    assert new_trades_1[0].tknout == WBTC_ADDRESS

    assert new_trades_2[0].tknin == ETH_ADDRESS
    assert new_trades_2[0].tknout == WBTC_ADDRESS

    assert new_trades_3[0].tknin == BNT_ADDRESS
    assert new_trades_3[0].tknout == USDC_ADDRESS

    assert _mix_trade._amtin_wei == new_trades_0[0]._amtin_wei + new_trades_0[1]._amtin_wei
    assert _mix_trade._amtout_wei == new_trades_0[0]._amtout_wei + new_trades_0[1]._amtout_wei

    assert _weth_trade._amtin_wei == new_trades_1[0]._amtin_wei
    assert _weth_trade._amtout_wei == new_trades_1[0]._amtout_wei

    assert _eth_trade._amtin_wei == new_trades_2[0]._amtin_wei
    assert _eth_trade._amtout_wei == new_trades_2[0]._amtout_wei

    assert _neither_trade._amtin_wei == new_trades_3[0]._amtin_wei
    assert _neither_trade._amtout_wei == new_trades_3[0]._amtout_wei



test_create_new_trades_from_carbon_exchanges()
# -





# ## Full Split Test

# +
split_trade_instructions_0_splitter = CarbonTradeSplitter(cfg).split_carbon_trades(trade_instructions_0)
split_trade_instructions_1_splitter = CarbonTradeSplitter(cfg).split_carbon_trades(trade_instructions_1)
split_trade_instructions_2_splitter = CarbonTradeSplitter(cfg).split_carbon_trades(trade_instructions_2)
split_trade_instructions_3_splitter = CarbonTradeSplitter(cfg).split_carbon_trades(trade_instructions_3)


assert len(split_trade_instructions_0_splitter) == len(trade_instructions_0) + 1
assert len(split_trade_instructions_1_splitter) == len(trade_instructions_1)
assert len(split_trade_instructions_2_splitter) == len(trade_instructions_2)
assert len(split_trade_instructions_3_splitter) == len(trade_instructions_3)
# -


