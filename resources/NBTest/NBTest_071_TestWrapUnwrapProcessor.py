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

from fastlane_bot.helpers import TradeInstruction, TxRouteHandler, WrapUnwrapProcessor
from fastlane_bot.testing import *
from dataclasses import dataclass
from fastlane_bot.helpers.poolandtokens import PoolAndTokens
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
    PLATFORM_ID_WRAP_UNWRAP = PLATFORM_ID_WRAP_UNWRAP

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

@dataclass
class QueryInterface:
    test_pools = test_pools

    def get_pool_from_dict(self, cid):
        cid = cid.split("-")[0]
        return next((pool for pool in self.test_pools if pool["cid"] == cid), None)

    def get_pool(self, cid):
        pool_dict = self.get_pool_from_dict(cid)
        pool = _test_create_pool(0, cfg, pool_dict)
        return pool

db = QueryInterface()
# -





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
    raw_txs=raw_tx_str_0,
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

# Get the deadline
deadline = 12345678

flashloan_struct_0 = [{'platformId': 2, 'sourceTokens': ['0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE'], 'sourceAmounts': [5000000000000000000]}]
flashloan_struct_1 = [{'platformId': 7, 'sourceTokens': ['0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2'], 'sourceAmounts': [20000000000000000000]}]
flashloan_struct_2 = [{'platformId': 2, 'sourceTokens': ['0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE'], 'sourceAmounts': [10000000000000000000]}]
flashloan_struct_3 = [{'platformId': 2, 'sourceTokens': ['0x1F573D6Fb3F13d689FF844B4cE37794d79a7FF1C'], 'sourceAmounts': [15000000000000000000]}]

# Get the route struct
route_struct_0 = [{'platformId': 6, 'sourceToken': '0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE', 'targetToken': '0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599', 'sourceAmount': 5000000000000000000, 'minTargetAmount': 50000000, 'deadline': 12345678, 'customAddress': '0xC537e898CD774e2dCBa3B14Ea6f34C93d5eA45e1', 'customInt': 0, 'customData': '0x000000000000000000000000000000000000000000000000000000000000002000000000000000000000000000000000000000000000000000000000000000010000000000000000000000000000001b000000000000000000000000000000c10000000000000000000000000000000000000000000000004563918244f40000'}, {'platformId': 6, 'sourceToken': '0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2', 'targetToken': '0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599', 'sourceAmount': 10000000000000000000, 'minTargetAmount': 100000000, 'deadline': 12345678, 'customAddress': '0xC537e898CD774e2dCBa3B14Ea6f34C93d5eA45e1', 'customInt': 0, 'customData': '0x00000000000000000000000000000000000000000000000000000000000000200000000000000000000000000000000000000000000000000000000000000001000000000000000000000000000000c5000000000000000000000000000002480000000000000000000000000000000000000000000000008ac7230489e80000'}, {'platformId': 4, 'sourceToken': '0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599', 'targetToken': '0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2', 'sourceAmount': 200000000, 'minTargetAmount': 20000000000000000000, 'deadline': 12345678, 'customAddress': '0xE592427A0AEce92De3Edee1F18E0157C05861564', 'customInt': 3000, 'customData': '0x0000000000000000000000000000000000000000000000000000000000000000'}]
route_struct_1 = [{'platformId': 6, 'sourceToken': '0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2', 'targetToken': '0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599', 'sourceAmount': 20000000000000000000, 'minTargetAmount': 200000000, 'deadline': 12345678, 'customAddress': '0xC537e898CD774e2dCBa3B14Ea6f34C93d5eA45e1', 'customInt': 0, 'customData': '0x00000000000000000000000000000000000000000000000000000000000000200000000000000000000000000000000000000000000000000000000000000002000000000000000000000000000000c5000000000000000000000000000002480000000000000000000000000000000000000000000000008ac7230489e80000000000000000000000000000000000c5000000000000000000000000000002480000000000000000000000000000000000000000000000008ac7230489e80000'}, {'platformId': 4, 'sourceToken': '0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599', 'targetToken': '0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2', 'sourceAmount': 200000000, 'minTargetAmount': 20000000000000000000, 'deadline': 12345678, 'customAddress': '0xE592427A0AEce92De3Edee1F18E0157C05861564', 'customInt': 3000, 'customData': '0x0000000000000000000000000000000000000000000000000000000000000000'}]
route_struct_2 = [{'platformId': 6, 'sourceToken': '0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE', 'targetToken': '0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599', 'sourceAmount': 10000000000000000000, 'minTargetAmount': 100000000, 'deadline': 12345678, 'customAddress': '0xC537e898CD774e2dCBa3B14Ea6f34C93d5eA45e1', 'customInt': 0, 'customData': '0x000000000000000000000000000000000000000000000000000000000000002000000000000000000000000000000000000000000000000000000000000000020000000000000000000000000000001b000000000000000000000000000000c10000000000000000000000000000000000000000000000004563918244f400000000000000000000000000000000001b000000000000000000000000000000c10000000000000000000000000000000000000000000000004563918244f40000'}, {'platformId': 4, 'sourceToken': '0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599', 'targetToken': '0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2', 'sourceAmount': 100000000, 'minTargetAmount': 10000000000000000000, 'deadline': 12345678, 'customAddress': '0xE592427A0AEce92De3Edee1F18E0157C05861564', 'customInt': 3000, 'customData': '0x0000000000000000000000000000000000000000000000000000000000000000'}]
route_struct_3 = [{'platformId': 6, 'sourceToken': '0x1F573D6Fb3F13d689FF844B4cE37794d79a7FF1C', 'targetToken': '0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48', 'sourceAmount': 15000000000000000000, 'minTargetAmount': 150000000, 'deadline': 12345678, 'customAddress': '0xC537e898CD774e2dCBa3B14Ea6f34C93d5eA45e1', 'customInt': 0, 'customData': '0x00000000000000000000000000000000000000000000000000000000000000200000000000000000000000000000000000000000000000000000000000000002000000000000000000000000000000070000000000000000000000000000017c0000000000000000000000000000000000000000000000008ac7230489e8000000000000000000000000000000000007000000000000000000000000000001e40000000000000000000000000000000000000000000000004563918244f40000'}, {'platformId': 1, 'sourceToken': '0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48', 'targetToken': '0x1F573D6Fb3F13d689FF844B4cE37794d79a7FF1C', 'sourceAmount': 150000000, 'minTargetAmount': 15000000000000000000, 'deadline': 12345678, 'customAddress': '0x874d8dE5b26c9D9f6aA8d7bab283F9A9c6f777f4', 'customInt': 0, 'customData': '0x'}]

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

    _segments_0 = _processor_0._segment_routes([trade_instruction_0_split_0, trade_instruction_0_split_1, trade_instruction_3], route_struct_0)
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


    
test_handle_wrap_or_unwrap()


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

    assert _new_route_struct_0[0]['platformId'] == 4, _new_route_struct_0
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








