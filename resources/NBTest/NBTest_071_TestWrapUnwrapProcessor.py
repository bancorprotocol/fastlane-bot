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

from fastlane_bot.helpers import TradeInstruction, add_wrap_or_unwrap_trades_to_route
from fastlane_bot.testing import *
from dataclasses import dataclass
plt.rcParams['figure.figsize'] = [12,6]
from fastlane_bot import __VERSION__
require("3.0", __VERSION__)

# +
ZERO_ADDRESS = "0x0000000000000000000000000000000000000000"
ETH_ADDRESS = "0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE"
PLATFORM_NAME_WRAP_UNWRAP = "wrap_or_unwrap"
BANCOR_V2_NAME = "bancor_v2"
BANCOR_V3_NAME = "bancor_v3"
CARBON_POL_NAME = "bancor_pol"
UNISWAP_V2_NAME = "uniswap_v2"
UNISWAP_V3_NAME = "uniswap_v3"
SUSHISWAP_V2_NAME = "sushiswap_v2"
SUSHISWAP_V3_NAME = "sushiswap_v3"
CARBON_V1_NAME = "carbon_v1"
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
            PLATFORM_NAME_WRAP_UNWRAP: 10,
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


# +
@dataclass
class Config:
    ZERO_ADDRESS = ZERO_ADDRESS
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
    PLATFORM_NAME_WRAP_UNWRAP = PLATFORM_NAME_WRAP_UNWRAP

cfg = Config()


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
class QueryInterface:
    test_pools = _test_pools

    def get_pool_from_dict(self, cid):
        cid = cid.split("-")[0]
        return next((pool for pool in self.test_pools if pool["cid"] == cid), None)

    def get_pool(self, cid):
        pool_dict = self.get_pool_from_dict(cid)
        pool = _test_create_pool(pool_dict)
        return pool

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
                    "tknin": "0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE",
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
raw_tx_list_0_split_0 = [raw_tx_0]
raw_tx_list_0_split_1 = [raw_tx_1]

#### WETH ONLY ####
raw_tx_list_1 = [raw_tx_0, raw_tx_0]

#### ETH ONLY ####
raw_tx_list_2 = [raw_tx_1, raw_tx_1]


#### NEITHER ####
raw_tx_list_3 = [raw_tx_2, raw_tx_3]


raw_tx_str_0 = str(raw_tx_list_0)
raw_tx_str_0_split_0 = str(raw_tx_list_0_split_0)
raw_tx_str_0_split_1 = str(raw_tx_list_0_split_1)

raw_tx_str_1 = str(raw_tx_list_1)
raw_tx_str_2 = str(raw_tx_list_2)

raw_tx_str_3 = str(raw_tx_list_3)

trade_instruction_0_split_0 = TradeInstruction(
    cid='67035626283424877302284797664058337657416-0',
    tknin='0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2',
    amtin=10,
    tknout='0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599',
    amtout=1.0,
    ConfigObj=cfg,
    db = db,
    tknin_dec_override =  18,
    tknout_dec_override = 8,
    tknin_addr_override = '0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2',
    tknout_addr_override = '0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599',
    exchange_override = 'carbon_v1',
    raw_txs=raw_tx_str_0_split_0,
)
trade_instruction_0_split_1 = TradeInstruction(
    cid='67035626283424877302284797664058337657416-0',
    tknin='0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE',
    amtin=5,
    tknout='0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599',
    amtout=0.5,
    ConfigObj=cfg,
    db = db,
    tknin_dec_override =  18,
    tknout_dec_override = 8,
    tknin_addr_override = '0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2',
    tknout_addr_override = '0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599',
    exchange_override = 'carbon_v1',
    raw_txs=raw_tx_str_0_split_1,
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
    tknin=ETH_ADDRESS,
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
trade_instruction_3_split = TradeInstruction(
    cid='0x1c15cb883c57ebba91d3e698aef9311ccd5e45ad3b8005e548d02290ed1ad974',
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

def _test_add_wrap_or_unwrap_trades_to_route(flashloans, routes, trade_instructions, token_amounts):
    new_routes = add_wrap_or_unwrap_trades_to_route(cfg, flashloans, routes, trade_instructions)

    for trade in new_routes:
        token_amounts[trade['sourceToken']] -= trade['sourceAmount']
        token_amounts[trade['targetToken']] += trade['minTargetAmount']
    for token, amount in token_amounts.items():
        assert amount >= 0, f'negative balance found: {token}: {amount}'

def test_add_wrap_or_unwrap_trades_to_route():
    flashloans_0 = [{'platformId': 2, 'sourceTokens': ['0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE'], 'sourceAmounts': [15000000000000000000]}]
    flashloans_1 = [{'platformId': 7, 'sourceTokens': ['0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2'], 'sourceAmounts': [20000000000000000000]}]
    flashloans_2 = [{'platformId': 2, 'sourceTokens': ['0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE'], 'sourceAmounts': [10000000000000000000]}]
    flashloans_3 = [{'platformId': 2, 'sourceTokens': ['0x1F573D6Fb3F13d689FF844B4cE37794d79a7FF1C'], 'sourceAmounts': [15000000000000000000]}]

    routes_0 = [{'platformId': 6, 'sourceToken': '0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE', 'targetToken': '0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599', 'sourceAmount': 5000000000000000000, 'minTargetAmount': 50000000, 'deadline': 12345678, 'customAddress': '0xC537e898CD774e2dCBa3B14Ea6f34C93d5eA45e1', 'customInt': 0, 'customData': '0x000000000000000000000000000000000000000000000000000000000000002000000000000000000000000000000000000000000000000000000000000000010000000000000000000000000000001b000000000000000000000000000000c10000000000000000000000000000000000000000000000004563918244f40000'}, {'platformId': 6, 'sourceToken': '0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2', 'targetToken': '0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599', 'sourceAmount': 10000000000000000000, 'minTargetAmount': 100000000, 'deadline': 12345678, 'customAddress': '0xC537e898CD774e2dCBa3B14Ea6f34C93d5eA45e1', 'customInt': 0, 'customData': '0x00000000000000000000000000000000000000000000000000000000000000200000000000000000000000000000000000000000000000000000000000000001000000000000000000000000000000c5000000000000000000000000000002480000000000000000000000000000000000000000000000008ac7230489e80000'}, {'platformId': 4, 'sourceToken': '0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599', 'targetToken': '0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2', 'sourceAmount': 150000000, 'minTargetAmount': 15000000000000000000, 'deadline': 12345678, 'customAddress': '0xE592427A0AEce92De3Edee1F18E0157C05861564', 'customInt': 3000, 'customData': '0x0000000000000000000000000000000000000000000000000000000000000000'}]
    routes_1 = [{'platformId': 6, 'sourceToken': '0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2', 'targetToken': '0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599', 'sourceAmount': 20000000000000000000, 'minTargetAmount': 200000000, 'deadline': 12345678, 'customAddress': '0xC537e898CD774e2dCBa3B14Ea6f34C93d5eA45e1', 'customInt': 0, 'customData': '0x00000000000000000000000000000000000000000000000000000000000000200000000000000000000000000000000000000000000000000000000000000002000000000000000000000000000000c5000000000000000000000000000002480000000000000000000000000000000000000000000000008ac7230489e80000000000000000000000000000000000c5000000000000000000000000000002480000000000000000000000000000000000000000000000008ac7230489e80000'}, {'platformId': 4, 'sourceToken': '0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599', 'targetToken': '0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2', 'sourceAmount': 200000000, 'minTargetAmount': 20000000000000000000, 'deadline': 12345678, 'customAddress': '0xE592427A0AEce92De3Edee1F18E0157C05861564', 'customInt': 3000, 'customData': '0x0000000000000000000000000000000000000000000000000000000000000000'}]
    routes_2 = [{'platformId': 6, 'sourceToken': '0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE', 'targetToken': '0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599', 'sourceAmount': 10000000000000000000, 'minTargetAmount': 100000000, 'deadline': 12345678, 'customAddress': '0xC537e898CD774e2dCBa3B14Ea6f34C93d5eA45e1', 'customInt': 0, 'customData': '0x000000000000000000000000000000000000000000000000000000000000002000000000000000000000000000000000000000000000000000000000000000020000000000000000000000000000001b000000000000000000000000000000c10000000000000000000000000000000000000000000000004563918244f400000000000000000000000000000000001b000000000000000000000000000000c10000000000000000000000000000000000000000000000004563918244f40000'}, {'platformId': 4, 'sourceToken': '0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599', 'targetToken': '0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2', 'sourceAmount': 100000000, 'minTargetAmount': 10000000000000000000, 'deadline': 12345678, 'customAddress': '0xE592427A0AEce92De3Edee1F18E0157C05861564', 'customInt': 3000, 'customData': '0x0000000000000000000000000000000000000000000000000000000000000000'}]
    routes_3 = [{'platformId': 6, 'sourceToken': '0x1F573D6Fb3F13d689FF844B4cE37794d79a7FF1C', 'targetToken': '0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48', 'sourceAmount': 15000000000000000000, 'minTargetAmount': 150000000, 'deadline': 12345678, 'customAddress': '0xC537e898CD774e2dCBa3B14Ea6f34C93d5eA45e1', 'customInt': 0, 'customData': '0x00000000000000000000000000000000000000000000000000000000000000200000000000000000000000000000000000000000000000000000000000000002000000000000000000000000000000070000000000000000000000000000017c0000000000000000000000000000000000000000000000008ac7230489e8000000000000000000000000000000000007000000000000000000000000000001e40000000000000000000000000000000000000000000000004563918244f40000'}, {'platformId': 1, 'sourceToken': '0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48', 'targetToken': '0x1F573D6Fb3F13d689FF844B4cE37794d79a7FF1C', 'sourceAmount': 150000000, 'minTargetAmount': 15000000000000000000, 'deadline': 12345678, 'customAddress': '0x874d8dE5b26c9D9f6aA8d7bab283F9A9c6f777f4', 'customInt': 0, 'customData': '0x'}]

    trade_instructions_0 = [trade_instruction_0_split_0, trade_instruction_0_split_1, trade_instruction_3_split]
    #### WETH ONLY ####
    trade_instructions_1 = [trade_instruction_1, trade_instruction_3]
    #### ETH ONLY ####
    trade_instructions_2 = [trade_instruction_2, trade_instruction_4]
    #### NEITHER ####
    trade_instructions_3 = [trade_instruction_5, trade_instruction_6]

    token_amounts_0 = {'0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2': 0, '0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE': 15000000000000000000, '0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599': 0}
    token_amounts_1 = {'0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2': 20000000000000000000, '0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE': 0, '0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599': 0}
    token_amounts_2 = {'0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2': 0, '0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE': 10000000000000000000, '0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599': 0}
    token_amounts_3 = {'0x1F573D6Fb3F13d689FF844B4cE37794d79a7FF1C': 15000000000000000000, '0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48': 0}

    _test_add_wrap_or_unwrap_trades_to_route(flashloans_0, routes_0, trade_instructions_0, token_amounts_0)
    _test_add_wrap_or_unwrap_trades_to_route(flashloans_1, routes_1, trade_instructions_1, token_amounts_1)
    _test_add_wrap_or_unwrap_trades_to_route(flashloans_2, routes_2, trade_instructions_2, token_amounts_2)
    _test_add_wrap_or_unwrap_trades_to_route(flashloans_3, routes_3, trade_instructions_3, token_amounts_3)

test_add_wrap_or_unwrap_trades_to_route()