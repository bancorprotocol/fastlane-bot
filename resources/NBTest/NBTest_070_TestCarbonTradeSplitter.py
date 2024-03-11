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
import json
from fastlane_bot.helpers import TradeInstruction, TxRouteHandler, split_carbon_trades
from fastlane_bot.testing import *
from typing import List
from dataclasses import dataclass
from fastlane_bot.events.interface import Token

plt.rcParams['figure.figsize'] = [12,6]
from fastlane_bot import __VERSION__
require("3.0", __VERSION__)

# +
ETH_ADDRESS = "0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE"
USDC_ADDRESS = "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48"
WETH_ADDRESS = "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2"
WBTC_ADDRESS = "0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599"
BNT_ADDRESS = "0x1F573D6Fb3F13d689FF844B4cE37794d79a7FF1C"
PLATFORM_ID_WRAP_UNWRAP = 10
BANCOR_V2_NAME = "bancor_v2"
BANCOR_V3_NAME = "bancor_v3"
CARBON_POL_NAME = "bancor_pol"
UNISWAP_V2_NAME = "uniswap_v2"
UNISWAP_V3_NAME = "uniswap_v3"
SUSHISWAP_V2_NAME = "sushiswap_v2"
SUSHISWAP_V3_NAME = "sushiswap_v3"
CARBON_V1_NAME = "carbon_v1"
BANCOR_POL_NAME = "bancor_pol"
BALANCER_NAME = "balancer"
SOLIDLY_V2_NAME = "solidly_v2"
AERODROME_V2_NAME = "aerodrome_v2"
PANCAKESWAP_V2_NAME = "pancakeswap_v2"
PANCAKESWAP_V3_NAME = "pancakeswap_v3"

NATIVE_GAS_TOKEN_ADDRESS = "0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE"
WRAPPED_GAS_TOKEN_ADDRESS = "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2"
EXCHANGE_IDS = {
            BANCOR_V2_NAME: 1,
            BANCOR_V3_NAME: 2,
            BALANCER_NAME: 7,
            CARBON_POL_NAME: 8,
            PLATFORM_ID_WRAP_UNWRAP: 10,
            UNISWAP_V2_NAME: 3,
            UNISWAP_V3_NAME: 4,
            SOLIDLY_V2_NAME: 11,
            AERODROME_V2_NAME: 12,
            CARBON_V1_NAME: 6,
        }
UNI_V2_FORKS = [UNISWAP_V2_NAME, PANCAKESWAP_V2_NAME, SUSHISWAP_V2_NAME]
UNI_V3_FORKS = [UNISWAP_V3_NAME, PANCAKESWAP_V3_NAME, SUSHISWAP_V3_NAME]
CARBON_V1_FORKS = [CARBON_V1_NAME]
SOLIDLY_V2_FORKS = [SOLIDLY_V2_NAME]


# -

@dataclass
class _Test_Pool:
    
    cid: str
    pair_name: str
    exchange_name: str
    tkn0_address: str
    tkn1_address: str

    @property
    def get_tokens(self):
        return [self.tkn0_address, self.tkn1_address]
    
    @property
    def get_token_addresses(self):
        return [self.tkn0_address, self.tkn1_address]



_test_pools = [
    {"cid": "67035626283424877302284797664058337657416", "exchange_name": "carbon_v1", "tkn0_address": "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2", "tkn1_address": "0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599", },
    {"cid": "9187623906865338513511114400657741709505", "exchange_name": "carbon_v1", "tkn0_address": "0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE", "tkn1_address": "0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599", },
    {"cid": "2381976568446569244243622252022377480572", "exchange_name": "carbon_v1", "tkn0_address": "0x1F573D6Fb3F13d689FF844B4cE37794d79a7FF1C", "tkn1_address": "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48", },
    {"cid": "2381976568446569244243622252022377480676", "exchange_name": "carbon_v1", "tkn0_address": "0x1F573D6Fb3F13d689FF844B4cE37794d79a7FF1C", "tkn1_address": "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48", },
    {"cid": "0x1c15cb883c57ebba91d3e698aef9311ccd5e45ad3b8005e548d02290ed1ad974", "exchange_name": "pancakeswap_v2", "tkn0_address": "0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599", "tkn1_address": "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2", },
    {"cid": "0xa680dccded6454dcad79d49c3a7f246fdb551bf782fcd020ca73bef2c5e0f074", "exchange_name": "bancor_v2", "tkn0_address": "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48", "tkn1_address": "0x1F573D6Fb3F13d689FF844B4cE37794d79a7FF1C", },
              ]


def _test_create_pool(record):
    return _Test_Pool(
        cid=record.get("cid"),
        pair_name=record.get("pair_name"),
        exchange_name=record.get("exchange_name"),
        tkn0_address=record.get("tkn0_address"),
        tkn1_address=record.get("tkn1_address"),
                      )


# +
@dataclass
class Config:
    CARBON_V1_FORKS = CARBON_V1_FORKS
    UNI_V2_FORKS = UNI_V2_FORKS
    UNI_V3_FORKS = UNI_V3_FORKS
    EXCHANGE_IDS = EXCHANGE_IDS
    UNISWAP_V2_NAME = UNISWAP_V2_NAME
    UNISWAP_V3_NAME = UNISWAP_V3_NAME
    SOLIDLY_V2_FORKS = SOLIDLY_V2_FORKS
    BALANCER_NAME = BALANCER_NAME
    WRAPPED_GAS_TOKEN_ADDRESS = WRAPPED_GAS_TOKEN_ADDRESS
    NATIVE_GAS_TOKEN_ADDRESS = NATIVE_GAS_TOKEN_ADDRESS

cfg = Config()

# +
ETH_ADDRESS = "0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE"
USDC_ADDRESS = "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48"
WETH_ADDRESS = "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2"
WBTC_ADDRESS = "0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599"
BNT_ADDRESS = "0x1F573D6Fb3F13d689FF844B4cE37794d79a7FF1C"

_test_tokens = {
    ETH_ADDRESS: Token(symbol="ETH", address=ETH_ADDRESS, decimals=18),
    WETH_ADDRESS: Token(symbol="WETH", address=WETH_ADDRESS, decimals=18),
    USDC_ADDRESS: Token(symbol="USDC", address=USDC_ADDRESS, decimals=6),
    WBTC_ADDRESS: Token(symbol="WBTC", address=WBTC_ADDRESS, decimals=8),
    BNT_ADDRESS: Token(symbol="BNT", address=BNT_ADDRESS, decimals=18),
}

@dataclass
class QueryInterface:
    test_pools = _test_pools
    test_tokens = _test_tokens
    def get_pool_from_dict(self, cid):
        cid = str(cid).split("-")[0]
        return next((pool for pool in self.test_pools if pool["cid"] == cid), None)

    def get_pool(self, cid):
        pool_dict = self.get_pool_from_dict(cid)
        pool = _test_create_pool(pool_dict)
        return pool
    def get_token(self, tkn_address):
        return self.test_tokens.get(tkn_address)
        

db = QueryInterface()

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

#### Pancake V2 WBTC > WETH ####
trade_instruction_3 = TradeInstruction(
    cid='0x1c15cb883c57ebba91d3e698aef9311ccd5e45ad3b8005e548d02290ed1ad974',
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
    exchange_override = 'pancakeswap_v2',
)

#### Pancake V2 WBTC > WETH ####
trade_instruction_4 = TradeInstruction(
    cid='0x1c15cb883c57ebba91d3e698aef9311ccd5e45ad3b8005e548d02290ed1ad974',
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
    exchange_override = 'pancakeswap_v2',
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

def test_split_carbon_trades():
    split_trade_instructions_0_splitter = split_carbon_trades(cfg, trade_instructions_0)
    split_trade_instructions_1_splitter = split_carbon_trades(cfg, trade_instructions_1)
    split_trade_instructions_2_splitter = split_carbon_trades(cfg, trade_instructions_2)
    split_trade_instructions_3_splitter = split_carbon_trades(cfg, trade_instructions_3)

    assert len(split_trade_instructions_0_splitter) == len(trade_instructions_0) + 1
    assert len(split_trade_instructions_1_splitter) == len(trade_instructions_1)
    assert len(split_trade_instructions_2_splitter) == len(trade_instructions_2)
    assert len(split_trade_instructions_3_splitter) == len(trade_instructions_3)

    assert split_trade_instructions_0_splitter[0].cid == "9187623906865338513511114400657741709505"
    assert split_trade_instructions_0_splitter[0].tknin == "0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE"
    assert split_trade_instructions_0_splitter[0].tknout == "0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599"
    assert split_trade_instructions_0_splitter[0].amtin == 5
    assert split_trade_instructions_0_splitter[0].amtout == 0.5
    assert split_trade_instructions_0_splitter[0]._amtin_wei == 5000000000000000000
    assert split_trade_instructions_0_splitter[0]._amtout_wei == 50000000
    assert len(json.loads(split_trade_instructions_0_splitter[0].raw_txs.replace("'", '"'))) == 1

    assert split_trade_instructions_0_splitter[1].cid == "67035626283424877302284797664058337657416"
    assert split_trade_instructions_0_splitter[1].tknin == "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2"
    assert split_trade_instructions_0_splitter[1].tknout == "0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599"
    assert split_trade_instructions_0_splitter[1].amtin == 10
    assert split_trade_instructions_0_splitter[1].amtout == 1
    assert split_trade_instructions_0_splitter[1]._amtin_wei == 10000000000000000000
    assert split_trade_instructions_0_splitter[1]._amtout_wei == 100000000
    assert len(json.loads(split_trade_instructions_0_splitter[0].raw_txs.replace("'", '"'))) == 1

    assert split_trade_instructions_0_splitter[2].cid == "0x1c15cb883c57ebba91d3e698aef9311ccd5e45ad3b8005e548d02290ed1ad974"
    assert split_trade_instructions_0_splitter[2].tknin == "0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599"
    assert split_trade_instructions_0_splitter[2].tknout == "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2"
    assert split_trade_instructions_0_splitter[2].amtin == 2
    assert split_trade_instructions_0_splitter[2].amtout == 20
    assert split_trade_instructions_0_splitter[2]._amtin_wei == 200000000
    assert split_trade_instructions_0_splitter[2]._amtout_wei == 20000000000000000000
    assert len(json.loads(split_trade_instructions_0_splitter[2].raw_txs.replace("'", '"'))) == 0

    assert split_trade_instructions_1_splitter[0].cid == "67035626283424877302284797664058337657416"
    assert split_trade_instructions_1_splitter[0].tknin == "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2"
    assert split_trade_instructions_1_splitter[0].tknout == "0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599"
    assert split_trade_instructions_1_splitter[0].amtin == 20
    assert split_trade_instructions_1_splitter[0].amtout == 2
    assert split_trade_instructions_1_splitter[0]._amtin_wei == 20000000000000000000
    assert split_trade_instructions_1_splitter[0]._amtout_wei == 200000000
    assert len(json.loads(split_trade_instructions_1_splitter[0].raw_txs.replace("'", '"'))) == 2

    assert split_trade_instructions_1_splitter[1].cid == "0x1c15cb883c57ebba91d3e698aef9311ccd5e45ad3b8005e548d02290ed1ad974"
    assert split_trade_instructions_1_splitter[1].tknin == "0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599"
    assert split_trade_instructions_1_splitter[1].tknout == "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2"
    assert split_trade_instructions_1_splitter[1].amtin == 2
    assert split_trade_instructions_1_splitter[1].amtout == 20
    assert split_trade_instructions_1_splitter[1]._amtin_wei == 200000000
    assert split_trade_instructions_1_splitter[1]._amtout_wei == 20000000000000000000
    assert len(json.loads(split_trade_instructions_1_splitter[1].raw_txs.replace("'", '"'))) == 0

    assert split_trade_instructions_2_splitter[0].cid == "9187623906865338513511114400657741709505"
    assert split_trade_instructions_2_splitter[0].tknin == "0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE"
    assert split_trade_instructions_2_splitter[0].tknout == "0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599"
    assert split_trade_instructions_2_splitter[0].amtin == 10
    assert split_trade_instructions_2_splitter[0].amtout == 1.0
    assert split_trade_instructions_2_splitter[0]._amtin_wei == 10000000000000000000
    assert split_trade_instructions_2_splitter[0]._amtout_wei == 100000000
    assert len(json.loads(split_trade_instructions_2_splitter[0].raw_txs.replace("'", '"'))) == 2

    assert split_trade_instructions_2_splitter[1].cid == "0x1c15cb883c57ebba91d3e698aef9311ccd5e45ad3b8005e548d02290ed1ad974"
    assert split_trade_instructions_2_splitter[1].tknin == "0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599"
    assert split_trade_instructions_2_splitter[1].tknout == "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2"
    assert split_trade_instructions_2_splitter[1].amtin == 1
    assert split_trade_instructions_2_splitter[1].amtout == 10
    assert split_trade_instructions_2_splitter[1]._amtin_wei == 100000000
    assert split_trade_instructions_2_splitter[1]._amtout_wei == 10000000000000000000
    assert len(json.loads(split_trade_instructions_2_splitter[1].raw_txs.replace("'", '"'))) == 0

    assert split_trade_instructions_3_splitter[0].cid == "2381976568446569244243622252022377480572"
    assert split_trade_instructions_3_splitter[0].tknin == "0x1F573D6Fb3F13d689FF844B4cE37794d79a7FF1C"
    assert split_trade_instructions_3_splitter[0].tknout == "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48"
    assert split_trade_instructions_3_splitter[0].amtin == 15
    assert split_trade_instructions_3_splitter[0].amtout == 150
    assert split_trade_instructions_3_splitter[0]._amtin_wei == 15000000000000000000
    assert split_trade_instructions_3_splitter[0]._amtout_wei == 150000000
    assert len(json.loads(split_trade_instructions_3_splitter[0].raw_txs.replace("'", '"'))) == 2

    assert split_trade_instructions_3_splitter[1].cid == "0xa680dccded6454dcad79d49c3a7f246fdb551bf782fcd020ca73bef2c5e0f074"
    assert split_trade_instructions_3_splitter[1].tknin == "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48"
    assert split_trade_instructions_3_splitter[1].tknout == "0x1F573D6Fb3F13d689FF844B4cE37794d79a7FF1C"
    assert split_trade_instructions_3_splitter[1].amtin == 150
    assert split_trade_instructions_3_splitter[1].amtout == 15
    assert split_trade_instructions_3_splitter[1]._amtin_wei == 150000000
    assert split_trade_instructions_3_splitter[1]._amtout_wei == 15000000000000000000
    assert len(json.loads(split_trade_instructions_3_splitter[1].raw_txs.replace("'", '"'))) == 0

test_split_carbon_trades()