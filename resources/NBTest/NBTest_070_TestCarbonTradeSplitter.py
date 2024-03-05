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

from fastlane_bot.helpers import TradeInstruction, TxRouteHandler, CarbonTradeSplitter
from fastlane_bot.testing import *
from typing import List
from dataclasses import dataclass
from fastlane_bot.helpers.poolandtokens import PoolAndTokens
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

def _test_create_pool(idx, cfg, record):
    tkn0_address, tkn1_address = record["tkn0_address"], record["tkn1_address"]
    tkn0 = tkn0_address
    tkn1 = tkn1_address
    pool = PoolAndTokens(
        ConfigObj=cfg,
        id=idx,
        cid=record.get("cid"),
        last_updated=record.get("last_updated"),
        last_updated_block=record.get("last_updated_block"),
        descr=record.get("descr"),
        pair_name=record.get("pair_name"),
        exchange_name=record.get("exchange_name"),
        fee=record.get("fee"),
        fee_float=record.get("fee_float"),
        tkn0_balance=record.get("tkn0_balance"),
        tkn1_balance=record.get("tkn1_balance"),
        z_0=record.get("z_0"),
        y_0=record.get("y_0"),
        A_0=record.get("A_0"),
        B_0=record.get("B_0"),
        z_1=record.get("z_1"),
        y_1=record.get("y_1"),
        A_1=record.get("A_1"),
        B_1=record.get("B_1"),
        sqrt_price_q96=record.get("sqrt_price_q96"),
        tick=record.get("tick"),
        tick_spacing=record.get("tick_spacing"),
        liquidity=record.get("liquidity"),
        address=record.get("address"),
        anchor=record.get("anchor"),
        tkn0=tkn0,
        tkn1=tkn1,
        tkn0_address=tkn0_address,
        tkn1_address=tkn1_address,
        tkn0_decimals=record.get("tkn0_decimals"),
        tkn1_decimals=record.get("tkn1_decimals"),
        tkn0_weight=record.get("tkn0_weight"),
        tkn1_weight=record.get("tkn1_weight"),
        tkn2=record.get("tkn2"),
        tkn2_balance=record.get("tkn2_balance"),
        tkn2_address=record.get("tkn2_address"),
        tkn2_decimals=record.get("tkn2_decimals"),
        tkn2_weight=record.get("tkn2_weight"),
        tkn3=record.get("tkn3"),
        tkn3_balance=record.get("tkn3_balance"),
        tkn3_address=record.get("tkn3_address"),
        tkn3_decimals=record.get("tkn3_decimals"),
        tkn3_weight=record.get("tkn3_weight"),
        tkn4=record.get("tkn4"),
        tkn4_balance=record.get("tkn4_balance"),
        tkn4_address=record.get("tkn4_address"),
        tkn4_decimals=record.get("tkn4_decimals"),
        tkn4_weight=record.get("tkn4_weight"),
        tkn5=record.get("tkn5"),
        tkn5_balance=record.get("tkn5_balance"),
        tkn5_address=record.get("tkn5_address"),
        tkn5_decimals=record.get("tkn5_decimals"),
        tkn5_weight=record.get("tkn5_weight"),
        tkn6=record.get("tkn6"),
        tkn6_balance=record.get("tkn6_balance"),
        tkn6_address=record.get("tkn6_address"),
        tkn6_decimals=record.get("tkn6_decimals"),
        tkn6_weight=record.get("tkn6_weight"),
        tkn7=record.get("tkn7"),
        tkn7_balance=record.get("tkn7_balance"),
        tkn7_address=record.get("tkn7_address"),
        tkn7_decimals=record.get("tkn7_decimals"),
        tkn7_weight=record.get("tkn7_weight"),
        pool_type=record.get("pool_type"),
    )
    return pool


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


test_pools = [
    {"cid": "67035626283424877302284797664058337657416", "last_updated": float('nan'), "last_updated_block": 18806136, "descr": "carbon_v1 0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2/0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599 2000", "pair_name": "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2/0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599", "exchange_name": "carbon_v1", "fee": "2000", "fee_float": 0.002, "address": "0xC537e898CD774e2dCBa3B14Ea6f34C93d5eA45e1", "anchor": float('nan'), "tkn0_address": "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2", "tkn1_address": "0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599", "tkn0_decimals": 18, "tkn1_decimals": 8, "exchange_id": float('nan'), "tkn0_symbol": "WETH", "tkn1_symbol": "WBTC", "timestamp": float('nan'), "tkn0_balance": float('nan'), "tkn1_balance": float('nan'), "liquidity": float('nan'), "sqrt_price_q96": float('nan'), "tick": float('nan'), "tick_spacing": float('nan'), "exchange": float('nan'), "pool_type": float('nan'), "tkn0_weight": float('nan'), "tkn1_weight": float('nan'), "tkn2_address": float('nan'), "tkn2_decimals": float('nan'), "tkn2_symbol": float('nan'), "tkn2_balance": float('nan'), "tkn2_weight": float('nan'), "tkn3_address": float('nan'), "tkn3_decimals": float('nan'), "tkn3_symbol": float('nan'), "tkn3_balance": float('nan'), "tkn3_weight": float('nan'), "tkn4_address": float('nan'), "tkn4_decimals": float('nan'), "tkn4_symbol": float('nan'), "tkn4_balance": float('nan'), "tkn4_weight": float('nan'), "tkn5_address": float('nan'), "tkn5_decimals": float('nan'), "tkn5_symbol": float('nan'), "tkn5_balance": float('nan'), "tkn5_weight": float('nan'), "tkn6_address": float('nan'), "tkn6_decimals": float('nan'), "tkn6_symbol": float('nan'), "tkn6_balance": float('nan'), "tkn6_weight": float('nan'), "tkn7_address": float('nan'), "tkn7_decimals": float('nan'), "tkn7_symbol": float('nan'), "tkn7_balance": float('nan'), "tkn7_weight": float('nan'), "y_0": 61417813737432694, "z_0": 61417813737432694, "A_0": 4172232392952960.0, "B_0": 5542627325489121.0, "y_1": 0, "z_1": 0, "A_1": 24075842.0, "B_1": 700414721.0},
    {"cid": "9187623906865338513511114400657741709505", "last_updated": float('nan'), "last_updated_block": 18806136, "descr": "carbon_v1 0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE/0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599 2000", "pair_name": "0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE/0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599", "exchange_name": "carbon_v1", "fee": "2000", "fee_float": 0.002, "address": "0xC537e898CD774e2dCBa3B14Ea6f34C93d5eA45e1", "anchor": float('nan'), "tkn0_address": "0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE", "tkn1_address": "0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599", "tkn0_decimals": 18, "tkn1_decimals": 8, "exchange_id": float('nan'), "tkn0_symbol": "ETH", "tkn1_symbol": "WBTC", "timestamp": float('nan'), "tkn0_balance": float('nan'), "tkn1_balance": float('nan'), "liquidity": float('nan'), "sqrt_price_q96": float('nan'), "tick": float('nan'), "tick_spacing": float('nan'), "exchange": float('nan'), "pool_type": float('nan'), "tkn0_weight": float('nan'), "tkn1_weight": float('nan'), "tkn2_address": float('nan'), "tkn2_decimals": float('nan'), "tkn2_symbol": float('nan'), "tkn2_balance": float('nan'), "tkn2_weight": float('nan'), "tkn3_address": float('nan'), "tkn3_decimals": float('nan'), "tkn3_symbol": float('nan'), "tkn3_balance": float('nan'), "tkn3_weight": float('nan'), "tkn4_address": float('nan'), "tkn4_decimals": float('nan'), "tkn4_symbol": float('nan'), "tkn4_balance": float('nan'), "tkn4_weight": float('nan'), "tkn5_address": float('nan'), "tkn5_decimals": float('nan'), "tkn5_symbol": float('nan'), "tkn5_balance": float('nan'), "tkn5_weight": float('nan'), "tkn6_address": float('nan'), "tkn6_decimals": float('nan'), "tkn6_symbol": float('nan'), "tkn6_balance": float('nan'), "tkn6_weight": float('nan'), "tkn7_address": float('nan'), "tkn7_decimals": float('nan'), "tkn7_symbol": float('nan'), "tkn7_balance": float('nan'), "tkn7_weight": float('nan'), "y_0": 352000000000000000, "z_0": 352000000000000000, "A_0": 0.0, "B_0": 5550942688830527.0, "y_1": 0, "z_1": 0, "A_1": 0.0, "B_1": 732916735.0},
    {"cid": "2381976568446569244243622252022377480572", "last_updated": float('nan'), "last_updated_block": 18806136, "descr": "carbon_v1 0x1F573D6Fb3F13d689FF844B4cE37794d79a7FF1C/0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48 2000", "pair_name": "0x1F573D6Fb3F13d689FF844B4cE37794d79a7FF1C/0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48", "exchange_name": "carbon_v1", "fee": "2000", "fee_float": 0.002, "address": "0xC537e898CD774e2dCBa3B14Ea6f34C93d5eA45e1", "anchor": float('nan'), "tkn0_address": "0x1F573D6Fb3F13d689FF844B4cE37794d79a7FF1C", "tkn1_address": "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48", "tkn0_decimals": 18, "tkn1_decimals": 6, "exchange_id": float('nan'), "tkn0_symbol": "BNT", "tkn1_symbol": "USDC", "timestamp": float('nan'), "tkn0_balance": float('nan'), "tkn1_balance": float('nan'), "liquidity": float('nan'), "sqrt_price_q96": float('nan'), "tick": float('nan'), "tick_spacing": float('nan'), "exchange": float('nan'), "pool_type": float('nan'), "tkn0_weight": float('nan'), "tkn1_weight": float('nan'), "tkn2_address": float('nan'), "tkn2_decimals": float('nan'), "tkn2_symbol": float('nan'), "tkn2_balance": float('nan'), "tkn2_weight": float('nan'), "tkn3_address": float('nan'), "tkn3_decimals": float('nan'), "tkn3_symbol": float('nan'), "tkn3_balance": float('nan'), "tkn3_weight": float('nan'), "tkn4_address": float('nan'), "tkn4_decimals": float('nan'), "tkn4_symbol": float('nan'), "tkn4_balance": float('nan'), "tkn4_weight": float('nan'), "tkn5_address": float('nan'), "tkn5_decimals": float('nan'), "tkn5_symbol": float('nan'), "tkn5_balance": float('nan'), "tkn5_weight": float('nan'), "tkn6_address": float('nan'), "tkn6_decimals": float('nan'), "tkn6_symbol": float('nan'), "tkn6_balance": float('nan'), "tkn6_weight": float('nan'), "tkn7_address": float('nan'), "tkn7_decimals": float('nan'), "tkn7_symbol": float('nan'), "tkn7_balance": float('nan'), "tkn7_weight": float('nan'), "y_0": 0, "z_0": 0, "A_0": 0.0, "B_0": 0.0, "y_1": 0, "z_1": 0, "A_1": 0.0, "B_1": 0.0},
    {"cid": "2381976568446569244243622252022377480676", "last_updated": float('nan'), "last_updated_block": 18806136, "descr": "carbon_v1 0x1F573D6Fb3F13d689FF844B4cE37794d79a7FF1C/0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48 2000", "pair_name": "0x1F573D6Fb3F13d689FF844B4cE37794d79a7FF1C/0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48", "exchange_name": "carbon_v1", "fee": "2000", "fee_float": 0.002, "address": "0xC537e898CD774e2dCBa3B14Ea6f34C93d5eA45e1", "anchor": float('nan'), "tkn0_address": "0x1F573D6Fb3F13d689FF844B4cE37794d79a7FF1C", "tkn1_address": "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48", "tkn0_decimals": 18, "tkn1_decimals": 6, "exchange_id": float('nan'), "tkn0_symbol": "BNT", "tkn1_symbol": "USDC", "timestamp": float('nan'), "tkn0_balance": float('nan'), "tkn1_balance": float('nan'), "liquidity": float('nan'), "sqrt_price_q96": float('nan'), "tick": float('nan'), "tick_spacing": float('nan'), "exchange": float('nan'), "pool_type": float('nan'), "tkn0_weight": float('nan'), "tkn1_weight": float('nan'), "tkn2_address": float('nan'), "tkn2_decimals": float('nan'), "tkn2_symbol": float('nan'), "tkn2_balance": float('nan'), "tkn2_weight": float('nan'), "tkn3_address": float('nan'), "tkn3_decimals": float('nan'), "tkn3_symbol": float('nan'), "tkn3_balance": float('nan'), "tkn3_weight": float('nan'), "tkn4_address": float('nan'), "tkn4_decimals": float('nan'), "tkn4_symbol": float('nan'), "tkn4_balance": float('nan'), "tkn4_weight": float('nan'), "tkn5_address": float('nan'), "tkn5_decimals": float('nan'), "tkn5_symbol": float('nan'), "tkn5_balance": float('nan'), "tkn5_weight": float('nan'), "tkn6_address": float('nan'), "tkn6_decimals": float('nan'), "tkn6_symbol": float('nan'), "tkn6_balance": float('nan'), "tkn6_weight": float('nan'), "tkn7_address": float('nan'), "tkn7_decimals": float('nan'), "tkn7_symbol": float('nan'), "tkn7_balance": float('nan'), "tkn7_weight": float('nan'), "y_0": 2709066128420262279740, "z_0": 2709066128420262279740, "A_0": 0.0, "B_0": 5517798046643646.0, "y_1": 0, "z_1": 1, "A_1": 0.0, "B_1": 310899273.0},
    {"cid": "0x1c15cb883c57ebba91d3e698aef9311ccd5e45ad3b8005e548d02290ed1ad974", "last_updated": float('nan'), "last_updated_block": 0, "descr": "pancakeswap_v2 0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599/0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2 3000.0", "pair_name": "0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599/0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2", "exchange_name": "pancakeswap_v2", "fee": 0.0025, "fee_float": 0.0025, "address": "0xCBCdF9626bC03E24f779434178A73a0B4bad62eD", "anchor": float('nan'), "tkn0_address": "0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599", "tkn1_address": "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2", "tkn0_decimals": 8, "tkn1_decimals": 18, "exchange_id": 4.0, "tkn0_symbol": "WBTC", "tkn1_symbol": "WETH", "timestamp": float('nan'), "tkn0_balance": float('nan'), "tkn1_balance": float('nan'), "liquidity": float('nan'), "sqrt_price_q96": float('nan'), "tick": float('nan'), "tick_spacing": 60.0, "exchange": "uniswap_v3", "pool_type": float('nan'), "tkn0_weight": float('nan'), "tkn1_weight": float('nan'), "tkn2_address": float('nan'), "tkn2_decimals": float('nan'), "tkn2_symbol": float('nan'), "tkn2_balance": float('nan'), "tkn2_weight": float('nan'), "tkn3_address": float('nan'), "tkn3_decimals": float('nan'), "tkn3_symbol": float('nan'), "tkn3_balance": float('nan'), "tkn3_weight": float('nan'), "tkn4_address": float('nan'), "tkn4_decimals": float('nan'), "tkn4_symbol": float('nan'), "tkn4_balance": float('nan'), "tkn4_weight": float('nan'), "tkn5_address": float('nan'), "tkn5_decimals": float('nan'), "tkn5_symbol": float('nan'), "tkn5_balance": float('nan'), "tkn5_weight": float('nan'), "tkn6_address": float('nan'), "tkn6_decimals": float('nan'), "tkn6_symbol": float('nan'), "tkn6_balance": float('nan'), "tkn6_weight": float('nan'), "tkn7_address": float('nan'), "tkn7_decimals": float('nan'), "tkn7_symbol": float('nan'), "tkn7_balance": float('nan'), "tkn7_weight": float('nan'), "y_0": float('nan'), "z_0": float('nan'), "A_0": float('nan'), "B_0": float('nan'), "y_1": float('nan'), "z_1": float('nan'), "A_1": float('nan'), "B_1": float('nan')},
    {"cid": "0xa680dccded6454dcad79d49c3a7f246fdb551bf782fcd020ca73bef2c5e0f074", "last_updated": float('nan'), "last_updated_block": 0, "descr": "bancor_v2 0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48/0x1F573D6Fb3F13d689FF844B4cE37794d79a7FF1C 0.01", "pair_name": "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48/0x1F573D6Fb3F13d689FF844B4cE37794d79a7FF1C", "exchange_name": "bancor_v2", "fee": 0.01, "fee_float": 0.01, "address": "0x23d1b2755d6C243DFa9Dd06624f1686b9c9E13EB", "anchor": "0x874d8dE5b26c9D9f6aA8d7bab283F9A9c6f777f4", "tkn0_address": "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48", "tkn1_address": "0x1F573D6Fb3F13d689FF844B4cE37794d79a7FF1C", "tkn0_decimals": 6, "tkn1_decimals": 18, "exchange_id": 1.0, "tkn0_symbol": "USDC", "tkn1_symbol": "BNT", "timestamp": float('nan'), "tkn0_balance": float('nan'), "tkn1_balance": float('nan'), "liquidity": float('nan'), "sqrt_price_q96": float('nan'), "tick": float('nan'), "tick_spacing": float('nan'), "exchange": "bancor_v2", "pool_type": float('nan'), "tkn0_weight": float('nan'), "tkn1_weight": float('nan'), "tkn2_address": float('nan'), "tkn2_decimals": float('nan'), "tkn2_symbol": float('nan'), "tkn2_balance": float('nan'), "tkn2_weight": float('nan'), "tkn3_address": float('nan'), "tkn3_decimals": float('nan'), "tkn3_symbol": float('nan'), "tkn3_balance": float('nan'), "tkn3_weight": float('nan'), "tkn4_address": float('nan'), "tkn4_decimals": float('nan'), "tkn4_symbol": float('nan'), "tkn4_balance": float('nan'), "tkn4_weight": float('nan'), "tkn5_address": float('nan'), "tkn5_decimals": float('nan'), "tkn5_symbol": float('nan'), "tkn5_balance": float('nan'), "tkn5_weight": float('nan'), "tkn6_address": float('nan'), "tkn6_decimals": float('nan'), "tkn6_symbol": float('nan'), "tkn6_balance": float('nan'), "tkn6_weight": float('nan'), "tkn7_address": float('nan'), "tkn7_decimals": float('nan'), "tkn7_symbol": float('nan'), "tkn7_balance": float('nan'), "tkn7_weight": float('nan'), "y_0": float('nan'), "z_0": float('nan'), "A_0": float('nan'), "B_0": float('nan'), "y_1": float('nan'), "z_1": float('nan'), "A_1": float('nan'), "B_1": float('nan')},
              ]

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
    test_pools = test_pools
    test_tokens = _test_tokens
    def get_pool_from_dict(self, cid):
        cid = str(cid).split("-")[0]
        return next((pool for pool in self.test_pools if pool["cid"] == cid), None)

    def get_pool(self, cid):
        pool_dict = self.get_pool_from_dict(cid)
        pool = _test_create_pool(0, cfg, pool_dict)
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




# +
def test_get_token_type():
    trade_splitter = CarbonTradeSplitter(ConfigObj=cfg)
    curve_0 = db.get_pool(cid=67035626283424877302284797664058337657416)
    curve_1 = db.get_pool(cid=9187623906865338513511114400657741709505)
    curve_2 = db.get_pool(cid=2381976568446569244243622252022377480572)

    assert trade_splitter._get_token_type(curve_0) == trade_splitter.WRAPPED
    assert trade_splitter._get_token_type(curve_1) == trade_splitter.NATIVE
    assert trade_splitter._get_token_type(curve_2) == trade_splitter.NEITHER


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


