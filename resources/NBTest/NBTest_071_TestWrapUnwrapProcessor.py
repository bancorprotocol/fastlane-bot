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

'''
This module tests the splitting of trade instructions
'''

from json import dumps
from dataclasses import dataclass
from fastlane_bot.testing import plt, require
from fastlane_bot.helpers import TradeInstruction, add_wrap_or_unwrap_trades_to_route

plt.rcParams['figure.figsize'] = [12,6]
from fastlane_bot import __VERSION__
require('3.0', __VERSION__)

BANCOR_V2_NAME      = 'bancor_v2'
CARBON_V1_NAME      = 'carbon_v1'
PANCAKESWAP_V2_NAME = 'pancakeswap_v2'
WRAP_UNWRAP_KEY     = 'wrap_or_unwrap'
WRAP_UNWRAP_VAL     = 1234

NONE_ADDRESS = '0x0000000000000000000000000000000000000000'
ETH_ADDRESS  = '0x1111111111111111111111111111111111111111'
WETH_ADDRESS = '0x2222222222222222222222222222222222222222'
USDC_ADDRESS = '0x3333333333333333333333333333333333333333'
WBTC_ADDRESS = '0x4444444444444444444444444444444444444444'
BNT_ADDRESS  = '0x5555555555555555555555555555555555555555'

@dataclass
class Token:
    symbol: str
    address: str
    decimals: int

@dataclass
class Pool:
    exchange_name: str
    tkn0_address: str
    tkn1_address: str

    @property
    def get_tokens(self):
        return [self.tkn0_address, self.tkn1_address]
    
    @property
    def get_token_addresses(self):
        return [self.tkn0_address, self.tkn1_address]

@dataclass
class Config:
    ZERO_ADDRESS = NONE_ADDRESS
    CARBON_V1_FORKS = [CARBON_V1_NAME]
    NATIVE_GAS_TOKEN_ADDRESS = ETH_ADDRESS
    WRAPPED_GAS_TOKEN_ADDRESS = WETH_ADDRESS
    WRAP_UNWRAP_NAME = WRAP_UNWRAP_KEY
    EXCHANGE_IDS = {WRAP_UNWRAP_NAME: WRAP_UNWRAP_VAL}
    UNI_V2_FORKS = []
    UNI_V3_FORKS = []
    SOLIDLY_V2_FORKS = []
    BALANCER_NAME = []

@dataclass
class DB:
    TOKENS = {
        ETH_ADDRESS : Token(symbol='ETH' , address=ETH_ADDRESS , decimals=18),
        WETH_ADDRESS: Token(symbol='WETH', address=WETH_ADDRESS, decimals=18),
        USDC_ADDRESS: Token(symbol='USDC', address=USDC_ADDRESS, decimals= 6),
        WBTC_ADDRESS: Token(symbol='WBTC', address=WBTC_ADDRESS, decimals= 8),
        BNT_ADDRESS : Token(symbol='BNT' , address=BNT_ADDRESS , decimals=18),
    }

    POOLS = {
        'CID1': Pool(exchange_name=CARBON_V1_NAME     , tkn0_address=WETH_ADDRESS, tkn1_address=WBTC_ADDRESS),
        'CID2': Pool(exchange_name=CARBON_V1_NAME     , tkn0_address=ETH_ADDRESS , tkn1_address=WBTC_ADDRESS),
        'CID3': Pool(exchange_name=CARBON_V1_NAME     , tkn0_address=BNT_ADDRESS , tkn1_address=USDC_ADDRESS),
        'CID4': Pool(exchange_name=CARBON_V1_NAME     , tkn0_address=BNT_ADDRESS , tkn1_address=USDC_ADDRESS),
        'CID5': Pool(exchange_name=PANCAKESWAP_V2_NAME, tkn0_address=WBTC_ADDRESS, tkn1_address=WETH_ADDRESS),
        'CID6': Pool(exchange_name=BANCOR_V2_NAME     , tkn0_address=USDC_ADDRESS, tkn1_address=BNT_ADDRESS ),
    }

    def get_token(self, tkn_address):
        return DB.TOKENS[tkn_address]

    def get_pool(self, cid):
        return DB.POOLS[cid]

cfg = Config()
db = DB()

flashloan_0 = {'sourceTokens': [ETH_ADDRESS ], 'sourceAmounts': [15000000000000000000]}
flashloan_1 = {'sourceTokens': [WETH_ADDRESS], 'sourceAmounts': [20000000000000000000]}
flashloan_2 = {'sourceTokens': [ETH_ADDRESS ], 'sourceAmounts': [10000000000000000000]}
flashloan_3 = {'sourceTokens': [BNT_ADDRESS ], 'sourceAmounts': [15000000000000000000]}

route_0 = {'id': 10, 'deadline': 20}
route_1 = {'id': 11, 'deadline': 21}
route_2 = {'id': 12, 'deadline': 22}
route_3 = {'id': 13, 'deadline': 23}
route_4 = {'id': 14, 'deadline': 24}
route_5 = {'id': 15, 'deadline': 25}
route_6 = {'id': 16, 'deadline': 26}
route_7 = {'id': 17, 'deadline': 27}
route_8 = {'id': 18, 'deadline': 28}

trade_instruction_0 = TradeInstruction(
    cid='CID1-0',
    tknin=WETH_ADDRESS,
    tknout=WBTC_ADDRESS,
    amtin=10,
    amtout=1.0,
    tknin_dec_override=18,
    tknout_dec_override=8,
    tknin_addr_override=WETH_ADDRESS,
    tknout_addr_override=WBTC_ADDRESS,
    exchange_override=CARBON_V1_NAME,
    ConfigObj=cfg,
    db=db,
    raw_txs=dumps(
        [
            {
                'cid': 'CID1-0',
                'tknin': WETH_ADDRESS,
                'tknout': WBTC_ADDRESS,
                'amtin': 10,
                'amtout': 1,
                '_amtin_wei': 10000000000000000000,
                '_amtout_wei': 100000000,
            },
        ]
    ),
)

trade_instruction_1 = TradeInstruction(
    cid='CID1-0',
    tknin=ETH_ADDRESS,
    tknout=WBTC_ADDRESS,
    amtin=5,
    amtout=0.5,
    tknin_dec_override=18,
    tknout_dec_override=8,
    tknin_addr_override=WETH_ADDRESS,
    tknout_addr_override=WBTC_ADDRESS,
    exchange_override=CARBON_V1_NAME,
    ConfigObj=cfg,
    db=db,
    raw_txs=dumps(
        [
            {
                'cid': 'CID2-0',
                'tknin': ETH_ADDRESS,
                'tknout': WBTC_ADDRESS,
                'amtin': 5,
                'amtout': 0.5,
                '_amtin_wei': 5000000000000000000,
                '_amtout_wei': 50000000,
            },
        ]
    ),
)

trade_instruction_2 = TradeInstruction(
    cid='CID5',
    tknin=WBTC_ADDRESS,
    tknout=WETH_ADDRESS,
    amtin=1.5,
    amtout=15,
    tknin_dec_override=8,
    tknout_dec_override=18,
    tknin_addr_override=WBTC_ADDRESS,
    tknout_addr_override=WETH_ADDRESS,
    exchange_override=PANCAKESWAP_V2_NAME,
    ConfigObj=cfg,
    db=db,
    raw_txs=dumps([]),
)

trade_instruction_3 = TradeInstruction(
    cid='CID1-0',
    tknin=WETH_ADDRESS,
    tknout=WBTC_ADDRESS,
    amtin=20,
    amtout=2,
    tknin_dec_override=18,
    tknout_dec_override=8,
    tknin_addr_override=WETH_ADDRESS,
    tknout_addr_override=WBTC_ADDRESS,
    exchange_override=CARBON_V1_NAME,
    ConfigObj=cfg,
    db=db,
    raw_txs=dumps(
        [
            {
                'cid': 'CID1-0',
                'tknin': WETH_ADDRESS,
                'tknout': WBTC_ADDRESS,
                'amtin': 10,
                'amtout': 1,
                '_amtin_wei': 10000000000000000000,
                '_amtout_wei': 100000000,
            },
            {
                'cid': 'CID1-0',
                'tknin': WETH_ADDRESS,
                'tknout': WBTC_ADDRESS,
                'amtin': 10,
                'amtout': 1,
                '_amtin_wei': 10000000000000000000,
                '_amtout_wei': 100000000,
            },
        ]
    ),
)

trade_instruction_4 = TradeInstruction(
    cid='CID5',
    tknin=WBTC_ADDRESS,
    tknout=WETH_ADDRESS,
    amtin=2,
    amtout=20,
    tknin_dec_override=8,
    tknout_dec_override=18,
    tknin_addr_override=WBTC_ADDRESS,
    tknout_addr_override=WETH_ADDRESS,
    exchange_override=PANCAKESWAP_V2_NAME,
    ConfigObj=cfg,
    db=db,
    raw_txs=dumps([]),
)

trade_instruction_5 = TradeInstruction(
    cid='CID1-0',
    tknin=ETH_ADDRESS,
    tknout=WBTC_ADDRESS,
    amtin=10,
    amtout=1,
    tknin_dec_override=18,
    tknout_dec_override=8,
    tknin_addr_override=WETH_ADDRESS,
    tknout_addr_override=WBTC_ADDRESS,
    exchange_override=CARBON_V1_NAME,
    ConfigObj=cfg,
    db=db,
    raw_txs=dumps(
        [
            {
                'cid': 'CID2-0',
                'tknin': ETH_ADDRESS,
                'tknout': WBTC_ADDRESS,
                'amtin': 5,
                'amtout': 0.5,
                '_amtin_wei': 5000000000000000000,
                '_amtout_wei': 50000000,
            },
            {
                'cid': 'CID2-0',
                'tknin': ETH_ADDRESS,
                'tknout': WBTC_ADDRESS,
                'amtin': 5,
                'amtout': 0.5,
                '_amtin_wei': 5000000000000000000,
                '_amtout_wei': 50000000,
            },
        ]
    ),
)

trade_instruction_6 = TradeInstruction(
    cid='CID5',
    tknin=WBTC_ADDRESS,
    tknout=WETH_ADDRESS,
    amtin=1,
    amtout=10,
    tknin_dec_override=8,
    tknout_dec_override=18,
    tknin_addr_override=WBTC_ADDRESS,
    tknout_addr_override=WETH_ADDRESS,
    exchange_override=PANCAKESWAP_V2_NAME,
    ConfigObj=cfg,
    db=db,
    raw_txs=dumps([]),
)

trade_instruction_7 = TradeInstruction(
    cid='CID1-0',
    tknin=BNT_ADDRESS,
    tknout=USDC_ADDRESS,
    amtin=15,
    amtout=150,
    tknin_dec_override=18,
    tknout_dec_override=6,
    tknin_addr_override=BNT_ADDRESS,
    tknout_addr_override=USDC_ADDRESS,
    exchange_override=CARBON_V1_NAME,
    ConfigObj=cfg,
    db=db,
    raw_txs=dumps(
        [
            {
                'cid': 'CID3-0',
                'tknin': BNT_ADDRESS,
                'tknout': USDC_ADDRESS,
                'amtin': 10,
                'amtout': 100,
                '_amtin_wei': 10000000000000000000,
                '_amtout_wei': 100000000,
            },
            {
                'cid': 'CID4-0',
                'tknin': BNT_ADDRESS,
                'tknout': USDC_ADDRESS,
                'amtin': 5,
                'amtout': 50,
                '_amtin_wei': 5000000000000000000,
                '_amtout_wei': 50000000,
            },
        ]
    ),
)

trade_instruction_8 = TradeInstruction(
    cid='CID6-0',
    tknin=USDC_ADDRESS,
    tknout=BNT_ADDRESS,
    amtin=150,
    amtout=15,
    tknin_dec_override=6,
    tknout_dec_override=18,
    tknin_addr_override=USDC_ADDRESS,
    tknout_addr_override=BNT_ADDRESS,
    exchange_override=BANCOR_V2_NAME,
    ConfigObj=cfg,
    db=db,
    raw_txs=dumps([]),
)

input_object_0 = {'flashloans': [flashloan_0], 'routes': [route_0, route_1, route_2], 'trade_instructions': [trade_instruction_0, trade_instruction_1, trade_instruction_2]}
input_object_1 = {'flashloans': [flashloan_1], 'routes': [route_3, route_4], 'trade_instructions': [trade_instruction_3, trade_instruction_4]}
input_object_2 = {'flashloans': [flashloan_2], 'routes': [route_5, route_6], 'trade_instructions': [trade_instruction_5, trade_instruction_6]}
input_object_3 = {'flashloans': [flashloan_3], 'routes': [route_7, route_8], 'trade_instructions': [trade_instruction_7, trade_instruction_8]}

expected_output_list_0 = [
    {
        'platformId': WRAP_UNWRAP_VAL,
        'sourceToken': ETH_ADDRESS,
        'targetToken': WETH_ADDRESS,
        'sourceAmount': 10000000000000000000,
        'minTargetAmount': 10000000000000000000,
        'deadline': route_0['deadline'],
        'customAddress': NONE_ADDRESS,
        'customInt': 0,
        'customData': '0x',
    },
    route_0,
    route_1,
    route_2,
    {
        'platformId': WRAP_UNWRAP_VAL,
        'sourceToken': WETH_ADDRESS,
        'targetToken': ETH_ADDRESS,
        'sourceAmount': 0,
        'minTargetAmount': 0,
        'deadline': route_0['deadline'],
        'customAddress': NONE_ADDRESS,
        'customInt': 0,
        'customData': '0x',
    },
]

expected_output_list_1 = [
    route_3,
    route_4,
]

expected_output_list_2 = [
    route_5,
    route_6,
    {
        'platformId': WRAP_UNWRAP_VAL,
        'sourceToken': WETH_ADDRESS,
        'targetToken': ETH_ADDRESS,
        'sourceAmount': 0,
        'minTargetAmount': 0,
        'deadline': route_5['deadline'],
        'customAddress': NONE_ADDRESS,
        'customInt': 0,
        'customData': '0x',
    },
]

expected_output_list_3 = [
    route_7,
    route_8,
]

def _test_add_wrap_or_unwrap_trades_to_route(cfg, input_object, expected_output_list):
    actual_output_list = add_wrap_or_unwrap_trades_to_route(cfg, input_object['flashloans'], input_object['routes'], input_object['trade_instructions'])
    assert len(actual_output_list) == len(expected_output_list)
    for actual_output, expected_output in zip(actual_output_list, expected_output_list):
        assert actual_output == expected_output

def test_add_wrap_or_unwrap_trades_to_route():
    _test_add_wrap_or_unwrap_trades_to_route(cfg, input_object_0, expected_output_list_0)
    _test_add_wrap_or_unwrap_trades_to_route(cfg, input_object_1, expected_output_list_1)
    _test_add_wrap_or_unwrap_trades_to_route(cfg, input_object_2, expected_output_list_2)
    _test_add_wrap_or_unwrap_trades_to_route(cfg, input_object_3, expected_output_list_3)

test_add_wrap_or_unwrap_trades_to_route()