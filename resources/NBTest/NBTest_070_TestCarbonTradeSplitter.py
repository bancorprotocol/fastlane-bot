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
from fastlane_bot.helpers import TradeInstruction, split_carbon_trades

plt.rcParams['figure.figsize'] = [12,6]
from fastlane_bot import __VERSION__
require('3.0', __VERSION__)

BANCOR_V2_NAME      = 'bancor_v2'
CARBON_V1_NAME      = 'carbon_v1'
PANCAKESWAP_V2_NAME = 'pancakeswap_v2'

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
    EXCHANGE_IDS = {BANCOR_V2_NAME: 1, CARBON_V1_NAME: 2, PANCAKESWAP_V2_NAME: 3}
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

trade_instruction_0 = TradeInstruction(
    cid='CID1-0',
    tknin=WETH_ADDRESS,
    tknout=WBTC_ADDRESS,
    amtin=15,
    amtout=1.5,
    ConfigObj=cfg,
    db=db,
    tknin_dec_override=18,
    tknout_dec_override=8,
    tknin_addr_override=WETH_ADDRESS,
    tknout_addr_override=WBTC_ADDRESS,
    exchange_override=CARBON_V1_NAME,
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
                'cid': 'CID2-0',
                'tknin': WETH_ADDRESS,
                'tknout': WBTC_ADDRESS,
                'amtin': 5,
                'amtout': 0.5,
                '_amtin_wei': 5000000000000000000,
                '_amtout_wei': 50000000,
            },
        ]
    ),
)

trade_instruction_1 = TradeInstruction(
    cid='CID1-0',
    tknin=WETH_ADDRESS,
    tknout=WBTC_ADDRESS,
    amtin=20,
    amtout=2,
    ConfigObj=cfg,
    db=db,
    tknin_dec_override=18,
    tknout_dec_override=8,
    tknin_addr_override=WETH_ADDRESS,
    tknout_addr_override=WBTC_ADDRESS,
    exchange_override=CARBON_V1_NAME,
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

trade_instruction_2 = TradeInstruction(
    cid='CID1-0',
    tknin=WETH_ADDRESS,
    tknout=WBTC_ADDRESS,
    amtin=10,
    amtout=1,
    ConfigObj=cfg,
    db=db,
    tknin_dec_override=18,
    tknout_dec_override=8,
    tknin_addr_override=WETH_ADDRESS,
    tknout_addr_override=WBTC_ADDRESS,
    exchange_override=CARBON_V1_NAME,
    raw_txs=dumps(
        [
            {
                'cid': 'CID2-0',
                'tknin': WETH_ADDRESS,
                'tknout': WBTC_ADDRESS,
                'amtin': 5,
                'amtout': 0.5,
                '_amtin_wei': 5000000000000000000,
                '_amtout_wei': 50000000,
            },
            {
                'cid': 'CID2-0',
                'tknin': WETH_ADDRESS,
                'tknout': WBTC_ADDRESS,
                'amtin': 5,
                'amtout': 0.5,
                '_amtin_wei': 5000000000000000000,
                '_amtout_wei': 50000000,
            }
        ]
    ),
)

trade_instruction_3 = TradeInstruction(
    cid='CID5-0',
    tknin=WBTC_ADDRESS,
    tknout=WETH_ADDRESS,
    amtin=2,
    amtout=20,
    ConfigObj=cfg,
    db=db,
    tknin_dec_override=8,
    tknout_dec_override=18,
    tknin_addr_override=WBTC_ADDRESS,
    tknout_addr_override=WETH_ADDRESS,
    exchange_override=PANCAKESWAP_V2_NAME,
)

trade_instruction_4 = TradeInstruction(
    cid='CID5-0',
    tknin=WBTC_ADDRESS,
    tknout=WETH_ADDRESS,
    amtin=1,
    amtout=10,
    ConfigObj=cfg,
    db=db,
    tknin_dec_override=8,
    tknout_dec_override=18,
    tknin_addr_override=WBTC_ADDRESS,
    tknout_addr_override=WETH_ADDRESS,
    exchange_override=PANCAKESWAP_V2_NAME,
)

trade_instruction_5 = TradeInstruction(
    cid='CID1-0',
    tknin=BNT_ADDRESS,
    tknout=USDC_ADDRESS,
    amtin=15,
    amtout=150,
    ConfigObj=cfg,
    db=db,
    tknin_dec_override=18,
    tknout_dec_override=6,
    tknin_addr_override=BNT_ADDRESS,
    tknout_addr_override=USDC_ADDRESS,
    exchange_override=CARBON_V1_NAME,
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

trade_instruction_6 = TradeInstruction(
    cid='CID6-0',
    tknin=USDC_ADDRESS,
    tknout=BNT_ADDRESS,
    amtin=150,
    amtout=15,
    ConfigObj=cfg,
    db=db,
    tknin_dec_override=6,
    tknout_dec_override=18,
    tknin_addr_override=USDC_ADDRESS,
    tknout_addr_override=BNT_ADDRESS,
    exchange_override=BANCOR_V2_NAME,
)

trade_instruction_7 = TradeInstruction(
    cid='CID1-0',
    tknin=WETH_ADDRESS,
    tknout=WBTC_ADDRESS,
    amtin=10,
    amtout=1,
    _amtin_wei=10000000000000000000,
    _amtout_wei=100000000,
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

trade_instruction_8 = TradeInstruction(
    cid='CID2-0',
    tknin=ETH_ADDRESS,
    tknout=WBTC_ADDRESS,
    amtin=5,
    amtout=0.5,
    _amtin_wei=5000000000000000000,
    _amtout_wei=50000000,
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

trade_instruction_9 = TradeInstruction(
    cid='CID5-0',
    tknin=WBTC_ADDRESS,
    tknout=WETH_ADDRESS,
    amtin=2,
    amtout=20,
    _amtin_wei=200000000,
    _amtout_wei=20000000000000000000,
    tknin_dec_override=8,
    tknout_dec_override=18,
    tknin_addr_override=WBTC_ADDRESS,
    tknout_addr_override=WETH_ADDRESS,
    exchange_override=PANCAKESWAP_V2_NAME,
    ConfigObj=cfg,
    db=db,
    raw_txs=dumps([]),
)

trade_instruction_10 = TradeInstruction(
    cid='CID1-0',
    tknin=WETH_ADDRESS,
    tknout=WBTC_ADDRESS,
    amtin=20,
    amtout=2,
    _amtin_wei=20000000000000000000,
    _amtout_wei=200000000,
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

trade_instruction_11 = TradeInstruction(
    cid='CID2-0',
    tknin=ETH_ADDRESS,
    tknout=WBTC_ADDRESS,
    amtin=10,
    amtout=1.0,
    _amtin_wei=10000000000000000000,
    _amtout_wei=100000000,
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

trade_instruction_12 = TradeInstruction(
    cid='CID5-0',
    tknin=WBTC_ADDRESS,
    tknout=WETH_ADDRESS,
    amtin=1,
    amtout=10,
    _amtin_wei=100000000,
    _amtout_wei=10000000000000000000,
    tknin_dec_override=8,
    tknout_dec_override=18,
    tknin_addr_override=WBTC_ADDRESS,
    tknout_addr_override=WETH_ADDRESS,
    exchange_override=PANCAKESWAP_V2_NAME,
    ConfigObj=cfg,
    db=db,
    raw_txs=dumps([]),
)

trade_instruction_13 = TradeInstruction(
    cid='CID3-0',
    tknin=BNT_ADDRESS,
    tknout=USDC_ADDRESS,
    amtin=15,
    amtout=150,
    _amtin_wei=15000000000000000000,
    _amtout_wei=150000000,
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

trade_instruction_14 = TradeInstruction(
    cid='CID6-0',
    tknin=USDC_ADDRESS,
    tknout=BNT_ADDRESS,
    amtin=150,
    amtout=15,
    _amtin_wei=150000000,
    _amtout_wei=15000000000000000000,
    tknin_dec_override=6,
    tknout_dec_override=18,
    tknin_addr_override=USDC_ADDRESS,
    tknout_addr_override=BNT_ADDRESS,
    exchange_override=BANCOR_V2_NAME,
    ConfigObj=cfg,
    db=db,
    raw_txs=dumps([]),
)

input_list_0 = [trade_instruction_0, trade_instruction_3]
input_list_1 = [trade_instruction_1, trade_instruction_3]
input_list_2 = [trade_instruction_2, trade_instruction_4]
input_list_3 = [trade_instruction_5, trade_instruction_6]

expected_output_list_0 = [trade_instruction_7, trade_instruction_8, trade_instruction_9]
expected_output_list_1 = [trade_instruction_10, trade_instruction_9]
expected_output_list_2 = [trade_instruction_11, trade_instruction_12]
expected_output_list_3 = [trade_instruction_13, trade_instruction_14]

def _test_split_carbon_trades(cfg, input_list, expected_output_list):
    actual_output_list = split_carbon_trades(cfg, input_list)
    assert len(actual_output_list) == len(expected_output_list)
    for actual_output, expected_output in zip(actual_output_list, expected_output_list):
        assert actual_output.ConfigObj            == expected_output.ConfigObj           
        assert actual_output.cid                  == expected_output.cid                 
        assert actual_output.tknin                == expected_output.tknin               
        assert actual_output.amtin                == expected_output.amtin               
        assert actual_output.tknout               == expected_output.tknout              
        assert actual_output.amtout               == expected_output.amtout              
        assert actual_output.pair_sorting         == expected_output.pair_sorting        
        assert actual_output.raw_txs              == expected_output.raw_txs             
        assert actual_output.custom_data          == expected_output.custom_data         
        assert actual_output.db                   == expected_output.db                  
        assert actual_output.tknin_dec_override   == expected_output.tknin_dec_override  
        assert actual_output.tknout_dec_override  == expected_output.tknout_dec_override 
        assert actual_output.tknin_addr_override  == expected_output.tknin_addr_override 
        assert actual_output.tknout_addr_override == expected_output.tknout_addr_override
        assert actual_output.exchange_override    == expected_output.exchange_override   
        assert actual_output._amtin_wei           == expected_output._amtin_wei          
        assert actual_output._amtout_wei          == expected_output._amtout_wei         
        assert actual_output.tknin_is_native      == expected_output.tknin_is_native     
        assert actual_output.tknout_is_native     == expected_output.tknout_is_native    
        assert actual_output.tknin_is_wrapped     == expected_output.tknin_is_wrapped    
        assert actual_output.tknout_is_wrapped    == expected_output.tknout_is_wrapped   

def test_split_carbon_trades():
    _test_split_carbon_trades(cfg, input_list_0, expected_output_list_0)
    _test_split_carbon_trades(cfg, input_list_1, expected_output_list_1)
    _test_split_carbon_trades(cfg, input_list_2, expected_output_list_2)
    _test_split_carbon_trades(cfg, input_list_3, expected_output_list_3)
