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
from pytest import fixture
from dataclasses import dataclass
from fastlane_bot.helpers import TradeInstruction, add_wrap_or_unwrap_trades_to_route

BANCOR_V2_NAME      = 'unique_id_1'
CARBON_V1_NAME      = 'unique_id_2'
PANCAKESWAP_V2_NAME = 'unique_id_3'
WRAP_UNWRAP_KEY     = 'unique_id_4'
WRAP_UNWRAP_VAL     = 'unique_id_5'

ETH_ADDRESS  = 'unique_id_11'
WETH_ADDRESS = 'unique_id_22'
USDC_ADDRESS = 'unique_id_33'
WBTC_ADDRESS = 'unique_id_44'
BNT_ADDRESS  = 'unique_id_55'
ZERO_ADDRESS = 'unique_id_66'

CID1 = 'unique_id_111'
CID2 = 'unique_id_222'
CID3 = 'unique_id_333'
CID4 = 'unique_id_444'
CID5 = 'unique_id_555'
CID6 = 'unique_id_666'

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
    ZERO_ADDRESS = ZERO_ADDRESS
    CARBON_V1_FORKS = [CARBON_V1_NAME]
    NATIVE_GAS_TOKEN_ADDRESS = ETH_ADDRESS
    WRAPPED_GAS_TOKEN_ADDRESS = WETH_ADDRESS
    WRAP_UNWRAP_NAME = WRAP_UNWRAP_KEY
    EXCHANGE_IDS = {WRAP_UNWRAP_KEY: WRAP_UNWRAP_VAL}
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
        CID1: Pool(exchange_name=CARBON_V1_NAME     , tkn0_address=WETH_ADDRESS, tkn1_address=WBTC_ADDRESS),
        CID2: Pool(exchange_name=CARBON_V1_NAME     , tkn0_address=ETH_ADDRESS , tkn1_address=WBTC_ADDRESS),
        CID3: Pool(exchange_name=CARBON_V1_NAME     , tkn0_address=BNT_ADDRESS , tkn1_address=USDC_ADDRESS),
        CID4: Pool(exchange_name=CARBON_V1_NAME     , tkn0_address=BNT_ADDRESS , tkn1_address=USDC_ADDRESS),
        CID5: Pool(exchange_name=PANCAKESWAP_V2_NAME, tkn0_address=WBTC_ADDRESS, tkn1_address=WETH_ADDRESS),
        CID6: Pool(exchange_name=BANCOR_V2_NAME     , tkn0_address=USDC_ADDRESS, tkn1_address=BNT_ADDRESS ),
    }

    def get_token(self, tkn_address):
        return DB.TOKENS[tkn_address]

    def get_pool(self, cid):
        return DB.POOLS[cid]

cfg = Config()
db = DB()

trade_instruction_0 = TradeInstruction(
    cid=CID1,
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
                'cid': CID1,
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
    cid=CID1,
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
                'cid': CID2,
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
    cid=CID5,
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
    cid=CID1,
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
                'cid': CID1,
                'tknin': WETH_ADDRESS,
                'tknout': WBTC_ADDRESS,
                'amtin': 10,
                'amtout': 1,
                '_amtin_wei': 10000000000000000000,
                '_amtout_wei': 100000000,
            },
            {
                'cid': CID1,
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
    cid=CID5,
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
    cid=CID1,
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
                'cid': CID2,
                'tknin': ETH_ADDRESS,
                'tknout': WBTC_ADDRESS,
                'amtin': 5,
                'amtout': 0.5,
                '_amtin_wei': 5000000000000000000,
                '_amtout_wei': 50000000,
            },
            {
                'cid': CID2,
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
    cid=CID5,
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
    cid=CID1,
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
                'cid': CID3,
                'tknin': BNT_ADDRESS,
                'tknout': USDC_ADDRESS,
                'amtin': 10,
                'amtout': 100,
                '_amtin_wei': 10000000000000000000,
                '_amtout_wei': 100000000,
            },
            {
                'cid': CID4,
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
    cid=CID6,
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

route_0 = {'deadline': 0}
route_1 = {'deadline': 1}
route_2 = {'deadline': 2}
route_3 = {'deadline': 3}
route_4 = {'deadline': 4}
route_5 = {'deadline': 5}
route_6 = {'deadline': 6}
route_7 = {'deadline': 7}
route_8 = {'deadline': 8}

route_9 = {
    'platformId': WRAP_UNWRAP_VAL,
    'sourceToken': ETH_ADDRESS,
    'targetToken': WETH_ADDRESS,
    'sourceAmount': 10000000000000000000,
    'minTargetAmount': 10000000000000000000,
    'deadline': 0,
    'customAddress': ZERO_ADDRESS,
    'customInt': 0,
    'customData': '0x',
}

route_10 = {
    'platformId': WRAP_UNWRAP_VAL,
    'sourceToken': WETH_ADDRESS,
    'targetToken': ETH_ADDRESS,
    'sourceAmount': 0,
    'minTargetAmount': 0,
    'deadline': 0,
    'customAddress': ZERO_ADDRESS,
    'customInt': 0,
    'customData': '0x',
}

route_11 = {
    'platformId': WRAP_UNWRAP_VAL,
    'sourceToken': WETH_ADDRESS,
    'targetToken': ETH_ADDRESS,
    'sourceAmount': 0,
    'minTargetAmount': 0,
    'deadline': 5,
    'customAddress': ZERO_ADDRESS,
    'customInt': 0,
    'customData': '0x',
}

flashloan_0 = {'sourceTokens': [ETH_ADDRESS ], 'sourceAmounts': [15000000000000000000]}
flashloan_1 = {'sourceTokens': [WETH_ADDRESS], 'sourceAmounts': [20000000000000000000]}
flashloan_2 = {'sourceTokens': [ETH_ADDRESS ], 'sourceAmounts': [10000000000000000000]}
flashloan_3 = {'sourceTokens': [BNT_ADDRESS ], 'sourceAmounts': [15000000000000000000]}

test_cases = [
    {
        'flashloans': [flashloan_0],
        'routes': [route_0, route_1, route_2],
        'trade_instructions': [trade_instruction_0, trade_instruction_1, trade_instruction_2],
        'expected_routes': [route_9, route_0, route_1, route_2, route_10]
    },
    {
        'flashloans': [flashloan_1],
        'routes': [route_3, route_4],
        'trade_instructions': [trade_instruction_3, trade_instruction_4],
        'expected_routes': [route_3, route_4]
    },
    {
        'flashloans': [flashloan_2],
        'routes': [route_5, route_6],
        'trade_instructions': [trade_instruction_5, trade_instruction_6],
        'expected_routes': [route_5, route_6, route_11]
    },
    {
        'flashloans': [flashloan_3],
        'routes': [route_7, route_8],
        'trade_instructions': [trade_instruction_7, trade_instruction_8],
        'expected_routes': [route_7, route_8]
    },
]

@fixture
def cfg_fixture():
    return Config()

@fixture(params=test_cases)

def test_case(request):
    return request.param

def test_add_wrap_or_unwrap_trades_to_route(test_case, cfg_fixture):
    flashloans = test_case['flashloans']
    routes = test_case['routes']
    trade_instructions = test_case['trade_instructions']
    expected_routes = test_case['expected_routes']
    actual_routes = add_wrap_or_unwrap_trades_to_route(cfg_fixture, flashloans, routes, trade_instructions)
    assert actual_routes == expected_routes
